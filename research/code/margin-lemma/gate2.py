"""Gate 2 (Fraction-exact): Theorem A for the SUB-searches.
For sub-search (t,c): objective g_v(t) over suffixes v with v_1 = c; its mode value H_c(t), runner-up H'_c(t)
(exact, by the same second-best search on the suffix problem), its margin mu = H/H', K_{>t} = max_d #distinct
V[d][t'] over t' > t, and its expansions exp_{t,c}. Claims:
  G2a  H'_c(t) == brute-force second-largest g_v(t)  (T <= 8)
  G2b  per node: every off-path expanded node u of sub-search (t,c) has K_u >= mu and sum_{V_u} g(u.v) >= H_c(t)
  G2c  a priori: mu > K_{>t}  =>  exp_{t,c} <= |v_{c,t}| + 1  (i.e. no off-path expansion)
"""
import random, heapq, time
from fractions import Fraction
from r1core import *
from t9core import brute_suffix_masses

def sub_search_instrumented(sub, W, Hsub, Vsub, c):
    """sub-search rooted at (c) with pi_0 = c forced; frames of sub are 0..L-1; Hsub[d][k] = H_d(t0+k)."""
    L = len(sub)
    root = root_forced(sub, c)
    def parts(node):
        Ab, An = node.Ab, node.An; last = node.u[-1]
        best = node.p; dbest = None; S = [0] * W
        for d in range(1, W):
            s = sum(map(mul, Ab, Hsub[d]))
            if last != d: s += sum(map(mul, An, Hsub[d]))
            S[d] = s
            if s > best: best = s; dbest = d
        return best, dbest, S
    root.B = parts(root)[0]
    inc = root.p; best = root.u; heap = [(-root.B, 0, root)]; cnt = 1; exp = 0; recs = []
    while heap:
        negB, _, node = heapq.heappop(heap)
        if -negB <= inc: break
        exp += 1
        if node.p > inc: inc, best = node.p, node.u
        B, d, S = parts(node)
        rec = dict(u=node.u, B=B, p=node.p, d=d, Sd=S[d] if d else None, K=0, sumc=0, maxc=0)
        if d is not None:
            okv = [node.Ab[k] + (0 if node.u[-1] == d else node.An[k]) for k in range(L + 1)]
            supp = [k for k in range(L) if okv[k] * Hsub[d][k] > 0]
            vs = set(Vsub[d][k] for k in supp)
            comps = {v: suffix_g(node.u + v, sub, 0) for v in vs}
            rec.update(K=len(vs), sumc=sum(comps.values()), maxc=max(comps.values()))
        recs.append(rec)
        for d in range(1, W):
            ch = child(node, d, sub)
            if ch.p > inc: inc, best = ch.p, ch.u
            ch.B = parts(ch)[0]
            if ch.B > inc: cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
    for r in recs: r['onpath'] = (best[:len(r['u'])] == r['u'])
    return best, inc, exp, recs

def sub_second_best(sub, W, Hsub, c, mode):
    root = root_forced(sub, c)
    bnd = lambda n: bound_H(n, Hsub, W)
    root.B = bnd(root); inc = root.p if root.u != mode else 0; best = root.u if root.u != mode else None
    heap = [(-root.B, 0, root)]; cnt = 1
    while heap:
        negB, _, node = heapq.heappop(heap)
        if -negB <= inc: break
        for d in range(1, W):
            ch = child(node, d, sub)
            if ch.u != mode and ch.p > inc: inc, best = ch.p, ch.u
            ch.B = bnd(ch)
            if ch.B > inc: cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
    return best, inc

rng = random.Random(7)
def rand_rows(T, W, F=Fraction):
    rows = []
    for _ in range(T):
        r = [F(rng.randint(1, 30)) for _ in range(W)]; s = sum(r); rows.append([v / s for v in r])
    return rows
def peaky_rows(T, W, conf, F=Fraction):
    conf = F(conf); rows = []
    for _ in range(T):
        win = 0 if rng.random() < 0.7 else rng.randrange(1, W)
        r = [(1 - conf) / (W - 1)] * W; r[win] = conf; rows.append(r)
    return rows
insts = []
for T in (6, 8, 10, 12):
    for W in (3, 4):
        insts.append((f"rand T={T} W={W}", rand_rows(T, W)))
        insts.append((f"peaky0.8 T={T} W={W}", peaky_rows(T, W, Fraction(4, 5))))
        insts.append((f"peaky0.6 T={T} W={W}", peaky_rows(T, W, Fraction(3, 5))))
        insts.append((f"pinned d=1 T={T} W={W}", fam_pinned(T, W, Fraction(1, 2), Fraction(1))))
        insts.append((f"tworate T={T} W={W}", fam_tworate(T, W, Fraction(3, 5), Fraction(1, 4), Fraction(1, 8), Fraction(1, 40))))
n = dict(a=0, b=0, c=0); viol = dict(a=0, b=0, c=0); t0 = time.time(); apriori_hits = 0
for name, tbl in insts:
    T = len(tbl); W = len(tbl[0])
    H, V, sb, per = backward_modes(tbl, W)
    nsub = 0; noff = 0
    for t in range(T):
        sub = tbl[t:]; Hsub = [H[d][t:] for d in range(W)]; Vsub = [V[d][t:] for d in range(W)]
        Kgt = max(len(set(V[d][t2] for t2 in range(t + 1, T) if V[d][t2] is not None)) for d in range(1, W)) if t + 1 < T else 0
        for c in range(1, W):
            if H[c][t] == 0: continue
            v, g, exp, recs = sub_search_instrumented(sub, W, Hsub, Vsub, c)
            assert g == H[c][t] and v == V[c][t]
            v2, g2 = sub_second_best(sub, W, Hsub, c, v)
            mu = (g / g2) if g2 else None
            nsub += 1
            if T <= 8:
                bm = brute_suffix_masses(tbl, W, t, c); vals = sorted(bm.values(), reverse=True)
                n['a'] += 1
                if not (vals[0] == g and (len(vals) < 2 or vals[1] == g2)): viol['a'] += 1; print("  G2a VIOL", name, t, c)
            for r in recs:
                if not r['onpath']:
                    noff += 1; n['b'] += 1
                    if mu is not None and not (r['K'] >= mu and r['sumc'] >= g): viol['b'] += 1; print("  G2b VIOL", name, t, c, r['u'])
            n['c'] += 1
            if mu is None or mu > Kgt:
                apriori_hits += 1
                if exp > len(v) + 1 or any(not r['onpath'] for r in recs): viol['c'] += 1; print("  G2c VIOL", name, t, c, exp, len(v))
    print(f"  {name:22s} sub-searches={nsub} off-path expansions total={noff}", flush=True)
print(f"({time.time()-t0:.0f}s)")
print(f"GATE G2a sub-search runner-up H'_c(t) == brute-force second-largest g_v(t) (T<=8): {n['a']} cells, violations {viol['a']} -> {'PASS' if viol['a']==0 else 'FAIL'}")
print(f"GATE G2b sub-search Theorem A per node (K_u >= mu, sum_{{V_u}} g(u.v) >= H_c(t)): {n['b']} off-path nodes, violations {viol['b']} -> {'PASS' if viol['b']==0 else 'FAIL'}")
print(f"GATE G2c sub-search Theorem A a priori (mu > K_(>t) => exp <= |v|+1): {n['c']} sub-searches ({apriori_hits} with mu > K), violations {viol['c']} -> {'PASS' if viol['c']==0 else 'FAIL'}")

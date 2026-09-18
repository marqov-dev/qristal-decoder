"""R1 harness: margin lemma for the certified-exact CTC decoder (variant 1c).

Uses T9's independent implementation read-only (sys.path import, no bytecode written) for the
primitives (root_empty/root_forced/child/bound_H/best_first/brute_all/prob) and as the reference
decoder. Adds:
  * backward_modes  : the backward pass that also records the ARGMAX suffix string V[d][t] per (d,t)
  * final_instrumented : the final search with per-expanded-node diagnostics
        (on-path flag, B, p, the d attaining S_d, support size, K_u = #distinct suffix modes over the
         support, sum/max of p(u.v) over those modes -> the over-approximation ratio R_d(u))
  * second_best     : exact p2 (runner-up) by the same admissible search excluding the mode
  * enumerate_above : all labellings with p >= theta (complete because B is admissible)
Everything works on Fraction tables (exact) and on float tables.
"""
import sys, os, heapq
sys.dont_write_bytecode = True
from fractions import Fraction
from operator import mul
from itertools import product
T9 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'adversarial-decoder-check')
if T9 not in sys.path: sys.path.insert(0, T9)
from t9core import (decode_exactbwd, brute_all, prob, suffix_g, root_empty, root_forced, child, bound_H,
                    best_first, Stats, compute_H, BLANK, Node)

# ---------------------------------------------------------------- backward pass with argmax strings
def backward_modes(table, W, cap=None):
    """H[d][t], V[d][t] (argmax suffix string), per-search stats [(t,c,exp,gen,len)] ; same searches as
    t9core.compute_H (same order, same bound), so H is identical (gated)."""
    T = len(table)
    H = [[0] * T for _ in range(W)]; V = [[None] * T for _ in range(W)]
    stats = Stats(); per = []
    for t0 in range(T - 1, -1, -1):
        sub = table[t0:]
        Hsub = [H[d][t0:] for d in range(W)]
        for c in range(1, W):
            root = root_forced(sub, c); s = Stats()
            v, g = best_first(root, W, sub, lambda n: bound_H(n, Hsub, W), s, cap=cap)
            stats.exp += s.exp; stats.gen += s.gen
            per.append((t0, c, s.exp, s.gen, len(v)))
            if s.capped: stats.capped = True; return H, V, stats, per
            H[c][t0] = g; V[c][t0] = v
    return H, V, stats, per

# ---------------------------------------------------------------- instrumented final search
def bound_parts(node, H, W):
    """returns (B, p, dbest, S) with S[d] = sum_t ok_d(t-1) H_d(t)  (frames 0-indexed: ok index k = t)."""
    Ab, An = node.Ab, node.An
    last = node.u[-1] if node.u else None
    S = [0] * W; best = node.p; dbest = None
    for d in range(1, W):
        hd = H[d]
        s = sum(map(mul, Ab, hd))
        if last != d: s += sum(map(mul, An, hd))
        S[d] = s
        if s > best: best = s; dbest = d
    return best, node.p, dbest, S

def ok_vec_node(node, d):
    last = node.u[-1] if node.u else None
    Ab, An = node.Ab, node.An
    return [Ab[k] + (0 if last == d else An[k]) for k in range(len(Ab))]

def final_instrumented(table, W, H, V, mode_ref=None, cap=None, diag=True):
    """Final search identical to t9core.best_first(root_empty, bound_H) but records every expanded node.
    rec fields: u, onpath, B, p, d, support (#t with ok_d(t-1)H_d(t)>0), K (distinct V[d][t] over support),
                sumc (sum over those distinct v of p(u.v)), maxc (max over them), Sd."""
    T = len(table)
    root = root_empty(table)
    B0, p0, d0, S0 = bound_parts(root, H, W); root.B = B0
    inc = root.p; best = root.u
    heap = [(-root.B, 0, root)]; cnt = 1
    exp = 0; gen = 0; recs = []; capped = False
    while heap:
        negB, _, node = heapq.heappop(heap)
        if -negB <= inc: break
        exp += 1
        if node.p > inc: inc, best = node.p, node.u
        if diag:
            B, p, d, S = bound_parts(node, H, W)
            rec = dict(u=node.u, B=B, p=p, d=d, Sd=(S[d] if d else None))
            if d is not None:
                okv = ok_vec_node(node, d)
                supp = [t for t in range(T) if okv[t] * H[d][t] > 0]
                vs = {}
                for t in supp: vs.setdefault(V[d][t], []).append(t)
                comps = {v: prob(node.u + v, table) for v in vs}
                rec.update(support=len(supp), K=len(vs), sumc=sum(comps.values()), maxc=max(comps.values()),
                           vs=vs, comps=comps)
            else:
                rec.update(support=0, K=0, sumc=0, maxc=0, vs={}, comps={})
            recs.append(rec)
        for d in range(1, W):
            ch = child(node, d, table); gen += 1
            if cap is not None and gen > cap: capped = True; return dict(mode=best, p=inc, exp=exp, gen=gen, recs=recs, capped=True)
            if ch.p > inc: inc, best = ch.p, ch.u
            ch.B = bound_parts(ch, H, W)[0]
            if ch.B > inc:
                cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
    if diag:
        for r in recs:
            r['onpath'] = (best[:len(r['u'])] == r['u'])
    return dict(mode=best, p=inc, exp=exp, gen=gen, recs=recs, capped=False)

# ---------------------------------------------------------------- exact runner-up
def second_best(table, W, H, mode, cap=None):
    """Best labelling != mode, by the same admissible best-first search (incumbent never set to mode).
    Returns (label2, p2, exp, gen). Admissible because B(u) >= max over ALL completions >= max over
    completions != mode."""
    root = root_empty(table); root.B = bound_H(root, H, W)
    inc = root.p if root.u != mode else 0; best = root.u if root.u != mode else None
    heap = [(-root.B, 0, root)]; cnt = 1; exp = 0; gen = 0
    while heap:
        negB, _, node = heapq.heappop(heap)
        if -negB <= inc: break
        exp += 1
        for d in range(1, W):
            ch = child(node, d, table); gen += 1
            if cap is not None and gen > cap: return None, None, exp, gen
            if ch.u != mode and ch.p > inc: inc, best = ch.p, ch.u
            ch.B = bound_H(ch, H, W)
            if ch.B > inc:
                cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
    return best, inc, exp, gen

def enumerate_above(table, W, H, theta, cap=None):
    """All labellings with p >= theta (theta > 0). Complete: every prefix u of such l has B(u) >= p(l) >= theta."""
    out = {}
    root = root_empty(table)
    stack = [root]; gen = 0
    while stack:
        node = stack.pop()
        if node.p >= theta: out[node.u] = node.p
        for d in range(1, W):
            ch = child(node, d, table); gen += 1
            if cap is not None and gen > cap: return None
            if bound_H(ch, H, W) >= theta: stack.append(ch)
    return out

# ---------------------------------------------------------------- whole pipeline
def analyse(table, W, want_p2=True, want_diag=True, cap=None, cap2=None):
    H, V, sb, per = backward_modes(table, W, cap=cap)
    if sb.capped: return dict(capped=True, gen_back=sb.gen)
    fin = final_instrumented(table, W, H, V, cap=cap, diag=want_diag)
    if fin['capped']: return dict(capped=True, gen_back=sb.gen, gen=sb.gen + fin['gen'])
    mode, ps = fin['mode'], fin['p']
    K = [len(set(v for v in V[d] if v is not None)) for d in range(W)]
    res = dict(mode=mode, p=ps, D=len(mode), exp_final=fin['exp'], gen_final=fin['gen'], gen_back=sb.gen,
               exp_back=sb.exp, gen=sb.gen + fin['gen'], K=max(K[1:]), Kd=K, H=H, V=V, recs=fin['recs'],
               per=per, capped=False)
    if want_p2:
        l2, p2, e2, g2 = second_best(table, W, H, mode, cap=cap2)
        res.update(l2=l2, p2=p2, margin=(ps / p2 if p2 else None), exp2=e2, gen2=g2)
    if want_diag:
        off = [r for r in fin['recs'] if not r['onpath']]
        res.update(n_off=len(off),
                   maxK_off=max([r['K'] for r in off], default=0),
                   maxR_off=max([(r['Sd'] / r['maxc']) for r in off if r['maxc']], default=0),
                   maxKeff_off=max([(r['sumc'] / r['maxc']) for r in off if r['maxc']], default=0))
    return res

# ---------------------------------------------------------------- families (Fraction by default)
def fam_pinned(T, W, rho, delta, boost0=10, F=Fraction):
    """A2 margin2 family: rows [rho, q(1+delta)^(W-2), q(1+delta)^(W-3), ..., q] renormalised, symbol 1
    boosted x boost0 in frame 0. Unique mode 1212... for delta>0."""
    rho = F(rho); delta = F(delta); q = (1 - rho) / (W - 1)
    row = [rho] + [q * (1 + delta) ** (W - 1 - c) for c in range(1, W)]; s = sum(row); row = [v / s for v in row]
    r0 = list(row); r0[1] *= boost0; s0 = sum(r0); r0 = [v / s0 for v in r0]
    return [r0] + [list(row) for _ in range(T - 1)]

def fam_tworate(T, W, rho, a, b, c=None, boost0=10, F=Fraction):
    """rows [rho, a, b, c, c, ...] (renormalised), symbol 1 boosted x boost0 in frame 0."""
    rho = F(rho); a = F(a); b = F(b); c = F(c) if c is not None else b
    row = [rho, a, b] + [c] * (W - 3); s = sum(row); row = [v / s for v in row]
    r0 = list(row); r0[1] *= boost0; s0 = sum(r0); r0 = [v / s0 for v in r0]
    return [r0] + [list(row) for _ in range(T - 1)]

def fam_blankdom(T, W, rho, F=Fraction):
    rho = F(rho); q = (1 - rho) / (W - 1)
    return [[rho] + [q] * (W - 1) for _ in range(T)]

def fam_alt(T, W, rho, F=Fraction):
    rho = F(rho); rows = []
    for t in range(T):
        r = [F(0)] * W
        if t % 2 == 0: r[1] = rho; r[2] = 1 - rho
        else: r[0] = F(1)
        rows.append(r)
    return rows

def to_float(tbl): return [[float(v) for v in r] for r in tbl]

def fmt(x):
    try: return f"{float(x):.4g}"
    except Exception: return str(x)

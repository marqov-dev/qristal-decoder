"""GATE A5 (sharper form of Theorem 1): for every expanded node u of the final search, with d* the maximising symbol
in B(u) and V = {argmax suffix v_t^{d*} : t with ok_{d*}(t-1) H_{d*}(t) > 0} the DISTINCT suffix-mode strings,
there is a labelling l = u.v (v in V) with p(l) >= p*/|V|.  Hence exp_final <= |prefix trie of {l : p(l) >= p*/m}|,
m = max_u |V_u|, and we report m vs T."""
import random, heapq
from fractions import Fraction
from a2core import *
rng = random.Random(5)
def norm(tbl): return [[v / sum(r) for v in r] for r in tbl]
fams = [('peaky0.8', lambda T, W: fam_peaky(T, W, rng, 0.8)), ('peaky0.6', lambda T, W: fam_peaky(T, W, rng, 0.6)),
        ('flat', lambda T, W: fam_flat(T, W)), ('blankdom0.5', lambda T, W: fam_blankdom(T, W, Fraction(1,2))),
        ('random', lambda T, W: norm([[Fraction(rng.randint(1, 30)) for _ in range(W)] for _ in range(T)]))]
n = 0; viol = 0; rows = []
for name, gen in fams:
    for T, W in ((8, 3), (10, 3), (7, 4), (8, 4)):
        for rep in range(2):
            tbl = gen(T, W); ex = brute_all(tbl, W); ps = max(ex.values())
            r = decode_exactbwd(tbl, W); H = r['H']; Hsub = [H[d] for d in range(W)]
            # argmax suffix per (t, d)
            arg = {}
            for t in range(T):
                for d in range(1, W):
                    sm = brute_suffix_masses(tbl, W, t, d); v, g = max(sm.items(), key=lambda kv: kv[1]); arg[(t, d)] = (v, g)
                    assert g == H[d][t]
            # replay final search recording expanded nodes
            root = root_empty(tbl); root.B = bound_H(root, Hsub, W); inc = root.p; heap = [(-root.B, 0, root)]; cnt = 1; expanded = []
            while heap:
                negB, _, node = heapq.heappop(heap)
                if -negB <= inc: break
                expanded.append(node)
                if node.p > inc: inc = node.p
                for d in range(1, W):
                    ch = child(node, d, tbl)
                    if ch.p > inc: inc = ch.p
                    ch.B = bound_H(ch, Hsub, W)
                    if ch.B > inc: cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
            assert len(expanded) == r['exp_final']
            mmax = 0
            for nd in expanded:
                n += 1; u = nd.u; last = u[-1] if u else None
                if nd.B == nd.p and nd.p >= ps: continue   # u itself is a labelling at the mode level
                best = None
                for d in range(1, W):
                    s = 0; V = set()
                    for t in range(T):
                        ok = nd.Ab[t] + (0 if last == d else nd.An[t])
                        if ok > 0 and H[d][t] > 0: s += ok * H[d][t]; V.add(arg[(t, d)][0])
                    if best is None or s > best[0]: best = (s, d, V)
                s, d, V = best
                assert s == nd.B, (s, nd.B)
                mmax = max(mmax, len(V))
                if not any(ex.get(u + v, 0) * len(V) >= ps for v in V): viol += 1
            rows.append((name, T, W, r['exp_final'], mmax))
for row in rows: print("  fam=%s T=%d W=%d exp_final=%d max|V_u|=%d" % row)
print(f"GATE A5 every expanded u has a labelling u.v (v a suffix mode) with p >= p*/|V_u| (distinct suffix modes): {n} expanded nodes, violations {viol} -> {'PASS' if viol==0 else 'FAIL'}")

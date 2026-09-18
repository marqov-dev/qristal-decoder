"""GATE B: Theorem 3 (strict FPT). k non-degenerate frames, all other frames point masses.
Claims: (i) #labellings with p>0 <= W^k; (ii) every search expands only prefixes of positive-probability
labellings, so exp_search <= W^k (T+1) and total exp <= (T(W-1)+1) W^k (T+1); (iii) every expanded node u
has max_v p(u.v) > 0 (checked directly)."""
import random
from fractions import Fraction
from a2core import *
rng = random.Random(3)
n = 0; v1 = v2 = v3 = 0; rows = []
for W in (3, 4):
    for T in ((8, 10, 12) if W == 3 else (8, 10)):
        for k in (0, 1, 2, 3, 4):
            for rep in range(3):
                tbl = fam_strict_k(T, W, k, rng)
                ex = brute_all(tbl, W); pos = {l for l, p in ex.items() if p > 0}
                per = []; r = decode_exactbwd(tbl, W, per_search=per)
                ps = max(ex.values()); assert r['p'] == ps
                n += 1
                if len(pos) > W ** k: v1 += 1
                tot = r['exp_final'] + sum(e for (_, _, e, _, _) in per)
                if r['exp_final'] > W ** k * (T + 1) or any(e > W ** k * (T + 1) for (_, _, e, _, _) in per): v2 += 1
                # (iii): re-run the final search recording expanded prefixes
                H = r['H']; Hsub = [H[d] for d in range(W)]
                expanded = []
                class S2(Stats): pass
                # replicate best_first but record expansions
                import heapq
                root = root_empty(tbl); root.B = bound_H(root, Hsub, W); inc = root.p; heap = [(-root.B, 0, root)]; cnt = 1
                while heap:
                    negB, _, node = heapq.heappop(heap)
                    if -negB <= inc: break
                    expanded.append(node.u)
                    if node.p > inc: inc = node.p
                    for d in range(1, W):
                        ch = child(node, d, tbl)
                        if ch.p > inc: inc = ch.p
                        ch.B = bound_H(ch, Hsub, W)
                        if ch.B > inc: cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
                assert len(expanded) == r['exp_final']
                for u in expanded:
                    if not any(l[:len(u)] == u for l in pos): v3 += 1
                rows.append((W, T, k, len(pos), W ** k, r['exp_final'], tot, (T * (W - 1) + 1) * W ** k * (T + 1)))
for row in rows[::4]: print("  W=%d T=%d k=%d |pos labellings|=%d W^k=%d exp_final=%d exp_total=%d bound_total=%d" % row)
print(f"GATE B1 #positive-probability labellings <= W^k: {n} instances, violations {v1} -> {'PASS' if v1==0 else 'FAIL'}")
print(f"GATE B2 every search exp <= W^k (T+1): {n} instances, violations {v2} -> {'PASS' if v2==0 else 'FAIL'}")
print(f"GATE B3 every expanded final-search node is a prefix of a positive-probability labelling: violations {v3} -> {'PASS' if v3==0 else 'FAIL'}")

"""GATE K: the (k, Lambda) form of Theorem 1. For random tables with k arbitrary frames and T-k frames of confidence
>= 1-eps: p* >= P_g >= (1-eps)^(T-k) W^-k, and exp_final <= (T+1) T / P_g ; total exp over all searches
<= (T+1)T/P_g + sum_{t,c} (L+1)(L-1)/P_g(t+1..T) (float decoder, p* checked by ctc_forward and by brute force at T<=8)."""
import random, math
from a2core import *
rng = random.Random(9); n = 0; v1 = v2 = 0; rows = []
for W in (3, 5):
    for T in (8, 16, 32):
        for k in (0, 2, 4):
            for eps in (0.02, 0.1):
                amb = set(rng.sample(range(T), k)); tbl = []
                for t in range(T):
                    if t in amb: r = [rng.random() for _ in range(W)]
                    else:
                        win = 0 if rng.random() < 0.7 else rng.randrange(1, W)
                        r = [rng.random() * eps for _ in range(W)]; s = sum(r) - r[win]; r = [v * eps / s for v in r]; r[win] = 1 - eps
                    s = sum(r); tbl.append([v / s for v in r])
                per = []; res = decode_exactbwd(tbl, W, per_search=per)
                Pg = greedy_mass(tbl); ps = res['p']
                assert abs(ctc_forward(res['mode'], tbl) - ps) <= 1e-12 * ps
                if T <= 8:
                    ex = brute_all(tbl, W); assert abs(max(ex.values()) - ps) <= 1e-12 * ps
                n += 1
                if ps < Pg * (1 - 1e-12) or Pg < (1 - eps) ** (T - k) * W ** (-k) * (1 - 1e-12): v1 += 1
                tot = res['exp_final'] + sum(e for (_, _, e, _, _) in per)
                bound = (T + 1) * T / Pg
                for (t0, c, e, g, lv) in per:
                    L = T - t0; Pgs = 1
                    for s in range(t0 + 1, T): Pgs *= max(tbl[s])
                    bound += (L + 1) * (L - 1) / Pgs
                if tot > bound: v2 += 1
                rows.append((W, T, k, eps, Pg, ps, res['exp_final'], tot, bound))
for row in rows[::2]: print("  W=%d T=%d k=%d eps=%.2f P_g=%.3g p*=%.3g exp_final=%d exp_total=%d bound_total=%.3g" % row)
print(f"GATE K1 p* >= P_g >= (1-eps)^(T-k) W^-k: {n} tables, violations {v1} -> {'PASS' if v1==0 else 'FAIL'}")
print(f"GATE K2 total expansions <= (T+1)T/P_g + sum_(t,c) (L+1)(L-1)/P_g(t+1..T): {n} tables, violations {v2} -> {'PASS' if v2==0 else 'FAIL'}")

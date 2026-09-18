"""Blank-dominant uniform-residual family at larger T (float decoder): exp_final vs the predicted tie-prefix
lower bound, and the exponent alpha in gen ~ (1/p*)^alpha per (W, rho). Prediction: n* = argmax_n p(no-repeat string
of length n) (via ctc_forward), ties = (W-1)(W-2)^(n*-1), LB1 = sum_{j<=n*-1} #norepeat(j)."""
import math, sys, time
from a2core import *
def rep_string(n): return tuple(1 + (i % 2) for i in range(n))
out = []
for W in (4, 5):
    for rho in (0.5, 0.6, 0.7, 0.8):
        q = (1 - rho) / (W - 1); T = 8
        while True:
            tbl = [[rho] + [q] * (W - 1) for _ in range(T)]
            pn = [ctc_forward(rep_string(n), tbl) for n in range(0, T + 1)]
            nstar = max(range(T + 1), key=lambda n: pn[n]); ps = pn[nstar]
            t0 = time.time(); r = decode_exactbwd(tbl, W, cap=1_500_000); sec = time.time() - t0
            if r['capped']:
                print(f"  W={W} rho={rho} T={T}: CAPPED at {r['gen']} gens (n*={nstar}, predicted LB1={sum(norepeat_count(W,j) for j in range(nstar))})"); break
            LB1 = sum(norepeat_count(W, j) for j in range(nstar)); LB2 = sum(norepeat_count(W, j) for j in range(max(nstar-1,0)))
            assert abs(r['p'] - ps) <= 1e-9 * ps and len(r['mode']) == nstar, (r['p'], ps, r['mode'], nstar)
            row = (W, rho, T, nstar, norepeat_count(W, nstar), r['exp_final'], LB2, LB1, r['exp_back'], r['gen'], 1 / ps, T * q / rho, sec)
            out.append(row)
            print("  W=%d rho=%.1f T=%d n*=%d ties=%d exp_final=%d LB2=%d LB1=%d exp_back=%d gen=%d 1/p*=%.3g pressure=%.2f sec=%.1f" % row, flush=True)
            if r['gen'] > 400_000 or sec > 240: break
            T += 8 if T < 64 else 16
# fits per (W, rho): gen = A (1/p*)^alpha over rows with n* >= 2 and 1/p* >= 30
print("--- fits: gen = A (1/p*)^alpha ; exp_final = A' (1/p*)^alpha' ; also exp_final vs LB1 ---")
import itertools
for (W, rho), grp in itertools.groupby(out, key=lambda r: (r[0], r[1])):
    grp = [g for g in grp if g[3] >= 2 and g[10] >= 30]
    if len(grp) < 3: print(f"  W={W} rho={rho}: <3 usable points"); continue
    xs = [math.log(g[10]) for g in grp]; ys = [math.log(g[9]) for g in grp]; ye = [math.log(g[5]) for g in grp]
    def fit(xs, ys):
        n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
        b = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / sum((x-mx)**2 for x in xs); return b, math.exp(my - b*mx)
    a, A = fit(xs, ys); ae, Ae = fit(xs, ye)
    ratios = [g[5] / g[7] for g in grp]
    print(f"  W={W} rho={rho}: gen = {A:.3g} (1/p*)^{a:.2f} ; exp_final = {Ae:.3g} (1/p*)^{ae:.2f} ; exp_final/LB1 in [{min(ratios):.2f}, {max(ratios):.2f}] ; n* range {grp[0][3]}..{grp[-1][3]} ; T range {grp[0][2]}..{grp[-1][2]}")

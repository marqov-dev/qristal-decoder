"""Scan 2: controlled-margin grid. Family 'rates': rows [rho, A q, B q, q, ...] renormalised (W-1 symbols; symbol 1
rate A, symbol 2 rate B, others 1), symbol 1 boosted x10 at frame 0. For each T the grid over (rho, A, B) is decoded
(float; exactness of the pipeline gated in gate1/scan1), the TRUE margin computed by the exact second-best search, and
for each margin band [m, inf) we report the MAX of exp_final/D, n_off, gen/T^2 over grid cells in the band (with the
cell that attains it). This is the statistic a constant-margin bound must control."""
import sys, time, itertools
from fractions import Fraction
from r1core import *

def fam_rates(T, W, rho, A, B, boost0=10.0):
    q = (1 - rho) / (W - 1)
    row = [rho, A * q, B * q] + [q] * (W - 3); s = sum(row); row = [v / s for v in row]
    r0 = list(row); r0[1] *= boost0; s0 = sum(r0); r0 = [v / s0 for v in r0]
    return [r0] + [list(row) for _ in range(T - 1)]

W = int(sys.argv[1]) if len(sys.argv) > 1 else 4
Ts = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [16, 24, 32, 48, 64, 80]
rhos = (0.4, 0.5, 0.6, 0.7, 0.8)
As = (1.5, 2, 3, 4, 6, 8, 12, 16, 24, 32)
Bs = (1, 1.5, 2, 3, 4, 6, 8)
bands = (1.0, 1.02, 1.05, 1.1, 1.2, 1.3, 1.5, 2.0, 3.0, 4.0)
print(f"# W={W} grid: rho in {rhos}, A in {As}, B in {Bs} (B<=A) ; margin = exact p*/p2")
for T in Ts:
    cells = []; t0 = time.time()
    for rho, A, B in itertools.product(rhos, As, Bs):
        if B > A: continue
        tbl = fam_rates(T, W, rho, A, B)
        r = analyse(tbl, W, want_diag=True, cap=1_500_000, cap2=1_500_000)
        if r['capped'] or r['p2'] is None or r['p2'] == 0: continue
        cells.append(dict(rho=rho, A=A, B=B, m=r['margin'], D=r['D'], exp=r['exp_final'], n_off=r['n_off'], gen=r['gen'],
                          K=r['K'], maxR=r['maxR_off'], maxK=r['maxK_off']))
    print(f"## T={T}: {len(cells)} cells ({time.time()-t0:.0f}s); margin range {min(c['m'] for c in cells):.3f}..{max(c['m'] for c in cells):.3f}")
    print(f"  {'band m>=':>9s} {'#cells':>6s} {'max exp/D':>9s} {'(cell)':>22s} {'max n_off':>9s} {'max exp':>7s} {'max gen/T2':>10s} {'max R_off':>9s} {'max K_u':>7s} {'D range':>9s}")
    for b in bands:
        sel = [c for c in cells if c['m'] >= b]
        if not sel: print(f"  {b:9.2f} {0:6d}"); continue
        w = max(sel, key=lambda c: c['exp'] / max(c['D'], 1))
        print(f"  {b:9.2f} {len(sel):6d} {w['exp']/max(w['D'],1):9.2f} {('rho=%.1f A=%g B=%g m=%.2f' % (w['rho'], w['A'], w['B'], w['m'])):>22s} "
              f"{max(c['n_off'] for c in sel):9d} {max(c['exp'] for c in sel):7d} {max(c['gen'] for c in sel)/T**2:10.2f} "
              f"{max(c['maxR'] for c in sel):9.2f} {max(c['maxK'] for c in sel):7d} {min(c['D'] for c in sel):3d}-{max(c['D'] for c in sel):<3d}", flush=True)

"""Scan 3: margin bands m in {1, 1.05, 1.2, 1.5, 2, 4, >=T} on families that REACH large margins:
 peaky generator (T2b/T9 ctc.peaky_table, conf in {0.5,0.55,0.6,0.7,0.8,0.9,0.95}), 3 seeds, W in {4,5};
 alternating family (rows [0,rho,1-rho] / [1,0,0]; margin = rho/(1-rho) exactly, bound exact) as the m = T control.
Per cell: true margin (exact second-best search), D, exp_final, exp/D, n_off, gen/T^2, K, maxR_off. Then per-T band table."""
import sys, os, random, time
from r1core import *
TK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder')
sys.path.insert(0, TK)
from ctc import peaky_table
bands = (1.0, 1.05, 1.2, 1.5, 2.0, 4.0, 'T')
Ts = (16, 24, 32, 48, 64, 80)
cells = {T: [] for T in Ts}
for T in Ts:
    t0 = time.time()
    for W in (4, 5):
        for conf in (0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 0.95):
            for seed in range(3):
                rng = random.Random(1000 * T + 10 * W + seed)
                tbl = peaky_table(T, W, rng, conf)
                r = analyse(tbl, W, cap=1_500_000, cap2=1_500_000)
                if r['capped'] or r['p2'] is None or r['p2'] == 0: print(f"  T={T} W={W} conf={conf} seed={seed}: CAPPED"); continue
                cells[T].append(dict(fam=f"peaky W={W} conf={conf} s={seed}", m=r['margin'], D=r['D'], exp=r['exp_final'], n_off=r['n_off'], gen=r['gen'], K=r['K'], maxR=r['maxR_off'], maxK=r['maxK_off']))
        for rho in (0.55, 0.7, 0.9, 0.99):
            tbl = to_float(fam_alt(T, 3, Fraction(rho).limit_denominator(1000)))
            r = analyse(tbl, 3)
            cells[T].append(dict(fam=f"alt rho={rho}", m=r['margin'], D=r['D'], exp=r['exp_final'], n_off=r['n_off'], gen=r['gen'], K=r['K'], maxR=r['maxR_off'], maxK=r['maxK_off']))
    cs = cells[T]
    print(f"## T={T}: {len(cs)} cells ({time.time()-t0:.0f}s)")
    print(f"  {'band m>=':>9s} {'#cells':>6s} {'max exp/D':>9s} {'(cell)':>26s} {'max n_off':>9s} {'max gen/T2':>10s} {'max R_off':>9s} {'max K_u':>7s} {'max K':>5s}")
    for b in bands:
        bb = T if b == 'T' else b
        sel = [c for c in cs if c['m'] >= bb]
        if not sel: print(f"  {str(b):>9s} {0:6d}"); continue
        w = max(sel, key=lambda c: c['exp'] / max(c['D'], 1))
        print(f"  {str(b):>9s} {len(sel):6d} {w['exp']/max(w['D'],1):9.2f} {(w['fam'] + ' m=%.2f' % w['m']):>26s} {max(c['n_off'] for c in sel):9d} "
              f"{max(c['gen'] for c in sel)/T**2:10.2f} {max(c['maxR'] for c in sel):9.2f} {max(c['maxK'] for c in sel):7d} {max(c['K'] for c in sel):5d}", flush=True)
    for c in sorted(cs, key=lambda c: c['m']):
        print(f"    {c['fam']:26s} m={c['m']:8.3f} D={c['D']:3d} exp={c['exp']:6d} exp/D={c['exp']/max(c['D'],1):7.2f} n_off={c['n_off']:5d} gen/T2={c['gen']/T**2:7.2f} K={c['K']:3d} maxR_off={c['maxR']:.2f}")

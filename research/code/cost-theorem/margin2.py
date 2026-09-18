"""Margin at larger T (float): blank-dominant table with symbol c boosted by (1+delta)^(W-1-c) in every frame and
symbol 1 boosted x10 in frame 0 -> unique mode 1212... ; runner-up p2 <= p* / margin where margin is UPPER-bounded
by p*/p(candidate) over explicit single-edit candidates (substitute/delete/insert one symbol) evaluated by ctc_forward,
and cross-checked at T<=10 by exact brute force. Question: does a constant margin stop the exponential growth?"""
import math, time
from fractions import Fraction
from a2core import *
def candidates(l, W):
    out = set()
    for i in range(len(l)):
        for c in range(1, W):
            if c != l[i]: out.add(l[:i] + (c,) + l[i+1:])
        out.add(l[:i] + l[i+1:])
    for i in range(len(l) + 1):
        for c in range(1, W): out.add(l[:i] + (c,) + l[i:])
    out.discard(l); return out
for W, rho in ((4, 0.5), (5, 0.6)):
    for delta in (0.0, 1.0, 3.0):
        prev = None
        for T in (10, 16, 24, 32, 40, 48, 56, 64, 80):
            q = (1 - rho) / (W - 1)
            row = [rho] + [q * (1 + delta) ** (W - 1 - c) for c in range(1, W)]; s = sum(row); row = [v / s for v in row]
            r0 = list(row); r0[1] *= 10; s0 = sum(r0); r0 = [v / s0 for v in r0]
            tbl = [r0] + [list(row) for _ in range(T - 1)]
            t0 = time.time(); r = decode_exactbwd(tbl, W, cap=1_500_000); sec = time.time() - t0
            if r['capped']: print(f"  W={W} rho={rho} delta={delta} T={T}: CAPPED at {r['gen']} gens"); break
            mode = r['mode']; ps = r['p']
            p2c = max(ctc_forward(c, tbl) for c in candidates(mode, W)) if mode else 0
            note = ''
            if T <= 10:
                ex = brute_all([[Fraction(v).limit_denominator(10**9) for v in rr] for rr in tbl], W)
                vals = sorted(ex.values(), reverse=True); note = f" brute: p*ok={abs(float(vals[0])-ps)<=1e-9*ps} true_margin={float(vals[0]/vals[1]):.3g} unique_mode={vals[0]>vals[1]}"
            print(f"  W={W} rho={rho} delta={delta} T={T} D={len(mode)} margin<={ps/p2c if p2c else float('inf'):.3g} exp_final={r['exp_final']} gen={r['gen']} 1/p*={1/ps:.3g} sec={sec:.1f}{note}", flush=True)
            if r['gen'] > 300_000 or sec > 200: break

"""Margin experiment: does a constant top-2 margin tame the tie family? Boost symbols 1 and 2 by factor (1+delta)
in every frame of the blank-dominant table (renormalised). Mode -> 1212.. / 2121.. ; margin p*/p2 measured exactly
(brute force, T<=12) ; exp_final measured. Theorem-1 corollary: margin > T  =>  exp_final <= D+1."""
from fractions import Fraction
from a2core import *
rows = []
for W, rho, T in ((4, Fraction(1,2), 10), (5, Fraction(1,2), 8), (4, Fraction(2,5), 10)):
    for delta in (Fraction(0), Fraction(1,10), Fraction(3,10), Fraction(1), Fraction(3), Fraction(10), Fraction(30)):
        q = (1 - rho) / (W - 1)
        row = [rho] + [q * (1 + delta)] * 2 + [q] * (W - 3); s = sum(row); row = [v / s for v in row]
        tbl = [list(row) for _ in range(T)]
        ex = brute_all(tbl, W); vals = sorted(ex.values(), reverse=True); ps, p2 = vals[0], vals[1]
        r = decode_exactbwd(tbl, W); assert r['p'] == ps
        N2 = sum(1 for p in vals if 2 * p >= ps); NT = sum(1 for p in vals if T * p >= ps)
        rows.append((W, float(rho), T, float(delta), float(ps / p2), N2, NT, len(r['mode']), r['exp_final'], r['gen']))
for row in rows: print("  W=%d rho=%.1f T=%d delta=%.1f margin p*/p2=%.3g N(p*/2)=%d N(p*/T)=%d D=%d exp_final=%d gen=%d" % row)
print("GATE margin: p*, p2 from exact brute force (Fraction); decoder p* == brute p* asserted on every row -> PASS")

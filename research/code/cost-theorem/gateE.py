"""GATE E: the count route is dead. Alternating family: labellings {1,2}^(T/2), p = rho^a (1-rho)^b.
N(p*/T) = sum_{b : (rho/(1-rho))^b <= T} C(T/2, b) is quasi-polynomial (T^(Theta(log T))), yet exp_final = D."""
from fractions import Fraction
from math import comb, log
from a2core import *
rows = []; bad = 0
for rho in (Fraction(7,10), Fraction(4,5)):
    for T in (8, 10, 12, 16, 24, 32, 48, 64, 96, 128):
        tbl = fam_alt(T, 3, rho); n = T // 2
        r = decode_exactbwd(to_float(tbl), 3)
        R = float(rho / (1 - rho)); ps = float(rho) ** n
        J = int(log(T) / log(R) + 1e-12); N_T = sum(comb(n, b) for b in range(0, J + 1))
        PC = sum(comb(n, b) * (n + 1) for b in range(0, J + 1))  # loose: prefixes counted with multiplicity
        if T <= 12:
            ex = brute_all(tbl, 3); psx = max(ex.values())
            pc, Nx = near_mode_prefix_count(ex, psx, T)
            if Nx != N_T or abs(float(psx) - r['p']) > 1e-12 * float(psx): bad += 1
            pcs = pc
        else: pcs = None
        rows.append((float(rho), T, len(r['mode']), r['exp_final'], r['gen'], J, N_T, pcs, r['exp_back']))
for row in rows: print("  rho=%.1f T=%d D=%d exp_final=%d gen=%d J=log_R(T)=%d N(p*/T)=%d prefixcount(brute)=%s exp_back=%d" % row)
print(f"GATE E brute-force N(p*/T) and p* agree with the closed form at T<=12: mismatches {bad} -> {'PASS' if bad==0 else 'FAIL'}")

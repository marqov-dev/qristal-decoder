"""Flat tables, exact Fractions: (i) # labellings exactly tied with the mode, (ii) # prefixes u of tied
labellings with B(u) > p* STRICTLY under the exact-H bound, (iii) exp_final. A best-first search that stops
only when top bound <= incumbent must expand every u with B(u) > p*, so (ii) is a rigorous lower bound."""
import sys
from fractions import Fraction
from t9core import *
for W, Ts in ((3, (8, 10, 12)), (4, (8, 10, 12)), (5, (8, 10))):
    for T in Ts:
        tbl = [[Fraction(1, W)]*W for _ in range(T)]
        r = decode_exactbwd(tbl, W); H = r['H']; ps = r['p']
        ex = brute_all(tbl, W)
        tied = [l for l, p in ex.items() if p == ps]
        prefs = set(l[:k] for l in tied for k in range(len(l)+1))
        strict = 0; equal = 0
        Hsub = [H[d] for d in range(W)]
        for u in prefs:
            n = root_empty(tbl)
            for d in u: n = child(n, d, tbl)
            b = bound_H(n, Hsub, W)
            if b > ps: strict += 1
            elif b == ps: equal += 1
            else: raise AssertionError("inadmissible")
        D = len(r['mode']); ratio = (W-1)*(W-2)**(D-1) if W > 2 else 1
        print(f"flat W={W} T={T}: D={D} 1/p*={float(1/ps):.3g} exact-tied labellings={len(tied)} (>= (W-1)(W-2)^(D-1) = {ratio}) | prefixes of tied: {len(prefs)}, with B(u) > p* strictly: {strict}, B(u) == p*: {equal} | exp_final={r['exp_final']}  lower bound holds: {r['exp_final'] >= strict}")

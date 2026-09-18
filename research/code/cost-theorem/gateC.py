"""GATE C: blank-dominant uniform-residual family (k=0 ambiguous frames at threshold rho).
Claims (exact Fraction): (i) p(l) for a no-adjacent-repeat string depends only on |l|; strings with an adjacent
repeat are strictly below the no-repeat string of the same length; (ii) the set of modes = all (W-1)(W-2)^(n*-1)
no-repeat strings of length n*; (iii) every proper prefix u of a tied mode with |u| <= n*-2 has B(u) > p*
(strictness lemma), hence exp_final >= sum_{j<=n*-2} #norepeat(j); (iv) measured exp_final vs sum_{j<=n*-1}."""
from fractions import Fraction
from a2core import *
import heapq
def rep_string(n): return tuple(1 + (i % 2) for i in range(n))
def has_repeat(l): return any(l[i] == l[i+1] for i in range(len(l)-1))
n = 0; v1 = v2 = v3 = 0; rows = []
for W in (3, 4, 5):
    for rho in (Fraction(1,2), Fraction(3,5), Fraction(7,10), Fraction(4,5)):
        for T in (8, 10, 12):
            if W == 5 and T > 8: continue
            if W == 4 and T > 10: continue
            tbl = fam_blankdom(T, W, rho)
            ex = brute_all(tbl, W); ps = max(ex.values())
            # (i)
            bylen = {}
            for l, p in ex.items():
                if not has_repeat(l): bylen.setdefault(len(l), set()).add(p)
            if any(len(s) != 1 for s in bylen.values()): v1 += 1
            for l, p in ex.items():
                if has_repeat(l) and p >= next(iter(bylen[len(l)])): v1 += 1
            # (ii)
            modes = {l for l, p in ex.items() if p == ps}; nstar = len(next(iter(modes)))
            if any(has_repeat(l) or len(l) != nstar for l in modes) or len(modes) != norepeat_count(W, nstar): v2 += 1
            # (iii) strictness: B(u) > p* for every proper prefix with |u| <= n*-2
            r = decode_exactbwd(tbl, W); H = r['H']; Hsub = [H[d] for d in range(W)]
            def B(u):
                nd = root_empty(tbl)
                for s in u: nd = child(nd, s, tbl)
                return bound_H(nd, Hsub, W)
            pref2 = {l[:j] for l in modes for j in range(0, nstar - 1)}
            pref1 = {l[:j] for l in modes for j in range(0, nstar)}
            if any(B(u) <= ps for u in pref2): v3 += 1
            strict1 = all(B(u) > ps for u in pref1)
            LB2 = sum(norepeat_count(W, j) for j in range(0, max(nstar - 1, 0)))
            LB1 = sum(norepeat_count(W, j) for j in range(0, nstar))
            n += 1
            assert len(pref2) == LB2 and len(pref1) == LB1
            rows.append((W, float(rho), T, nstar, len(modes), r['exp_final'], LB2, LB1, strict1, float(1/ps), float(T*(1-rho)/((W-1)*rho))))
for row in rows: print("  W=%d rho=%.2f T=%d n*=%d ties=%d exp_final=%d LB(|u|<=n*-2)=%d LB(|u|<=n*-1)=%d strict_n*-1=%s 1/p*=%.3g pressure=T q/rho=%.2f" % row)
print(f"GATE C1 no-repeat strings of equal length tie exactly; repeat strings strictly below: {n} tables, violations {v1} -> {'PASS' if v1==0 else 'FAIL'}")
print(f"GATE C2 mode set == all (W-1)(W-2)^(n*-1) no-repeat strings of length n*: violations {v2} -> {'PASS' if v2==0 else 'FAIL'}")
print(f"GATE C3 B(u) > p* for every proper prefix of a mode with |u| <= n*-2 (strictness lemma): violations {v3} -> {'PASS' if v3==0 else 'FAIL'}")

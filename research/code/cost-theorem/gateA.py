"""GATE A: Theorem 1 (final search): exp_final <= |prefixes of {l: p(l) >= p*/T}| <= (T+1)*T/p*,
and the sharper distinct-suffix form; Theorem 1 (sub-searches): exp_{t,c} <= |prefixes of {w: g_w(t) >= H_c(t)/(L-1)}|
<= (L+1)(L-1) y_t[c]/H_c(t).  Exact Fraction arithmetic, brute force over all paths."""
import random, sys
from fractions import Fraction
from a2core import *

rng = random.Random(11)
fams = []
for conf in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
    fams.append((f'peaky{conf}', lambda T, W, c=conf: fam_peaky(T, W, rng, c)))
fams += [('flat', lambda T, W: fam_flat(T, W)),
         ('blankdom0.5', lambda T, W: fam_blankdom(T, W, Fraction(1, 2))),
         ('blankdom0.8', lambda T, W: fam_blankdom(T, W, Fraction(4, 5))),
         ('alt0.7', lambda T, W: fam_alt(T, W, Fraction(7, 10))),
         ('random', lambda T, W: [[Fraction(rng.randint(1, 30)) for _ in range(W)] for _ in range(T)])]
def norm(tbl): return [[v / sum(r) for v in r] for r in tbl]

cells = [(8, 3), (10, 3), (12, 3), (7, 5), (8, 5), (6, 5)]
n = 0; viol_final = 0; viol_final_mass = 0; viol_sub = 0; viol_sub_mass = 0; nsub = 0
worst_ratio_final = 0; rows = []
for name, gen in fams:
    for T, W in cells:
        for rep in range(2):
            tbl = norm(gen(T, W))
            ex = brute_all(tbl, W); ps = max(ex.values())
            per = []
            r = decode_exactbwd(tbl, W, per_search=per)
            assert r['p'] == ps, (name, T, W, r['p'], ps)
            pc, N = near_mode_prefix_count(ex, ps, T)
            massb = (T + 1) * T / ps
            n += 1
            if r['exp_final'] > pc: viol_final += 1
            if r['exp_final'] > massb: viol_final_mass += 1
            worst_ratio_final = max(worst_ratio_final, r['exp_final'] / pc)
            # sub-searches: per = [(t0, c, exp, gen, len(v))]
            for (t0, c, e, g, lv) in per:
                L = T - t0
                if L - 1 <= 0: continue   # last frame: root only, no terms
                sm = brute_suffix_masses(tbl, W, t0, c); H = max(sm.values())
                assert H == r['H'][c][t0]
                if H == 0:
                    assert e == 0; continue
                pcs, Ns = near_mode_prefix_count(sm, H, L - 1)
                nsub += 1
                if e > pcs: viol_sub += 1
                if e > (L + 1) * (L - 1) * tbl[t0][c] / H: viol_sub_mass += 1
            rows.append((name, T, W, r['exp_final'], pc, N, float(massb), len(r['mode'])))
for row in rows[::3]: print("  fam=%s T=%d W=%d exp_final=%d prefixcount=%d N_T=%d massbound=%.3g D=%d" % row)
print(f"GATE A1 exp_final <= |prefixes of labellings with p >= p*/T|: {n} instances (Fraction-exact), violations {viol_final} -> {'PASS' if viol_final == 0 else 'FAIL'}")
print(f"GATE A2 exp_final <= (T+1)T/p*: {n} instances, violations {viol_final_mass} -> {'PASS' if viol_final_mass == 0 else 'FAIL'}")
print(f"GATE A3 sub-search exp <= |prefixes of suffixes with g >= H_c(t)/(L-1)|: {nsub} sub-searches, violations {viol_sub} -> {'PASS' if viol_sub == 0 else 'FAIL'}")
print(f"GATE A4 sub-search exp <= (L+1)(L-1) y_t[c]/H_c(t): {nsub} sub-searches, violations {viol_sub_mass} -> {'PASS' if viol_sub_mass == 0 else 'FAIL'}")

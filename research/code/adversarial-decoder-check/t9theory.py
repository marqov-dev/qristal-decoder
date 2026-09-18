"""(1) Fraction-exact expansion counts on flat tables (is the blowup a float-tie artefact?)
   (2) empirical check of the theorem: final-search expansions <= |{u : max_v p(u.v) >= p*/T}|"""
import sys, random
from fractions import Fraction
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder'))
from ctc import brute_ctc, peaky_table
from t9core import *
import t9bench as B

print("--- (1) flat tables, exact Fraction arithmetic vs float ---")
for W in (3, 4, 5):
    for T in (6, 8, 10, 12):
        if W == 5 and T > 10: continue
        tf = [[Fraction(1, W)]*W for _ in range(T)]
        rf = decode_exactbwd(tf, W)
        rl = decode_exactbwd([[1.0/W]*W for _ in range(T)], W)
        ex = brute_ctc([[1.0/W]*W for _ in range(T)]); ps = max(ex.values())
        ties = sum(1 for p in ex.values() if abs(p-ps) <= 1e-12*ps)
        print(f"flat W={W} T={T}: Fraction exp_final={rf['exp_final']} gen={rf['gen']} | float exp_final={rl['exp_final']} gen={rl['gen']} | D={len(rf['mode'])} exact-tied labellings={ties} 1/p*={1/ps:.3g}")

print("--- (2) expansions vs prefix-count bound ---")
rng = random.Random(5)
viol = 0; n = 0; rows = []
fams = [('random', lambda T, W: B.fam_uniform_random(T, W, rng)),
        ('flat', lambda T, W: B.fam_flat(T, W, rng)),
        ('peaky.8', lambda T, W: peaky_table(T, W, rng, 0.8)),
        ('peaky.5', lambda T, W: peaky_table(T, W, rng, 0.5)),
        ('neartie3', lambda T, W: B.fam_neartie(T, W, rng, spread=3)),
        ('spreadpair', lambda T, W: B.fam_spread_pair(T, W, rng, m=3, q=0.5))]
for name, gen in fams:
    for T, W in [(8,3),(9,3),(10,3),(8,4)]:
        for _ in range(3):
            tbl = gen(T, W)
            ex = brute_ctc(tbl); ps = max(ex.values())
            r = decode_exactbwd(tbl, W)
            prefixes = set()
            for l, p in ex.items():
                if p >= ps/T:
                    for k in range(len(l)+1): prefixes.add(l[:k])
            KT = sum(1 for p in ex.values() if p >= ps/T)
            K2 = sum(1 for p in ex.values() if p >= ps/2)
            n += 1
            if r['exp_final'] > len(prefixes): viol += 1
            rows.append((name, T, W, r['exp_final'], len(prefixes), KT, K2, len(r['mode'])))
for row in rows: print("  fam=%s T=%d W=%d exp_final=%d prefixbound=%d K_T=%d K_2=%d D=%d" % row)
print(f"GATE exp_final <= |prefixes of labellings with p >= p*/T|: {n} instances, violations {viol} -> {'PASS' if viol == 0 else 'FAIL'}")

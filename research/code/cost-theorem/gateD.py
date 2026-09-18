"""GATE D: dependence on k cannot be removed. k flat frames + (T-k) deterministic-blank frames:
exp_final equals the flat-table count at T=k (T9: 53,161,485,1457 for k=8,10,12,14 at W=5 = (W-2)^(k/2) growth),
although the padded table has only k ambiguous frames and zero deviation mass elsewhere (eps=0)."""
from fractions import Fraction
from a2core import *
rows = []; bad = 0
for W in (4, 5):
    for k in (8, 10, 12, 14):
        if W == 5 and k > 12: continue
        pad = to_float(fam_padded_flat(2 * k, k, W)); flat = to_float(fam_flat(k, W))
        rp = decode_exactbwd(pad, W); rf = decode_exactbwd(flat, W)
        # deterministic-blank padding: p* checked against ctc_forward on the returned mode; the flat T=k modes were brute-forced by T9 (theory.log)
        ok = abs(ctc_forward(rp['mode'], pad) - rp['p']) <= 1e-12 * rp['p'] and abs(ctc_forward(rf['mode'], flat) - rf['p']) <= 1e-12 * rf['p']
        if rp['exp_final'] != rf['exp_final']: bad += 1
        rows.append((W, k, 2 * k, rp['exp_final'], rf['exp_final'], rp['gen'], rf['gen'], (W - 2) ** (k // 2), ok))
for row in rows: print("  W=%d k=%d T=%d padded exp_final=%d flat(T=k) exp_final=%d padded gen=%d flat gen=%d (W-2)^(k/2)=%d p_fwd_ok=%s" % row)
print(f"GATE D padded-flat exp_final == flat exp_final at T=k: {len(rows)} cells, mismatches {bad} -> {'PASS' if bad==0 else 'FAIL'}")

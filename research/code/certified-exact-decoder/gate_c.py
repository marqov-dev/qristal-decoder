"""Gate the C port: (1) vs stdlib decode_exact_backward on 300 tables T<=12 W<=8 (p*, mode, exact H table);
(2) vs brute force incl. certified runner-up on 200 tables T<=6 W<=8."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
from cdecoder import decode_c
rng = random.Random(606); n = 0; bad_p = bad_l = bad_H = 0; worstH = 0.0
for i in range(300):
    T, W = rng.choice([(6,3),(8,3),(10,3),(12,3),(8,5),(10,5),(12,5),(8,8),(12,8)])
    tb = random_table(rng, T, W) if i % 2 else peaky_table(T, W, rng, rng.choice([0.7,0.8,0.9]))
    Hp = H_policy(tb); He, _ = H_exact_backward(tb, Hp); rp = best_first(tb, lambda nd: bound_from_H(nd, tb, He))
    rc = decode_c(tb, want_H=True); n += 1
    if abs(rc['p1'] - rp[0]) > 1e-12 * rp[0]: bad_p += 1
    if rc['l1'] != rp[1] and abs(ctc_forward(rc['l1'], tb) - rp[0]) > 1e-12 * rp[0]: bad_l += 1
    for c in range(1, W):
        for t in range(1, T+1):
            worstH = max(worstH, abs(rc['H'][c][t] - He[c][t]) / max(He[c][t], 1e-300))
print(f"GATE C port vs stdlib exact-backward: {n} tables (T<=12, W<=8), p* mismatches {bad_p}, argmax mismatches {bad_l}, worst rel |H_C - H_py| {worstH:.2e} -> {'PASS' if bad_p == 0 and bad_l == 0 and worstH < 1e-10 else 'FAIL'}")
rng = random.Random(707); n = 0; bad1 = bad2 = 0; ties = 0
for i in range(200):
    T, W = rng.choice([(4,5),(5,5),(6,5),(4,8),(5,8),(6,8),(6,3)])
    tb = random_table(rng, T, W) if i % 2 else peaky_table(T, W, rng, rng.choice([0.7,0.8,0.9]))
    ex = brute_ctc(tb); srt = sorted(ex.items(), key=lambda kv: -kv[1]); (l1, p1), (l2, p2) = srt[0], srt[1]
    rc = decode_c(tb); n += 1
    if abs(rc['p1'] - p1) > 1e-12 * p1 or (rc['l1'] != l1 and abs(ex.get(rc['l1'], -1) - p1) > 1e-12 * p1): bad1 += 1
    if abs(rc['p2'] - p2) > 1e-12 * p2 or (rc['l2'] != l2 and abs(ex.get(rc['l2'], -1) - p2) > 1e-12 * p2): bad2 += 1
    if rc['l1'] != l1 or rc['l2'] != l2: ties += 1
print(f"GATE C port vs brute force (mode AND certified runner-up): {n} tables (T<=6, W<=8), mode wrong {bad1}, runner-up wrong {bad2}, exact ties {ties} -> {'PASS' if bad1 == 0 and bad2 == 0 else 'FAIL'}")

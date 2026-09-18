"""Supplementary argmax gate at the vocabulary sizes used in the tables (W=5, 8; T<=6, brute force 8^6=262k paths)."""
import sys, os, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
rng = random.Random(2026); bad = {'graves':0,'bidir':0,'policy':0,'exactbwd':0}; n = 0; ties = 0
for i in range(120):
    T, W = rng.choice([(4,5),(5,5),(6,5),(4,8),(5,8),(6,8)])
    tb = random_table(rng, T, W) if i % 2 == 0 else peaky_table(T, W, rng, rng.choice([0.8,0.9]))
    l, p, ex = brute_mode(tb); n += 1
    for k, r in {'graves': decode_graves(tb), 'bidir': decode_bidir(tb, math.sqrt(beam_incumbent(tb,16)[1])),
                 'policy': decode_policy(tb), 'exactbwd': decode_exact_backward(tb)}.items():
        if r[1] != l:
            if abs(ex.get(r[1], -1.0) - p) <= 1e-12 and abs(r[0]-p) <= 1e-12: ties += 1
            else: bad[k] += 1
print(f"GATE argmax vs brute force at W in {{5,8}}, T<=6: {n} instances (60 random + 60 peaky), wrong = {bad}, exact ties {ties} -> {'PASS' if not any(bad.values()) else 'FAIL'}")

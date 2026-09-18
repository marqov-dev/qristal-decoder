import sys, os, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
rng = random.Random(1000*32 + 10*8 + 0)
for i in range(3):
    tb = random_table(rng, 32, 8)
    c = Counter(); t0 = time.perf_counter(); r = decode_exact_backward(tb, cap=300000, cnt=c); dt = time.perf_counter()-t0
    print(f"random T=32 W=8 inst {i}: p*={r[0]:.3e} D={len(r[1]) if r[1] else -1} 1/p*={1/r[0] if r[0] else float('inf'):.2e} exactbwd exp={r[2]} gen={c.gen} bwd_exp={r[5]} sec={dt:.2f} capped={r[4]}", flush=True)

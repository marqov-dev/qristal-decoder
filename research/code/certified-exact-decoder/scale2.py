"""Real-audio-scale T sweep for the exact-backward decoder alone (policy caps at T>=200, Graves at T>=64)."""
import sys, os, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
W = int(sys.argv[1]); conf = float(sys.argv[2]); Ts = [int(x) for x in sys.argv[3].split(',')]; N = int(sys.argv[4])
print(f"# exactbwd only, W={W} conf={conf} N={N}")
print(f"{'T':>4} {'inst':>4} {'p*':>10} {'D':>4} {'log10(1/p*)':>11} {'final exp':>9} {'bwd exp':>8} {'gen':>9} {'sec':>7} {'gen/(T^2 W)':>11}")
for T in Ts:
    rng = random.Random(4242 + T + W)
    for i in range(N):
        tb = peaky_table(T, W, rng, conf)
        c = Counter(); t0 = time.perf_counter(); r = decode_exact_backward(tb, cap=300000, cnt=c); dt = time.perf_counter()-t0
        if r[4]: print(f"{T:>4} {i:>4} capped"); continue
        print(f"{T:>4} {i:>4} {r[0]:>10.2e} {len(r[1]):>4} {-math.log10(r[0]):>11.1f} {r[2]:>9} {r[5]:>8} {c.gen:>9} {dt:>7.2f} {c.gen/(T*T*W):>11.3f}", flush=True)

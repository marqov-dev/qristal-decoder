"""Real-audio-scale T sweep for the decoders that survive: expansions, generated, seconds, p*, D."""
import sys, os, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
def gmean(xs): return math.exp(sum(math.log(max(x,1e-300)) for x in xs)/len(xs))
W = int(sys.argv[1]); conf = float(sys.argv[2]); Ts = [int(x) for x in sys.argv[3].split(',')]; N = int(sys.argv[4])
CAP = 300000
print(f"# W={W} conf={conf} N={N}")
print(f"{'T':>4} {'p*':>10} {'D':>4} {'log10(1/p*)':>11} | {'policy exp':>10} {'gen':>8} {'sec':>7} | {'exactbwd exp':>12} {'gen':>9} {'sec':>7} {'bwd exp':>8} | {'bidir exp':>9} {'gen':>9} {'sec':>7}")
for T in Ts:
    rng = random.Random(4242 + T + W); P=[]; E=[]; Bd=[]; ps=[]; Ds=[]
    for _ in range(N):
        tb = peaky_table(T, W, rng, conf)
        c = Counter(); t0 = time.perf_counter(); r = decode_policy(tb, cap=CAP, cnt=c); dtp = time.perf_counter()-t0
        c2 = Counter(); t0 = time.perf_counter(); r2 = decode_exact_backward(tb, cap=CAP, cnt=c2); dte = time.perf_counter()-t0
        c3 = Counter(); t0 = time.perf_counter(); r3 = decode_bidir(tb, math.sqrt(beam_incumbent(tb, 32)[1]), cap=CAP, cnt=c3) if T <= 100 else (r[0], r[1], float('nan'), 0, False, 0); dtb = time.perf_counter()-t0
        if r[4] or r2[4] or r3[4]: print(f"{T:>4} capped: policy={r[4]} exactbwd={r2[4]} bidir={r3[4]}"); continue
        assert abs(r[0]-r2[0]) <= 1e-12*r[0] and abs(r[0]-r3[0]) <= 1e-12*r[0] and r[1]==r2[1]==r3[1], (r[0], r2[0], r3[0])
        ps.append(r[0]); Ds.append(len(r[1])); P.append((r[2], c.gen, dtp)); E.append((r2[2], c2.gen, dte, r2[5])); Bd.append((r3[2], c3.gen, dtb))
    if ps:
        print(f"{T:>4} {gmean(ps):>10.2e} {sum(Ds)/len(Ds):>4.0f} {-math.log10(gmean(ps)):>11.1f} | {gmean([x[0] for x in P]):>10.1f} {gmean([x[1] for x in P]):>8.0f} {gmean([x[2] for x in P]):>7.2f} | {gmean([x[0] for x in E]):>12.1f} {gmean([x[1] for x in E]):>9.0f} {gmean([x[2] for x in E]):>7.2f} {gmean([x[3] for x in E]):>8.0f} | {gmean([x[0] for x in Bd]):>9.1f} {gmean([x[1] for x in Bd]):>9.0f} {gmean([x[2] for x in Bd]):>7.2f}", flush=True)

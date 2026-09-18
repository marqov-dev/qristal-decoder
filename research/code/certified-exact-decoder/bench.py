"""Benchmark every decoder on IDENTICAL instances.  Prints one line per (T, W, conf, decoder):
geometric-mean expansions, generated nodes (child() calls, each O(T)), wall-clock, and cap hits.
Usage: bench.py <mode: peaky|random> <n_per_cell> <cap> [Ts] [Ws] [confs]"""
import sys, os, math, time, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *

mode = sys.argv[1]; N = int(sys.argv[2]); CAP = int(sys.argv[3])
Ts = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else [12, 16, 24, 32, 48]
Ws = [int(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else [3, 5]
confs = [float(x) for x in sys.argv[6].split(',')] if len(sys.argv) > 6 else [0.8, 0.9, 0.95]
if mode == 'random': confs = [0.0]
only = set(sys.argv[7].split(',')) if len(sys.argv) > 7 else None

def gmean(xs): return math.exp(sum(math.log(max(x, 1e-300)) for x in xs)/len(xs))

def run(name, f, tbl, truth_p):
    cnt = Counter(); t0 = time.perf_counter()
    r = f(tbl, cnt)
    dt = time.perf_counter() - t0
    bp, bl, exp, gen, hit = r[0], r[1], r[2], r[3], r[4]
    ok = (not hit) and abs(bp - truth_p) <= 1e-12*max(truth_p, 1e-300)
    return dict(exp=exp, gen=cnt.gen, t=dt, hit=hit, ok=ok, extra=(r[5] if len(r) > 5 else None))

DEC = {
  'graves':    lambda tb, c: decode_graves(tb, cap=CAP, cnt=c),
  'childF':    lambda tb, c: decode_childF(tb, cap=CAP, cnt=c),
  'graves+beam': lambda tb, c: decode_graves(tb, *beam_incumbent(tb, 32)[::-1], cap=CAP, cnt=c),
  'dfsBB+beam':  lambda tb, c: dfs_bb(tb, lambda n: graves_F(n, tb), *beam_incumbent(tb, 32)[::-1], cap=CAP, cnt=c),
  'bidir':     lambda tb, c: decode_bidir(tb, math.sqrt(beam_incumbent(tb, 32)[1]), cap=CAP, cnt=c),
  'policy':    lambda tb, c: decode_policy(tb, cap=CAP, cnt=c),
  'exactbwd':  lambda tb, c: decode_exact_backward(tb, cap=CAP, cnt=c),
}
if only: DEC = {k: v for k, v in DEC.items() if k in only}

print(f"# mode={mode} N={N} cap={CAP}")
print(f"{'T':>3} {'W':>2} {'conf':>5} {'p*':>9} {'D':>3} {'1/p*':>9} | {'decoder':<12} {'exp':>9} {'gen':>9} {'sec':>8} {'caps':>4} {'wrong':>5} | {'exp/graves':>10} {'gen/graves':>10} {'t/graves':>9}")
rows = []
for T in Ts:
    for W in Ws:
        for conf in confs:
            rng = random.Random(1000*T + 10*W + int(conf*100))
            tbls = [random_table(rng, T, W) if mode == 'random' else peaky_table(T, W, rng, conf) for _ in range(N)]
            # reference p*: exact-backward decoder is gated; cross-check with policy decoder.
            refs = []
            for tb in tbls:
                r1 = decode_policy(tb, cap=CAP); r2 = decode_exact_backward(tb, cap=CAP)
                if r1[4] or r2[4]: refs.append(None); continue
                assert abs(r1[0]-r2[0]) <= 1e-12*r1[0], (r1[0], r2[0])
                refs.append((r1[0], r1[1]))
            res = {}
            for name, f in DEC.items():
                stats = []
                for tb, ref in zip(tbls, refs):
                    if ref is None: continue
                    stats.append(run(name, f, tb, ref[0]))
                res[name] = stats
            good = [r for r in refs if r is not None]
            if not good: print(f"{T:>3} {W:>2} {conf:>5} -- all capped"); continue
            ps = gmean([r[0] for r in good]); D = sum(len(r[1]) for r in good)/len(good)
            base = res.get('graves')
            for name, stats in res.items():
                if not stats: continue
                e = gmean([s['exp'] for s in stats]); g = gmean([s['gen'] for s in stats]); t = gmean([s['t'] for s in stats])
                caps = sum(s['hit'] for s in stats); wrong = sum((not s['ok']) and (not s['hit']) for s in stats)
                if base:
                    be = gmean([s['exp'] for s in base]); bg = gmean([s['gen'] for s in base]); bt = gmean([s['t'] for s in base])
                    rel = f"{e/be:>10.3f} {g/bg:>10.3f} {t/bt:>9.3f}"
                else: rel = ''
                print(f"{T:>3} {W:>2} {conf:>5} {ps:>9.2e} {D:>3.0f} {1/ps:>9.2e} | {name:<12} {e:>9.1f} {g:>9.1f} {t:>8.3f} {caps:>4} {wrong:>5} | {rel}", flush=True)
                rows.append(dict(T=T, W=W, conf=conf, pstar=ps, D=D, dec=name, exp=e, gen=g, t=t, caps=caps, wrong=wrong,
                                 extra=[s['extra'] for s in stats]))
            print('-'*120, flush=True)
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'bench_{mode}.json'), 'w'))

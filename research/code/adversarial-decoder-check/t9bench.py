import sys, random, time, math, json
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder'))
from ctc import ctc_forward, brute_ctc, peaky_table, topk_labellings
from t9core import *

def norm(rows): return [[x/sum(r) for x in r] for r in rows]

# ---------------- families ----------------
def fam_peaky(T, W, rng, conf=0.8): return peaky_table(T, W, rng, conf)
def fam_uniform_random(T, W, rng): return norm([[rng.random() for _ in range(W)] for _ in range(T)])
def fam_flat(T, W, rng): return [[1.0/W]*W for _ in range(T)]
def fam_alt3(T, W, rng, conf=0.9, period=4):
    """structured W=3: alternating high-confidence a/b, every `period`-th frame uniform."""
    rows = []
    for t in range(T):
        if t % period == period-1: rows.append([1.0/3]*3)
        else:
            win = 1 + (t // 2) % 2 if False else 1 + (t % 2)
            r = [(1-conf)/2]*3; r[win] = conf; rows.append(r)
    return rows
def fam_alt3_blankgap(T, W, rng, conf=0.9):
    """a b a b ... each symbol frame followed by a frame that is 50/50 blank/same symbol (spread starts)"""
    rows = []
    for t in range(T):
        sym = 1 + (t//2) % 2
        if t % 2 == 0: r = [(1-conf)/2]*3; r[sym] = conf
        else: r = [0.5, 0.0, 0.0]; r[sym] = 0.5
        rows.append(r)
    return rows
def fam_neartie(T, W, rng, eps=1e-3, spread=1):
    """every other frame: near-tie between symbols 1 and 2 (0.5+-eps); other frames blank.
    spread>1: the ambiguous symbol row is repeated `spread` frames with blank mass so the segment
    can start at several frames."""
    rows = []; t = 0; i = 0
    while len(rows) < T:
        e = eps if (i % 2 == 0) else -eps
        for s in range(spread):
            r = [0.0]*W; r[1] = 0.5+e; r[2] = 0.5-e
            if spread > 1:
                r = [0.0]*W; r[0] = 0.5; r[1] = (0.5+e)/2; r[2] = (0.5-e)/2
            rows.append(r)
        rows.append([1.0]+[0.0]*(W-1)); i += 1
    return rows[:T]
def fam_neartie_soft(T, W, rng, conf=0.5, eps=0.02):
    """peaky-like but the winning symbol is a near-tie between two symbols with blank mass elsewhere"""
    rows = []
    for t in range(T):
        if rng.random() < 0.5:
            r = [(1-conf)/(W-1)]*W; r[0] = conf
        else:
            a, b = rng.sample(range(1, W), 2)
            r = [(1-2*conf+0.0)/(W-1) if False else 0.0]*W
            rest = 1 - 2*conf
            r = [rest/(W-2)]*W; r[a] = conf*(1+eps); r[b] = conf*(1-eps)
        rows.append(r)
    return norm(rows)
def fam_degenerate(T, W, rng, conf=0.8):
    """peaky with 20% exactly-uniform frames and symbol W-1 having zero probability everywhere"""
    rows = peaky_table(T, W-1, rng, conf)
    out = []
    for t, r in enumerate(rows):
        if rng.random() < 0.2: r = [1.0/(W-1)]*(W-1)
        out.append(list(r) + [0.0])
    return out
def fam_spread(T, W, rng, m=4, q=0.5):
    """each symbol occupies a run of m frames with prob q (blank 1-q): many start frames per symbol"""
    rows = []; t = 0
    while len(rows) < T:
        d = rng.randrange(1, W)
        for _ in range(m):
            r = [0.0]*W; r[0] = 1-q; r[d] = q; rows.append(r)
    return rows[:T]
def fam_spread_pair(T, W, rng, m=3, q=0.5):
    """runs of two symbols overlapping: frames in a run carry (blank, a, b) = (1-q, q/2, q/2)"""
    rows = []
    while len(rows) < T:
        a, b = rng.sample(range(1, W), 2)
        for _ in range(m):
            r = [0.0]*W; r[0] = 1-q; r[a] = q/2; r[b] = q/2; rows.append(r)
    return rows[:T]

# ---------------- runner ----------------
def run_instance(tbl, W, cap=400_000, gcap=200_000, do_graves=True, beam=256, brute=False):
    T = len(tbl)
    out = dict(T=T, W=W)
    ps = []
    t0 = time.time(); r = decode_exactbwd(tbl, W, cap=cap, per_search=ps); out['sec'] = time.time()-t0
    out.update(exp_final=r['exp_final'], gen_final=r['gen_final'], exp_back=r['exp_back'], gen_back=r['gen_back'],
               gen=r['gen'], capped=r['capped'], D=(len(r['mode']) if r['mode'] is not None else None),
               p=r['p'])
    if ps:
        out['max_sub_exp'] = max(s[2] for s in ps); out['mean_sub_exp'] = sum(s[2] for s in ps)/len(ps)
        out['max_sub_gen'] = max(s[3] for s in ps)
    if do_graves:
        t0 = time.time(); g = decode_graves(tbl, W, cap=gcap); out['g_sec'] = time.time()-t0
        out.update(g_exp=g['exp'], g_gen=g['gen'], g_capped=g['capped'], g_p=g['p'])
        if not g['capped'] and not r['capped']:
            out['agree'] = (abs(g['p'] - r['p']) <= 1e-9*max(g['p'], 1e-300))
    if not r['capped']:
        # certify: p(mode) recomputed by toolkit forward equals p; beam search cannot beat it
        pf = ctc_forward(list(r['mode']), tbl)
        out['p_fwd_ok'] = abs(pf - r['p']) <= 1e-9*max(pf, 1e-300)
        if brute:
            ex = brute_ctc(tbl); ps_ = max(ex.values())
            out['brute_ok'] = abs(ex.get(r['mode'], 0.0) - ps_) <= 1e-12*ps_
        else:
            bl = topk_labellings(tbl, beam=beam, k=1)
            out['beam_p'] = bl[0][0] if bl else 0.0
            out['beam_ok'] = (r['p'] >= out['beam_p']*(1-1e-9))
            out['beam_same'] = (bl and tuple(bl[0][1]) == r['mode'])
    return out

def fmt(o):
    def f(x):
        if x is None: return '-'
        if isinstance(x, float): return f"{x:.3g}"
        return str(x)
    keys = ['T','W','D','p','exp_final','exp_back','gen','max_sub_exp','sec','capped','g_exp','g_gen','g_capped','g_sec','agree','p_fwd_ok','brute_ok','beam_ok','beam_same']
    return ' '.join(f"{k}={f(o.get(k))}" for k in keys if k in o)

def _find_coupled(rng, W=3, Tb=4, tries=400):
    """random block pairs (Tb frames each) whose concat mode != concat of block modes"""
    from ctc import brute_ctc
    found = []
    for _ in range(tries):
        b1 = norm([[rng.random() for _ in range(W)] for _ in range(Tb)])
        b2 = norm([[rng.random() for _ in range(W)] for _ in range(Tb)])
        m1 = max(brute_ctc(b1).items(), key=lambda kv: kv[1])[0]
        m2 = max(brute_ctc(b2).items(), key=lambda kv: kv[1])[0]
        m12 = max(brute_ctc(b1+b2).items(), key=lambda kv: kv[1])[0]
        if m12 != m1 + m2 and m12 != (m1 + m2[1:] if m1 and m2 and m1[-1] == m2[0] else None):
            found.append(b1 + b2)
    return found
_COUPLED = None
def fam_coupled(T, W, rng):
    global _COUPLED
    if _COUPLED is None: _COUPLED = _find_coupled(random.Random(3), W=W)
    rows = []
    while len(rows) < T: rows += rng.choice(_COUPLED)
    return rows[:T]



def fam_flatnoise(T, W, rng, eps=1e-3):
    """uniform rows with multiplicative noise (1 +- eps): near-ties, no exact ties"""
    return norm([[1.0 + eps*(2*rng.random()-1) for _ in range(W)] for _ in range(T)])

if __name__ == '__main__':
    fam = sys.argv[1]; Ts = [int(x) for x in sys.argv[2].split(',')]; W = int(sys.argv[3])
    N = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    kw = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
    cap = int(kw.pop('cap', 400_000)); gcap = int(kw.pop('gcap', 200_000)); do_g = bool(kw.pop('graves', True))
    gen = globals()['fam_'+fam]
    rng = random.Random(7)
    for T in Ts:
        for i in range(N):
            tbl = gen(T, W, rng, **kw)
            o = run_instance(tbl, W, cap=cap, gcap=gcap, do_graves=do_g, brute=(T <= 8 and W <= 4) or (T <= 6 and W <= 8))
            o['fam'] = fam; o['i'] = i; o['kw'] = kw
            print(fam, kw, fmt(o), flush=True)
            with open(f'log_{fam}.jsonl', 'a') as fh: fh.write(json.dumps({k: v for k, v in o.items()}) + '\n')

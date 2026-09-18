"""Hunt 2: two adversarial objectives, larger T, structured seeds.
 (a) maximise max_u R_d(u) over EXPANDED off-path nodes (any margin)      -> how fast can R_max grow with T?
 (b) maximise n_off subject to margin >= m_target (m in 1.5, 2, 3)        -> does any off-path expansion exist at margin >= 2?
Seeds: random, blank-dominant, clock (rigid symbols every g frames with free insertion symbol), pinned family.
Best tables re-analysed in exact Fraction arithmetic."""
import sys, random, math, time
from fractions import Fraction
from r1core import *

def evaluate(tbl, W):
    r = analyse(tbl, W, cap=300_000, cap2=300_000)
    if r['capped'] or r['p2'] is None or r['p2'] == 0: return None
    return r

def mutate(tbl, rng, scale):
    T = len(tbl); W = len(tbl[0]); new = [list(r) for r in tbl]
    k = rng.random()
    if k < 0.45:
        t = rng.randrange(T); row = [v * math.exp(scale * rng.gauss(0, 1)) for v in new[t]]; s = sum(row); new[t] = [v / s for v in row]
    elif k < 0.75:
        t = rng.randrange(T); s_ = rng.randrange(W); new[t][s_] *= math.exp(3 * scale * rng.gauss(0, 1)); s = sum(new[t]); new[t] = [v / s for v in new[t]]
    elif k < 0.9:
        t = rng.randrange(T); t2 = min(T - 1, max(0, t + rng.choice((-1, 1)))); new[t2] = list(new[t])
    else:                                  # swap two rows
        t = rng.randrange(T); t2 = rng.randrange(T); new[t], new[t2] = new[t2], new[t]
    return new

def seed(kind, T, W, rng):
    if kind == 'rand': tbl = [[rng.random() ** 2 + 1e-4 for _ in range(W)] for _ in range(T)]
    elif kind == 'blankdom': tbl = [[0.6] + [0.4 / (W - 1) * math.exp(0.3 * rng.gauss(0, 1)) for _ in range(W - 1)] for _ in range(T)]
    elif kind == 'clock':
        g = rng.choice((2, 3, 4)); m2 = rng.choice((1.5, 2, 3, 5)); tbl = []
        for t in range(T):
            if t % g == g - 1:
                sym = 2 + (t // g) % (W - 2) if W > 3 else 2
                row = [1.0] + [0.05] * (W - 1); row[sym] = m2 * 1.0; row[1] = 0.05
            else:
                row = [0.6, 0.4 * rng.choice((0.3, 0.6, 1.0))] + [0.01] * (W - 2)
            tbl.append(row)
    elif kind == 'pinned':
        tbl = to_float(fam_pinned(T, W, Fraction(1, 2), Fraction(rng.choice((1, 2, 3)))))
    return [[v / sum(row) for v in row] for row in tbl]

def climb(T, W, objective, rng, restarts, iters):
    best = (-1e9, None, None)
    kinds = ['rand', 'blankdom', 'clock', 'pinned']
    for rs in range(restarts):
        tbl = seed(kinds[rs % 4], T, W, rng); r = evaluate(tbl, W); cur = (objective(r), tbl, r); scale = 0.5
        for it in range(iters):
            cand = mutate(cur[1], rng, scale); rc = evaluate(cand, W); sc = objective(rc)
            if sc >= cur[0]: cur = (sc, cand, rc)
            if it % 60 == 59: scale *= 0.8
        if cur[0] > best[0]: best = cur
    return best

def obj_R(r): return -1e9 if r is None else r['maxR_off'] + 0.01 * r['n_off']
def obj_off(m):
    return lambda r: -1e9 if r is None else r['n_off'] + 0.1 * r['maxR_off'] + (0 if r['margin'] >= m else -50 * (m - r['margin']))

rng = random.Random(77)
mode = sys.argv[1]
if mode == 'R':
    for T, W in ((10, 3), (12, 3), (16, 3), (20, 3), (12, 4), (16, 4)):
        t0 = time.time(); sc, tbl, r = climb(T, W, obj_R, rng, restarts=8, iters=220 if T <= 12 else 160)
        ftbl = [[Fraction(v).limit_denominator(10 ** 6) for v in row] for row in tbl]; ftbl = [[v / sum(row) for v in row] for row in ftbl]
        re = analyse(ftbl, W)
        w = max((x for x in re['recs'] if not x['onpath']), key=lambda x: x['Sd'] / x['maxc'] if x['maxc'] else 0, default=None)
        print(f"R-hunt T={T} W={W}: exact maxR_off={float(re['maxR_off']):.3f} margin={float(re['margin']):.4f} D={re['D']} exp_final={re['exp_final']} "
              f"n_off={re['n_off']} K={re['K']} maxK_off={re['maxK_off']} maxKeff_off={float(re['maxKeff_off']):.2f} ({time.time()-t0:.0f}s)")
        if w: print(f"   worst u={''.join(map(str,w['u']))} K_u={w['K']} R={float(w['Sd']/w['maxc']):.3f} B/p*={float(w['B']/re['p']):.3f} maxc/p*={float(w['maxc']/re['p']):.3f} "
                    f"comps/p*={[round(float(c/re['p']),3) for c in w['comps'].values()]} vs={[''.join(map(str,v)) for v in w['vs']]}")
        print("   rows:", [[round(float(v), 3) for v in row] for row in ftbl], flush=True)
else:
    for T, W in ((16, 3), (20, 3), (16, 4), (20, 4)):
        for m in (1.5, 2.0, 3.0):
            t0 = time.time(); sc, tbl, r = climb(T, W, obj_off(m), rng, restarts=8, iters=160)
            ftbl = [[Fraction(v).limit_denominator(10 ** 6) for v in row] for row in tbl]; ftbl = [[v / sum(row) for v in row] for row in ftbl]
            re = analyse(ftbl, W)
            print(f"off-hunt T={T} W={W} target m>={m}: exact margin={float(re['margin']):.4f} D={re['D']} exp_final={re['exp_final']} n_off={re['n_off']} "
                  f"exp/D={re['exp_final']/max(re['D'],1):.2f} K={re['K']} maxK_off={re['maxK_off']} maxR_off={float(re['maxR_off']):.3f} ({time.time()-t0:.0f}s)", flush=True)
            if re['n_off'] > 0 and re['margin'] >= m:
                print("   rows:", [[round(float(v), 3) for v in row] for row in ftbl])
                for x in [x for x in re['recs'] if not x['onpath']][:5]:
                    print(f"     off-path u={''.join(map(str,x['u']))} B/p*={float(x['B']/re['p']):.3f} K_u={x['K']} R={float(x['Sd']/x['maxc']):.3f} maxc/p*={float(x['maxc']/re['p']):.3f}")
print("GATE H2 every reported table re-analysed exactly (Fraction, limit_denominator 1e6)")

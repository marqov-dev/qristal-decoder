"""Adversarial hunt (task 2d): maximise the number of OFF-path final-search expansions subject to a true margin
p*/p2 >= m_target, by random-restart hill climbing over the table entries (float), then verify the best table
in exact Fraction arithmetic (limit_denominator 10^6) and by brute force (T <= 10).
Reports n_off, exp/D, max R(u), max K_u, K and the table, per (T, W, m_target)."""
import sys, random, math, time
from fractions import Fraction
from r1core import *

def evaluate(tbl, W):
    r = analyse(tbl, W, cap=200_000, cap2=200_000)
    if r['capped'] or r['p2'] is None or r['p2'] == 0: return None
    return r

def mutate(tbl, rng, scale):
    T = len(tbl); W = len(tbl[0]); new = [list(r) for r in tbl]
    kind = rng.random()
    if kind < 0.5:                      # perturb one row multiplicatively
        t = rng.randrange(T)
        row = [v * math.exp(scale * rng.gauss(0, 1)) for v in new[t]]; s = sum(row); new[t] = [v / s for v in row]
    elif kind < 0.8:                    # perturb one cell strongly
        t = rng.randrange(T); s_ = rng.randrange(W)
        new[t][s_] *= math.exp(3 * scale * rng.gauss(0, 1)); s = sum(new[t]); new[t] = [v / s for v in new[t]]
    else:                               # copy a row onto a neighbour
        t = rng.randrange(T); t2 = min(T - 1, max(0, t + rng.choice((-1, 1)))); new[t2] = list(new[t])
    return new

def score(r, m_target):
    if r is None: return -1e9
    pen = 0 if r['margin'] >= m_target else -50 * (m_target - r['margin'])
    return r['n_off'] + 0.1 * r['maxR_off'] + pen

def hunt(T, W, m_target, rng, restarts=12, iters=250):
    best = (-1e9, None, None)
    for rs in range(restarts):
        # seeds: random dirichlet-ish or blank-dominant with noise
        if rs % 3 == 0:
            tbl = [[rng.random() ** 2 for _ in range(W)] for _ in range(T)]
        elif rs % 3 == 1:
            tbl = [[0.6] + [0.4 / (W - 1) * math.exp(0.3 * rng.gauss(0, 1)) for _ in range(W - 1)] for _ in range(T)]
        else:
            tbl = [[0.5] + [0.5 / (W - 1) * (1 + 0.5 * rng.random()) for _ in range(W - 1)] for _ in range(T)]
        tbl = [[v / sum(row) for v in row] for row in tbl]
        r = evaluate(tbl, W); sc = score(r, m_target); cur = (sc, tbl, r); scale = 0.5
        for it in range(iters):
            cand = mutate(cur[1], rng, scale); rc = evaluate(cand, W); sc2 = score(rc, m_target)
            if sc2 >= cur[0]: cur = (sc2, cand, rc)
            if it % 50 == 49: scale *= 0.8
        if cur[0] > best[0]: best = cur
    return best

rng = random.Random(2026)
out = []
for T, W in ((8, 3), (10, 3), (12, 3), (8, 4), (10, 4), (12, 4)):
    for m_target in (1.05, 1.2, 1.5, 2.0, 3.0):
        t0 = time.time()
        sc, tbl, r = hunt(T, W, m_target, rng, restarts=9 if T < 12 else 6, iters=200 if T < 12 else 150)
        # exact verification
        ftbl = [[Fraction(v).limit_denominator(10 ** 6) for v in row] for row in tbl]
        ftbl = [[v / sum(row) for v in row] for row in ftbl]
        re = analyse(ftbl, W)
        note = ''
        if T <= 10:
            ex = brute_all(ftbl, W); vals = sorted(ex.values(), reverse=True)
            note = f" brute:{'ok' if vals[0] == re['p'] and vals[1] == re['p2'] else 'MISMATCH'}"
        line = (f"T={T} W={W} target m>={m_target}: exact margin={float(re['margin']):.4f} D={re['D']} exp_final={re['exp_final']} "
                f"n_off={re['n_off']} exp/D={re['exp_final']/max(re['D'],1):.2f} K={re['K']} maxK_off={re['maxK_off']} "
                f"maxR_off={float(re['maxR_off']):.3f} maxKeff_off={float(re['maxKeff_off']):.2f} mode={''.join(map(str,re['mode']))} "
                f"l2={''.join(map(str,re['l2']))} ({time.time()-t0:.0f}s){note}")
        print(line, flush=True)
        out.append((T, W, m_target, re, ftbl))
        if re['n_off'] >= 3 and re['margin'] >= m_target:
            print("   table (rows):"); [print("    ", [f"{float(v):.3f}" for v in row]) for row in ftbl]
            offs = [x for x in re['recs'] if not x['onpath']]
            for x in offs[:6]:
                print(f"     off-path u={''.join(map(str,x['u']))} B/p*={float(x['B']/re['p']):.3f} K_u={x['K']} R={float(x['Sd']/x['maxc']):.3f} "
                      f"maxc/p*={float(x['maxc']/re['p']):.3f} vs={[''.join(map(str,v)) for v in x['vs']]}")
print("GATE H exact (Fraction) re-analysis of every hunted table; brute-force p*,p2 agreement at T<=10 reported per line")

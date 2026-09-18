import sys, random, time
from fractions import Fraction
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder'))
from ctc import ctc_forward, brute_ctc, collapse as tk_collapse, peaky_table
from prefixprob import prefix_prob
from t9core import *

def frac_table(T, W, rng, den=97):
    rows = []
    for _ in range(T):
        r = [Fraction(rng.randrange(1, den)) for _ in range(W)]
        s = sum(r); rows.append([x/s for x in r])
    return rows

def float_table(T, W, rng):
    rows = []
    for _ in range(T):
        r = [rng.random() for _ in range(W)]; s = sum(r); rows.append([x/s for x in r])
    return rows

def frac_peaky(T, W, rng, conf):
    tbl = peaky_table(T, W, rng, conf)
    return [[Fraction(x).limit_denominator(10**6) for x in row] for row in tbl]

rng = random.Random(20260918)

# --- sanity: prob() vs ctc_forward (float)
worst = 0.0; n = 0
for _ in range(200):
    T, W = rng.choice([(3,2),(4,3),(6,3),(8,3),(5,4)])
    tbl = float_table(T, W, rng)
    ex = brute_ctc(tbl)
    for l, p in ex.items():
        worst = max(worst, abs(prob(l, tbl) - p)/max(p, 1e-300)); n += 1
print(f"GATE T9 prob() vs brute force: {n} labellings, worst rel err {worst:.2e} -> {'PASS' if worst < 1e-9 else 'FAIL'}")

# --- Graves bound vs toolkit prefix_prob
worst = 0.0; n = 0
for _ in range(100):
    T, W = rng.choice([(4,3),(6,3),(8,3),(6,4)])
    tbl = float_table(T, W, rng)
    nbsum = [sum(row[d] for d in range(1, W)) for row in tbl]
    node = root_empty(tbl)
    for depth in range(4):
        F = bound_graves(node, tbl, nbsum)
        worst = max(worst, abs(F - prefix_prob(list(node.u), tbl))); n += 1
        node = child(node, rng.randrange(1, W), tbl)
print(f"GATE T9 graves bound vs toolkit prefix_prob: {n} prefixes, worst abs err {worst:.2e} -> {'PASS' if worst < 1e-12 else 'FAIL'}")

# --- (a) decomposition p(u.v) = sum_t ok_{v1}(t) g_v(t), exact Fractions
bad = 0; n = 0
while n < 320:
    T, W = rng.choice([(3,2),(4,2),(5,3),(6,3),(7,3),(5,4)])
    tbl = frac_table(T, W, rng)
    ex = brute_all(tbl, W)
    labs = [l for l in ex if len(l) >= 1]
    for _ in range(4):
        l = rng.choice(labs)
        k = rng.randrange(0, len(l))         # split: u = l[:k], v = l[k:] nonempty
        u, v = l[:k], l[k:]
        okv = ok_vec(u, tbl, v[0])
        lhs = ex[l]
        rhs = sum(okv[t]*suffix_g(v, tbl, t) for t in range(T))
        n += 1
        if lhs != rhs:
            bad += 1
            if bad <= 3: print("  decomposition mismatch", u, v, lhs, rhs)
print(f"GATE (a) decomposition p(u.v) == sum_t ok*g (exact Fraction): {n} triples, mismatches {bad} -> {'PASS' if bad == 0 else 'FAIL'}")

# --- (b) H_c(t) from backward sub-searches vs brute-force max over ALL suffixes (exact Fractions)
bad = 0; cells = 0; tables = 0
for i in range(110):
    T, W = rng.choice([(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(5,4),(6,4)])
    if i % 3 == 0: tbl = frac_peaky(T, W, rng, rng.choice([0.6, 0.8, 0.9]))
    else: tbl = frac_table(T, W, rng)
    st = Stats(); H = compute_H(tbl, W, st)
    tables += 1
    for t0 in range(T):
        for c in range(1, W):
            bm = max(brute_suffix_masses(tbl, W, t0, c).values())
            cells += 1
            if H[c][t0] != bm:
                bad += 1
                if bad <= 3: print("  H mismatch", t0, c, H[c][t0], bm)
print(f"GATE (b) H_c(t) exact-backward vs brute-force max_v g_v(t) (exact Fraction): {tables} tables, {cells} cells, mismatches {bad} -> {'PASS' if bad == 0 else 'FAIL'}")

# --- (c) decoder argmax vs brute force
def check(tbl, W, tag, counts):
    ex = brute_ctc(tbl)
    pstar = max(ex.values())
    r = decode_exactbwd(tbl, W)
    g = decode_graves(tbl, W)
    counts['n'] += 1
    okr = abs(ex.get(r['mode'], 0.0) - pstar) <= 1e-12*pstar and abs(r['p'] - pstar) <= 1e-9*pstar
    okg = abs(ex.get(g['mode'], 0.0) - pstar) <= 1e-12*pstar
    if not okr: counts['wrong_exactbwd'] += 1; print("  WRONG exactbwd", tag, r['mode'], r['p'], pstar)
    if not okg: counts['wrong_graves'] += 1; print("  WRONG graves", tag, g['mode'], pstar)
    if r['mode'] != g['mode']: counts['ties'] += 1

c1 = dict(n=0, wrong_exactbwd=0, wrong_graves=0, ties=0)
for i in range(300):
    T, W = rng.choice([(3,2),(4,2),(5,3),(6,3),(7,3),(8,3),(8,2)])
    check(float_table(T, W, rng), W, f"rnd{i}", c1)
print(f"GATE (c1) argmax vs brute force, random T<=8 W<=3: {c1}")
c2 = dict(n=0, wrong_exactbwd=0, wrong_graves=0, ties=0)
for i in range(100):
    T, W = rng.choice([(6,3),(8,3),(8,4),(7,4)])
    check(peaky_table(T, W, rng, rng.choice([0.6,0.7,0.8,0.9])), W, f"peaky{i}", c2)
print(f"GATE (c2) argmax vs brute force, peaky T<=8 W<=4: {c2}")
c3 = dict(n=0, wrong_exactbwd=0, wrong_graves=0, ties=0)
t0 = time.time()
for i in range(100):
    W = 5 if i % 2 == 0 else 8
    T = rng.choice([4,5,6]) if W == 5 else rng.choice([4,5])
    tbl = float_table(T, W, rng) if i % 4 < 2 else peaky_table(T, W, rng, rng.choice([0.6,0.8]))
    check(tbl, W, f"w{W}_{i}", c3)
print(f"GATE (c3) argmax vs brute force, W in {{5,8}} T<=6: {c3}  ({time.time()-t0:.0f}s)")

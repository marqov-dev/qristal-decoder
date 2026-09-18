"""Gate 1 (all Fraction-exact):
 G1a instrumented pipeline == t9core.decode_exactbwd (mode, p*, exp_final, gen_back, gen)  [identity of the harness]
 G1b p*, p2 from exact brute force == decoder p*, second_best p2   (T <= 10)
 G1c Lemma 3 on EVERY expanded node: S_d(u) <= sum_{v in V_u} p(u.v)  and B(u) == max(p(u), S_d(u))
 G1d Theorem A (per node): every OFF-path expanded u has  sum_{v in V_u} p(u.v) >= p*  and  K_u >= margin
     (i.e. margin <= K_u), and max_v p(u.v) >= p*/K_u
 G1e Theorem A (a priori): whenever margin > K := max_d |{V[d][t]}|, exp_final <= D+1 and no off-path node
 G1f enumerate_above(theta) == brute-force set {l : p(l) >= theta}  (T <= 10, theta = p*/(2K))
 G1g Theorem B (per depth): #off-path expanded at depth j <= (2/m) * (N(p*/2K) - 1)
"""
import random, sys, time
from fractions import Fraction
from r1core import *

rng = random.Random(1)
def rand_rows(T, W, F=Fraction):
    rows = []
    for _ in range(T):
        r = [F(rng.randint(1, 30)) for _ in range(W)]; s = sum(r); rows.append([v / s for v in r])
    return rows
def peaky_rows(T, W, conf, F=Fraction):
    conf = F(conf); rows = []
    for _ in range(T):
        win = 0 if rng.random() < 0.7 else rng.randrange(1, W)
        r = [(1 - conf) / (W - 1)] * W; r[win] = conf; rows.append(r)
    return rows

insts = []
for T in (6, 8, 10):
    for W in (3, 4, 5):
        insts.append((f"rand T={T} W={W}", rand_rows(T, W)))
        insts.append((f"peaky0.8 T={T} W={W}", peaky_rows(T, W, Fraction(4, 5))))
        insts.append((f"peaky0.6 T={T} W={W}", peaky_rows(T, W, Fraction(3, 5))))
        insts.append((f"blankdom0.6 T={T} W={W}", fam_blankdom(T, W, Fraction(3, 5))))
        for delta in (Fraction(1), Fraction(3)):
            insts.append((f"pinned d={delta} T={T} W={W}", fam_pinned(T, W, Fraction(1, 2), delta)))
        insts.append((f"tworate T={T} W={W}", fam_tworate(T, W, Fraction(3, 5), Fraction(1, 4), Fraction(1, 8), Fraction(1, 40))))
    insts.append((f"alt0.7 T={T} W=3", fam_alt(T, 3, Fraction(7, 10))))
# larger instances for G1a/c/d/e only (no brute force)
big = []
for T in (14, 18):
    for W in (3, 4):
        big.append((f"pinned d=1 T={T} W={W}", fam_pinned(T, W, Fraction(1, 2), Fraction(1))))
        big.append((f"tworate T={T} W={W}", fam_tworate(T, W, Fraction(3, 5), Fraction(1, 4), Fraction(1, 8), Fraction(1, 40))))
        big.append((f"rand T={T} W={W}", rand_rows(T, W)))

viol = dict(a=0, b=0, c=0, d=0, e=0, f=0, g=0); n = dict(a=0, b=0, c=0, d=0, e=0, f=0, g=0)
t0 = time.time()
for name, tbl in insts + big:
    W = len(tbl[0]); T = len(tbl)
    ref = decode_exactbwd(tbl, W)
    r = analyse(tbl, W)
    n['a'] += 1
    if not (ref['mode'] == r['mode'] and ref['p'] == r['p'] and ref['exp_final'] == r['exp_final']
            and ref['gen_back'] == r['gen_back'] and ref['gen'] == r['gen']):
        viol['a'] += 1; print("  G1a MISMATCH", name, ref['exp_final'], r['exp_final'], ref['gen'], r['gen'])
    ps, p2, m, K, D = r['p'], r['p2'], r['margin'], r['K'], r['D']
    brute = None
    if T <= 10:
        brute = brute_all(tbl, W); vals = sorted(brute.values(), reverse=True)
        n['b'] += 1
        if not (vals[0] == ps and vals[1] == p2):
            viol['b'] += 1; print("  G1b MISMATCH", name, float(vals[0]), float(ps), float(vals[1]), float(p2))
    off_by_depth = {}
    for rec in r['recs']:
        n['c'] += 1
        Bchk = max(rec['p'], rec['Sd']) if rec['Sd'] is not None else rec['p']
        if rec['Sd'] is not None and rec['Sd'] > rec['sumc']: viol['c'] += 1; print("  G1c Lemma3 VIOL", name, rec['u'])
        if Bchk != rec['B']: viol['c'] += 1; print("  G1c B VIOL", name, rec['u'])
        if not rec['onpath']:
            n['d'] += 1
            ok = (rec['sumc'] >= ps) and (rec['K'] >= m) and (rec['maxc'] * rec['K'] >= ps)
            if not ok: viol['d'] += 1; print("  G1d VIOL", name, rec['u'], float(rec['sumc'] / ps), rec['K'], float(m))
            off_by_depth[len(rec['u'])] = off_by_depth.get(len(rec['u']), 0) + 1
    n['e'] += 1
    if m > K:
        if r['n_off'] != 0 or r['exp_final'] > D + 1: viol['e'] += 1; print("  G1e VIOL", name, r['n_off'], r['exp_final'], D)
    theta = ps / (2 * K)
    above = enumerate_above(tbl, W, r['H'], theta)
    if brute is not None:
        n['f'] += 1
        bset = {l: p for l, p in brute.items() if p >= theta}
        if bset != above: viol['f'] += 1; print("  G1f VIOL", name, len(bset), len(above))
    N2K = len(above)
    for j, cnt in off_by_depth.items():
        n['g'] += 1
        if cnt > (2 / m) * (N2K - 1): viol['g'] += 1; print("  G1g VIOL", name, j, cnt, float((2 / m) * (N2K - 1)))
    print(f"  {name:26s} D={D} p*={fmt(ps)} margin={fmt(m)} K={K} exp_final={r['exp_final']} off={r['n_off']} "
          f"maxK_off={r['maxK_off']} maxR_off={fmt(r['maxR_off'])} maxKeff_off={fmt(r['maxKeff_off'])} N(p*/2K)={N2K}", flush=True)
print(f"({time.time()-t0:.0f}s)")
def line(k, txt): print(f"GATE G1{k} {txt}: {n[k]} checks, violations {viol[k]} -> {'PASS' if viol[k]==0 else 'FAIL'}")
line('a', "instrumented pipeline == t9core.decode_exactbwd (mode, p*, exp_final, gen_back, gen)")
line('b', "brute-force (Fraction) p*, p2 == decoder p*, second_best p2 (T<=10)")
line('c', "Lemma 3 on every expanded node: S_d(u) <= sum_{v in V_u} p(u.v), B(u) == max(p(u), S_d(u))")
line('d', "Theorem A per node: off-path expanded u has sum_{V_u} p(u.v) >= p*, K_u >= margin, max_v p(u.v) >= p*/K_u")
line('e', "Theorem A a priori: margin > K  =>  no off-path expansion and exp_final <= D+1")
line('f', "enumerate_above(p*/2K) == brute-force near-mode set (T<=10)")
line('g', "Theorem B per depth: #off-path expanded at depth j <= (2/m)(N(p*/2K)-1)")

"""Gates for every decoder / bound in bounds.py.  Nothing is reported without these passing."""
import random, math, sys, os
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bounds import *
from prefixprob import prefix_prob

def brute_g(table, t, c):
    """g_v(t) for every v with v_1=c, by enumerating paths on frames t..T with pi_t = c."""
    T = len(table); W = len(table[0]); out = {}
    for tail in product(range(W), repeat=T-t):
        path = (c,) + tail; p = 1.0
        for i, s in enumerate(path): p *= table[t-1+i][s]
        v = collapse(path); out[v] = out.get(v, 0.0) + p
    return out

def gate_F():
    rng = random.Random(7); worst = 0.0; n = 0
    for _ in range(200):
        T, W = rng.choice([(3,2),(4,2),(5,2),(3,3),(4,3),(6,2),(5,3)])
        tbl = random_table(rng, T, W)
        stack = [root_node(tbl)]
        while stack:
            node = stack.pop()
            got = graves_F(node, tbl); truth = prefix_prob(node.u, tbl)
            worst = max(worst, abs(got - truth)); n += 1
            if len(node.u) < 4:
                for d in range(1, W): stack.append(child(node, d, tbl))
    return n, worst

def gate_admissible():
    """Every Hhat family must dominate brute-force H_c(t); the exact-backward one must EQUAL it."""
    rng = random.Random(11); n = 0; viol = {'tree': 0, 'policy': 0, 'exact': 0}; worst_eq = 0.0
    for i in range(160):
        T, W = rng.choice([(3,2),(4,2),(5,2),(3,3),(4,3),(6,2),(5,3),(6,3)])
        tbl = random_table(rng, T, W) if i % 2 == 0 else peaky_table(T, W, rng, rng.choice([0.8, 0.9, 0.95]))
        theta = rng.choice([1e-3, 1e-2, 0.05, 0.2, 0.5])
        Ht, _ = H_suffix_tree(tbl, theta); Hp = H_policy(tbl); He, _ = H_exact_backward(tbl, Hp)
        for t in range(1, T+1):
            for c in range(1, W):
                g = brute_g(tbl, t, c); Hc = max(g.values())
                n += 1
                if Ht[c][t] < Hc - 1e-12: viol['tree'] += 1
                if Hp[c][t] < Hc - 1e-12: viol['policy'] += 1
                if He[c][t] < Hc - 1e-12: viol['exact'] += 1
                worst_eq = max(worst_eq, abs(He[c][t] - Hc))
    return n, viol, worst_eq

def gate_argmax(decoders, n_rand=300, n_peaky=100, seed=3):
    rng = random.Random(seed); bad = {k: 0 for k in decoders}; n = 0; ties = 0
    inst = []
    for _ in range(n_rand):
        T, W = rng.choice([(4,2),(5,2),(6,2),(7,2),(8,2),(4,3),(5,3),(6,3),(7,3),(8,3)])
        inst.append(random_table(rng, T, W))
    for _ in range(n_peaky):
        T, W = rng.choice([(5,2),(6,2),(7,2),(8,2),(5,3),(6,3),(7,3),(8,3)])
        inst.append(peaky_table(T, W, rng, rng.choice([0.8, 0.9, 0.95])))
    for tbl in inst:
        l, p, ex = brute_mode(tbl); n += 1
        for k, f in decoders.items():
            r = f(tbl)
            bp, bl = r[0], r[1]
            if bl != l and not (abs(ex.get(bl, -1.0) - p) <= 1e-12 and abs(bp - p) <= 1e-12):
                bad[k] += 1
            elif bl != l: ties += 1
    return n, bad, ties

if __name__ == '__main__':
    n, w = gate_F()
    print(f"GATE graves_F vs prefix_prob: {n} prefixes, worst abs err {w:.2e} -> {'PASS' if w < 1e-12 else 'FAIL'}")
    n, viol, we = gate_admissible()
    ok = all(v == 0 for v in viol.values()) and we < 1e-12
    print(f"GATE admissibility Hhat >= brute-force H_c(t): {n} (t,c) cells, violations {viol}, "
          f"exact-backward worst |H - brute| {we:.2e} -> {'PASS' if ok else 'FAIL'}")
    decs = {
        'graves':   lambda tb: decode_graves(tb),
        'childF':   lambda tb: decode_childF(tb),
        'bidir':    lambda tb: decode_bidir(tb, math.sqrt(beam_incumbent(tb, 16)[1])),
        'bidir.1':  lambda tb: decode_bidir(tb, 0.1),
        'policy':   lambda tb: decode_policy(tb),
        'exactbwd': lambda tb: decode_exact_backward(tb),
        'dfs_bb':   lambda tb: dfs_bb(tb, lambda n: graves_F(n, tb), *beam_incumbent(tb, 8)[::-1]),
        'graves+beam': lambda tb: decode_graves(tb, *beam_incumbent(tb, 8)[::-1]),
        'policy+vit':  lambda tb: decode_policy(tb, *viterbi_collapse(tb)[::-1]),
    }
    n, bad, ties = gate_argmax(decs)
    ok = all(v == 0 for v in bad.values())
    print(f"GATE argmax vs brute force: {n} instances (300 random T<=8 W<=3 + 100 peaky), wrong = {bad}, "
          f"exact ties {ties} -> {'PASS' if ok else 'FAIL'}")

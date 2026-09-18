"""CTC prefix probability Pr(output labelling begins with l), and the truncated-tree
size |T_p|.  Gated against brute-force enumeration before any use.

DP over the extended label sequence for l, plus an ABSORB state entered when the path
emits a symbol BEYOND l (such a labelling still has l as a prefix, so it counts)."""
import sys
from itertools import product
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from ctc import brute_ctc, collapse, peaky_table, topk_labellings

def prefix_prob(l, table, blank=0):
    """Pr(the output labelling has l as a prefix)."""
    T = len(table)
    if len(l) == 0: return 1.0
    ext = [blank]
    for s in l: ext += [s, blank]
    S = len(ext)
    a = [0.0]*S; absorb = 0.0
    a[0] = table[0][ext[0]]
    if S > 1: a[1] = table[0][ext[1]]
    for t in range(1, T):
        b = [0.0]*S
        for s in range(S):
            v = a[s]
            if s >= 1: v += a[s-1]
            if s >= 2 and ext[s] != blank and ext[s] != ext[s-2]: v += a[s-2]
            b[s] = v * table[t][ext[s]]
        # mass that leaves the end-of-l states by emitting a NEW symbol -> still prefix l
        nb = 1.0 - table[t][blank]
        new_abs = absorb + a[S-1]*nb
        if S >= 2:
            last = ext[S-2]
            new_abs += a[S-2]*max(0.0, nb - table[t][last])
        a, absorb = b, new_abs
    return a[S-1] + (a[S-2] if S >= 2 else 0.0) + absorb

def truncated_tree_size(table, p, blank=0, cap=2_000_000):
    """|T_p| = number of prefixes l with Pr(prefix l) >= p.  BFS; ancestor-closed."""
    W = len(table[0]); n = 0; frontier = [()]
    while frontier:
        nxt = []
        for pref in frontier:
            n += 1
            if n > cap: return None
            for c in range(W):
                if c == blank: continue
                ch = pref + (c,)
                if prefix_prob(ch, table, blank) >= p: nxt.append(ch)
        frontier = nxt
    return n

def gate():
    """prefix_prob must equal the summed brute-force mass of all extensions."""
    import random
    rng = random.Random(1234); worst = 0.0; n = 0
    for _ in range(200):
        T, W = rng.choice([(3,2),(4,2),(5,2),(3,3),(4,3),(6,2)])
        tbl = [[rng.random() for _ in range(W)] for _ in range(T)]
        tbl = [[v/sum(r) for v in r] for r in tbl]
        exact = brute_ctc(tbl)
        cands = set()
        for b in exact:
            for k in range(len(b)+1): cands.add(b[:k])
        for l in cands:
            truth = sum(p for b, p in exact.items() if b[:len(l)] == l)
            got = prefix_prob(l, tbl)
            worst = max(worst, abs(got-truth)); n += 1
    return n, worst

if __name__ == '__main__':
    n, worst = gate()
    ok = worst < 1e-12
    print(f"GATE prefix_prob vs brute force: {n} prefixes, worst abs error {worst:.2e} "
          f"-> {'PASS' if ok else 'FAIL'}")
    if not ok: raise SystemExit(1)

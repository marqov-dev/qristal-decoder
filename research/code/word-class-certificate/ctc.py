"""Exact CTC tools: forward recursion + peaky table generation.
Validated against brute-force enumeration before use (see validate_ctc()).
"""
import math, random
from itertools import product

def collapse(path, blank=0):
    return tuple(s for t, s in enumerate(path)
                 if (t == 0 or s != path[t-1]) and s != blank)

def brute_ctc(table, blank=0):
    W = len(table[0]); out = {}
    for path in product(range(W), repeat=len(table)):
        p = 1.0
        for t, s in enumerate(path): p *= table[t][s]
        b = collapse(path, blank); out[b] = out.get(b, 0.0) + p
    return out

def ctc_forward(l, table, blank=0):
    """Exact p(l|y) by the CTC forward recursion. O(T*|l|). Graves 2006 sec 4.1."""
    T = len(table); k = len(l)
    ext = [blank]
    for s in l: ext += [s, blank]          # blank, l1, blank, l2, ... blank
    S = len(ext)
    a = [0.0]*S
    a[0] = table[0][ext[0]]
    if S > 1: a[1] = table[0][ext[1]]
    for t in range(1, T):
        b = [0.0]*S
        for s in range(S):
            v = a[s]
            if s >= 1: v += a[s-1]
            if s >= 2 and ext[s] != blank and ext[s] != ext[s-2]: v += a[s-2]
            b[s] = v * table[t][ext[s]]
        a = b
    return a[S-1] + (a[S-2] if S >= 2 else 0.0)

def peaky_table(T, W, rng, conf):
    """Realistic CTC posterior: blank-dominated, near-one-hot. `conf` = mass on the
    winning symbol (CTC posteriors are notoriously peaky -- arXiv:2105.14849)."""
    rows = []
    for _ in range(T):
        # ~70% of frames spike on blank, as real CTC does
        win = 0 if rng.random() < 0.7 else rng.randrange(1, W)
        row = [(1.0-conf)/(W-1)]*W
        row[win] = conf
        rows.append(row)
    return rows

def topk_labellings(table, blank=0, beam=400, k=5):
    """Proper CTC prefix beam search, tracking (p_blank, p_nonblank) per prefix.
    With a large enough beam this is EXACT. Returns [(p(l|y), l), ...] descending."""
    T, W = len(table), len(table[0])
    # prefix -> [p_blank, p_nonblank]
    cur = {(): [1.0, 0.0]}
    for t in range(T):
        nxt = {}
        for pref, (pb, pnb) in cur.items():
            tot = pb + pnb
            if tot <= 0.0: continue
            for c in range(W):
                y = table[t][c]
                if y <= 0.0: continue
                if c == blank:
                    e = nxt.setdefault(pref, [0.0, 0.0]); e[0] += tot * y
                elif pref and pref[-1] == c:
                    # extending with the same symbol: merges unless separated by a blank
                    e = nxt.setdefault(pref, [0.0, 0.0]);      e[1] += pnb * y
                    e2 = nxt.setdefault(pref + (c,), [0.0, 0.0]); e2[1] += pb * y
                else:
                    e = nxt.setdefault(pref + (c,), [0.0, 0.0]); e[1] += tot * y
        cur = dict(sorted(nxt.items(), key=lambda kv: -(kv[1][0] + kv[1][1]))[:beam])
    scored = sorted(((pb + pnb, l) for l, (pb, pnb) in cur.items()), reverse=True)
    return scored[:k]

def validate_beam():
    """Gate: does the beam search find the TRUE argmax and exact scores?"""
    import random as _r
    rng = _r.Random(99); bad_arg = 0; worst = 0.0; n = 0
    for _ in range(300):
        T, W = rng.choice([(3,2),(4,2),(5,2),(3,3),(4,3),(6,2)])
        tbl = [[rng.random() for _ in range(W)] for _ in range(T)]
        tbl = [[v/sum(r) for v in r] for r in tbl]
        exact = brute_ctc(tbl)
        truth = max(exact.items(), key=lambda kv: kv[1])
        got = topk_labellings(tbl, beam=10000, k=1)
        n += 1
        if not got or got[0][1] != truth[0]:
            if not got or abs(got[0][0] - truth[1]) > 1e-12: bad_arg += 1
        if got: worst = max(worst, abs(got[0][0] - exact.get(got[0][1], 0.0)))
    return n, bad_arg, worst

def validate_ctc():
    """Gate: forward recursion must match brute force before we trust it at large T."""
    rng = random.Random(42); worst = 0.0; n = 0
    for _ in range(300):
        T, W = rng.choice([(2,2),(3,2),(4,2),(2,3),(3,3),(5,2)])
        tbl = [[rng.random() for _ in range(W)] for _ in range(T)]
        tbl = [[v/sum(r) for v in r] for r in tbl]
        exact = brute_ctc(tbl)
        for l, p in exact.items():
            got = ctc_forward(l, tbl)
            worst = max(worst, abs(got-p)/max(p, 1e-300)); n += 1
    return n, worst

if __name__ == '__main__':
    n, worst = validate_ctc()
    print(f"GATE ctc_forward vs brute force: {n} labellings checked, "
          f"worst relative error {worst:.2e}  -> {'PASS' if worst < 1e-9 else 'FAIL'}")
    n2, bad, w2 = validate_beam()
    print(f"GATE prefix beam search vs brute force: {n2} instances, {bad} wrong argmax, "
          f"worst score error {w2:.2e}  -> {'PASS' if bad == 0 and w2 < 1e-12 else 'FAIL'}")

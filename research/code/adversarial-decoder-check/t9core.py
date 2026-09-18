"""T9 independent re-implementation of the T2b 'exact backward suffix mode' decoder,
written from the T2b report's algorithm description only (no T2b code read).

Conventions: frames 0..T-1 (0-indexed), blank = 0. Works for float and Fraction tables.
A search node for prefix u over a sub-table sub[0..L-1] carries
  Ab[k], An[k] (k = 0..L): mass of paths over the first k frames of the sub-table that collapse
  to u and end in the blank-after-u state / the last-symbol state.
  ok_d(k) = Ab[k] + [u_last != d] * An[k]  (mass that lets symbol d start FRESH at sub-frame k)
  p(u) = Ab[L] + An[L]
Bound (exact-backward): B(u) = max(p(u), max_d sum_k ok_d(k) * H[d][t0+k]),
  H[d][t] = max over suffixes v with v_1 = d of g_v(t) (g = mass of paths over frames t..T-1 with pi_t = d
  collapsing to v).
Graves' bound: F(u) = p(u) + sum_k sum_{d != blank} ok_d(k) * y[t0+k][d].
"""
import heapq
from operator import mul
from itertools import product

BLANK = 0

class Node:
    __slots__ = ('u', 'Ab', 'An', 'p', 'B')
    def __init__(self, u, Ab, An):
        self.u = u; self.Ab = Ab; self.An = An
        self.p = Ab[-1] + An[-1]; self.B = None

def root_empty(sub):
    """Empty prefix over the sub-table."""
    L = len(sub); Ab = [0]*(L+1); An = [0]*(L+1)
    Ab[0] = 1
    for k in range(1, L+1):
        Ab[k] = Ab[k-1]*sub[k-1][BLANK]
    return Node((), Ab, An)

def root_forced(sub, c):
    """Prefix (c,) with pi at sub-frame 0 FORCED to be c (the suffix-search root)."""
    L = len(sub); Ab = [0]*(L+1); An = [0]*(L+1)
    An[1] = sub[0][c]
    for k in range(2, L+1):
        An[k] = An[k-1]*sub[k-1][c]
        Ab[k] = (Ab[k-1] + An[k-1])*sub[k-1][BLANK]
    return Node((c,), Ab, An)

def child(node, d, sub):
    L = len(sub); Ab = node.Ab; An = node.An
    same = (len(node.u) > 0 and node.u[-1] == d)
    nAb = [0]*(L+1); nAn = [0]*(L+1)
    for k in range(1, L+1):
        row = sub[k-1]
        start = Ab[k-1] if same else Ab[k-1] + An[k-1]
        nAn[k] = (nAn[k-1] + start)*row[d]
        nAb[k] = (nAb[k-1] + nAn[k-1])*row[BLANK]
    return Node(node.u + (d,), nAb, nAn)

# ---------- bounds ----------
def bound_H(node, Hsub, W):
    """Hsub[d] = [H[d][t0+k] for k in 0..L-1]. Exact-backward bound."""
    Ab, An = node.Ab, node.An
    last = node.u[-1] if node.u else None
    best = node.p
    for d in range(1, W):
        hd = Hsub[d]
        s = sum(map(mul, Ab, hd))
        if last != d:
            s += sum(map(mul, An, hd))
        if s > best: best = s
    return best

def bound_graves(node, sub, nbsum):
    """nbsum[k] = sum_{d != blank} sub[k][d]."""
    Ab, An = node.Ab, node.An
    s = node.p + sum(map(mul, Ab, nbsum))
    if node.u:
        last = node.u[-1]
        s += sum(map(mul, An, [nb - row[last] for nb, row in zip(nbsum, sub)]))
    else:
        s += sum(map(mul, An, nbsum))
    return s

# ---------- generic best-first ----------
class Stats:
    def __init__(self): self.exp = 0; self.gen = 0; self.capped = False

def best_first(root, W, sub, bound, stats, cap=None, update_on_gen=True):
    """Best-first search over prefixes; terminates when the top bound <= incumbent.
    Returns (best_prefix, best_p)."""
    root.B = bound(root)
    inc = root.p; best = root.u
    heap = [(-root.B, 0, root)]; cnt = 1
    while heap:
        negB, _, node = heapq.heappop(heap)
        if -negB <= inc: break
        stats.exp += 1
        if node.p > inc: inc, best = node.p, node.u
        for d in range(1, W):
            ch = child(node, d, sub); stats.gen += 1
            if cap is not None and stats.gen > cap:
                stats.capped = True; return best, inc
            if update_on_gen and ch.p > inc: inc, best = ch.p, ch.u
            ch.B = bound(ch)
            if ch.B > inc:
                cnt += 1; heapq.heappush(heap, (-ch.B, cnt, ch))
    return best, inc

# ---------- exact-backward decoder ----------
def compute_H(table, W, stats, cap=None, per_search=None):
    """H[d][t] for all d in 1..W-1, t in 0..T-1, computed backward by best-first sub-searches
    whose bounds read only H[.][t'] for t' > t."""
    T = len(table)
    H = [[0]*T for _ in range(W)]   # H[0] unused
    for t0 in range(T-1, -1, -1):
        sub = table[t0:]
        Hsub = [H[d][t0:] for d in range(W)]   # H[d][t0] is still 0 but ok_d(0)=0 for every node here
        for c in range(1, W):
            root = root_forced(sub, c)
            s = Stats()
            bnd = lambda n: bound_H(n, Hsub, W)
            v, g = best_first(root, W, sub, bnd, s, cap=None if cap is None else cap - stats.gen)
            stats.exp += s.exp; stats.gen += s.gen
            if per_search is not None: per_search.append((t0, c, s.exp, s.gen, len(v)))
            if s.capped: stats.capped = True; return H
            H[c][t0] = g
    return H

def decode_exactbwd(table, W=None, cap=None, per_search=None):
    """Returns dict(mode, p, exp_final, gen_final, exp_back, gen_back, gen, capped, H)."""
    if W is None: W = len(table[0])
    sb = Stats()
    H = compute_H(table, W, sb, cap=cap, per_search=per_search)
    if sb.capped:
        return dict(mode=None, p=None, capped=True, gen=sb.gen, exp_back=sb.exp, gen_back=sb.gen,
                    exp_final=0, gen_final=0, H=H)
    sub = table
    Hsub = [H[d] for d in range(W)]
    sf = Stats()
    root = root_empty(sub)
    mode, p = best_first(root, W, sub, lambda n: bound_H(n, Hsub, W), sf,
                         cap=None if cap is None else cap - sb.gen)
    return dict(mode=mode, p=p, capped=sf.capped, gen=sb.gen + sf.gen, exp_back=sb.exp, gen_back=sb.gen,
                exp_final=sf.exp, gen_final=sf.gen, H=H)

def decode_graves(table, W=None, cap=None):
    if W is None: W = len(table[0])
    nbsum = [sum(row[d] for d in range(1, W)) for row in table]
    s = Stats()
    root = root_empty(table)
    mode, p = best_first(root, W, table, lambda n: bound_graves(n, table, nbsum), s, cap=cap)
    return dict(mode=mode, p=p, capped=s.capped, exp=s.exp, gen=s.gen)

# ---------- exact reference helpers (Fraction-safe) ----------
def collapse(path):
    return tuple(s for t, s in enumerate(path) if (t == 0 or s != path[t-1]) and s != BLANK)

def brute_all(table, W):
    out = {}
    for path in product(range(W), repeat=len(table)):
        p = 1
        for t, s in enumerate(path): p = p*table[t][s]
        b = collapse(path); out[b] = out.get(b, 0) + p
    return out

def brute_suffix_masses(table, W, t0, c):
    """{v: g_v(t0)} over all paths on frames t0..T-1 with pi_t0 = c."""
    out = {}
    L = len(table) - t0
    for rest in product(range(W), repeat=L-1):
        path = (c,) + rest
        p = table[t0][c]
        for k, s in enumerate(rest): p = p*table[t0+1+k][s]
        b = collapse(path); out[b] = out.get(b, 0) + p
    return out

def prob(l, table):
    """p(l|y) via forward states (same code path as the search)."""
    n = root_empty(table)
    for d in l: n = child(n, d, table)
    return n.p

def suffix_g(v, table, t0):
    """g_v(t0) via the forced root + children."""
    sub = table[t0:]
    n = root_forced(sub, v[0])
    for d in v[1:]: n = child(n, d, sub)
    return n.p

def ok_vec(u, table, d):
    n = root_empty(table)
    for s in u: n = child(n, s, table)
    last = u[-1] if u else None
    return [n.Ab[k] + (0 if last == d else n.An[k]) for k in range(len(table)+1)]

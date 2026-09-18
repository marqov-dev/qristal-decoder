"""Pure-Python core of certctc: a line-for-line mirror of `_core/certctc.c` (itself the T2b
`exactbwd.c` search, i.e. T2b `bounds.py::decode_exact_backward` plus runner-up certification).

Every arithmetic operation is performed in the same order as in the C core, and the binary heap
is the same algorithm with the same comparisons, so on float tables the two backends produce
bit-identical probabilities, H tables, labellings and node counts (gated in the test suite).
The arithmetic is generic: `fractions.Fraction` tables give exact rational results (used by the
exactness gates).

Conventions: frames 1..T, blank = column 0 (the public API permutes other blanks to 0).
"""
import time

__all__ = ['decode_python', 'suffix_root', 'final_root', 'make_child', 'bound_of', 'make_ctx']


class _Node(object):
    __slots__ = ('parent', 'sym', 'tmin', 'Ab', 'An', 'p')

    def __init__(self, parent, sym, tmin, Ab, An):
        self.parent = parent; self.sym = sym; self.tmin = tmin
        self.Ab = Ab; self.An = An
        self.p = Ab[-1] + An[-1]

    def labelling(self):
        out = []; n = self
        while n is not None:
            if n.sym > 0: out.append(n.sym)
            n = n.parent
        out.reverse(); return tuple(out)


class _Ctx(object):
    __slots__ = ('table', 'T', 'W', 'H', 'Mmax', 'gen', 'gen_cap', 'deadline', 'status',
                 'exp_final', 'exp_bwd')


class _Heap(object):
    """Binary max-heap on bound, ported operation-for-operation from the C core (same tie behaviour)."""
    __slots__ = ('b', 'it')

    def __init__(self): self.b = []; self.it = []

    def __len__(self): return len(self.b)

    def push(self, bound, node):
        b = self.b; it = self.it
        b.append(bound); it.append(node); i = len(b) - 1
        while i > 0:
            p = (i - 1) // 2
            if b[p] >= b[i]: break
            b[p], b[i] = b[i], b[p]; it[p], it[i] = it[i], it[p]; i = p

    def pop(self):
        b = self.b; it = self.it
        top = (b[0], it[0])
        lb = b.pop(); li = it.pop()
        n = len(b)
        if n > 0:
            b[0] = lb; it[0] = li; i = 0
            while True:
                l = 2 * i + 1; r = l + 1; m = i
                if l < n and b[l] > b[m]: m = l
                if r < n and b[r] > b[m]: m = r
                if m == i: break
                b[m], b[i] = b[i], b[m]; it[m], it[i] = it[i], it[m]; i = m
        return top


def suffix_root(table, t, c):
    """Root of the suffix problem: symbol c forced at frame t (1-based), nothing before."""
    T = len(table); Ab = [0] * (T + 1); An = [0] * (T + 1)
    An[t] = table[t - 1][c]
    for s in range(t + 1, T + 1):
        An[s] = An[s - 1] * table[s - 1][c]
        Ab[s] = (Ab[s - 1] + An[s - 1]) * table[s - 1][0]
    return _Node(None, c, t, Ab, An)


def final_root(table):
    T = len(table); Ab = [0] * (T + 1); An = [0] * (T + 1); Ab[0] = 1
    for s in range(1, T + 1): Ab[s] = Ab[s - 1] * table[s - 1][0]
    return _Node(None, 0, 0, Ab, An)


def make_child(ctx, p, d):
    T = ctx.T; tb = ctx.table
    Ab = [0] * (T + 1); An = [0] * (T + 1)
    pAb = p.Ab; pAn = p.An; same = (p.sym == d)
    for s in range(p.tmin + 1, T + 1):
        y = tb[s - 1]
        ok = pAb[s - 1] if same else pAb[s - 1] + pAn[s - 1]
        An[s] = (An[s - 1] + ok) * y[d]
        Ab[s] = (Ab[s - 1] + An[s - 1]) * y[0]
    ctx.gen += 1
    tmin = p.tmin + 1
    if tmin > T: tmin = T
    return _Node(p, d, tmin, Ab, An)


def bound_of(ctx, n, thresh):
    """B(u) = max(p(u), max_d sum_t ok_d(t-1) H_d(t)); quick admissible filter with Mmax first."""
    T = ctx.T; W = ctx.W; best = n.p; t0 = n.tmin
    Ab = n.Ab; An = n.An; M = ctx.Mmax
    s1 = 0
    for t in range(t0 + 1, T + 1): s1 += (Ab[t - 1] + An[t - 1]) * M[t]
    if s1 <= thresh and best <= thresh: return best if best > s1 else s1
    Hh = ctx.H; sym = n.sym
    for d in range(1, W):
        H = Hh[d]; s = 0
        if d == sym:
            for t in range(t0 + 1, T + 1): s += Ab[t - 1] * H[t]
        else:
            for t in range(t0 + 1, T + 1): s += (Ab[t - 1] + An[t - 1]) * H[t]
        if s > best: best = s
    return best


def _search(ctx, root, k2):
    """Best-first search from `root`; k2: also certify the runner-up.
    Returns (b1, b2, node1, node2, expansions)."""
    W = ctx.W; b1 = 0; b2 = 0; n1 = None; n2 = None; exp = 0
    if root.p > b1: b1 = root.p; n1 = root
    heap = _Heap(); heap.push(bound_of(ctx, root, b2 if k2 else b1), root)
    while len(heap) > 0:
        top_b, top = heap.pop()
        thr = b2 if k2 else b1
        if top_b <= thr: break
        if (exp & 255) == 0 and time.perf_counter() > ctx.deadline: ctx.status = 1; break
        if ctx.gen >= ctx.gen_cap: ctx.status = 2; break
        exp += 1
        for d in range(1, W):
            ch = make_child(ctx, top, d)
            if ch.p > b1: b2 = b1; n2 = n1; b1 = ch.p; n1 = ch
            elif ch.p > b2: b2 = ch.p; n2 = ch
            thr = b2 if k2 else b1
            bd = bound_of(ctx, ch, thr)
            if bd > thr: heap.push(bd, ch)
            else: ch.Ab = ch.An = None
        top.Ab = top.An = None
    return b1, b2, n1, n2, exp


def decode_python(table, time_limit=float('inf'), gen_cap=None, want_H=True):
    """table: list of T rows of W numbers (float or Fraction), blank = column 0.
    Returns dict(status, p1, p2, l1, l2, gen, exp_final, exp_bwd, H) with the C core's semantics."""
    T = len(table); W = len(table[0])
    ctx = _Ctx(); ctx.table = table; ctx.T = T; ctx.W = W
    ctx.gen = 0; ctx.gen_cap = gen_cap if gen_cap is not None else float('inf')
    ctx.deadline = time.perf_counter() + time_limit; ctx.status = 0
    ctx.exp_final = 0; ctx.exp_bwd = 0
    H = [[0] * (T + 1) for _ in range(W)]
    for d in range(1, W):
        for t in range(1, T + 1): H[d][t] = table[t - 1][d]
    Mmax = [0] * (T + 1)
    for t in range(1, T + 1):
        m = 0
        for d in range(1, W):
            if H[d][t] > m: m = H[d][t]
        Mmax[t] = m
    ctx.H = H; ctx.Mmax = Mmax
    for t in range(T, 0, -1):
        if ctx.status: break
        for cc in range(1, W):
            b1, b2, n1, n2, e = _search(ctx, suffix_root(table, t, cc), 0)
            ctx.exp_bwd += e
            if ctx.status: break
            H[cc][t] = b1
        m = 0
        for d in range(1, W):
            if H[d][t] > m: m = H[d][t]
        Mmax[t] = m
    p1 = 0; p2 = 0; l1 = (); l2 = ()
    if ctx.status == 0:
        p1, p2, n1, n2, e = _search(ctx, final_root(table), 1)
        ctx.exp_final = e
        if ctx.status == 0:
            l1 = n1.labelling() if n1 is not None else ()
            l2 = n2.labelling() if n2 is not None else ()
    return dict(status=ctx.status, p1=p1, p2=p2, l1=l1, l2=l2, gen=ctx.gen,
                exp_final=ctx.exp_final, exp_bwd=ctx.exp_bwd, H=(H if want_H else None))


def make_ctx(table, H):
    """Context for evaluating `bound_of` / `make_child` against a given H table (used by the gates)."""
    T = len(table); W = len(table[0])
    ctx = _Ctx(); ctx.table = table; ctx.T = T; ctx.W = W; ctx.H = H
    ctx.gen = 0; ctx.gen_cap = float('inf'); ctx.deadline = float('inf'); ctx.status = 0
    ctx.exp_final = 0; ctx.exp_bwd = 0
    Mmax = [0] * (T + 1)
    for t in range(1, T + 1):
        m = 0
        for d in range(1, W):
            if H[d][t] > m: m = H[d][t]
        Mmax[t] = m
    ctx.Mmax = Mmax
    return ctx

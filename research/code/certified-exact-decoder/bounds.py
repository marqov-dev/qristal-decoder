"""T2b -- exact CTC decoders built on ONE best-first search with a pluggable admissible bound.

Notation.  Frames 1..T (table[t-1] is frame t), blank = 0.  For a prefix u:
  Ab[t] = mass of paths over frames 1..t collapsing to u and ending in the blank-after-u state
          (for u = () this is the all-blank path mass; Ab[0] = 1 for u = (), else 0)
  An[t] = mass ending in the non-blank state of u's last symbol (0 for u = ())
  ok_d(t) = Ab[t] + [u_last != d] * An[t]   -- prefix mass at frame t that may start symbol d at t+1
  p(u)   = Ab[T] + An[T]
For a suffix v with v_1 = c and start frame t:
  g_v(t) = mass of paths over frames t..T with pi_t = c and collapse v.
Exact decomposition (a path's (|u|+1)-th segment starts at a unique frame t):
  p(u.v) = sum_t ok_{v_1}(t-1) * g_v(t)
Hence for ANY family Hhat_d(t) >= H_d(t) := max_{v: v_1 = d} g_v(t) the quantity
  B(u) = max( p(u), max_d sum_t ok_d(t-1) * Hhat_d(t) )
is an admissible bound on max_v p(u.v)  (sum of maxes >= max of sums).
Graves' prefix probability is the special case Hhat_d(t) = y_t[d] summed (not maxed) over d.
"""
import heapq, math, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctc import brute_ctc, ctc_forward, collapse, peaky_table, topk_labellings

BLANK = 0

class Node:
    __slots__ = ('u', 'Ab', 'An', 'p', 'bound')
    def __init__(self, u, Ab, An):
        self.u, self.Ab, self.An = u, Ab, An
        self.p = Ab[-1] + An[-1]
        self.bound = None

def root_node(table):
    T = len(table); Ab = [0.0]*(T+1); An = [0.0]*(T+1); Ab[0] = 1.0
    for t in range(1, T+1): Ab[t] = Ab[t-1]*table[t-1][BLANK]
    return Node((), Ab, An)

def suffix_root(table, t0, c):
    """Root of the suffix problem: symbol c forced at frame t0 (1-based), nothing before."""
    T = len(table); Ab = [0.0]*(T+1); An = [0.0]*(T+1)
    An[t0] = table[t0-1][c]
    for s in range(t0+1, T+1):
        An[s] = An[s-1]*table[s-1][c]
        Ab[s] = (Ab[s-1] + An[s-1])*table[s-1][BLANK]
    return Node((c,), Ab, An)

class Counter:
    __slots__ = ('gen', 'exp')
    def __init__(self): self.gen = 0; self.exp = 0

def child(node, d, table, cnt=None):
    T = len(table); Ab = [0.0]*(T+1); An = [0.0]*(T+1)
    pAb, pAn = node.Ab, node.An
    same = bool(node.u) and node.u[-1] == d
    for s in range(1, T+1):
        y = table[s-1]
        ok = pAb[s-1] if same else pAb[s-1] + pAn[s-1]
        An[s] = (An[s-1] + ok)*y[d]
        Ab[s] = (Ab[s-1] + An[s-1])*y[BLANK]
    if cnt is not None: cnt.gen += 1
    return Node(node.u + (d,), Ab, An)

def graves_F(node, table):
    """Exact prefix probability P(labelling begins with u) = p(u) + sum_d sum_t ok_d(t-1) y_t[d]."""
    T = len(table); W = len(table[0]); Ab, An = node.Ab, node.An
    last = node.u[-1] if node.u else None
    tot = node.p
    for t in range(1, T+1):
        y = table[t-1]; a, b = Ab[t-1], An[t-1]
        for d in range(1, W):
            tot += (a if d == last else a + b)*y[d]
    return tot

def bound_from_H(node, table, Hhat):
    """B(u) = max(p(u), max_d sum_t ok_d(t-1) Hhat[d][t]).  Hhat[d] indexed 1..T."""
    T = len(table); W = len(table[0]); Ab, An = node.Ab, node.An
    last = node.u[-1] if node.u else None
    best = node.p
    for d in range(1, W):
        H = Hhat[d]; s = 0.0
        if d == last:
            for t in range(1, T+1): s += Ab[t-1]*H[t]
        else:
            for t in range(1, T+1): s += (Ab[t-1] + An[t-1])*H[t]
        if s > best: best = s
    return best

def H_trivial(table):
    """Hhat_d(t) = y_t[d]: with SUM over d this is Graves' bound; with MAX it is the child-F bound."""
    T = len(table); W = len(table[0])
    return [[0.0] + [table[t-1][d] for t in range(1, T+1)] for d in range(W)]

# ---------------------------------------------------------------- the search

def best_first(table, bound_fn, root=None, incumbent=0.0, incumbent_l=None, cap=None, cnt=None):
    """Exact best-first search over the prefix tree with admissible bound bound_fn(node).
    Returns (best_p, best_l, expansions, generated, hit_cap)."""
    W = len(table[0])
    if cnt is None: cnt = Counter()
    if root is None: root = root_node(table)
    best_p, best_l = incumbent, incumbent_l
    if root.p > best_p: best_p, best_l = root.p, root.u
    root.bound = bound_fn(root)
    heap = [(-root.bound, 0, root)]; tie = 1; exp = 0; gen0 = cnt.gen
    while heap:
        nb, _, node = heapq.heappop(heap)
        if -nb <= best_p: break
        if cap is not None and exp >= cap: return best_p, best_l, exp, cnt.gen - gen0, True
        exp += 1; cnt.exp += 1
        for d in range(1, W):
            ch = child(node, d, table, cnt)
            if ch.p > best_p: best_p, best_l = ch.p, ch.u
            ch.bound = bound_fn(ch)
            if ch.bound > best_p:
                heapq.heappush(heap, (-ch.bound, tie, ch)); tie += 1
    return best_p, best_l, exp, cnt.gen - gen0, False

def dfs_bb(table, bound_fn, incumbent=0.0, incumbent_l=None, cap=None, cnt=None):
    """Depth-first branch-and-bound with the same bound; children visited best-bound-first."""
    W = len(table[0])
    if cnt is None: cnt = Counter()
    root = root_node(table); best = [incumbent, incumbent_l]
    if root.p > best[0]: best[0], best[1] = root.p, root.u
    exp = 0; stack = [root]; gen0 = cnt.gen; hit = False
    root.bound = bound_fn(root)
    while stack:
        node = stack.pop()
        if node.bound <= best[0]: continue
        if cap is not None and exp >= cap: hit = True; break
        exp += 1; cnt.exp += 1
        kids = []
        for d in range(1, W):
            ch = child(node, d, table, cnt)
            if ch.p > best[0]: best[0], best[1] = ch.p, ch.u
            ch.bound = bound_fn(ch)
            if ch.bound > best[0]: kids.append(ch)
        kids.sort(key=lambda n: n.bound)          # push worst first -> best popped first
        stack.extend(kids)
    return best[0], best[1], exp, cnt.gen - gen0, hit

# ---------------------------------------------------------------- decoders

def decode_graves(table, incumbent=0.0, incumbent_l=None, cap=None, cnt=None):
    """D0: Graves 2006 prefix search, priority = exact prefix probability F(u)."""
    return best_first(table, lambda n: graves_F(n, table), incumbent=incumbent, incumbent_l=incumbent_l, cap=cap, cnt=cnt)

def decode_childF(table, incumbent=0.0, incumbent_l=None, cap=None, cnt=None):
    """D0+: same information as Graves but bound = max(p(u), max_d F(u.d)) (max instead of sum over d)."""
    H = H_trivial(table)
    return best_first(table, lambda n: bound_from_H(n, table, H), incumbent=incumbent, incumbent_l=incumbent_l, cap=cap, cnt=cnt)

# --- D1a: suffix-tree bound ---------------------------------------------------
def H_suffix_tree(table, theta, cnt=None, cap=None):
    """Hhat_d(t) = min(y_t[d], max( max_{v in S, v_1=d} g_v(t), theta / w_d(t) )),
    S = {v : P(labelling ends with v) >= theta}, w_d(t) = 1 - y_{t-1}[d] (w_d(1) = 1).
    Admissible: P(ends with v) = sum_t w_{v_1}(t) g_v(t)  (the segment for v_1 starts at a unique t,
    and the prefix mass ending at t-1 not in state v_1 is exactly 1 - y_{t-1}[v_1] by the product measure),
    so v not in S  =>  g_v(t) < theta / w_{v_1}(t) for every t.
    S is enumerated as the prefix tree of the REVERSED table (collapse(rev pi) = rev(collapse pi)),
    and g_v(t) = An_rev[T-t+1] of the node rev(v)."""
    T = len(table); W = len(table[0]); rt = table[::-1]
    if cnt is None: cnt = Counter()
    Hh = [[0.0]*(T+1) for _ in range(W)]
    for d in range(1, W):
        for t in range(1, T+1):
            w = 1.0 if t == 1 else 1.0 - table[t-2][d]
            Hh[d][t] = (theta/w) if w > 0 else 0.0
    stack = [root_node(rt)]; kept = 0
    while stack:
        node = stack.pop()
        for d in range(1, W):
            ch = child(node, d, rt, cnt)
            if graves_F(ch, rt) >= theta:
                kept += 1; stack.append(ch)
                if cap is not None and kept > cap: return None, kept
                Hd = Hh[d]; An = ch.An
                for t in range(1, T+1):
                    g = An[T-t+1]
                    if g > Hd[t]: Hd[t] = g
    for d in range(1, W):
        for t in range(1, T+1):
            if Hh[d][t] > table[t-1][d]: Hh[d][t] = table[t-1][d]
    return Hh, kept

def decode_bidir(table, theta, incumbent=0.0, incumbent_l=None, cap=None, cnt=None):
    if cnt is None: cnt = Counter()
    Hh, kept = H_suffix_tree(table, theta, cnt, cap=cap)
    if Hh is None: return 0.0, None, cap, cnt.gen, True, kept
    r = best_first(table, lambda n: bound_from_H(n, table, Hh), incumbent=incumbent, incumbent_l=incumbent_l, cap=cap, cnt=cnt)
    return r + (kept,)

# --- D1b: frame-policy relaxation DP ------------------------------------------
def H_policy(table):
    """Backward DP, O(W T^2):
      Hhat_c(t) = y_t[c] * max( Tail_c(t), sum_{t'>t} [ Rn_c(t,t') M_{!=c}(t') + Rb_c(t,t') M(t') ] )
    Rn = frames t+1..t'-1 all c (no blank: next symbol must differ), Rb = c* blank+ (any next symbol),
    Tail = c* blank* to the end, M(t') = max_d Hhat_d(t'), M_{!=c} = max_{d!=c}.
    Admissible by backward induction: the recursion for g_{c.v'}(t) sums over the start frame t' of v';
    replacing g_{v'}(t') by its max over v' (separately per t') can only increase the value."""
    T = len(table); W = len(table[0])
    Hh = [[0.0]*(T+1) for _ in range(W)]
    M = [0.0]*(T+2); M2 = [[0.0]*(T+2) for _ in range(W)]   # M2[c][t'] = max_{d != c} Hh[d][t']
    for t in range(T, 0, -1):
        y = table[t-1]
        for c in range(1, W):
            rn = 1.0; rb = 0.0; acc = 0.0
            for tp in range(t+1, T+1):
                acc += rn*M2[c][tp] + rb*M[tp]
                yp = table[tp-1]
                rb = (rb + rn)*yp[BLANK]
                rn = rn*yp[c]
            tail = rn + rb
            Hh[c][t] = y[c]*max(tail, acc)
        vals = [Hh[c][t] for c in range(W)]
        M[t] = max(vals)
        for c in range(1, W):
            M2[c][t] = max(vals[d] for d in range(W) if d != c) if W > 2 else 0.0
    return Hh

def decode_policy(table, incumbent=0.0, incumbent_l=None, cap=None, cnt=None):
    Hh = H_policy(table)
    return best_first(table, lambda n: bound_from_H(n, table, Hh), incumbent=incumbent, incumbent_l=incumbent_l, cap=cap, cnt=cnt)

# --- D1c: exact backward suffix modes (islands with a 2W boundary state) ------
def H_exact_backward(table, seed_H=None, cnt=None, cap=None):
    """For t = T..1 and each c, compute H_c(t) = max_{v_1=c} g_v(t) EXACTLY by a best-first search
    over suffixes rooted at (t, c), whose bound uses the already-exact H_d(t') for t' > t
    (and seed_H, e.g. the policy DP, as the initial guess -- only t' > t is ever read)."""
    T = len(table); W = len(table[0])
    if cnt is None: cnt = Counter()
    Hh = [row[:] for row in seed_H] if seed_H is not None else H_trivial(table)
    total_exp = 0
    for t in range(T, 0, -1):
        for c in range(1, W):
            root = suffix_root(table, t, c)
            bp, bl, exp, gen, hit = best_first(table, lambda n: bound_from_H(n, table, Hh),
                                               root=root, cnt=cnt, cap=cap)
            if hit: return None, None
            Hh[c][t] = bp; total_exp += exp
    return Hh, total_exp

def decode_exact_backward(table, incumbent=0.0, incumbent_l=None, cap=None, cnt=None, seed='policy'):
    if cnt is None: cnt = Counter()
    seed_H = H_policy(table) if seed == 'policy' else None
    Hh, bexp = H_exact_backward(table, seed_H, cnt, cap=cap)
    if Hh is None: return 0.0, None, cap, cnt.gen, True, cap
    r = best_first(table, lambda n: bound_from_H(n, table, Hh), incumbent=incumbent, incumbent_l=incumbent_l, cap=cap, cnt=cnt)
    return r + (bexp,)

# --- D2: Viterbi-collapse incumbent ----------------------------------------------
def viterbi_collapse(table):
    path = tuple(max(range(len(row)), key=lambda s: row[s]) for row in table)
    l = collapse(path); return l, ctc_forward(l, table)

def beam_incumbent(table, beam=32):
    top = topk_labellings(table, beam=beam, k=1)
    if not top: return (), 0.0
    return top[0][1], top[0][0]

# ---------------------------------------------------------------- helpers
def random_table(rng, T, W):
    tbl = [[rng.random() for _ in range(W)] for _ in range(T)]
    return [[v/sum(r) for v in r] for r in tbl]

def brute_mode(table):
    ex = brute_ctc(table); l, p = max(ex.items(), key=lambda kv: kv[1]); return l, p, ex

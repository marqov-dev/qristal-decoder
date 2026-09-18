"""Exact posterior mass of a regular set under a CTC posterior.

P(L | y) = sum_{l in L} p(l | y) = sum_{paths pi : B(pi) in L} prod_t y_t[pi_t]

computed by the CTC forward recursion over the product of the CTC "collapse" automaton with a DFA
for L.  The collapse automaton's state is the symbol emitted at the previous frame (blank or a
label): frame t emits a new label c iff pi_t = c != blank and pi_{t-1} != c.  So

    alpha_t(q, s) = mass of paths over frames 1..t with pi_t = s and DFA state q = delta*(q0, B(pi_1..t))

    alpha_1(q0, blank)      = y_1[blank]
    alpha_1(delta(q0,c), c) = y_1[c]                                  (c != blank)
    alpha_{t+1}(q, blank)   = y_{t+1}[blank] * sum_s alpha_t(q, s)
    alpha_{t+1}(q, c)       = y_{t+1}[c] * alpha_t(q, c)                       (repeat: no emission)
                            + y_{t+1}[c] * sum_{q': delta(q',c)=q} sum_{s != c} alpha_t(q', s)   (new emission)
    P(L | y) = sum_{q in F} sum_s alpha_T(q, s)

Paths that leave the DFA (dead state) are dropped.  Cost O(T * |Q| * W) time, O(|Q| * W) memory
(the inner sum over s is a per-(q) total m_q = sum_s alpha_t(q, s) minus alpha_t(q, c)).

Two implementations: pure Python (works on fractions.Fraction rows for exact gates) and numpy.
"""
from fractions import Fraction
from itertools import product


def class_posterior_py(table, dfa, blank):
    """table: list of T rows (list of W numbers, float or Fraction). Returns P(L|y) in the row type."""
    T = len(table); W = len(table[0])
    mat, acc = dfa.as_arrays(); Q = len(mat)
    zero = table[0][0] * 0
    alpha = [[zero] * W for _ in range(Q)]
    y = table[0]
    alpha[dfa.start][blank] = y[blank]
    for c in range(W):
        if c == blank: continue
        q = mat[dfa.start][c]
        if q >= 0: alpha[q][c] += y[c]
    for t in range(1, T):
        y = table[t]
        new = [[zero] * W for _ in range(Q)]
        for q in range(Q):
            row = alpha[q]; m = sum(row)
            if m == 0: continue
            new[q][blank] += m * y[blank]
            for c in range(W):
                if c == blank: continue
                if row[c]: new[q][c] += row[c] * y[c]                 # repeat, no emission
                q2 = mat[q][c]
                if q2 >= 0:
                    em = m - row[c]
                    if em: new[q2][c] += em * y[c]                    # new emission of c
        alpha = new
    return sum(sum(alpha[q]) for q in range(Q) if acc[q])


def class_posterior_np(table, dfa, blank):
    import numpy as np
    y = np.asarray(table, dtype=np.float64); T, W = y.shape
    mat, acc = dfa.as_arrays(); Q = len(mat)
    mat = np.asarray(mat, dtype=np.int64); acc = np.asarray(acc, dtype=bool)
    alpha = np.zeros((Q, W))
    alpha[dfa.start, blank] = y[0, blank]
    for c in range(W):
        if c == blank: continue
        q = mat[dfa.start, c]
        if q >= 0: alpha[q, c] += y[0, c]
    nonblank = [c for c in range(W) if c != blank]
    for t in range(1, T):
        m = alpha.sum(axis=1)
        new = np.zeros((Q, W))
        new[:, blank] = m * y[t, blank]
        for c in nonblank:
            new[:, c] += alpha[:, c] * y[t, c]
            tgt = mat[:, c]; ok = tgt >= 0
            if ok.any():
                em = (m[ok] - alpha[ok, c]) * y[t, c]
                new[:, c] += np.bincount(tgt[ok], weights=em, minlength=Q)
        alpha = new
    return float(alpha[acc].sum())


def class_posterior(table, dfa, blank, delimiter=None, exact=False):
    """P(L|y). `delimiter` is informational (the DFA already encodes word boundaries)."""
    if exact or isinstance(table[0][0], Fraction): return class_posterior_py(table, dfa, blank)
    return class_posterior_np(table, dfa, blank)


# ------------------------------------------------------------------ exact references for gates
def collapse(path, blank):
    return tuple(s for t, s in enumerate(path) if (t == 0 or s != path[t-1]) and s != blank)


def ctc_forward_exact(l, table, blank):
    """Graves 2006 forward recursion, type-preserving (Fraction rows -> Fraction result)."""
    T = len(table); zero = table[0][0] * 0
    ext = [blank]
    for s in l: ext += [s, blank]
    S = len(ext); a = [zero] * S
    a[0] = table[0][ext[0]]
    if S > 1: a[1] = table[0][ext[1]]
    for t in range(1, T):
        b = [zero] * S
        for s in range(S):
            v = a[s]
            if s >= 1: v = v + a[s-1]
            if s >= 2 and ext[s] != blank and ext[s] != ext[s-2]: v = v + a[s-2]
            b[s] = v * table[t][ext[s]]
        a = b
    return a[S-1] + (a[S-2] if S >= 2 else zero)


def brute_class_paths(table, dfa, blank):
    """(a) sum over all W^T paths whose collapse is accepted."""
    T = len(table); W = len(table[0]); tot = table[0][0] * 0
    for path in product(range(W), repeat=T):
        if dfa.accepts(collapse(path, blank)):
            p = table[0][path[0]]
            for t in range(1, T): p = p * table[t][path[t]]
            tot += p
    return tot


def brute_class_labellings(table, dfa, blank):
    """(b) sum of ctc_forward over every accepted labelling of length <= T (longer ones have p = 0)."""
    T = len(table); W = len(table[0]); syms = [c for c in range(W) if c != blank]; tot = table[0][0] * 0
    for L in range(0, T + 1):
        for l in product(syms, repeat=L):
            if dfa.accepts(l): tot += ctc_forward_exact(l, table, blank)
    return tot

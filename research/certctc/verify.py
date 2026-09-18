"""Independent verification of a Certificate.

`ctc_prob` is the standard CTC forward recursion over the extended label sequence
(blank, l1, blank, l2, ..., blank) -- Graves et al. 2006, section 4.1.  It shares no code or state
with the search (which uses the prefix recursion Ab/An), so agreement between the two is an
independent check of p(mode) and p(runner-up).  What it cannot check is *maximality* -- that is
the search's admissible-bound argument, and it is gated separately against brute force in the
test suite.
"""
import math

__all__ = ['ctc_prob', 'verify', 'VerifyReport', 'VerificationError']


class VerificationError(AssertionError):
    pass


class VerifyReport(object):
    __slots__ = ('ok', 'p_mode_recomputed', 'p_runner_up_recomputed', 'rel_err_mode', 'rel_err_runner_up', 'problems')

    def __init__(self, ok, pm, pr, em, er, problems):
        self.ok = ok; self.p_mode_recomputed = pm; self.p_runner_up_recomputed = pr
        self.rel_err_mode = em; self.rel_err_runner_up = er; self.problems = problems

    def __bool__(self): return self.ok

    def __repr__(self):
        return 'VerifyReport(ok=%r, rel_err_mode=%.2e, rel_err_runner_up=%.2e, problems=%r)' % (
            self.ok, self.rel_err_mode, self.rel_err_runner_up, self.problems)


def ctc_prob(labelling, table, blank=0):
    """Exact p(labelling | table) by the forward recursion over the extended label sequence.
    Works for float and Fraction tables. O(T * |labelling|)."""
    T = len(table)
    ext = [blank]
    for s in labelling: ext += [s, blank]
    S = len(ext)
    a = [0] * S
    a[0] = table[0][ext[0]]
    if S > 1: a[1] = table[0][ext[1]]
    for t in range(1, T):
        row = table[t]; b = [0] * S
        for s in range(S):
            v = a[s]
            if s >= 1: v += a[s - 1]
            if s >= 2 and ext[s] != blank and ext[s] != ext[s - 2]: v += a[s - 2]
            b[s] = v * row[ext[s]]
        a = b
    return a[S - 1] + (a[S - 2] if S >= 2 else 0)


def _rel(a, b):
    m = max(abs(a), abs(b))
    return abs(a - b) / m if m > 0 else 0.0


def verify(table, cert, rtol=1e-9, raise_on_fail=False):
    """Recompute p(mode) and p(runner_up) independently and check the certificate's internal
    consistency.  Returns a VerifyReport (truthy iff everything passed)."""
    problems = []
    T = len(table); W = len(table[0])
    if cert.T != T or cert.W != W: problems.append('shape mismatch: cert (%d,%d) vs table (%d,%d)' % (cert.T, cert.W, T, W))
    if cert.status != 'ok': problems.append('status is %r, not a certificate' % (cert.status,))
    mode = tuple(cert.mode)
    if cert.D != len(mode): problems.append('D=%d != len(mode)=%d' % (cert.D, len(mode)))
    if any((s < 0 or s >= W or s == cert.blank) for s in mode): problems.append('mode contains blank or out-of-range symbol')
    pm = ctc_prob(mode, table, cert.blank)
    em = _rel(pm, cert.p_mode)
    if em > rtol: problems.append('p_mode: certificate %.17g vs forward recursion %.17g (rel %.2e)' % (cert.p_mode, pm, em))
    pr = 0.0; er = 0.0
    if cert.runner_up is not None:
        ru = tuple(cert.runner_up)
        if ru == mode: problems.append('runner_up equals mode')
        if any((s < 0 or s >= W or s == cert.blank) for s in ru): problems.append('runner_up contains blank or out-of-range symbol')
        pr = ctc_prob(ru, table, cert.blank)
        er = _rel(pr, cert.p_runner_up)
        if er > rtol: problems.append('p_runner_up: certificate %.17g vs forward recursion %.17g (rel %.2e)' % (cert.p_runner_up, pr, er))
        if cert.p_runner_up > cert.p_mode: problems.append('p_runner_up > p_mode')
        if cert.p_runner_up > 0:
            if _rel(cert.margin, cert.p_mode / cert.p_runner_up) > 1e-12: problems.append('margin != p_mode / p_runner_up')
        elif not math.isinf(cert.margin): problems.append('p_runner_up == 0 but margin is finite')
    elif W > 1 and T >= 1: problems.append('no runner_up although at least two labellings exist')
    if cert.pruned_mass_bound != 0: problems.append('pruned_mass_bound != 0 (not an exact certificate)')
    ok = not problems
    rep = VerifyReport(ok, pm, pr, em, er, problems)
    if raise_on_fail and not ok: raise VerificationError('; '.join(problems))
    return rep

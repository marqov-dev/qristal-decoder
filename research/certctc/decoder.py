"""certctc.decoder -- certified-exact CTC mode + runner-up decoding (T2b variant 1c).

decode(table, blank=0) -> Certificate

The certificate states: `mode` is a labelling of maximum CTC probability p_mode; every labelling
other than `mode` has probability <= p_runner_up, and `runner_up` attains it; margin =
p_mode / p_runner_up.  Both probabilities are exact (up to float64 rounding); nothing is
approximated, so `pruned_mass_bound` is identically 0 -- see README "What is certified".
"""
import dataclasses, json, math, time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from . import _pysearch, _csearch

__all__ = ['decode', 'Certificate', 'BudgetExceeded']

_STATUS = {0: 'ok', 1: 'deadline', 2: 'gen_cap', 3: 'pool_cap'}


class BudgetExceeded(RuntimeError):
    """Raised when time_limit / max_generations stopped the search before it could certify.
    `.partial` holds the raw counters of the aborted run."""
    def __init__(self, status, partial):
        RuntimeError.__init__(self, 'search stopped: %s (gen=%d)' % (status, partial.get('gen', -1)))
        self.status = status; self.partial = partial


@dataclass
class Certificate:
    mode: Tuple[int, ...]
    p_mode: float
    runner_up: Optional[Tuple[int, ...]]
    p_runner_up: float
    margin: float                      # p_mode / p_runner_up (inf if p_runner_up == 0)
    pruned_mass_bound: float           # always 0.0: no labelling is ever discarded uncertified
    T: int
    W: int
    D: int                             # len(mode)
    expansions_final: int              # heap pops expanded in the final (forward) search
    generations_total: int             # child() calls in all T*(W-1) backward searches + final
    wall_seconds: float
    backend: str                       # "c" or "python"
    blank: int = 0
    expansions_backward: int = 0       # heap pops expanded in the backward searches
    status: str = 'ok'
    H: Optional[List[List[float]]] = field(default=None, repr=False, compare=False)   # exact suffix modes H[d][t], t=1..T

    def to_dict(self, with_H=False):
        d = dataclasses.asdict(self)
        d['mode'] = list(self.mode); d['runner_up'] = None if self.runner_up is None else list(self.runner_up)
        if not with_H: d.pop('H', None)
        if isinstance(d.get('margin'), float) and math.isinf(d['margin']): d['margin'] = 'inf'
        return d

    def to_json(self, indent=None, with_H=False):
        return json.dumps(self.to_dict(with_H=with_H), indent=indent)

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        d['mode'] = tuple(d['mode']); d['runner_up'] = None if d.get('runner_up') is None else tuple(d['runner_up'])
        if d.get('margin') == 'inf': d['margin'] = float('inf')
        d.setdefault('H', None)
        return cls(**d)

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))

    def summary(self):
        ru = '-' if self.runner_up is None else ' '.join(map(str, self.runner_up))
        return ('mode (D=%d): %s\np_mode      = %.6e\nrunner_up  : %s\np_runner_up = %.6e\nmargin      = %s\n'
                'T=%d W=%d blank=%d  final expansions=%d  backward expansions=%d  generations=%d  '
                '%.3f s  backend=%s  status=%s  pruned_mass_bound=%g' % (
                    self.D, ' '.join(map(str, self.mode)) or '(empty)', self.p_mode, ru, self.p_runner_up,
                    ('%.6g' % self.margin), self.T, self.W, self.blank, self.expansions_final,
                    self.expansions_backward, self.generations_total, self.wall_seconds, self.backend,
                    self.status, self.pruned_mass_bound))


def _as_rows(table):
    """Return (rows as list of lists, is_float)."""
    try:
        import numpy as np
        if isinstance(table, np.ndarray):
            if table.ndim != 2: raise ValueError('table must be 2-D (T, W)')
            return np.asarray(table, dtype=np.float64).tolist(), True
    except ImportError:
        pass
    rows = [list(r) for r in table]
    if not rows or not rows[0]: raise ValueError('table must be non-empty (T >= 1, W >= 1)')
    W = len(rows[0])
    if any(len(r) != W for r in rows): raise ValueError('ragged table')
    is_float = all(isinstance(x, (float, int)) for r in rows for x in r)
    return rows, is_float


def decode(table, blank=0, backend='auto', time_limit=None, max_generations=None, want_H=False):
    """Certified-exact CTC decoding of a (T, W) posterior table (rows need not sum to 1).

    blank: index of the blank column.  backend: 'auto' (C if it can be built, else Python), 'c',
    'python'.  time_limit (seconds) / max_generations: optional budgets; exceeding either raises
    BudgetExceeded -- a Certificate is only ever returned for a completed search.
    want_H: also return the exact suffix-mode table H[d][t] (in the original symbol indices).
    """
    rows, is_float = _as_rows(table)
    T = len(rows); W = len(rows[0])
    if not (0 <= blank < W): raise ValueError('blank out of range')
    if any(x < 0 for r in rows for x in r): raise ValueError('negative entry in table')
    perm = [blank] + [s for s in range(W) if s != blank]       # perm[j] = original symbol of column j
    if blank != 0: rows = [[r[s] for s in perm] for r in rows]
    tl = float('inf') if time_limit is None else float(time_limit)
    use_c = False
    if backend == 'c':
        if not is_float: raise ValueError('C backend needs float tables')
        if _csearch.load() is None: raise RuntimeError('C backend unavailable: %r' % (_csearch.load_error(),))
        use_c = True
    elif backend == 'auto':
        use_c = is_float and _csearch.load() is not None
    elif backend != 'python':
        raise ValueError('backend must be auto, c or python')
    t0 = time.perf_counter()
    if use_c:
        r = _csearch.decode_c(rows, time_limit=tl, gen_cap=max_generations, want_H=want_H)
    else:
        r = _pysearch.decode_python(rows, time_limit=tl, gen_cap=max_generations, want_H=want_H)
    wall = time.perf_counter() - t0
    status = _STATUS[r['status']]
    if status != 'ok':
        raise BudgetExceeded(status, dict(r, wall_seconds=wall, backend='c' if use_c else 'python'))
    l1 = tuple(perm[s] for s in r['l1'])
    l2 = tuple(perm[s] for s in r['l2'])
    p1, p2 = r['p1'], r['p2']
    has_ru = (W >= 2) and (l2 != l1 or p2 > 0)
    if not has_ru:
        l2 = None; margin = float('inf')
    else:
        margin = (p1 / p2) if p2 > 0 else float('inf')
    H = None
    if want_H and r['H'] is not None:
        H = [None] * W
        for j in range(W): H[perm[j]] = list(r['H'][j])
    return Certificate(mode=l1, p_mode=p1, runner_up=l2, p_runner_up=p2, margin=margin,
                       pruned_mass_bound=0.0, T=T, W=W, D=len(l1), expansions_final=r['exp_final'],
                       generations_total=r['gen'], wall_seconds=wall, backend='c' if use_c else 'python',
                       blank=blank, expansions_backward=r['exp_bwd'], status='ok', H=H)

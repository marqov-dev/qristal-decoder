"""Small finite-automaton library over integer symbol alphabets (stdlib only).

NFA (Thompson construction) -> DFA (subset construction) -> minimal DFA (Moore refinement),
plus complete-DFA products (intersection / union / difference). A DFA here is over the alphabet
`sigma` = every non-blank symbol id of the CTC model; a missing transition is the dead state (-1).

Word-level builders: a CTC labelling is a character string with the delimiter symbol `|` as word
boundary; its *text* is the delimiter-split string with empty words dropped.  A word-level pattern
P is compiled to the character-level DFA accepting exactly the labellings whose text matches P
(so leading / trailing / repeated delimiters are all accepted — they are the same text).
"""
from collections import deque

EPS = None


class NFA:
    """States 0..n-1; trans[q] = list of (sym|EPS, q'); one start, one accept (Thompson)."""
    def __init__(self):
        self.trans = []
        self.start = None
        self.accept = None

    def new(self):
        self.trans.append([])
        return len(self.trans) - 1

    def add(self, q, sym, r):
        self.trans[q].append((sym, r))

    @staticmethod
    def sym(c):
        n = NFA(); s = n.new(); a = n.new(); n.add(s, c, a); n.start, n.accept = s, a; return n

    @staticmethod
    def symset(cs):
        n = NFA(); s = n.new(); a = n.new()
        for c in cs: n.add(s, c, a)
        n.start, n.accept = s, a; return n

    @staticmethod
    def eps():
        n = NFA(); s = n.new(); n.start = n.accept = s; return n

    def _copy_into(self, other):
        """Copy `other`'s states into self; return (start, accept) in self's numbering."""
        off = len(self.trans)
        for q, lst in enumerate(other.trans):
            self.trans.append([(sym, r + off) for sym, r in lst])
        return other.start + off, other.accept + off

    @staticmethod
    def seq(*parts):
        n = NFA(); prev_acc = None
        for p in parts:
            s, a = n._copy_into(p)
            if prev_acc is None: n.start = s
            else: n.add(prev_acc, EPS, s)
            prev_acc = a
        n.accept = prev_acc
        if n.start is None: n.start = n.accept = n.new()
        return n

    @staticmethod
    def alt(*parts):
        n = NFA(); s = n.new(); a = n.new()
        for p in parts:
            ps, pa = n._copy_into(p); n.add(s, EPS, ps); n.add(pa, EPS, a)
        n.start, n.accept = s, a; return n

    @staticmethod
    def star(p):
        n = NFA(); s = n.new(); a = n.new(); ps, pa = n._copy_into(p)
        n.add(s, EPS, ps); n.add(s, EPS, a); n.add(pa, EPS, ps); n.add(pa, EPS, a)
        n.start, n.accept = s, a; return n

    @staticmethod
    def plus(p):
        return NFA.seq(p, NFA.star(p))

    @staticmethod
    def opt(p):
        return NFA.alt(p, NFA.eps())

    @staticmethod
    def string(syms):
        return NFA.seq(*[NFA.sym(c) for c in syms]) if syms else NFA.eps()

    def eps_closure(self, S):
        st = list(S); seen = set(S)
        while st:
            q = st.pop()
            for sym, r in self.trans[q]:
                if sym is EPS and r not in seen: seen.add(r); st.append(r)
        return frozenset(seen)

    def to_dfa(self, sigma):
        """Subset construction over alphabet `sigma`; returns a (possibly non-minimal) DFA."""
        sigma = list(sigma)
        start = self.eps_closure({self.start})
        idx = {start: 0}; states = [start]; delta = []; queue = deque([start])
        while queue:
            S = queue.popleft(); row = {}
            for c in sigma:
                moved = set()
                for q in S:
                    for sym, r in self.trans[q]:
                        if sym == c: moved.add(r)
                if moved:
                    Tset = self.eps_closure(moved)
                    if Tset not in idx:
                        idx[Tset] = len(states); states.append(Tset); queue.append(Tset)
                    row[c] = idx[Tset]
            delta.append(row)
        accept = {i for S, i in idx.items() if self.accept in S}
        return DFA(sigma, delta, 0, accept).minimize()


class DFA:
    """delta[q] = dict sym -> q' (missing = dead); accept = set of states."""
    def __init__(self, sigma, delta, start, accept):
        self.sigma = list(sigma); self.delta = delta; self.start = start; self.accept = set(accept)

    @property
    def n(self):
        return len(self.delta)

    def step(self, q, c):
        if q < 0: return -1
        return self.delta[q].get(c, -1)

    def accepts(self, syms):
        q = self.start
        for c in syms:
            q = self.step(q, c)
            if q < 0: return False
        return q in self.accept

    def _reachable(self):
        seen = {self.start}; st = [self.start]
        while st:
            q = st.pop()
            for r in self.delta[q].values():
                if r not in seen: seen.add(r); st.append(r)
        return seen

    def _coreachable(self):
        rev = [[] for _ in range(self.n)]
        for q in range(self.n):
            for r in self.delta[q].values(): rev[r].append(q)
        seen = set(self.accept); st = list(self.accept)
        while st:
            q = st.pop()
            for p in rev[q]:
                if p not in seen: seen.add(p); st.append(p)
        return seen

    def trim(self):
        """Drop unreachable states and states that cannot reach acceptance (they become dead)."""
        keep = self._reachable() & self._coreachable()
        if self.start not in keep:            # empty language
            return DFA(self.sigma, [{}], 0, set())
        order = sorted(keep); new = {q: i for i, q in enumerate(order)}
        delta = [{c: new[r] for c, r in self.delta[q].items() if r in keep} for q in order]
        return DFA(self.sigma, delta, new[self.start], {new[q] for q in self.accept if q in keep})

    def minimize(self):
        """Moore partition refinement on the trimmed automaton (dead state implicit)."""
        d = self.trim()
        if not d.accept: return d
        n = d.n; cls = [1 if q in d.accept else 0 for q in range(n)]
        while True:
            sig = {}; newcls = [0] * n
            for q in range(n):
                key = (cls[q],) + tuple(cls[d.delta[q][c]] if c in d.delta[q] else -1 for c in d.sigma)
                if key not in sig: sig[key] = len(sig)
                newcls[q] = sig[key]
            if len(sig) == len(set(cls)):
                cls = newcls; break
            cls = newcls
        k = len(set(cls)); delta = [None] * k
        for q in range(n):
            if delta[cls[q]] is None:
                delta[cls[q]] = {c: cls[r] for c, r in d.delta[q].items()}
        return DFA(d.sigma, delta, cls[d.start], {cls[q] for q in d.accept})

    # ---- boolean combinations (product construction on complete automata; dead = -1 kept implicit)
    def _product(self, other, kind):
        """kind: 'and' (drop pairs with a dead component), 'or' / 'diff' (keep unless both dead)."""
        assert self.sigma == other.sigma
        start = (self.start, other.start); idx = {start: 0}; states = [start]; delta = []; q = deque([start])
        while q:
            (a, b) = q.popleft(); row = {}
            for c in self.sigma:
                a2 = self.step(a, c); b2 = other.step(b, c)
                if (a2 < 0 and b2 < 0) or (kind == 'and' and (a2 < 0 or b2 < 0)): continue
                key = (a2, b2)
                if key not in idx: idx[key] = len(states); states.append(key); q.append(key)
                row[c] = idx[key]
            delta.append(row)
        fn = {'and': lambda x, y: x and y, 'or': lambda x, y: x or y, 'diff': lambda x, y: x and not y}[kind]
        accept = {i for (a, b), i in idx.items() if fn(a >= 0 and a in self.accept, b >= 0 and b in other.accept)}
        return DFA(self.sigma, delta, 0, accept).minimize()

    def intersect(self, other): return self._product(other, 'and')
    def union(self, other): return self._product(other, 'or')
    def difference(self, other): return self._product(other, 'diff')

    def complement(self):
        """Complement w.r.t. sigma* (dead state made explicit and accepting)."""
        n = self.n; delta = [dict(row) for row in self.delta] + [{}]
        for q in range(n + 1):
            for c in self.sigma:
                if c not in delta[q]: delta[q][c] = n
        return DFA(self.sigma, delta, self.start, set(range(n + 1)) - self.accept).minimize()

    def is_empty(self):
        return not self.trim().accept

    def as_arrays(self):
        """(delta matrix Q x W with -1 for dead, indexed by symbol id; accept bool list)."""
        W = max(self.sigma) + 1
        mat = [[-1] * W for _ in range(self.n)]
        for q in range(self.n):
            for c, r in self.delta[q].items(): mat[q][c] = r
        return mat, [q in self.accept for q in range(self.n)]


def all_strings_dfa(sigma):
    n = NFA.star(NFA.symset(sigma)); return n.to_dfa(sigma)


# ---------------------------------------------------------------- word-level patterns
class WordAlphabet:
    """Maps words (str) to character-symbol sequences for a given CTC vocab.

    Convention: a word-level pattern is a char-level NFA over the *boundary-extended* labelling
    `| l |`; every word token is `|+ w` (leading separators) and `compile()` appends the final `|+`
    and then converts to a DFA on plain labellings by fixing start = delta(q0, '|') and
    accept = {q : delta(q, '|') in F}.  So `lit`, `anyword`, `wstar`, ... compose like ordinary
    regexes with no separator bookkeeping, and leading / trailing / repeated `|` are all accepted.
    """
    def __init__(self, char_to_id, delim_id, blank_id, W):
        self.char_to_id = dict(char_to_id); self.delim = delim_id; self.blank = blank_id; self.W = W
        self.sigma = [c for c in range(W) if c != blank_id]              # every non-blank symbol
        self.nondelim = [c for c in self.sigma if c != delim_id]

    def word(self, w):
        return [self.char_to_id[ch] for ch in w]

    def sep(self):
        return NFA.plus(NFA.sym(self.delim))

    def token(self, w):
        return NFA.seq(self.sep(), NFA.string(self.word(w)))

    def lit(self, text):
        return NFA.seq(*[self.token(w) for w in text.split()])

    def anyword(self):
        return NFA.seq(self.sep(), NFA.plus(NFA.symset(self.nondelim)))

    def wseq(self, *parts):
        return NFA.seq(*[p for p in parts if p is not None])

    def wstar(self, p):
        return NFA.star(p)

    def wplus(self, p):
        return NFA.plus(p)

    def wopt(self, p):
        return NFA.opt(p)

    def wrepeat(self, p, lo, hi):
        return NFA.alt(*[NFA.seq(*([p] * k)) if k > 0 else NFA.eps() for k in range(lo, hi + 1)])

    def anywhere(self, p):
        """... p ... : p as a contiguous word-subsequence, any words before/after."""
        return NFA.seq(NFA.star(self.anyword()), p, NFA.star(self.anyword()))

    def compile(self, p):
        """word-level NFA -> char-level DFA over sigma accepting exactly the labellings whose text matches."""
        full = NFA.seq(p, self.sep()).to_dfa(self.sigma)
        start = full.step(full.start, self.delim)
        accept = {q for q in range(full.n) if full.step(q, self.delim) in full.accept}
        if start < 0: return DFA(self.sigma, [{}], 0, set())
        return DFA(self.sigma, full.delta, start, accept).minimize()

    def text(self, labelling, id_to_char):
        s = "".join(id_to_char[i] for i in labelling)
        return " ".join(w for w in s.split(id_to_char[self.delim]) if w)

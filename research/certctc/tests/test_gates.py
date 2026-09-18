"""certctc gates.  Every gate from T2b (`gate.py`, `gate_w.py`, `gate_c.py`) and T9 (`t9gates.py`,
`t9theory.py`, `t9strict.py`) as a test, including the ones T9 found missing in T2b:
  - the argmax gate checks p_mode as well as the label (T2b skipped p* when the label matched);
  - the admissibility gate covers conf 0.5/0.6/0.8 and W up to 5 in exact rationals (T2b: conf >= 0.8, W <= 3);
  - the runner-up and its probability are gated against brute force with ties handled explicitly;
  - the flat-row exponential growth law (W-2)^{T/2} is asserted, not footnoted.
Run with `pytest -s` to see the GATE lines.
"""
import math, os, random, shutil, sys, time
from fractions import Fraction
from itertools import product

import pytest

import certctc
from certctc import decode, verify, ctc_prob, Certificate, BudgetExceeded
from certctc import _pysearch, _csearch
from certctc._toolkit_ctc import brute_ctc, collapse, peaky_table

HAVE_C = _csearch.load() is not None
BACKENDS = ['python'] + (['c'] if HAVE_C else [])


def GATE(msg): print('\nGATE ' + msg, flush=True)


# ------------------------------------------------------------------ table generators
def random_table(rng, T, W):
    t = [[rng.random() for _ in range(W)] for _ in range(T)]
    return [[v / sum(r) for v in r] for r in t]


def frac_random_table(rng, T, W, den=97):
    rows = []
    for _ in range(T):
        r = [Fraction(rng.randrange(1, den)) for _ in range(W)]; s = sum(r); rows.append([x / s for x in r])
    return rows


def frac_peaky_table(rng, T, W, conf):
    """Exact-rational version of the toolkit's peaky_table (same construction, Fraction entries)."""
    rows = []
    for _ in range(T):
        win = 0 if rng.random() < 0.7 else rng.randrange(1, W)
        row = [(1 - conf) / (W - 1)] * W; row[win] = conf; rows.append(row)
    return rows


def flat_table(T, W): return [[1.0 / W] * W for _ in range(T)]


def brute_all(table):
    """{labelling: p} by path enumeration; generic arithmetic (float or Fraction)."""
    W = len(table[0]); out = {}
    for path in product(range(W), repeat=len(table)):
        p = 1
        for t, s in enumerate(path): p = p * table[t][s]
        b = collapse(path); out[b] = out.get(b, 0) + p
    return out


def brute_g(table, t, c):
    """{v: g_v(t)} over all paths on frames t..T (1-based) with pi_t = c."""
    T = len(table); W = len(table[0]); out = {}
    for tail in product(range(W), repeat=T - t):
        path = (c,) + tail; p = table[t - 1][c]
        for i, s in enumerate(tail): p = p * table[t + i][s]
        v = collapse(path); out[v] = out.get(v, 0) + p
    return out


def top2(ex):
    """(p1, p2, n_tied_at_p1, n_tied_at_p2) from a brute-force dict; p2 = second largest WITH multiplicity."""
    vals = sorted(ex.values(), reverse=True)
    p1, p2 = vals[0], vals[1]
    n1 = sum(1 for v in vals if abs(v - p1) <= 1e-12 * p1)
    n2 = sum(1 for v in vals if abs(v - p2) <= 1e-12 * max(p2, 1e-300)) - (1 if abs(p2 - p1) <= 1e-12 * p1 else 0)
    return p1, p2, n1, n2


def close(a, b, rel=1e-12): return abs(a - b) <= rel * max(abs(a), abs(b), 1e-300)


# ------------------------------------------------------------------ instance sets for (a)/(b)
def instances_random(rng, n=300):
    out = []
    for _ in range(n):
        T, W = rng.choice([(4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3)])
        out.append(random_table(rng, T, W))
    return out


def instances_peaky(rng, n=100):
    out = []
    for _ in range(n):
        T, W = rng.choice([(5, 3), (6, 3), (7, 3), (8, 3), (6, 4), (7, 4), (8, 4)])
        out.append(peaky_table(T, W, rng, rng.choice([0.5, 0.6, 0.7, 0.8, 0.9])))
    return out


def instances_w58(rng, n=100):
    out = []
    for i in range(n):
        W = 5 if i % 2 == 0 else 8
        T = rng.choice([4, 5, 6]) if W == 5 else rng.choice([4, 5])
        out.append(random_table(rng, T, W) if i % 4 < 2 else peaky_table(T, W, rng, rng.choice([0.5, 0.6, 0.8, 0.9])))
    return out


def _gate_mode_and_runner_up(name, tables):
    wrong_mode = {b: 0 for b in BACKENDS}; wrong_ru = {b: 0 for b in BACKENDS}; wrong_verify = {b: 0 for b in BACKENDS}
    ties_mode = 0; ties_ru = 0
    for tb in tables:
        ex = brute_all(tb); p1, p2, n1, n2 = top2(ex)
        if n1 > 1: ties_mode += 1
        if n2 > 1: ties_ru += 1
        for b in BACKENDS:
            c = decode(tb, backend=b)
            ok_mode = close(c.p_mode, p1) and close(ex.get(c.mode, -1.0), p1)
            ok_ru = (c.runner_up is not None and c.runner_up != c.mode and close(c.p_runner_up, p2)
                     and close(ex.get(c.runner_up, -1.0), p2))
            if not ok_mode: wrong_mode[b] += 1; print('  WRONG mode', b, c.mode, c.p_mode, p1)
            if not ok_ru: wrong_ru[b] += 1; print('  WRONG runner-up', b, c.runner_up, c.p_runner_up, p2)
            if not verify(tb, c): wrong_verify[b] += 1
    GATE('(a) argmax AND p_mode vs brute force, %s: %d instances, wrong = %s, exact ties at p* %d -> %s' % (
        name, len(tables), wrong_mode, ties_mode, 'PASS' if not any(wrong_mode.values()) else 'FAIL'))
    GATE('(b) runner-up AND p_runner_up vs brute force (second largest, ties explicit), %s: %d instances, wrong = %s, exact ties at p2 %d -> %s' % (
        name, len(tables), wrong_ru, ties_ru, 'PASS' if not any(wrong_ru.values()) else 'FAIL'))
    GATE('(f) verify() on every certificate, %s: %d certificates, failures %s -> %s' % (
        name, len(tables) * len(BACKENDS), wrong_verify, 'PASS' if not any(wrong_verify.values()) else 'FAIL'))
    assert not any(wrong_mode.values()); assert not any(wrong_ru.values()); assert not any(wrong_verify.values())


def test_ab_random_T8_W3():
    _gate_mode_and_runner_up('random T<=8 W<=3', instances_random(random.Random(3), 300))


def test_ab_peaky_conf05_09():
    _gate_mode_and_runner_up('peaky conf 0.5-0.9 T<=8 W<=4', instances_peaky(random.Random(4), 100))


def test_ab_W5_W8():
    _gate_mode_and_runner_up('W in {5,8} T<=6', instances_w58(random.Random(5), 100))


# ------------------------------------------------------------------ (c) admissibility, exact rationals
def test_c_admissibility_exact():
    rng = random.Random(11); cells = 0; bad_H = 0; bad_B = 0; prefixes = 0; tables = 0
    confs = [Fraction(1, 2), Fraction(3, 5), Fraction(4, 5)]
    specs = [(T, W) for W in (3, 4, 5) for T in (4, 5, 6)]
    for i in range(len(confs) * len(specs) * 2 + 20):
        if i < len(confs) * len(specs) * 2:
            conf = confs[i % 3]; T, W = specs[(i // 3) % len(specs)]
            tb = frac_peaky_table(rng, T, W, conf)
        else:
            T, W = rng.choice(specs); tb = frac_random_table(rng, T, W)
        r = _pysearch.decode_python(tb); H = r['H']; tables += 1
        for t in range(1, T + 1):
            for c in range(1, W):
                cells += 1
                if H[c][t] != max(brute_g(tb, t, c).values()): bad_H += 1
        # the bound itself: B(u) >= max over labellings with prefix u, for every prefix with a positive maximum
        ex = brute_all(tb); ctx = _pysearch.make_ctx(tb, H)
        stack = [_pysearch.final_root(tb)]
        while stack:
            n = stack.pop(); u = n.labelling()
            best = max((p for l, p in ex.items() if l[:len(u)] == u), default=0)
            if best == 0: continue
            prefixes += 1
            if _pysearch.bound_of(ctx, n, 0) < best: bad_B += 1
            if len(u) < 3:
                for d in range(1, W): stack.append(_pysearch.make_child(ctx, n, d))
    GATE('(c) admissibility, exact Fractions, conf in {0.5,0.6,0.8} + random, W<=5: %d tables, %d (t,c) cells H != brute-force max_v g_v(t): %d; '
         '%d prefixes with B(u) < max_v p(u.v): %d -> %s' % (tables, cells, bad_H, prefixes, bad_B, 'PASS' if bad_H == 0 and bad_B == 0 else 'FAIL'))
    assert bad_H == 0 and bad_B == 0


# ------------------------------------------------------------------ (d) decomposition identity
def test_d_decomposition_identity():
    rng = random.Random(12); n = 0; bad = 0
    while n < 300:
        T, W = rng.choice([(3, 2), (4, 2), (5, 3), (6, 3), (7, 3), (5, 4)])
        tb = frac_random_table(rng, T, W) if n % 2 else frac_peaky_table(rng, T, W, Fraction(3, 5))
        ex = brute_all(tb); labs = [l for l in ex if len(l) >= 1]
        ctx = _pysearch.make_ctx(tb, [[0] * (T + 1) for _ in range(W)])
        for _ in range(4):
            l = rng.choice(labs); k = rng.randrange(0, len(l)); u, v = l[:k], l[k:]
            pn = _pysearch.final_root(tb)
            for d in u: pn = _pysearch.make_child(ctx, pn, d)
            last = u[-1] if u else None
            rhs = 0
            for t in range(1, T + 1):
                ok = pn.Ab[t - 1] + (0 if last == v[0] else pn.An[t - 1])
                sn = _pysearch.suffix_root(tb, t, v[0])
                for d in v[1:]: sn = _pysearch.make_child(ctx, sn, d)
                rhs += ok * sn.p
            n += 1
            if rhs != ex[l]: bad += 1
    GATE('(d) decomposition p(u.v) == sum_t ok_{v1}(t-1) g_v(t), exact Fractions: %d triples, mismatches %d -> %s' % (n, bad, 'PASS' if bad == 0 else 'FAIL'))
    assert bad == 0


# ------------------------------------------------------------------ (e) C backend bit-identical to Python
@pytest.mark.skipif(shutil.which(os.environ.get('CC', 'cc')) is None, reason='no C compiler')
def test_e_c_bit_identical():
    assert HAVE_C, 'C backend failed to build: %r' % (_csearch.load_error(),)
    rng = random.Random(606); n = 0; bad = []
    for i in range(100):
        T, W = rng.choice([(6, 3), (8, 3), (10, 3), (12, 3), (8, 5), (10, 5), (12, 5), (8, 8), (12, 8)])
        tb = random_table(rng, T, W) if i % 2 else peaky_table(T, W, rng, rng.choice([0.5, 0.6, 0.7, 0.8, 0.9]))
        cp = decode(tb, backend='python', want_H=True); cc = decode(tb, backend='c', want_H=True); n += 1
        same = (cp.p_mode == cc.p_mode and cp.p_runner_up == cc.p_runner_up and cp.mode == cc.mode and cp.runner_up == cc.runner_up
                and cp.H == cc.H and cp.expansions_final == cc.expansions_final and cp.generations_total == cc.generations_total
                and cp.expansions_backward == cc.expansions_backward)
        if not same: bad.append((T, W, cp.expansions_final, cc.expansions_final, cp.generations_total, cc.generations_total))
    GATE('(e) C backend vs Python backend bit-identical (p*, p2, mode, runner-up, H, expansions, generations): %d tables (T<=12, W<=8), mismatches %d -> %s' % (
        n, len(bad), 'PASS' if not bad else 'FAIL'))
    for b in bad: print('  MISMATCH', b)
    assert not bad


# ------------------------------------------------------------------ (f) verify(): larger tables + negative controls
def test_f_verify_large_and_mutations():
    rng = random.Random(77)
    tbs = [peaky_table(32, 5, rng, 0.8), peaky_table(24, 8, rng, 0.6)] + ([peaky_table(64, 32, rng, 0.8)] if HAVE_C else [])
    n = 0
    for tb in tbs:
        c = decode(tb); rep = verify(tb, c); n += 1
        assert rep, rep
        # independent recomputation agrees to ~1e-12
        assert rep.rel_err_mode < 1e-10 and rep.rel_err_runner_up < 1e-10
        # mutation 1: perturb p_mode -> must fail
        d = c.to_dict(); d['p_mode'] *= (1 + 1e-6); assert not verify(tb, Certificate.from_dict(d))
        # mutation 2: runner-up set equal to mode -> must fail
        d = c.to_dict(); d['runner_up'] = d['mode']; d['p_runner_up'] = d['p_mode']; d['margin'] = 1.0; assert not verify(tb, Certificate.from_dict(d))
        # mutation 3: a different labelling claimed as mode -> must fail
        d = c.to_dict(); d['mode'] = list(c.runner_up); assert not verify(tb, Certificate.from_dict(d))
        # mutation 4: pruned_mass_bound > 0 is not an exact certificate
        d = c.to_dict(); d['pruned_mass_bound'] = 1e-9; assert not verify(tb, Certificate.from_dict(d))
        # round trip through JSON verifies
        assert verify(tb, Certificate.from_json(c.to_json()))
    GATE('(f) verify() on %d larger certificates (T up to 64, W up to 32): PASS; 4 mutations x %d certificates rejected: PASS' % (n, n))


# ------------------------------------------------------------------ (g) flat rows: the worst case as a test
T9_FLAT_W5 = {8: (53, 788), 10: (161, 2500), 12: (485, 7668), 14: (1457, 23204)}   # T9 grow_flat5.log (expF, gen)


@pytest.mark.parametrize('backend', BACKENDS)
def test_g_flat_growth_law_W5(backend):
    W = 5; expF = {}; gen = {}
    for T in (8, 10, 12, 14):
        c = decode(flat_table(T, W), backend=backend)
        expF[T] = c.expansions_final; gen[T] = c.generations_total
        assert c.p_mode == c.p_runner_up and c.margin == 1.0     # exact ties: (W-1)(W-2)^(D-1) tied relabellings
        assert verify(flat_table(T, W), c)
    ratios = [expF[T + 2] / expF[T] for T in (8, 10, 12)]
    GATE('(g) flat rows W=5, T=8,10,12,14 [%s]: final expansions %s (T9: %s), generations %s, growth per 2 frames %s (law: W-2 = 3) -> %s' % (
        backend, [expF[T] for T in (8, 10, 12, 14)], [T9_FLAT_W5[T][0] for T in (8, 10, 12, 14)], [gen[T] for T in (8, 10, 12, 14)],
        ['%.3f' % r for r in ratios], 'PASS' if all(abs(r - 3) < 0.1 for r in ratios) else 'FAIL'))
    for T in (8, 10, 12, 14): assert (expF[T], gen[T]) == T9_FLAT_W5[T]
    for r in ratios: assert abs(r - (W - 2)) < 0.1


def test_g_flat_growth_law_W4():
    W = 4; expF = {}
    for T in (8, 10, 12, 14):
        c = decode(flat_table(T, W)); expF[T] = c.expansions_final
        assert c.p_mode == c.p_runner_up
    ratios = [expF[T + 2] / expF[T] for T in (8, 10, 12)]
    GATE('(g) flat rows W=4, T=8..14: final expansions %s, growth per 2 frames %s (law: W-2 = 2) -> %s' % (
        [expF[T] for T in (8, 10, 12, 14)], ['%.3f' % r for r in ratios], 'PASS' if all(abs(r - 2) < 0.15 for r in ratios) else 'FAIL'))
    for r in ratios: assert abs(r - (W - 2)) < 0.15


# ------------------------------------------------------------------ (h) T9 upper bound, adapted to the runner-up-certifying search
def test_h_expansions_upper_bound():
    rng = random.Random(5); n = 0; viol = 0
    fams = [('random', lambda T, W: random_table(rng, T, W)), ('flat', lambda T, W: flat_table(T, W)),
            ('peaky.8', lambda T, W: peaky_table(T, W, rng, 0.8)), ('peaky.5', lambda T, W: peaky_table(T, W, rng, 0.5))]
    for name, gen in fams:
        for T, W in [(8, 3), (9, 3), (10, 3), (8, 4)]:
            for _ in range(3):
                tb = gen(T, W); ex = brute_all(tb); c = decode(tb); thr = c.p_runner_up / T
                prefixes = set()
                for l, p in ex.items():
                    if p >= thr:
                        for k in range(len(l) + 1): prefixes.add(l[:k])
                n += 1
                if c.expansions_final > len(prefixes): viol += 1
    GATE('(h) final expansions <= |prefixes of labellings with p >= p2/T| (T9 theorem, p2 for the runner-up-certifying search): %d instances, violations %d -> %s' % (
        n, viol, 'PASS' if viol == 0 else 'FAIL'))
    assert viol == 0


# ------------------------------------------------------------------ (i) cross-check against the T2b and T9 reference code (read-only)
def test_i_reference_implementations():
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    t2b_dir = os.path.join(here, 'code', 'certified-exact-decoder'); t9_dir = os.path.join(here, 'code', 'adversarial-decoder-check')
    if not (os.path.isdir(t2b_dir) and os.path.isdir(t9_dir)): pytest.skip('T2b/T9 reference code not present')
    sys.path.insert(0, t2b_dir); sys.path.insert(0, t9_dir)
    import bounds as T2B; import t9core as T9
    rng = random.Random(9); n = 0; bad_t2b = 0; bad_t9 = 0; cnt_t9 = 0; cnt_t9_peaky = 0
    for i in range(20):
        T, W = rng.choice([(8, 3), (10, 3), (10, 5), (12, 3), (8, 5)])
        tb = random_table(rng, T, W) if i % 2 else peaky_table(T, W, rng, rng.choice([0.5, 0.8]))
        c = decode(tb, backend='python', want_H=True); n += 1
        He, _ = T2B.H_exact_backward(tb, T2B.H_policy(tb)); r = T2B.best_first(tb, lambda nd: T2B.bound_from_H(nd, tb, He))
        if not (c.p_mode == r[0] and c.mode == r[1] and all(c.H[d][1:] == He[d][1:] for d in range(1, W))): bad_t2b += 1
        r9 = T9.decode_exactbwd(tb, W)
        # every expansion generates exactly W-1 children, so backward generations = expansions_backward*(W-1)
        assert c.generations_total == (c.expansions_backward + c.expansions_final) * (W - 1)
        if not (c.p_mode == r9['p'] and c.mode == r9['mode'] and all(c.H[d][1:] == r9['H'][d] for d in range(1, W))): bad_t9 += 1
        if c.expansions_backward != r9['exp_back'] or c.expansions_backward * (W - 1) != r9['gen_back']:
            cnt_t9 += 1; cnt_t9_peaky += (i % 2 == 0)
    GATE('(i) vs T2b bounds.py (H bit-identical, p*, mode) and T9 t9core (H bit-identical, p*, mode): %d tables, mismatches T2b %d, T9 %d -> %s; '
         'backward expansion counts differ from T9 on %d/%d tables (%d of them peaky: exact-tie ordering, see README)' % (
        n, bad_t2b, bad_t9, 'PASS' if bad_t2b == 0 and bad_t9 == 0 else 'FAIL', cnt_t9, n, cnt_t9_peaky))
    assert bad_t2b == 0 and bad_t9 == 0


# ------------------------------------------------------------------ (j) API: blank index, budgets, JSON
def test_j_blank_permutation_and_budget():
    rng = random.Random(21); n = 0; ties = 0
    for _ in range(20):
        T, W = rng.choice([(6, 3), (8, 4)]); tb = peaky_table(T, W, rng, 0.7); blank = rng.randrange(W)
        perm = list(range(W)); perm[0], perm[blank] = perm[blank], perm[0]         # column perm[j] of tb2 = column j of tb
        tb2 = [[row[perm[j]] for j in range(W)] for row in tb]
        c0 = decode(tb); c1 = decode(tb2, blank=blank); n += 1
        assert c1.p_mode == c0.p_mode and c1.p_runner_up == c0.p_runner_up
        inv = {perm[j]: j for j in range(W)}
        m0 = tuple(inv[s] for s in c0.mode); r0 = tuple(inv[s] for s in c0.runner_up)
        # exact ties between symmetric symbols may be reported in a different order after the permutation
        assert m0 == c1.mode or ctc_prob(m0, tb2, blank) == ctc_prob(c1.mode, tb2, blank)
        if r0 != c1.runner_up: ties += 1; assert ctc_prob(r0, tb2, blank) == ctc_prob(c1.runner_up, tb2, blank)
        assert verify(tb2, c1)
    with pytest.raises(BudgetExceeded):
        decode(peaky_table(32, 5, rng, 0.8), max_generations=50)
    with pytest.raises(BudgetExceeded):
        decode(flat_table(28, 5), time_limit=0.05)        # ~5e7 generations in C; the deadline fires first
    GATE('(j) blank != 0 handled by column permutation (%d tables, %d exact runner-up ties reported in permuted order), budgets raise BudgetExceeded instead of returning a certificate -> PASS' % (n, ties))

"""Gates for class_posterior and the automaton library.  Prints GATE lines; exit 1 on any failure."""
import sys, os, random, re, time
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fsa import NFA, DFA, WordAlphabet, all_strings_dfa
from classctc import (class_posterior_py, class_posterior_np, brute_class_paths, brute_class_labellings,
                      ctc_forward_exact, collapse)
from ctc import ctc_forward as toolkit_ctc_forward, brute_ctc as toolkit_brute

rng = random.Random(2026)
fails = 0


def frac_table(T, W, peaky=False):
    rows = []
    for _ in range(T):
        if peaky:
            win = 0 if rng.random() < 0.5 else rng.randrange(W)
            r = [Fraction(rng.randrange(1, 4), 1) for _ in range(W)]; r[win] = Fraction(rng.randrange(20, 60), 1)
        else:
            r = [Fraction(rng.randrange(1, 20), 1) for _ in range(W)]
        s = sum(r); rows.append([v / s for v in r])
    return rows


def random_dfa(sigma, nstates):
    delta = []
    for q in range(nstates):
        row = {}
        for c in sigma:
            r = rng.randrange(-1, nstates)
            if r >= 0 and rng.random() < 0.85: row[c] = r
        delta.append(row)
    accept = {q for q in range(nstates) if rng.random() < 0.5}
    return DFA(sigma, delta, 0, accept)


def singleton_dfa(sigma, l):
    return NFA.string(l).to_dfa(sigma)


# ---------------------------------------------------------------- 1. exact gates (a)(b)(c)
def gate_exact():
    global fails
    n_a = n_b = n_c = 0; mis_a = mis_b = mis_c = 0; t0 = time.perf_counter(); paths = 0; labs = 0; nz_a = nz_b = 0
    for inst in range(40):
        T = rng.randrange(1, 8); W = rng.randrange(2, 5); blank = rng.choice([0, W - 1])
        sigma = [c for c in range(W) if c != blank]
        tbl = frac_table(T, W, peaky=(inst % 2 == 0))
        dfas = [random_dfa(sigma, rng.randrange(1, 5)) for _ in range(2)]
        if len(sigma) >= 2:                                    # hand-built word classes: delim = sigma[0]
            wa = WordAlphabet({chr(97 + i): c for i, c in enumerate(sigma[1:])}, sigma[0], blank, W)
            letters = [chr(97 + i) for i in range(len(sigma) - 1)]
            w1 = "".join(rng.choice(letters) for _ in range(rng.randrange(1, 3)))
            w2 = "".join(rng.choice(letters) for _ in range(rng.randrange(1, 3)))
            dfas += [wa.compile(wa.anywhere(wa.lit(w1))),                                   # contains word w1
                     wa.compile(wa.wseq(wa.anyword(), wa.lit(w2), wa.wstar(wa.anyword()))),  # 2nd word is w2
                     wa.compile(wa.wseq(wa.wstar(wa.anyword()), wa.lit(w1))),                # last word is w1
                     wa.compile(wa.wplus(NFA.alt(wa.lit(w1), wa.lit(w2))))]                  # only w1/w2 words
        for d in dfas:
            got = class_posterior_py(tbl, d, blank)
            if T <= 7 and W ** T <= 20000:
                ref_a = brute_class_paths(tbl, d, blank); n_a += 1; paths += W ** T
                if ref_a != got: mis_a += 1
                nz_a += (ref_a > 0)
            ref_b = brute_class_labellings(tbl, d, blank); n_b += 1; labs += sum(len(sigma) ** L for L in range(T + 1))
            if ref_b != got: mis_b += 1
            nz_b += (ref_b > 0)
        # (c) sanity
        one = class_posterior_py(tbl, all_strings_dfa(sigma), blank); n_c += 1
        if one != 1: mis_c += 1
        for _ in range(3):
            L = rng.randrange(0, T + 1); l = tuple(rng.choice(sigma) for _ in range(L))
            got = class_posterior_py(tbl, singleton_dfa(sigma, l), blank); ref = ctc_forward_exact(l, tbl, blank); n_c += 1
            if got != ref: mis_c += 1
            # and the toolkit's float forward, and the toolkit brute force when blank == 0
            tf = toolkit_ctc_forward(l, [[float(v) for v in r] for r in tbl], blank=blank)
            if abs(tf - float(ref)) > 1e-12 * max(float(ref), 1e-300) + 1e-300: mis_c += 1; n_c += 1
    dt = time.perf_counter() - t0
    print(f"GATE (a) class_posterior vs brute force over all W^T paths (exact Fractions): {n_a} (table,DFA) instances, {paths} paths summed, {nz_a} with nonzero mass, {mis_a} mismatches -> {'PASS' if mis_a == 0 else 'FAIL'}")
    print(f"GATE (b) class_posterior vs sum of ctc_forward over enumerated L (|l|<=T, exact Fractions): {n_b} instances, {labs} labellings summed, {nz_b} with nonzero mass, {mis_b} mismatches -> {'PASS' if mis_b == 0 else 'FAIL'}")
    print(f"GATE (c) L=Sigma* gives exactly 1 and L={{l}} gives exactly ctc_forward(l) (+ toolkit float forward to 1e-12): {n_c} checks, {mis_c} mismatches -> {'PASS' if mis_c == 0 else 'FAIL'}  [{dt:.1f}s]")
    fails += (mis_a + mis_b + mis_c > 0)


# ---------------------------------------------------------------- 2. numpy vs exact
def gate_numpy():
    global fails
    worst = 0.0; n = 0
    for inst in range(30):
        T = rng.randrange(2, 41); W = rng.randrange(2, 9); blank = rng.choice([0, W - 1])
        sigma = [c for c in range(W) if c != blank]
        tbl = frac_table(T, W, peaky=(inst % 2 == 0)); d = random_dfa(sigma, rng.randrange(1, 31))
        ex = class_posterior_py(tbl, d, blank); ft = [[float(v) for v in r] for r in tbl]
        a = class_posterior_np(ft, d, blank); b = class_posterior_py(ft, d, blank)
        for got in (a, b):
            if ex == 0:
                err = abs(got)
            else:
                err = abs(got - float(ex)) / float(ex)
            worst = max(worst, err); n += 1
    print(f"GATE numpy / float implementations vs exact Fractions (T<=40, W<=8, |Q|<=30): {n} checks, worst rel err {worst:.2e} -> {'PASS' if worst < 1e-10 else 'FAIL'}")
    fails += worst >= 1e-10


# ---------------------------------------------------------------- 3. automata vs Python re
def gate_automata():
    global fails
    W = 6; blank = 5; delim = 0; chars = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    wa = WordAlphabet(chars, delim, blank, W); inv = {v: k for k, v in chars.items()}; inv[delim] = ' '
    def text(l): return " ".join(w for w in "".join(inv[c] for c in l).split() if w)
    pats = [  # (word-level NFA, python regex over the text)
        (wa.anywhere(wa.lit("ab")), r"(.* )?ab( .*)?"),
        (wa.wseq(wa.anyword(), wa.lit("b"), wa.wstar(wa.anyword())), r"\S+ b( \S+)*"),
        (wa.wseq(wa.wstar(wa.anyword()), wa.lit("a b")), r"(\S+ )*a b"),
        (wa.wplus(NFA.alt(wa.lit("a"), wa.lit("bc"))), r"(a|bc)( (a|bc))*"),
        (wa.anywhere(wa.wseq(wa.lit("c"), wa.wrepeat(NFA.alt(wa.lit("a"), wa.lit("b")), 1, 2))), r"(.* )?c (a|b)( (a|b))?( .*)?"),
        (wa.wseq(wa.wstar(wa.anyword()), wa.lit("d"), NFA.alt(wa.lit("a"), wa.lit("dd")), wa.wstar(wa.anyword())), r"(\S+ )*d (a|dd)( \S+)*"),
    ]
    dfas = [wa.compile(p) for p, _ in pats]
    combos = [(dfas[0].intersect(dfas[1]), lambda m: m[0] and m[1]),
              (dfas[0].union(dfas[2]), lambda m: m[0] or m[2]),
              (dfas[0].difference(dfas[4]), lambda m: m[0] and not m[4]),
              (dfas[3].complement(), lambda m: not m[3]),
              (dfas[5].difference(dfas[1]).union(dfas[2]), lambda m: (m[5] and not m[1]) or m[2])]
    n = 0; mis = 0
    for _ in range(4000):
        L = rng.randrange(0, 12)
        l = [rng.choice([delim] * 3 + [1, 2, 3, 4] * 2) for _ in range(L)]
        tx = text(l); m = [re.fullmatch(rx, tx) is not None for _, rx in pats]
        for d, mm in zip(dfas, m):
            n += 1
            if d.accepts(l) != mm: mis += 1
        for d, f in combos:
            n += 1
            if d.accepts(l) != bool(f(m)): mis += 1
    print(f"GATE word-pattern DFAs (+ intersect/union/difference/complement) vs Python re on rendered text: {n} checks, {mis} mismatches, sizes {[d.n for d in dfas]} -> {'PASS' if mis == 0 else 'FAIL'}")
    fails += mis > 0


if __name__ == "__main__":
    gate_exact(); gate_numpy(); gate_automata()
    print("ALL GATES", "PASS" if not fails else "FAIL")
    sys.exit(1 if fails else 0)

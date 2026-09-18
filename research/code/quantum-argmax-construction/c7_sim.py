"""C7: weighted-start amplitude amplification + exact-threshold Durr-Hoyer for argmax_l p(l|y).
Statevector simulation on (path register) x (label register), T in {3,4}, W in {2,3}.
Every reported number comes from a run whose GATE lines print PASS."""
import sys, math, random
from fractions import Fraction
from itertools import product
import numpy as np
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certified-exact-decoder'))
from ctc import brute_ctc, ctc_forward, collapse, peaky_table   # toolkit, read-only

# ---------------- classical pieces ----------------
def my_brute(table, blank=0):
    """Independent enumeration (my own), returns {label: p}."""
    T, W = len(table), len(table[0]); out = {}
    for path in product(range(W), repeat=T):
        p = 1.0
        for t, s in enumerate(path): p *= table[t][s]
        lab = []
        for t, s in enumerate(path):
            if s != blank and (t == 0 or s != path[t-1]): lab.append(s)
            # NOTE: collapse = merge adjacent repeats THEN delete blanks; repeat merging
            # is on the raw path, so 'a blank a' -> 'aa', 'a a' -> 'a'.
        out[tuple(lab)] = out.get(tuple(lab), 0.0) + p
    return out

def rational_table(T, W, rng, den=48):
    """Uniform-random rows with rational entries k/den, rows summing to exactly 1."""
    rows = []
    for _ in range(T):
        cuts = sorted(rng.sample(range(1, den), W-1))
        parts = [b - a for a, b in zip([0]+cuts, cuts+[den])]
        rows.append([k/den for k in parts])
    return rows

# ---------------- quantum pieces ----------------
class C7Sim:
    def __init__(self, table, blank=0):
        self.table = table; self.T = len(table); self.W = len(table[0]); self.blank = blank
        self.paths = list(product(range(self.W), repeat=self.T))
        self.NP = len(self.paths)
        labs = sorted({collapse(pi, blank) for pi in self.paths}, key=lambda l: (len(l), l))
        # label register basis: index 0 must be the empty label so |0>_label is a legal state
        assert labs[0] == ()
        self.labels = labs; self.NL = len(labs); self.lidx = {l: i for i, l in enumerate(labs)}
        # reversible collapsing map B: |pi>|j> -> |pi>|j + idx(B(pi)) mod NL>  (a permutation)
        N = self.NP * self.NL
        perm = np.zeros(N, dtype=np.int64)
        for a, pi in enumerate(self.paths):
            k = self.lidx[collapse(pi, blank)]
            for j in range(self.NL):
                perm[a*self.NL + j] = a*self.NL + ((j + k) % self.NL)
        assert len(set(perm.tolist())) == N, "B is not a permutation"
        self.perm = perm
        # product state on the path register: amplitude sqrt(prod_t y[t][pi_t])
        amp = np.ones(self.NP)
        for a, pi in enumerate(self.paths):
            for t, s in enumerate(pi): amp[a] *= math.sqrt(table[t][s])
        psi = np.zeros(N); psi[np.arange(self.NP)*self.NL] = amp     # |pi>|0>
        Bpsi = np.zeros(N); Bpsi[perm] = psi                        # apply B
        self.Psi = Bpsi                                             # A|0>
        assert abs(np.linalg.norm(self.Psi) - 1) < 1e-12
        # label of each basis state
        self.lab_of_basis = np.array([i % self.NL for i in range(N)])
        # exact p(l|y) by the forward recursion (what the reversible oracle computes)
        self.p = np.array([ctc_forward(l, table, blank) for l in labs])
        self.n_A = 0        # applications of A or A^-1 (each Grover iteration = 2)
        self.n_grover = 0   # Grover iterations (each = one oracle + one reflection)

    def label_marginal(self, state):
        pr = np.abs(state)**2
        return np.bincount(self.lab_of_basis, weights=pr, minlength=self.NL)

    def grover_step(self, state, marked):
        """Q = -A S_0 A^-1 S_chi = (2|Psi><Psi| - I) S_chi ; S_chi flips phase on marked labels."""
        s = state.copy()
        s[marked[self.lab_of_basis]] *= -1
        s = 2*self.Psi*np.dot(self.Psi, s) - s
        self.n_grover += 1; self.n_A += 2
        return s

    def measure_label(self, state, rng):
        pr = self.label_marginal(state); pr = pr/pr.sum()
        return rng.choices(range(self.NL), weights=pr)[0]

    def qsearch(self, marked, rng, c=1.5, M_cap=None, K=12):
        """BHMT Thm 3 QSearch with a cap: after M reaches M_cap, K further failed loops -> 'empty'.
        Returns (label or None, grover iterations used in this call)."""
        g0 = self.n_grover; l = 0; at_cap = 0
        while True:
            l += 1; M = math.ceil(c**l)
            if M_cap is not None and M >= M_cap:
                M = M_cap; at_cap += 1
                if at_cap > K: return None, self.n_grover - g0
            # step 3: classical-style sample from A|0>
            self.n_A += 1
            z = self.measure_label(self.Psi, rng)
            if marked[z]: return z, self.n_grover - g0
            # steps 4-7
            j = rng.randint(1, M)
            s = self.Psi
            for _ in range(j): s = self.grover_step(s, marked)
            z = self.measure_label(s, rng)
            if marked[z]: return z, self.n_grover - g0

    def durr_hoyer(self, rng, pfun=None, K=12, kappa=2.0):
        """Threshold-raising loop. pfun = the (possibly rounded) oracle function of the label."""
        p = self.p if pfun is None else pfun
        self.n_A = 0; self.n_grover = 0
        self.n_A += 1
        cur = self.measure_label(self.Psi, rng)      # initial threshold = a Born-rule sample
        theta = p[cur]; rounds = 0; g_search = 0; g_detect = 0
        while True:
            marked = p > theta
            M_cap = max(1, math.ceil(kappa/math.sqrt(theta))) if theta > 0 else None
            z, g = self.qsearch(marked, rng, M_cap=M_cap, K=K)
            if z is None:
                g_detect += g; break
            g_search += g; rounds += 1
            assert p[z] > theta
            cur, theta = z, p[z]
        return self.labels[cur], rounds, g_search, g_detect, self.n_A

def expected_rounds_exact(p):
    """Sum_r p_r / P_r over labels sorted descending = E[# thresholds ever chosen] (incl. initial)."""
    ps = sorted(p, reverse=True); P = 0.0; tot = 0.0
    for x in ps:
        P += x
        if x > 0: tot += x/P
    return tot

def run(ntables=200, seed=7, verbose=True):
    rng = random.Random(seed)
    configs = [(3,2),(4,2),(3,3),(4,3)]
    rows = []; fails = 0; worst_bf = 0.0; worst_my = 0.0; n_lab = 0
    for i in range(ntables):
        T, W = configs[i % len(configs)]
        kind = i % 2
        if kind == 0: tbl = peaky_table(T, W, rng, rng.choice([0.6, 0.8, 0.9]))
        else:         tbl = rational_table(T, W, rng)
        sim = C7Sim(tbl)
        # GATE 1: forward recursion (the oracle function) == toolkit brute force == my brute force
        bf = brute_ctc(tbl); mine = my_brute(tbl)
        for l, idx in sim.lidx.items():
            worst_bf = max(worst_bf, abs(sim.p[idx] - bf.get(l, 0.0)))
            worst_my = max(worst_my, abs(sim.p[idx] - mine.get(l, 0.0))); n_lab += 1
        # GATE 2: Born-rule marginal of A|0> equals p(l|y)
        marg = sim.label_marginal(sim.Psi)
        worst_bf = max(worst_bf, float(np.max(np.abs(marg - sim.p))))
        # brute-force argmax (both enumerations)
        arg_bf = max(bf.items(), key=lambda kv: kv[1]); arg_my = max(mine.items(), key=lambda kv: kv[1])
        pstar = arg_bf[1]
        lab, rounds, gs, gd, nA = sim.durr_hoyer(rng)
        ok = abs(ctc_forward(lab, tbl) - pstar) <= 1e-12*max(1.0, pstar)
        if not ok: fails += 1
        rows.append(dict(T=T, W=W, kind='peaky' if kind==0 else 'rational', NL=sim.NL, pstar=pstar,
                         inv_sqrt=1/math.sqrt(pstar), rounds=rounds, g_search=gs, g_detect=gd,
                         nA=nA, exact_lab=(lab == arg_bf[0]), ok=ok, Er=expected_rounds_exact(sim.p),
                         lnbound=1+math.log(1/pstar)))
    print(f"GATE oracle p(l|y) [ctc_forward] vs toolkit brute_ctc AND my own enumeration AND Born marginal of A|0>: "
          f"{n_lab} labellings, worst abs err {max(worst_bf, worst_my):.2e} -> {'PASS' if max(worst_bf,worst_my) < 1e-12 else 'FAIL'}")
    print(f"GATE Durr-Hoyer returned label has p == p* (brute force): {ntables} tables, {fails} failures -> "
          f"{'PASS' if fails == 0 else 'FAIL'}")
    return rows

if __name__ == '__main__':
    rows = run()
    import statistics as st
    ex = sum(r['exact_lab'] for r in rows)
    print(f"exact-label matches (ties excluded from the gate): {ex}/{len(rows)}")
    print("\nPer-config summary (means):")
    print(f"{'T':>2} {'W':>2} {'kind':>8} {'n':>3} {'NL':>4} {'p*':>7} {'1/sqrt p*':>9} {'rounds':>6} {'E[r] exact':>10} {'1+ln(1/p*)':>10} {'G_search':>8} {'G_detect':>8} {'G_tot/inv':>9} {'G_srch/inv':>10}")
    for (T, W) in [(3,2),(4,2),(3,3),(4,3)]:
        for kind in ('peaky','rational'):
            sub = [r for r in rows if r['T']==T and r['W']==W and r['kind']==kind]
            if not sub: continue
            m = lambda k: st.mean(r[k] for r in sub)
            print(f"{T:>2} {W:>2} {kind:>8} {len(sub):>3} {m('NL'):>4.1f} {m('pstar'):>7.3f} {m('inv_sqrt'):>9.2f} {m('rounds'):>6.2f} {m('Er'):>10.2f} {m('lnbound'):>10.2f} "
                  f"{m('g_search'):>8.1f} {m('g_detect'):>8.1f} {st.mean((r['g_search']+r['g_detect'])/r['inv_sqrt'] for r in sub):>9.2f} {st.mean(r['g_search']/r['inv_sqrt'] for r in sub):>10.2f}")
    allr = rows
    print(f"\nALL {len(allr)} tables: mean rounds {st.mean(r['rounds'] for r in allr):.2f} (exact E incl. initial sample {st.mean(r['Er'] for r in allr):.2f}; bound 1+ln(1/p*) {st.mean(r['lnbound'] for r in allr):.2f})")
    print(f"  mean G_search/(1/sqrt p*) = {st.mean(r['g_search']/r['inv_sqrt'] for r in allr):.2f}   (theory: <= 9/sqrt(p*) using BBHT's 9/2 per round)")
    print(f"  mean G_detect/(1/sqrt p*) = {st.mean(r['g_detect']/r['inv_sqrt'] for r in allr):.2f}   (theory: ~K*kappa/2 = {12*2.0/2:.0f})")
    print(f"  max rounds {max(r['rounds'] for r in allr)}, max G_total {max(r['g_search']+r['g_detect'] for r in allr)}, min p* {min(r['pstar'] for r in allr):.4f}")

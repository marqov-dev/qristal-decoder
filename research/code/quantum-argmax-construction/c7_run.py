"""C7 experiment driver: brief sizes on the FULL (path x label) statevector; extension sizes on a
COMPRESSED simulator (state provably stays in span{|pi>|B(pi)>}); precision experiment with rounded oracle."""
import sys, math, random, statistics as st
import numpy as np
sys.path.insert(0, '.')
from c7_sim import C7Sim, my_brute, rational_table, expected_rounds_exact
from ctc import brute_ctc, ctc_forward, collapse, peaky_table
from itertools import product

class C7Compressed(C7Sim):
    """Same algorithm on the W^T-dim path register; label = B(path) is a deterministic function of the path.
    Q = (2|Psi><Psi| - I) S_chi with S_chi diagonal in the path basis via lab_of_basis."""
    def __init__(self, table, blank=0):
        self.table = table; self.T = len(table); self.W = len(table[0]); self.blank = blank
        self.paths = list(product(range(self.W), repeat=self.T)); self.NP = len(self.paths)
        labs = sorted({collapse(pi, blank) for pi in self.paths}, key=lambda l: (len(l), l))
        self.labels = labs; self.NL = len(labs); self.lidx = {l: i for i, l in enumerate(labs)}
        amp = np.ones(self.NP)
        for a, pi in enumerate(self.paths):
            for t, s in enumerate(pi): amp[a] *= math.sqrt(table[t][s])
        self.Psi = amp; assert abs(np.linalg.norm(amp)-1) < 1e-12
        self.lab_of_basis = np.array([self.lidx[collapse(pi, blank)] for pi in self.paths])
        self.p = np.array([ctc_forward(l, table, blank) for l in labs])
        self.n_A = 0; self.n_grover = 0

def qsearch(self, marked, rng, c=1.5, M_cap=None, K=12):
    g0 = self.n_grover; l = 0; at_cap = 0
    while True:
        l += 1; M = math.ceil(c**l)
        if M_cap is not None and M >= M_cap:
            if at_cap >= K: return None, self.n_grover - g0
            M = M_cap; at_cap += 1
        self.n_A += 1
        z = self.measure_label(self.Psi, rng)
        if marked[z]: return z, self.n_grover - g0
        j = rng.randint(1, M); s = self.Psi
        for _ in range(j): s = self.grover_step(s, marked)
        z = self.measure_label(s, rng)
        if marked[z]: return z, self.n_grover - g0
C7Sim.qsearch = qsearch

def durr_hoyer(self, rng, pfun=None, K=12, kappa=2.0, theta_floor=0.0):
    p = self.p if pfun is None else pfun
    self.n_A = 1; self.n_grover = 0
    cur = self.measure_label(self.Psi, rng); theta = p[cur]; rounds = 0; gs = 0; gd = 0
    while True:
        marked = p > theta
        th = max(theta, theta_floor); M_cap = max(1, math.ceil(kappa/math.sqrt(th)))
        z, g = self.qsearch(marked, rng, M_cap=M_cap, K=K)
        if z is None: gd += g; break
        gs += g; rounds += 1; assert p[z] > theta; cur, theta = z, p[z]
    return self.labels[cur], rounds, gs, gd, self.n_A
C7Sim.durr_hoyer = durr_hoyer

def flat_table(T, W, rng, den=64):
    rows = []
    for _ in range(T):
        base = den // W; parts = [base]*W; extra = den - base*W
        for _ in range(extra): parts[rng.randrange(W)] += 1
        for _ in range(W):   # small random perturbation keeping positivity
            i, j = rng.randrange(W), rng.randrange(W); d = rng.randint(0, base//2)
            if parts[i] - d >= 1: parts[i] -= d; parts[j] += d
        rows.append([k/den for k in parts])
    return rows

def cost_sum(p):
    ps = sorted(p, reverse=True); P = ps[0]; tot = 0.0
    for x in ps[1:]:
        if x <= 0: break
        Pp = P; P += x; tot += (x/P)/math.sqrt(Pp)
    return tot

rng = random.Random(2026); K = 12; kappa = 2.0
rows = []; fails = 0; worst = 0.0; nlab = 0; worst_cs = 0.0
def one(T, W, kind, tag, cls):
    global fails, worst, nlab, worst_cs
    tbl = {'peaky': lambda: peaky_table(T, W, rng, rng.choice([0.6,0.8,0.9])),
           'rational': lambda: rational_table(T, W, rng), 'flat': lambda: flat_table(T, W, rng)}[kind]()
    sim = cls(tbl); bf = brute_ctc(tbl); mine = my_brute(tbl)
    for l, i in sim.lidx.items():
        worst = max(worst, abs(sim.p[i]-bf.get(l,0.0)), abs(sim.p[i]-mine.get(l,0.0))); nlab += 1
    worst = max(worst, float(np.max(np.abs(sim.label_marginal(sim.Psi)-sim.p))))
    pstar = max(bf.values()); arg = max(bf.items(), key=lambda kv: kv[1])[0]
    lab, rounds, gs, gd, nA = sim.durr_hoyer(rng, K=K, kappa=kappa)
    ok = abs(ctc_forward(lab, tbl)-pstar) <= 1e-12
    if not ok: fails += 1
    worst_cs = max(worst_cs, cost_sum(sim.p)*math.sqrt(pstar))
    srt = sorted(sim.p, reverse=True); p2 = srt[1]
    rows.append(dict(tag=tag, T=T, W=W, kind=kind, NL=sim.NL, pstar=pstar, p2=p2, inv=1/math.sqrt(pstar),
                     rounds=rounds, gs=gs, gd=gd, Er=expected_rounds_exact(sim.p), ln=1+math.log(1/pstar),
                     Mcap=math.ceil(kappa/math.sqrt(pstar)), ok=ok, exact=(lab==arg), sim=sim, tbl=tbl))

# GATE 0: compressed simulator == full simulator (same seed sequence -> identical trajectories)
mism = 0
for i in range(24):
    T, W = [(3,2),(4,2),(3,3),(4,3)][i % 4]
    tbl = rational_table(T, W, random.Random(100+i)) if i % 2 else peaky_table(T, W, random.Random(100+i), 0.7)
    a = C7Sim(tbl).durr_hoyer(random.Random(7+i), K=K, kappa=kappa)
    b = C7Compressed(tbl).durr_hoyer(random.Random(7+i), K=K, kappa=kappa)
    if a != b: mism += 1
print(f"GATE compressed (path-only) simulator reproduces the full (path x label) simulator trajectory: 24 tables, {mism} mismatches -> {'PASS' if mism==0 else 'FAIL'}")

brief = [(3,2),(4,2),(3,3),(4,3)]
ext = [(6,4),(7,4),(6,5),(7,5),(6,6),(5,6)]
for i in range(200):
    T, W = brief[i % 4]; one(T, W, ['peaky','rational'][(i//4) % 2], 'brief', C7Sim)
for i in range(72):
    T, W = ext[i % 6]; one(T, W, ['flat','rational','peaky'][(i//6) % 3], 'ext', C7Compressed)

print(f"GATE oracle p(l|y) [ctc_forward] vs toolkit brute_ctc AND my own enumeration AND Born marginal of A|0>: {nlab} labellings, worst abs err {worst:.2e} -> {'PASS' if worst<1e-12 else 'FAIL'}")
print(f"GATE Durr-Hoyer returned label has p == p* (brute force): {len(rows)} tables ({sum(r['tag']=='brief' for r in rows)} brief + {sum(r['tag']=='ext' for r in rows)} extended), {fails} failures -> {'PASS' if fails==0 else 'FAIL'}")
print(f"GATE weighted-DH cost-sum  sum_r (p_r/P_r)/sqrt(P_(r-1)) <= 2/sqrt(p*): worst sum*sqrt(p*) = {worst_cs:.3f} -> {'PASS' if worst_cs<=2 else 'FAIL'}")
print(f"exact-label matches: {sum(r['exact'] for r in rows)}/{len(rows)} (non-matches are exact ties, p==p*)")
print("\nTABLE (means per config). G = Grover iterations (1 oracle + 1 reflection each). detect = final certification round, K=12 loops at M_cap=ceil(2/sqrt(theta)).")
print(f"{'T':>2} {'W':>2} {'kind':>8} {'n':>3} {'NL':>5} {'p*':>7} {'margin':>7} {'1/sqrt p*':>9} {'rounds':>6} {'E[r]':>6} {'ln(1/p*)':>8} {'G_srch':>7} {'G_srch/inv':>10} {'G_det':>7} {'G_det/inv':>9} {'G_tot/inv':>9}")
for tag, cfgs, kinds in (('brief', brief, ('peaky','rational')), ('ext', ext, ('flat','rational','peaky'))):
    for (T,W) in cfgs:
        for kind in kinds:
            sub = [r for r in rows if r['T']==T and r['W']==W and r['kind']==kind]
            if not sub: continue
            m = lambda k: st.mean(r[k] for r in sub)
            print(f"{T:>2} {W:>2} {kind:>8} {len(sub):>3} {m('NL'):>5.1f} {m('pstar'):>7.4f} {st.median(r['pstar']/r['p2'] for r in sub):>7.2f} {m('inv'):>9.2f} {m('rounds'):>6.2f} {m('Er')-1:>6.2f} {m('ln')-1:>8.2f} "
                  f"{m('gs'):>7.1f} {st.mean(r['gs']/r['inv'] for r in sub):>10.2f} {m('gd'):>7.1f} {st.mean(r['gd']/r['inv'] for r in sub):>9.2f} {st.mean((r['gs']+r['gd'])/r['inv'] for r in sub):>9.2f}")
print(f"\nALL {len(rows)}: rounds mean {st.mean(r['rounds'] for r in rows):.2f} vs exact E[rounds] {st.mean(r['Er']-1 for r in rows):.2f} vs bound ln(1/p*) {st.mean(r['ln']-1 for r in rows):.2f}; max rounds {max(r['rounds'] for r in rows)}")
print(f"  G_search/(1/sqrt p*): mean {st.mean(r['gs']/r['inv'] for r in rows):.2f}, max {max(r['gs']/r['inv'] for r in rows):.2f}  (bound 9 = (9/2)*2)")
print(f"  G_detect: mean {st.mean(r['gd'] for r in rows):.1f} vs K*(M_cap+1)/2 = {st.mean(K*(r['Mcap']+1)/2 for r in rows):.1f};  G_detect/(1/sqrt p*) mean {st.mean(r['gd']/r['inv'] for r in rows):.2f}")
ex = [r for r in rows if r['tag']=='ext']
print(f"  EXT only (n={len(ex)}): p* range {min(r['pstar'] for r in ex):.4f}-{max(r['pstar'] for r in ex):.4f}; rounds mean {st.mean(r['rounds'] for r in ex):.2f} vs E[r] {st.mean(r['Er']-1 for r in ex):.2f} vs ln(1/p*) {st.mean(r['ln']-1 for r in ex):.2f}; G_search/inv {st.mean(r['gs']/r['inv'] for r in ex):.2f} (max {max(r['gs']/r['inv'] for r in ex):.2f}); G_tot/inv {st.mean((r['gs']+r['gd'])/r['inv'] for r in ex):.2f}")

print("\nPRECISION: oracle computes p~ = floor(p*2^b)/2^b (absolute fixed point, theta floored at 2^-b for the cap).")
print(f"{'b':>3} {'tables':>6} {'safe(p*-p2>2^-b)':>17} {'safe&wrong':>10} {'ambig':>6} {'ambig&wrong':>11} {'p~-argmax ok':>12}")
sub = [r for r in rows if r['NL'] >= 3]
allok = True
for b in (3,4,6,8,10,12):
    safe=sw=amb=aw=okmax=0
    for r in sub:
        sim = r['sim']; pt = np.floor(sim.p*2**b)/2**b
        lab, *_ = sim.durr_hoyer(rng, pfun=pt, K=K, kappa=kappa, theta_floor=2.0**-b)
        i = sim.lidx[lab]; wrong = abs(ctc_forward(lab, r['tbl'])-r['pstar']) > 1e-12
        if pt[i] >= pt.max()-1e-15: okmax += 1
        if r['pstar']-r['p2'] > 2**-b: safe += 1; sw += wrong
        else: amb += 1; aw += wrong
    allok &= (sw == 0 and okmax == len(sub))
    print(f"{b:>3} {len(sub):>6} {safe:>17} {sw:>10} {amb:>6} {aw:>11} {okmax:>12}")
print(f"GATE precision: returned label always maximises the ROUNDED oracle, and is never wrong when p*-p2 > 2^-b -> {'PASS' if allok else 'FAIL'}")

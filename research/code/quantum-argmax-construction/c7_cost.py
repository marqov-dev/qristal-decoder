"""Equal-units cost model for C7 vs classical prefix search. Units: one b-bit fixed-point multiply-add
== one Toffoli-equivalent (deliberately generous to quantum: a Toffoli in FT costs >> a FLOP)."""
import math
c = 1.8          # |T_{p*}| ~ c/p*  (N30)
W = 32           # wav2vec2 char vocab (blank + letters + apostrophe + separator)
Kdet = 12        # detection loops at the cap (failure <= (5/8)^12 = 3.5e-3)
kappa = 2.0      # M_cap = kappa/sqrt(theta)
def bits(pstar, margin, T, S):
    # abs error of the b-bit forward recursion <= T*S*2^-b (L1 non-amplification), need < (p*-p2)/2
    return math.ceil(math.log2(2*T*S/(pstar*(1-1/margin))))
def C_cell(b, W=W):
    # Munoz-Coreas & Thapliyal 1706.05113: n-bit multiplier T-count 21n^2-14 (Table IV) -> Toffoli-equiv (7T) 3b^2-2
    # + two b-bit additions (Gidney 1709.06648: n Toffoli-equiv each) + one W-way symbol lookup of a b-bit constant (W*b)
    return 3*b*b - 2 + 2*b + W*b
def quantum(pstar, margin, T, D, uncompute=2, G_const=None):
    S = 2*D+1; b = bits(pstar, margin, T, S)
    G = (9 + Kdet*kappa/2)/math.sqrt(pstar) if G_const is None else G_const/math.sqrt(pstar)
    per_oracle = uncompute * T * S * C_cell(b)
    reflect = T*(W + 4*math.ceil(math.log2(W)))    # U, U^dagger (T W-dim rotations) + B; negligible
    return dict(b=b, S=S, G=G, per_oracle=per_oracle, total=G*(per_oracle+reflect), qubits_full=T*S*b,
                qubits_pebble=2*math.ceil(math.sqrt(T))*S*b)
def classical(pstar, T, per_child=3):
    # Graves 2006 sec 3.2 / topk_labellings: each expansion scores W-1 children, each O(T) with ~3 mult-adds per frame
    return c/pstar * (W-1) * T * per_child, c/pstar * T * per_child   # (with children, per-node-only a la N60)
def crossover(margin, T, D):
    S = 2*D+1
    # solve p* = [3c(W-1) / (2 G_const S C_cell(b))]^2 with b depending on p* -> iterate
    p = 1e-6
    for _ in range(50):
        b = bits(p, margin, T, S); p = (3*c*(W-1)/(2*(9+Kdet*kappa/2)*S*C_cell(b)))**2
    return p, b
if __name__ == '__main__':
    print(f"Assumptions: c={c}, W={W}, K_det={Kdet}, kappa={kappa}, G = (9 + K*kappa/2)/sqrt(p*) = {9+Kdet*kappa/2:.0f}/sqrt(p*), uncompute x2, per-cell Toffoli = 3b^2-2+2b+W*b")
    pts = [("10 dB", 1.2e-2, 1.25), ("5 dB", 5.0e-12, 1.12), ("0 dB", 6.0e-18, 1.02)]
    print(f"\n{'point':>6} {'T':>4} {'D':>3} {'b':>3} {'C_cell':>7} {'per-oracle':>10} {'G':>9} {'Q total':>9} {'C (w/ children)':>15} {'speedup':>8} {'C (node-only)':>13} {'speedup2':>9} {'qubits(pebble)':>14}")
    for name, ps, m in pts:
        for T, D in ((100,20),(300,40),(500,60)):
            q = quantum(ps, m, T, D); cl, cl2 = classical(ps, T)
            print(f"{name:>6} {T:>4} {D:>3} {q['b']:>3} {C_cell(q['b']):>7} {q['per_oracle']:>10.2e} {q['G']:>9.2e} {q['total']:>9.2e} {cl:>15.2e} {cl/q['total']:>8.2f} {cl2:>13.2e} {cl2/q['total']:>9.4f} {q['qubits_pebble']:>14.2e}")
    print("\nCrossover p*_x (quantum total == classical with children), T cancels; b solved self-consistently at T=300:")
    for m in (1.02, 1.12, 1.25):
        for D in (20, 40, 60):
            p, b = crossover(m, 300, D); print(f"  margin {m:<5} D={D:<3} -> p*_x = {p:.2e}  (b={b})  speedup at p* = sqrt(p*_x/p*)")
    print("\nSensitivity: G constant 21 -> 9 (no certification) and uncompute x2 -> x1 (oracle without uncompute is not unitary-clean; lower bound only):")
    for name, ps, m in pts:
        q = quantum(ps, m, 300, 40, uncompute=1, G_const=9); cl, _ = classical(ps, 300)
        print(f"  {name:>6}: most-optimistic speedup {cl/q['total']:.2f}x, Q total {q['total']:.2e}")

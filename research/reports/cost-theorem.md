# Worst-case cost of the certified-exact CTC decoder (variant 1c) on peaky tables

Date 2026-09-18. Code, logs: `../code/cost-theorem/` (`a2core.py` harness; `gateA.py`/`gateA5.py`/`gateB.py`/`gateC.py`/`gateD.py`/`gateE.py`/`gateK.py`/`margin.py`/`margin2.py`/`scanC.py`/`scanP.py`, each with a `.log`). The decoder under test is the adversarial-decoder-check report's independent implementation `t9core.decode_exactbwd` (imported read-only; node-for-node identical to the certified-exact-decoder report's per the adversarial-decoder-check report's diff gate). Exact arithmetic (`Fraction`) wherever a statement is a claim about ties or strict inequalities. Nothing outside the working directory was modified (bytecode writes disabled).

## 0. Headline

**Refuted for ρ; proven for Λ = greedy log-loss (equivalently (k, ε·T)); FPT in k; the "count near-modes then apply the adversarial-decoder-check report's bound" route is dead; the top-2 margin is the one candidate not refuted (proven for margin > T, effective at margin 1.3 in experiment).**

1. **No bound f(T, W, ρ) exists** — not for ρ-confidence, not for "k ambiguous frames at threshold ρ", not for "longest ambiguous run at threshold ρ" — for any fixed ρ < 1 and W ≥ 4. The counterexample has **zero** ambiguous frames at threshold ρ: every row is `[ρ, q, …, q]`, q = (1−ρ)/(W−1) (the two decoder reports' peaky generator with blank fraction 1.0 instead of 0.7). Proven (Fraction-exact gates): the mode set is *all* (W−1)(W−2)^{n*−1} no-adjacent-repeat strings of length n*, every proper prefix of every mode of length ≤ n*−2 has B(u) > p* and is therefore expanded, and n* → ∞ with T. Measured: at ρ = 0.8, W = 5 the total generations grow as 8.0·(1/p*)^0.63 (exp_final = 85 / 341 / 2333 at T = 64 / 80 / 96) and exceed 1.5·10⁶ at T = 112.
2. **Theorem 1 (proven, universal, every search).** Final search: `exp ≤ |Pref{l : p(l) ≥ p*/T}| ≤ T(T+1)/p*`. Sub-search (t, c) with L = T−t+1 frames: `exp ≤ |Pref{v : g_v(t) ≥ H_c(t)/(L−1)}| ≤ (L+1)(L−1)·y_t[c]/H_c(t)`. Summed, with P_g := ∏_t max_s y[t][s] (the greedy path's mass): **total generations ≤ (W−1)·[T(T+1) + (W−1)(T³/3 + T²/2)] / P_g = O(W²T³·e^Λ)**, Λ := −ln P_g, and O(W³T⁴·e^Λ) arithmetic. Gates A1–A5, K1–K2: 0 violations.
3. **Corollary (FPT).** If k frames are arbitrary and the other T−k have max ≥ 1−ε: total cost ≤ O(W²T³)·W^k·e^{εT/(1−ε)}. If the T−k frames are exact point masses: every search expands ≤ W^k(T+1) nodes (Gate B). Variant 1c achieves both **automatically** (it never has to know k).
4. **Both parameters are necessary.** k: flat rows on k frames padded with point-mass blanks cost exactly what flat rows on T = k cost, (W−2)^{k/2}·Θ(1) expansions with ε = 0 (Gate D). εT: family 1 has k = 0 and cost exponential in εT.
5. **The count route is dead.** On the alternating family (rows `[0, ρ, 1−ρ]` / `[1, 0, 0]`) the near-mode count N(p*/T) is T^{Θ(log T)} — 8.3·10⁶ at T = 128, ρ = 0.7 — while the decoder expands exactly D = 64 nodes (Gate E). So no theorem of the form "exp ≤ poly(N(p*/T))" is tight, and a polynomial bound on N(p*/T) under any confidence parameter is false even on tables where the decoder is optimal.
6. **Margin (not refuted).** Corollary 1.3 proves margin p*/p₂ > T ⇒ the final search expands ≤ D+1 nodes. Empirically far less is needed: pinning a unique mode in family 1 with margin only 1.3–1.5 (or 1.9–3.6) turns exp_final from 6664 (T = 40, margin 1) into 31 = 1.8·D, and the growth into gen ∝ T^{2.0–2.8} up to T = 80 (§8); the adversarial-decoder-check report's ±10⁻³ noise (margin ≈ 1.001) is below the Lemma-4 slack and still blows up. No family with a constant margin and exponential cost was found; a proof for constant margin is open (§4.4).
7. **Gap.** Proven exponent in 1/p* is 1 (with a T² prefactor); the worst observed is 0.82 (flat rows, the adversarial-decoder-check report) and 0.63–0.75 (family 1, all ρ ∈ [0.5, 0.8]). The the adversarial-decoder-check report exponents 0.08 / 0.17 / 0.31 at conf 0.8 / 0.6 / 0.5 are a property of the 70 %-blank generator (blank runs too short for insertions to pay), not of ρ: `scanP.log` shows exp_final = D exactly iff the largest blank-run "insertion pressure" n_b·q/ρ stays below ≈ 0.8, and 12–430·D once it exceeds 1.

## 1. Setting

Frames 1..T (code is 0-indexed), blank = 0, symbols 1..W−1. p(l) = Σ_{π∈B⁻¹(l)} ∏_t y_t[π_t]. For a prefix u: Ab_u[t], An_u[t] = mass over frames 1..t collapsing to u and ending in the blank-after-u / last-symbol state; ok_d(t) = Ab[t] + [u_last ≠ d]·An[t]; p(u) = Ab[T] + An[T]. For a suffix v with v₁ = c and start frame t: g_v(t) = mass over frames t..T with π_t = c collapsing to v. H_c(t) = max_{v₁ = c} g_v(t).

- **Lemma 1 (decomposition; the certified-exact-decoder report, gated exact by the adversarial-decoder-check report).** p(u·v) = Σ_{t=1}^{T} ok_{v₁}(t−1)·g_v(t).
- **Bound.** B(u) = max(p(u), max_d S_d(u)), S_d(u) := Σ_t ok_d(t−1)·H_d(t). Admissible: B(u) ≥ max_{v} p(u·v) with v = ε allowed.
- **Search** (`best_first`): heap ordered by B; pop; stop if B ≤ incumbent; else expand (generate the W−1 children, update the incumbent with each child's p, push a child iff B(child) > incumbent). Sub-search (t, c): root = (c) with π_t = c forced; same bound over frames t+1..T using the already-exact H(t' > t).
- Cost units: **expansions** (pops that generate children) and **generations** = (W−1)·expansions; each generation costs O(L) for the child and O(W·L) for the bound.

## 2. The parameter (Task 1)

| candidate | verdict | why |
|---|---|---|
| ρ-confidence: max_s y[t][s] ≥ ρ ∀t | **fails** | family 1 (§4.1) is ρ-confident with k = 0 and costs (W−2)^{Ω(n*)}, n* → ∞ |
| k = #frames with max < ρ (fixed ρ < 1) | **fails** | same family, k = 0 |
| longest run of frames with max < ρ | **fails** | same family, run length 0 |
| margin p*/p₂ ≥ 1+δ (constant) | **open — not refuted** | proven only for margin > T (Corollary 1.3); in family 1 a margin of 1.3 already removes the blow-up (§4.4, §8); no constant-margin family with exponential cost found; unlike the others it is not a property of the rows one can read off before decoding |
| **Λ = −ln P_g = −Σ_t ln max_s y[t][s]** (greedy log-loss), equivalently **(k, Σ_{confident t} ε_t)** | **works** | it is the only candidate that lower-bounds p* *and* every conditional suffix mode H_c(t)/y_t[c]; Theorem 1 then gives poly(T, W)·e^Λ, and §4 shows both k and εT are necessary |

Why Λ rather than (k, ε): the bound is monotone in the choice of which frames are called "ambiguous" — W ≥ 1/max_s y[t][s] on every frame, so declaring a frame ambiguous (cost factor W) never beats charging its greedy loss (factor 1/max). Λ is therefore the canonical single parameter; (k, εT) is its FPT reading.

## 3. Theorem 1 — universal upper bound (Tasks 2, 3)

**Lemma 2 (every expanded node is at the mode level).** Let l* be a labelling with p(l*) = p* (any mode). Every node the final search expands has B(u) ≥ p*.
*Proof.* The incumbent is always ≤ p*. If the incumbent is p* when u is popped, B(u) > incumbent = p*. Otherwise no node with p = p* has been generated, so l* has not; then some proper prefix of l* is in the heap: () is pushed initially, and whenever a prefix u′ ⊏ l* is popped it is expanded (B(u′) ≥ p(l*) = p* > incumbent) and its child on l* is pushed (its bound ≥ p* > incumbent). The heap pops its maximum, so B(u) ≥ B(u′) ≥ p*. ∎

**Lemma 3 (the split is loose by at most the number of distinct suffix modes).** If B(u) = S_d(u) > 0, let V = {v_t : t with ok_d(t−1)H_d(t) > 0} be the set of *distinct* argmax suffix strings (v_t attains H_d(t)). Then max_{v∈V} p(u·v) ≥ S_d(u)/|V|, and |V| ≤ n_u ≤ T.
*Proof.* S_d(u) = Σ_{v∈V} Σ_{t: v_t = v} ok_d(t−1)g_v(t) ≤ Σ_{v∈V} p(u·v) by Lemma 1 (dropping terms). ∎

**Theorem 1.** (a) Final search: exp_final ≤ |Pref(𝓛_T)|, 𝓛_F := {l : p(l) ≥ p*/F}, Pref = set of all prefixes (proper or not). Hence exp_final ≤ Σ_{l∈𝓛_T}(|l|+1) ≤ (T+1)·N(T) ≤ (T+1)T/p*. Sharper: exp_final ≤ |Pref(𝓛_m)| with m = max_u |V_u|.
(b) Sub-search (t, c), L = T−t+1: exp_{t,c} ≤ |Pref{v : g_v(t) ≥ H_c(t)/(L−1)}| ≤ (L+1)(L−1)·y_t[c]/H_c(t).
(c) Greedy lower bounds: p* ≥ P_g and H_c(t)/y_t[c] ≥ P_g(t+1..T) := ∏_{s>t} max y_s ≥ P_g. Hence
total expansions ≤ [T(T+1) + (W−1)(T³/3 + T²/2)]/P_g, total generations ≤ (W−1)× that, arithmetic O(W³T⁴/P_g).
*Proof.* (a) By Lemma 2 an expanded u has B(u) ≥ p*. If B(u) = p(u), then u ∈ 𝓛_1 ⊆ 𝓛_T. Else Lemma 3 gives v with p(u·v) ≥ p*/|V| ≥ p*/T, so u ∈ Pref(𝓛_T). Mass counting: Σ_l p(l) ≤ 1 ⇒ N(F) ≤ F/p*. (b) The sub-search is the same algorithm on the suffix problem: objective g_v(t), root (c), start frames t′ ∈ (t, T] (L−1 of them), Σ_v g_v(t) = y_t[c]; Lemmas 2–3 apply verbatim with p* → H_c(t), T → L−1, and suffix strings have ≤ L+1 prefixes. (c) The path "greedy everywhere" collapses to some labelling, so p* ≥ P_g; the path "c at t, greedy after" collapses to a suffix starting with c, so H_c(t) ≥ y_t[c]·P_g(t+1..T). Σ_{L=2}^{T}(L²−1) ≤ T³/3 + T²/2. ∎

**Corollary 1.1 (sub-tables inherit the parameter).** P_g(t+1..T) ≥ P_g, so the per-suffix bound needs nothing beyond the full-table parameter; ρ-peaky sub-tables are ρ-peaky, (k, ε) sub-tables have k_t ≤ k, ε-budget ≤ the full one. This is Task 3: **total cost ≤ T·(W−1)·(per-suffix bound)·O(W·T) + final**, and the per-suffix bound is the *same function* of the suffix table's P_g. It also explains the adversarial-decoder-check report's finding (v) that sub-searches blow up exactly where the final search does.

**Corollary 1.2 (the (k, ε) form).** k arbitrary frames, the rest with max ≥ 1−ε: P_g ≥ (1−ε)^{T−k}·W^{−k} ≥ e^{−ε(T−k)/(1−ε)}·W^{−k}, so total generations ≤ (W−1)[T(T+1) + (W−1)(T³/3 + T²/2)]·W^k·e^{εT/(1−ε)}. Polynomial × W^k whenever εT = O(1). (Gate K: 0 violations of either inequality on 36 tables up to T = 32, W = 5, k ≤ 4.)

**Corollary 1.3 (T-margin ⇒ optimal search).** If every labelling other than the mode has p < p*/T, then exp_final ≤ D+1 (only Pref(l*) qualifies). Same for a sub-search whose runner-up suffix is below H_c(t)/(L−1).

**Gate lines (`gateA.log`, `gateA5.log`, `gateK.log`; brute force = enumeration of all W^T paths in `Fraction`):**
```
GATE A1 exp_final <= |prefixes of labellings with p >= p*/T|: 132 instances (Fraction-exact), violations 0 -> PASS
GATE A2 exp_final <= (T+1)T/p*: 132 instances, violations 0 -> PASS
GATE A3 sub-search exp <= |prefixes of suffixes with g >= H_c(t)/(L-1)|: 2620 sub-searches, violations 0 -> PASS
GATE A4 sub-search exp <= (L+1)(L-1) y_t[c]/H_c(t): 2620 sub-searches, violations 0 -> PASS
GATE A5 every expanded u has a labelling u.v (v a suffix mode) with p >= p*/|V_u| (distinct suffix modes): 227 expanded nodes, violations 0 -> PASS
GATE K1 p* >= P_g >= (1-eps)^(T-k) W^-k: 36 tables, violations 0 -> PASS
GATE K2 total expansions <= (T+1)T/P_g + sum_(t,c) (L+1)(L-1)/P_g(t+1..T): 36 tables, violations 0 -> PASS
```
A1–A4 cover peaky conf ∈ {0.5, 0.6, 0.7, 0.8, 0.9, 0.95}, flat, blank-dominant ρ ∈ {0.5, 0.8}, alternating, random rows; T ∈ {6, 7, 8, 10, 12}, W ∈ {3, 5}. Gate A5 also checks S_d(u) recomputed from the brute-force suffix modes equals the decoder's B(u) on every expanded node.

## 4. Lower bounds and counterexample families

**Lemma 4 (forced expansion on strictly positive tables).** Let all y_t[s] > 0. For any labelling l, any j ≤ |l|−2, u = l_{1..j}, d = l_{j+1}:
B(u) ≥ S_d(u) ≥ p(l) + Ab_u[T−1]·y_T[d] > p(l).
If l is a mode, every prefix u of l with |u| ≤ |l|−2 has B(u) > p* and **is expanded** by the final search.
*Proof.* With v = l_{j+1..|l|}: S_d(u) = Σ_t ok_d(t−1)H_d(t) ≥ Σ_{t≤T−1} ok_d(t−1)g_v(t) + ok_d(T−1)H_d(T). Since |v| ≥ 2, g_v(T) = 0, so the first sum is Σ_{t≤T} ok·g_v = p(l) (Lemma 1); H_d(T) ≥ g_{(d)}(T) = y_T[d]; ok_d(T−1) ≥ Ab_u[T−1] > 0 because |u| ≤ T−2 and all entries are positive. Expansion: the root is expanded (B(()) > p* ≥ incumbent); inductively u's parent (also a prefix of l of length ≤ |l|−2) is expanded, so u is generated and pushed (B(u) > p* ≥ incumbent); the search cannot stop while the heap holds a node with B > p* ≥ incumbent; when u is popped it is expanded. ∎
The slack Ab_u[T−1]·y_T[d] is the quantitative form of the adversarial-decoder-check report's observation that ±10⁻³ noise leaves the flat-row counts unchanged: any l with p(l) > p* − (that slack) has the same forced prefixes.

### 4.1 Family 1 — the tie family (kills ρ, k-at-threshold, run length)

Rows y_t = [ρ, q, …, q], q = (1−ρ)/(W−1), ρ > 1/W, all t. **This is the two decoder reports' peaky generator with blank fraction 1.0.**

- (F1) For strings without adjacent repeats, p(l) = p_{|l|} depends only on |l|: p(l) is a sum over run placements a₁ ≤ b₁ < a₂ ≤ b₂ < … (adjacent runs may touch since consecutive symbols differ) of q^{Σ(b_i−a_i+1)}ρ^{T−Σ}, independent of the symbols.
- (F2) A string with an adjacent repeat is strictly below the no-repeat string of its length: its placements must satisfy b_i + 1 < a_{i+1} at the repeat — a strict subset with the same weights.
- (F3) Hence the mode set is *all* no-repeat strings of length n* = argmax_n p_n: **(W−1)(W−2)^{n*−1} exact ties.**
- (F4) n* → ∞ as T → ∞ at fixed ρ, W. Proof: a placement with m runs has weight ≤ ρ^T(q/ρ)^m (q < ρ) and there are ≤ C(T+m, 2m) placements, so p_m ≤ ρ^T (T+m)^{2m}(q/ρ)^m — polynomial in T for fixed m. But p_n ≥ C(T, n)(q/ρ)^n ρ^T ≥ ρ^T (q/(ρθ))^{θT} for n = ⌊θT⌋, θ < q/ρ — exponential in T. So for every fixed n₀ and large T, p_{⌊θT⌋} > max_{m≤n₀} p_m, i.e. n* > n₀. Numerically n* ≈ T·q/ρ ("insertion pressure", table below).
- (F5) By Lemma 4: **exp_final ≥ Σ_{j=0}^{n*−2} #{no-repeat strings of length j} = 1 + (W−1)((W−2)^{n*−2} − 1)/(W−3) ≥ (W−1)(W−2)^{n*−3}** (W ≥ 4). By Theorem 1 the same instance is also ≤ T(T+1)/p*.

**Gate lines (`gateC.log`, Fraction-exact, 24 tables, W ∈ {3,4,5}, ρ ∈ {0.5, 0.6, 0.7, 0.8}, T ≤ 12):**
```
GATE C1 no-repeat strings of equal length tie exactly; repeat strings strictly below: 24 tables, violations 0 -> PASS
GATE C2 mode set == all (W-1)(W-2)^(n*-1) no-repeat strings of length n*: violations 0 -> PASS
GATE C3 B(u) > p* for every proper prefix of a mode with |u| <= n*-2 (strictness lemma): violations 0 -> PASS
```
(C3 also reports that prefixes of length n*−1 were strictly over-bounded on 23/24 tables — the lemma's |u| ≤ |l|−2 is what is proven, the search in practice expands the length-(n*−1) prefixes too.)

**Growth at larger T (`scanC.log`, float decoder; p* asserted equal to max_n p_n computed by `ctc_forward` on a representative string of every length, and |mode| = n* on every row):**

| W | ρ | T | n* = D | ties | exp_final | LB (F5, ≤ n*−2) | LB (≤ n*−1) | gen | 1/p* | T·q/ρ |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 5 | 0.8 | 48 | 3 | 36 | 21 | 5 | 17 | 2 628 | 8.9e3 | 3.0 |
| 5 | 0.8 | 64 | 4 | 108 | 85 | 17 | 53 | 14 164 | 1.3e5 | 4.0 |
| 5 | 0.8 | 80 | 5 | 324 | 341 | 53 | 161 | 66 916 | 1.8e6 | 5.0 |
| 5 | 0.8 | 96 | 6 | 972 | 2 333 | 161 | 485 | 323 252 | 2.5e7 | 6.0 |
| 5 | 0.8 | 112 | 7 | 2 916 | — | 485 | 1 457 | > 1.5e6 (cap) | — | 7.0 |
| 4 | 0.8 | 64 | 5 | 48 | 169 | 22 | 46 | 14 547 | 3.5e4 | 5.3 |
| 4 | 0.8 | 96 | 7 | 192 | 4 789 | 94 | 190 | 330 717 | 3.4e6 | 8.0 |
| 4 | 0.7 | 64 | 8 | 384 | 7 537 | 190 | 382 | 327 774 | 3.7e6 | 9.1 |
| 4 | 0.6 | 56 | 11 | 3 072 | 41 884 | 1 534 | 3 070 | 1 334 109 | 3.2e7 | 12.4 |
| 4 | 0.5 | 40 | 11 | 3 072 | 13 846 | 1 534 | 3 070 | 410 187 | 4.3e6 | 13.3 |

Fits over rows with n* ≥ 2 and 1/p* ≥ 30 (`scanC.log`): gen = A·(1/p*)^α with **α = 0.75 / 0.70 / 0.73 / 0.73 (W = 4, ρ = 0.5 / 0.6 / 0.7 / 0.8) and 0.74 / 0.69 / 0.65 / 0.63 (W = 5)**; exp_final/LB(≤ n*−1) ∈ [1.00, 25]. So (i) the proven tie-prefix lower bound is attained (ratio 1.00 at small T) and (ii) the actual cost grows faster than the tie count — prefixes of near-modes of length n*±1 are expanded too — with an exponent in 1/p* that is *independent of ρ*. Raising ρ only rescales T (via T·q/ρ); it does not change the class.

**Consequence for the peaky generator (`scanP.log`, W = 5, T ∈ {32, 48, 64}, 2 seeds each).** The 70 %-blank generator's blank runs are geometric with mean ≈ 3.3, so the largest run's insertion pressure n_b·q/ρ is < 1 at conf ≥ 0.7 and the greedy collapse is the mode: exp_final/D = 1.00 on 11/12 cells at conf ≥ 0.8 (max 1.18), 1.0–2.4 at conf 0.7 (pressure 0.64–0.96). At conf ≤ 0.6 the pressure crosses 1 on most seeds and the mode stops being the greedy collapse (mode ≠ greedy on 9 of the 10 finished cells at conf 0.5–0.55); exp_final/D is 18–430 on every cell with pressure > 1 at conf ≤ 0.55 (430·D at conf 0.5, T = 48, pressure 2.0; both T = 64 cells capped at 6·10⁵ generations) and 1.0 on the single such cell with pressure 0.82. the adversarial-decoder-check report's "α interpolates with confidence" is this threshold crossing, sampled at three points of ρ; it is not a smooth law in ρ.

### 4.2 Family 2 — padded flat rows (k is necessary; ε = 0)

k flat frames [1/W]^W followed by T−k point-mass blank frames. Zero deviation mass outside the k frames (ε = 0, Λ_conf = 0), so Corollary 1.2 gives ≤ poly·W^k. Measured (`gateD.log`): the padded table's final search expands **exactly** what the flat table on T = k expands — 22 / 46 / 94 / 190 at W = 4, k = 8 / 10 / 12 / 14 and 53 / 161 / 485 at W = 5, k = 8 / 10 / 12 — the adversarial-decoder-check report's (W−2)^{k/2}·Θ(1) law, with identical generation counts.
```
GATE D padded-flat exp_final == flat exp_final at T=k: 7 cells, mismatches 0 -> PASS
```
So the k-dependence is exponential in both directions, with base between √(W−2) (this family) and W (Corollary 1.2).

### 4.3 Family 3 — alternating rows (the count route is dead)

Odd frames [0, ρ, 1−ρ, 0…], even frames point-mass blank. Labellings = {1,2}^{T/2}, p = ρ^{#1}(1−ρ)^{#2}, mode = 1^{T/2}. N(p*/T) = Σ_{b ≤ log_R T} C(T/2, b), R = ρ/(1−ρ): **quasi-polynomial**, T^{Θ(log T / log R)}. The decoder expands exactly D = T/2 nodes because ok_d(t−1) is non-zero at a single frame for every prefix (each symbol's frame is forced), so B(u) = max_v p(u·v) exactly (`gateE.log`):

| ρ | T | D | exp_final | N(p*/T) | the adversarial-decoder-check report-bound |Pref(𝓛_T)| (brute, T ≤ 12) |
|--:|--:|--:|--:|--:|--:|
| 0.7 | 12 | 6 | 6 | 22 | 63 |
| 0.7 | 64 | 32 | 32 | 41 449 | — |
| 0.7 | 128 | 64 | 64 | 8 303 633 | — |
| 0.8 | 128 | 64 | 64 | 43 745 | — |
```
GATE E brute-force N(p*/T) and p* agree with the closed form at T<=12: mismatches 0 -> PASS
```
Therefore: (i) Task 2's target — "on ρ-peaky tables N(p*/F) ≤ poly(T, W, F)·h(ρ)" — is **false**: here for F = T on a table where every frame is ρ-confident and the decoder is optimal, and in family 1 already for F = 1 (N(1) = (W−1)(W−2)^{n*−1} exact ties); (ii) any bound obtained by multiplying the adversarial-decoder-check report's prefix-count bound by a near-mode count is off by 10⁵ here, so the count route cannot produce a tight theorem; (iii) N(F) ≤ F/p* (mass counting) is the only universally valid count and Theorem 1 already uses it.

### 4.4 Margin

Two experiments. (a) Symmetric boost of symbols 1 and 2 in family 1 (`margin.log`, Fraction-exact, T ≤ 10): the mode stays a 2-way tie (1212… / 2121…, margin 1); N(p*/2) falls from 57 to 6 as the boost grows while exp_final does not fall (10 → 11). So the count within a constant factor is not what drives the cost — an exact tie of *two* modes plus their near-modes suffices, as Lemma 4 predicts. (b) Unique mode (`margin2.log`): symbol c boosted by (1+δ)^{W−1−c} in every frame and symbol 1 by ×10 in frame 0; the margin is *upper*-bounded by p*/p(best single-edit candidate) via `ctc_forward`, and exact by brute force at T = 10 (1.32 / 1.16 / 1.23 on the three δ > 0 rows there). Result (§8): at margin 1 the cost grows as before (exp_final 4 → 6664 from T = 10 to 40 at W = 4, ρ = 0.5); at margin ≈ 1.4–1.5 (δ = 1) it is 5 → 169 from T = 10 to 80, ≈ 1–5·D, with gen 5 037 → 35 538 from T = 40 to 80 (∝ T^{2.8}); at margin ≈ 1.9 (δ = 3, W = 4) 4 → 45, gen 2 757 → 13 368 (∝ T^{2.3}); at W = 5, ρ = 0.6 the same (margin 1.4–1.5: ×7.0 from T = 40 to 80, T^{2.8}; margin 3.6: ×4.0, T^{2.0}). The transition therefore sits between margin 1.001 (the adversarial-decoder-check report's noisy flat rows, still exponential) and 1.3. I could not prove a constant-margin bound: Lemma 3 only yields |V_u| ≥ M distinct suffix modes per off-mode expansion, and V_u can have ~n* members (the truncations 1212…), so the proof would need Σ_{v∈V_u} p(u·v) < p* for every off-mode u, a statement about how the suffix-mode masses decay with the truncation length. That is the concrete open lemma.

## 5. Theorem statement (Task 4)

**Theorem (proven).** Let y be a T×W CTC table, P_g = ∏_t max_s y_t[s], Λ = −ln P_g. The certified-exact decoder (variant 1c: T·(W−1) backward best-first sub-searches with the exact later suffix modes, then one forward best-first search with B) performs at most
  **(W−1)·[T(T+1) + (W−1)(T³/3 + T²/2)] · e^Λ**
node generations, each O(W·T) arithmetic, i.e. O(W³T⁴·e^Λ) operations; the final search alone expands ≤ T(T+1)/p* nodes and, more finely, ≤ |Pref{l : p(l) ≥ p*/m}| with m the largest number of distinct suffix modes any node's bound sums over. In the (k, ε) reading — k arbitrary frames, all others with max ≥ 1−ε — the bound is O(W²T³)·W^k·e^{εT/(1−ε)}.

**Necessity.** (i) The dependence on k cannot be removed: with ε = 0 the cost is ≥ (W−2)^{k/2−O(1)} (family 2). (ii) The dependence on εT cannot be removed: with k = 0 the cost is ≥ (W−1)(W−2)^{n*−3} with n* → ∞ linearly in εT/(W−1) (family 1), and measured ∝ (1/p*)^{0.63–0.75}. (iii) No parameter among {ρ-confidence, #frames below ρ, longest run below ρ} admits any bound f(T, W, param): family 1 has the best possible value of each and exponential cost. The top-2 margin is the exception: proven sufficient only above T, empirically sufficient at 1.3 (§4.4, §8), and no counterexample found.

**Gap (stated exactly).** Upper exponent in 1/p* is 1 (Theorem 1); the largest observed is 0.82 (flat rows, the adversarial-decoder-check report's fit, W = 5) / 0.73–0.75 (family 1). Whether some family reaches exponent 1 − o(1), or whether T²·(1/p*)^{c} with c < 1 is provable, is open; Lemma 3 shows the only source of looseness is the number m of distinct suffix modes summed in one bound, so a proof of c < 1 must bound m·N(p*/m) below T/p*, which fails on flat rows (there N(1)·p* is a constant fraction of the mass). Fitted exponents for the record: the adversarial-decoder-check report's 70 %-blank peaky generator (W = 5) α = 0.08 (conf 0.8), 0.17 (0.6), 0.31 (0.5); uniform-random rows 0.24 (W=5), 0.15 (W=8); flat 0.71–0.82; family 1 here 0.63–0.75 at every ρ ∈ {0.5, 0.6, 0.7, 0.8}, W ∈ {4, 5}. The T²W² law of the certified-exact-decoder report is the Theorem-1 prefactor at P_g ≈ 1 with the D-dependence absorbed: on the 70 real posteriors P_g is far below 1 (p* down to 10⁻²⁶) yet the cost is 0.002–0.5·T²W² — those tables sit in the regime "mode = greedy collapse, insertion pressure ≪ 1" where Lemma 3's m is O(1) and the near-mode trie is O(D) (the certified-exact-decoder report's exp_final = 1–58·D), which is exactly what Theorem 1 cannot see and what §4.1 shows is not a consequence of ρ.

## 6. FPT bonus (Task 5)

**Theorem 3 (strict).** Let k₀ = #frames whose row is not a point mass. (i) At most W^{k₀} labellings have p > 0 — each is the collapse of a path that agrees with every point-mass frame, and there are W^{k₀} such paths; the repeat-collapse changes nothing because the collapse is a function of the path (the hardness-attempt report's Lemma 3 argument goes through verbatim for full CTC). (ii) Variant 1c pushes a node only if B > incumbent ≥ 0, and B(u) > 0 implies some p(u·v) > 0 (B = p(u) > 0, or a term ok_d(t−1)·g_{v_t}(t) > 0 which is ≤ p(u·v_t)). So every expanded node, in every search, is a prefix of a positive-probability labelling (or suffix): **≤ W^{k₀}(T+1) expansions per search, ≤ (T(W−1)+1)·W^{k₀}(T+1) in total, O(W^{k₀+3}T³) arithmetic — without knowing k₀**. Versus the hardness-attempt report's O((|Σ|+1)^k·T²) for SUBSEQ-MODE by explicit enumeration: same parameter, same base (W = |Σ|+1), one extra factor T·W from the backward pass.
```
GATE B1 #positive-probability labellings <= W^k: 75 instances, violations 0 -> PASS
GATE B2 every search exp <= W^k (T+1): 75 instances, violations 0 -> PASS
GATE B3 every expanded final-search node is a prefix of a positive-probability labelling: violations 0 -> PASS
```
(k ∈ {0,…,4}, W ∈ {3, 4}, T ∈ {8, 10, 12}, exact brute force; e.g. W = 3, T = 12, k = 4: 23 positive labellings ≤ 81, exp_total = 17 ≤ 26 325.)

**ε-relaxation.** the hardness-attempt report remarked that "max mass ≥ 1−ε" does not give FPT by the enumeration argument. Sharpened here: full CTC decoding by 1c **is** FPT in the pair (k, εT) (Corollary 1.2, cost ≤ poly·W^k·e^{εT/(1−ε)}) and **is not** bounded by any f(k)·poly(T, W) at fixed ε (family 1: k = 0, cost exponential in εT). This is a statement about the decoder's cost, not about the problem: family 1's mode is found by symmetry in O(T) time, so no hardness for k = 0 is claimed.

## 7. What this changes for the quantum-costing thread

The honest classical exact count is now a theorem, not a fit: **≤ O(W²T³)/P_g generations**, and on the tie family Ω((W−2)^{n*}) with n* ≈ T·q/ρ. Against 1/√p*-type finding costs the comparison must be made per regime: on real/peaky posteriors (mode = greedy collapse, insertion pressure ≪ 1) the measured 0.002–0.5·T²W² stands and is polynomial in practice, but it is not implied by any confidence level; the provable statement in terms of the table is e^Λ·poly, which is exactly the c/p* class with a T² prefactor.

## 8. Appendix — margin at larger T (`margin2.log`)

Family 1 rows [ρ, q, …, q] with symbol c multiplied by (1+δ)^{W−1−c} in every frame (renormalised) and symbol 1 by ×10 in frame 0. Margin column = p*/max over single-edit candidates of p(candidate) (an upper bound on the true margin; exact at T = 10 by brute force, where the true margins are 1.32 / 1.16 / 1.32 / 1.23 for the δ > 0 rows). p* of every row checked against `ctc_forward` on the returned mode. Selected rows (full log: `../code/cost-theorem/margin2.log`):

| W | ρ | δ | T | D | margin ≤ | exp_final | gen | 1/p* |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 4 | 0.5 | 0 | 40 | 11 | 1 | 6 664 | 388 641 | 2.9e6 |
| 4 | 0.5 | 1 | 40 | 17 | 1.50 | 31 | 5 037 | 1.2e5 |
| 4 | 0.5 | 1 | 80 | 35 | 1.44 | 169 | 35 538 | 5.1e9 |
| 4 | 0.5 | 3 | 40 | 15 | 1.91 | 16 | 2 757 | 825 |
| 4 | 0.5 | 3 | 80 | 29 | 1.91 | 45 | 13 368 | 2.0e5 |
| 5 | 0.6 | 0 | 48 | 8 | 1 | 5 629 | 819 428 | 4.5e7 |
| 5 | 0.6 | 1 | 48 | 21 | 1.45 | 42 | 14 232 | 1.0e7 |
| 5 | 0.6 | 1 | 80 | 35 | 1.44 | 169 | 62 768 | 2.4e11 |
| 5 | 0.6 | 3 | 80 | 27 | 3.58 | 31 | 19 412 | 2.8e4 |

At margin 1 the cost is exponential in T (family 1); at margin ≥ 1.3 it is ≈ 1–5·D expansions and gen ∝ T^{2.0–2.8} (T = 40 → 80), including at 1/p* = 2.4·10¹¹. Note that at δ = 1 the 1/p* values are *larger* than at δ = 0 for the same T (the boosted table has longer modes), so the tamed cost is not a p* effect.

## 9. File index

- `../code/cost-theorem/a2core.py` — families (`fam_blankdom`, `fam_flat`, `fam_alt`, `fam_padded_flat`, `fam_strict_k`, `fam_peaky`), exact helpers (`near_mode_prefix_count`, `norepeat_count`, `greedy_mass`).
- `../code/cost-theorem/gateA.py` → `gateA.log` (Theorem 1 a, b, mass forms); `gateA5.py` → `gateA5.log` (distinct-suffix-mode form); `gateK.py` → `gateK.log` ((k, ε) form, total bound).
- `../code/cost-theorem/gateB.py` → `gateB.log` (Theorem 3); `gateC.py` → `gateC.log` (family 1 lemmas F1–F3, Lemma 4); `gateD.py` → `gateD.log` (family 2); `gateE.py` → `gateE.log` (family 3).
- `../code/cost-theorem/scanC.py` → `scanC.log` (family 1 growth and α fits); `scanP.py` → `scanP.log` (peaky-generator pressure table); `margin.py`/`margin2.py` → logs (margin).

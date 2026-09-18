# The margin lemma for the certified-exact CTC decoder (variant 1c)

Date 2026-09-18. Code, logs: `../code/margin-lemma/` (`r1core.py` harness on top of the adversarial-decoder-check report's `t9core.py`, imported read-only; `gate1.py`→`gate1.log`, `gate2.py`→`gate2.log`, `scan1.py`→`scan1.log`, `scan2.py`→`scan2_w3.log`/`scan2_w4.log`, `scan3.py`→`scan3.log`, `hunt.py`→`hunt.log`, `hunt2.py`→`hunt2_R.log`/`hunt2_off.log`, `real_run.py`→`real_run_a.log`/`real_run_b.log`, `real_rows.py`→`real_rows.log`). Every statement about ties, strict inequalities or a margin is checked in `fractions.Fraction`; float runs are gated against the Fraction pipeline (gate S1). No other directory was modified (bytecode writes disabled).

## 0. Headline — LEMMA + GAP

**Proven (Theorem A).** Let K be the number of distinct suffix-mode strings per symbol that the backward pass returns (K = max_d |{v_{d,t} : t}| ≤ T; computed for free by the decoder, before the final search). If the top-2 margin m = p*/p₂ exceeds K, the final search expands exactly the D proper prefixes of the mode (plus the mode itself iff B(l*) > p*): **exp_final ∈ {D, D+1}**. The same holds for every backward sub-search with its own margin and K. This replaces Corollary 1.3's "margin > T". On real posteriors K = D+1 (measured on four T = 112, W = 32 tables), so the a-priori certificate reads **margin > D+1**; it fires on 4 of the 70 certified real tables (margins 30.9, 82, 333, 718).

**Exact per-node form (Theorem A′).** An off-path prefix u is expanded only if its over-approximation ratio R_d(u) := S_d(u)/max_{v∈V_u} p(u·v) satisfies **R_d(u) ≥ m**, where V_u is the set of distinct suffix modes over u's support. R_d(u) ≤ K_eff(u) ≤ K_u ≤ K. So the margin lemma is equivalent to a bound on R over expanded nodes, and "straddle" over-approximation is bounded by K_u, never larger.

**Refuted / withdrawn.** (i) Per-frame margin and ρ-confidence are dead as hypotheses (cost-theorem family 1: per-frame margin ρ/q arbitrary, top-2 margin 1, exponential cost). (ii) the cost-theorem report §8's evidence that "margin 1.3–3.6 tames family 1" is **withdrawn**: the true margins of that family (exact second-best search, this report) are **1.00–1.25 and oscillate with T**; its W = 3, δ = 3 variant has margin 1.03–1.11 and still blows up to exp_final/D = 616, gen/T² = 77 at T = 80. The taming in the cost-theorem report came from the symbol asymmetry (polynomially many near-modes), not from the margin. (iii) The strong conjecture "exp_final ≤ f(m)·D" is **not refuted**: in ≈ 2 300 tables (three structured families, two adversarial hill-climbs at T ≤ 20, four real tables) **no table with margin ≥ 2.1 has a single off-path expansion**, and none with margin ≥ 1.5 has exp_final > 1.75·D.

**The gap (exact).** Define R_max(T,W) := sup over tables and over expanded off-path nodes of R_d(u). Proven: R_max ≤ K ≤ T. Measured: R_max ≤ 3.4 up to T = 80 (blank-dominant grid maxima 1.66 / 1.85 / 2.01 / 2.25 / 2.47 at T = 16 / 24 / 32 / 48 / 64; adversarial maxima 2.3 / 3.1 / 3.0 / 2.8 at T = 10 / 12 / 16 / 20; peaky conf 0.5 reaches 3.10 at T = 48 and 3.42 at T = 64, always at margin ≤ 1.02). If R_max were bounded by a constant c₀ (≈ 3–4), the margin lemma would be **"margin > c₀ ⇒ exp_final ≤ D+1"** for all T, which is exactly what every experiment shows (no off-path expansion at margin ≥ 2.1). The open lemma is stated in §5 as a lower bound on max_s Σ_t λ_t·M[s][t] for the suffix-mode overlap matrix M; the tie family is where R grows (R − 1 ∝ T^{0.45} in the grid maxima), and it is also where the margin is forced to 1 + O(1/D) — the two hypotheses of a counterexample pull against each other, but I could not turn that into a proof.

## 1. Setting and the conjecture, stated precisely

Frames 1..T, blank = 0, symbols 1..W−1. p(l) = Σ_{π∈B⁻¹(l)} ∏_t y_t[π_t]; p* = max, p₂ = second-largest value, m = p*/p₂; m > 1 ⇔ the mode l* is unique; D = |l*|. For a prefix u: ok_d(t−1) = mass over frames < t collapsing to u in a state that lets d start fresh at t; for a suffix v with v₁ = d: g_v(t) = mass over frames t..T with π_t = d collapsing to v; H_d(t) = max_v g_v(t) with argmax string v_{d,t} (the string returned by sub-search (t,d)). Lemma 1 (the certified-exact-decoder report, gated exact by the adversarial-decoder-check report): p(u·v) = Σ_t ok_{v₁}(t−1)·g_v(t). Bound B(u) = max(p(u), max_d S_d(u)), S_d(u) = Σ_t ok_d(t−1)·H_d(t). Search = best-first on B, terminate when top B ≤ incumbent.

**Three candidate shapes for the hypothesis.**

| shape | verdict |
|---|---|
| per-frame margin (max_s y_t[s] ≥ m·second) | **dead** — cost-theorem family 1 has it for any m and exponential cost with p*/p₂ = 1 |
| "gap" condition on every off-path prefix bound: B(u) < p* for all u ⊄ l* | tautologically equivalent to "the final search expands D+1 nodes"; its content is Theorem A′: B(u) < p* ⇔ R_d(u) < p*/max_v p(u·v), which the margin implies when R_d(u) < m |
| top-2 margin m = p*/p₂ | the right object; **the weakest hypothesis under which the proof goes through is m > max over off-path u of R_d(u)**, and the a-priori (table-level) version is m > K |

**Conjecture C1 (strong, the cost-theorem report §6).** m > 1 ⇒ exp_final ≤ f(m, W)·D. Status: open, not refuted; every measurement is consistent with f ≡ 1 for m ≥ 2.1 (§4).
**Conjecture C0 (constant-R).** R_max(T, W) ≤ c₀ for a universal c₀ (≈ 3–4). C0 ⇒ "m > c₀ ⇒ exp_final ≤ D+1" ⇒ C1 for m > c₀. Status: open; proven only c₀ ≤ T (Lemma 3 of the cost-theorem report).
**What is proven:** C1 with f ≡ 1 for m > K (Theorem A), and the per-node characterisation (Theorem A′).

## 2. Theorems and proofs

**Lemma 1 (expansions; the cost-theorem report Lemma 2 sharpened).** Assume m > 1. Every expanded node has B(u) ≥ p*. Every proper prefix of l* is expanded; l* itself is expanded iff B(l*) > p*. Hence exp_final ≥ D and exp_final − (D + [B(l*) > p*]) = number of expanded off-path nodes =: n_off.
*Proof.* B(u) ≥ p* for expanded u is the cost-theorem report Lemma 2. The mode is generated only when its parent is expanded; before that the incumbent is < p* (unique mode), so a proper prefix u ⊏ l* popped at that time has B(u) ≥ p(l*) = p* > incumbent and is expanded; and u is popped before l* is generated because l*'s parent is u or a not-yet-generated descendant of u. The heap holds a prefix of l* until l* is generated, so the search cannot stop earlier. After l* is generated the incumbent is p* and l* is expanded iff B(l*) > p*. ∎

**Lemma 2 (the cost-theorem report Lemma 3, restated).** For any u and d, with V_u := {v_{d,t} : ok_d(t−1)·H_d(t) > 0} (distinct strings) and K_u := |V_u|: S_d(u) ≤ Σ_{v∈V_u} p(u·v) ≤ K_u·max_{v∈V_u} p(u·v). (Group the terms of S_d(u) by the string v_{d,t} and drop terms from Lemma 1.) ∎

**Theorem A (K-margin).** Let K_d := |{v_{d,t} : 1 ≤ t ≤ T, H_d(t) > 0}| and K := max_d K_d. If m > K then n_off = 0, i.e. exp_final = D + [B(l*) > p*] ∈ {D, D+1}.
**Theorem A′ (per node).** If m > 1 and an off-path u is expanded, then for the d attaining B(u) = S_d(u): (i) K_u ≥ m; (ii) Σ_{v∈V_u} p(u·v) ≥ p*; (iii) max_{v∈V_u} p(u·v) ≥ p*/K_u; (iv) R_d(u) := S_d(u)/max_{v∈V_u} p(u·v) ≥ m.
*Proof.* Off-path u expanded ⇒ B(u) ≥ p* (Lemma 1). If B(u) = p(u) then p(u) ≥ p*, so u is a mode, so u = l* (unique) — but l* is on-path. Hence B(u) = S_d(u) ≥ p* for some d. Every completion u·v with v ∈ V_u is a labelling ≠ l* (l* does not have prefix u), so p(u·v) ≤ p₂ = p*/m. By Lemma 2: p* ≤ S_d(u) ≤ Σ_{v∈V_u} p(u·v) ≤ K_u·p*/m, giving (i)–(iii); (iv) is S_d(u) ≥ p* ≥ m·max_v p(u·v). Theorem A: K_u ≤ K_d ≤ K < m contradicts (i). ∎
*Remarks.* (a) V_u is defined with the argmax strings the decoder's own sub-searches return; the proof holds for any choice of argmax per (d,t), so ties in H do not matter. (b) K is a property of the backward pass, available before the final search: the certificate "exp_final ≤ D+1" is free. (c) K ≤ T always; K = D+1 on the real tables (§4.5), K ≈ 0.2–0.45·T on blank-dominant families (§4.1–4.2), where the suffix modes are the truncations of one alternating string.

**Theorem A (sub-searches).** For sub-search (t,c) — objective g_v(t) over suffixes v with v₁ = c, mode value H_c(t), string v_{c,t}, runner-up H′_c(t), margin μ_{c,t} = H_c(t)/H′_c(t), K^{(>t)} := max_d |{v_{d,t′} : t′ > t}| — if μ_{c,t} > K^{(>t)} the sub-search expands ≤ |v_{c,t}| + 1 nodes, and the per-node statements hold with (p*, l*, m) → (H_c(t), v_{c,t}, μ_{c,t}). *Proof:* verbatim; the sub-search is the same algorithm on the suffix problem with the root's first frame forced and the bound reading only H(t′ > t). ∎

**Theorem B (margin-weighted count).** Under margin m, the number of off-path expansions at depth j is ≤ (2/m)·(N_{2K} − 1) with N_F := #{l : p(l) ≥ p*/F}, and also ≤ 2(1−p*)/p*; hence exp_final ≤ D + 1 + (T+1)·(2/m)·(N_{2K} − 1).
*Proof.* For an expanded off-path u, Σ_{v∈V_u} p(u·v) ≥ p* (A′ ii). The v with p(u·v) < p*/(2K_u) contribute < K_u·p*/(2K_u) = p*/2, so the completions with p(u·v) ≥ p*/(2K_u) ≥ p*/(2K) carry ≥ p*/2; they are near-modes at threshold 2K and ≠ l*, so each has mass ≤ p*/m. Distinct u at the same depth have disjoint completion sets. Summing over the n_j expanded off-path u at depth j: n_j·p*/2 ≤ Σ_{l∈𝓛_{2K}\{l*}} p(l) ≤ (N_{2K} − 1)·p*/m, and ≤ 1 − p*. ∎
(This is Theorem 1 of the cost-theorem report improved by the factor 2/m at a threshold 2K ≤ 2T; it is stated for completeness — the per-node Theorem A′ is what matters.)

**Proposition D (the "straddle" phenomenon is bounded by K_u).** For every node, B(u) ≤ max(p(u), K_u·max_v p(u·v)) ≤ T·max_v p(u·v). So "huge B(u) from split-frame ambiguity with poor completions" is impossible beyond a factor K_u ≤ T, and under margin m an off-path node is expanded only if its over-approximation R_d(u) is at least m. Measured R_d(u) on expanded off-path nodes never exceeded 3.5 in any experiment (§4.6), including tables with K_u = 34 and supports of 102 frames.

**Gate lines (Fraction-exact; `gate1.log`, `gate2.log`):**
```
GATE G1a instrumented pipeline == t9core.decode_exactbwd (mode, p*, exp_final, gen_back, gen): 78 checks, violations 0 -> PASS
GATE G1b brute-force (Fraction) p*, p2 == decoder p*, second_best p2 (T<=10): 66 checks, violations 0 -> PASS
GATE G1c Lemma 3 on every expanded node: S_d(u) <= sum_{v in V_u} p(u.v), B(u) == max(p(u), S_d(u)): 341 checks, violations 0 -> PASS
GATE G1d Theorem A per node: off-path expanded u has sum_{V_u} p(u.v) >= p*, K_u >= margin, max_v p(u.v) >= p*/K_u: 79 checks, violations 0 -> PASS
GATE G1e Theorem A a priori: margin > K  =>  no off-path expansion and exp_final <= D+1: 78 checks, violations 0 -> PASS
GATE G1f enumerate_above(p*/2K) == brute-force near-mode set (T<=10): 66 checks, violations 0 -> PASS
GATE G1g Theorem B per depth: #off-path expanded at depth j <= (2/m)(N(p*/2K)-1): 62 checks, violations 0 -> PASS
GATE G2a sub-search runner-up H'_c(t) == brute-force second-largest g_v(t) (T<=8): 350 cells, violations 0 -> PASS
GATE G2b sub-search Theorem A per node (K_u >= mu, sum_{V_u} g(u.v) >= H_c(t)): 122 off-path nodes, violations 0 -> PASS
GATE G2c sub-search Theorem A a priori (mu > K_(>t) => exp <= |v|+1): 900 sub-searches (461 with mu > K), violations 0 -> PASS
GATE S1 float pipeline == Fraction pipeline (mode, exp_final, n_off, margin to 1e-9) at T<=24: 48 cells, violations 0 -> PASS
```
G1 covers random, peaky (conf 0.6/0.8), blank-dominant, the cost-theorem report's pinned family, a two-rate family and the alternating family at T ∈ {6,8,10} (brute force) and T ∈ {14,18} (exact search only), W ∈ {3,4,5}. The exact runner-up p₂ is computed by the same admissible best-first search with the mode excluded from the incumbent (`second_best`; admissible because B(u) ≥ max over all completions ≥ max over completions ≠ l*); G1b checks it against brute force.

## 3. Correction to the cost-theorem report §4.4 / §8 (the "margin 1.3–1.5" family)

the cost-theorem report's margin column was an upper bound p*/max over single-edit candidates. The true margin (exact second-best search; `scan1.log`, exact at T ≤ 24, float gated by S1 beyond) of the same tables:

| family (cost-theorem margin2) | T=10 | 14 | 18 | 24 | 32 | 40 | 48 | 56 | 64 | 80 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| W=4 ρ=0.5 δ=1 — the cost-theorem report said "≤ 1.44–1.50" — true m | 1.32 | 1.10 | 1.10 | 1.19 | 1.07 | 1.23 | 1.15 | **1.006** | 1.10 | 1.04 |
| … exp_final / D / n_off | 5/5/0 | 8/7/1 | 11/7/3 | 15/11/4 | 24/13/10 | 31/17/13 | 42/21/20 | 76/25/50 | 103/27/75 | 169/35/133 |
| W=4 ρ=0.5 δ=3 — the cost-theorem report "≤ 1.91" — true m | 1.16 | 1.48 | 1.25 | 1.21 | 1.11 | 1.05 | 1.13 | 1.01 | 1.08 | 1.03 |
| W=5 ρ=0.6 δ=3 — the cost-theorem report "≤ 3.58" — true m | 1.23 | 1.55 | 1.13 | 1.10 | 1.20 | 1.04 | 1.06 | 1.10 | 1.02 | 1.06 |
| W=3 ρ=0.5 δ=3 (new) — true m | 1.20 | 1.16 | 1.04 | 1.13 | 1.07 | 1.02 | 1.08 | 1.11 | 1.06 | 1.03 |
| … exp_final / D | 4/3 | 8/4 | 16/5 | 36/6 | 70/8 | 235/9 | 503/11 | 881/13 | 2381/15 | **11087/18** |

The runner-up is always a length neighbour of the mode (`l2` column in the log: the mode with one symbol dropped or added). Mechanism (heuristic, not needed for any theorem): in a blank-dominant table the mass of the k-th truncation of the alternating string behaves like a Poisson-type sequence with alternating rates μ₁, μ₂; the margin over the two length neighbours is min(μ₁φ/(k*+1), (k*+1)/(μ₂φ)) ≤ √(μ₁/μ₂), and where k*+1 sits in [μ₂φ, μ₁φ] oscillates with T — which is the observed 1.0–1.25 sawtooth. So the cost-theorem report's family is not a constant-margin family, its cost at T = 80 is D·(1.2–5) at W ≥ 4 only because the symbol asymmetry makes the near-mode trie polynomial, and at W = 3 (no third symbol to make substitutions costly) the same margin band gives exp/D = 616 and gen ∝ T^{5.7} (T = 64 → 80: ×4.7). Everything in the cost-theorem report's §4.4(b)/§8 that reads "margin ≈ 1.4–3.6" should read "margin 1.0–1.25 (oscillating)".

## 4. Measurements — expansions/D and generations/T² versus the true margin

All margins are exact (second-best search); "band m ≥ x" = all grid cells with true margin ≥ x; the statistic reported is the **maximum** over the band, which is what a margin lemma must control. exp/D = exp_final/D; n_off = off-path expansions; R = max over expanded off-path nodes of R_d(u).

### 4.1 Structured grid — rates family (`scan2_w3.log`, `scan2_w4.log`)
Rows [ρ, A·q, B·q, q, …] renormalised, symbol 1 ×10 at frame 0; ρ ∈ {0.4,…,0.8}, A ∈ {1.5,…,32}, B ∈ {1,…,8}, B ≤ A: 275 cells per (T, W). The largest margin the family reaches decays with T (1.65 → 1.54 → 1.37 → 1.25 → 1.24 at T = 16 → 64), as §3 explains.

| T | W | band m ≥ 1.0 (all): max exp/D, n_off, gen/T², R | m ≥ 1.05 | m ≥ 1.1 | m ≥ 1.2 | m ≥ 1.3 | m ≥ 1.5 |
|--:|--:|---|---|---|---|---|---|
| 16 | 4 | 6.67, 34, 4.7, 1.66 | 5.00, 16, 3.1 | 5.00, 16, 3.1 | 2.50, 6, 2.3 | 2.00, 5, 2.2 | **1.00, 0**, 2.0 (11 cells) |
| 24 | 4 | 40.4, 354, 17.9, 1.85 | 19.3, 110, 9.5 | 19.3, 110, 9.5 | 5.11, 36, 4.1 | 1.78, 6, 2.5 | **1.09, 0**, 2.1 (1 cell) |
| 32 | 4 | 213, 2754, 79.8, 2.01 | 43.3, 338, 23.3 | 14.1, 105, 9.0 | 3.75, 34, 4.8 | 1.54, 6, 2.5 | — (0 cells) |
| 48 | 4 | 6507, 123620, 2003, 2.25 | 471, 5166, 146 | 61.2, 1142, 49 | 5.40, 65, 5.1 | — | — |
| 16 | 3 | 3.75, 10, 1.2, 1.66 | 3.00, 8, 1.1 | 2.75, 7, 1.1 | 2.00, 6, 1.1 | 2.00, 5, 1.0 | **1.00, 0** (14 cells) |
| 24 | 3 | 9.67, 53, 2.5, 1.80 | 7.00, 53, 2.4 | 6.00, 36, 1.9 | 5.11, 36, 1.9 | 1.67, 6, 1.1 | — |
| 32 | 3 | 24.9, 234, 5.7, 1.98 | 17.9, 218, 5.1 | 5.20, 34, 2.2 | 3.75, 34, 2.2 | 1.07, 0, 1.0 | — |
| 48 | 3 | 173, 3261, 34.7, 2.22 | 115, 1387, 22.7 | 82.7, 1387, 21.0 | 2.05, 21, 1.4 | — | — |
| 64 | 3 | 1465, 36591, 248, 2.47 | 1465, 36591, 248 | 247, 5648, 64.6 | 1.00, 0, 0.1 | — | — |

Reading: at margin ≥ 1.5 no cell has an off-path expansion; at 1.2–1.3 the band maximum is 2–5·D and flat in T; below 1.1 the cost is exponential in T (the tie-family regime).

### 4.2 Peaky generator and alternating control (`scan3.log`)
The two decoder reports' `peaky_table` (70 % blank frames, conf ∈ {0.5,…,0.95}), W ∈ {4,5}, 3 seeds each, plus the alternating family (margin ρ/(1−ρ) exactly, bound exact) for the m = T column. 50 cells per T.

| T | m ≥ 1.0 | m ≥ 1.05 | m ≥ 1.2 | m ≥ 1.5 | m ≥ 2 | m ≥ 4 | m ≥ T |
|--:|---|---|---|---|---|---|---|
| 16 | 10.8, n_off 39, R 1.91 | 3.00, 10 | 1.29, 2 | **1.00, 0** (28 cells) | 1.00, 0 (25) | 1.00, 0 (16) | 1.00, 0 |
| 24 | 77.9, 537, 2.61 | 11.8, 97 | 1.00, 0 | 1.00, 0 (22) | 1.00, 0 (17) | 1.00, 0 (9) | 1.00, 0 |
| 32 | 67.2, 728, 2.65 | 6.42, 65 | 1.17, 2 | 1.00, 0 (25) | 1.00, 0 (22) | 1.00, 0 (14) | 1.00, 0 |
| 48 | 693, 10383, **3.10** | 4.00, 47 | 1.60, 9 | 1.00, 0 (22) | 1.00, 0 (19) | 1.00, 0 (12) | 1.00, 0 |
| 64 | 894, 21431, **3.42** (m=1.02) | 14.4, 227 | 1.44, 7 | 1.00, 0 (19) | 1.00, 0 (18) | 1.00, 0 (11) | 1.00, 0 |

gen/T² in the m ≥ 1.5 band: 3.6 / 2.8 / 3.2 / 2.5 / 2.8 (T = 16 → 64), i.e. the certified-exact-decoder law with the D-dependence absorbed; in the m ≥ 1 band 6.6 / 19 / 64 / 162 / 891 (tie-family blow-up at conf 0.5).

### 4.3 Adversarial hill-climbs (`hunt.log`, `hunt2_off.log`, `hunt2_R.log`; every reported table re-analysed in Fraction, brute-forced at T ≤ 10)
Objective (b): maximise n_off subject to true margin ≥ m_target, unrestricted tables (random / blank-dominant / clock / pinned seeds, 6–9 restarts × 150–250 mutations per cell).

| T, W | best found at m ≥ 1.05 | m ≥ 1.2 | m ≥ 1.5 | m ≥ 2 | m ≥ 3 |
|---|---|---|---|---|---|
| 8, 3 | m=1.19: exp/D 2.25, n_off 5 | 1.23: 2.00, 2 | 2.21: 1.33, 1 | 3.15: **1.00, 0** | 10.2: 1.00, 0 |
| 10, 3 | 1.02: 2.67, 10 | 1.21: 2.25, 5 | 1.57: 1.50, 2 | 2.75: 1.00, 0 | 3.14: 1.00, 0 |
| 12, 3 | 1.07: 3.00, 10 | 1.24: 2.83, 11 | 1.62: 1.75, 3 | 2.17: 1.00, 0 | 3.21: 1.00, 0 |
| 8, 4 | 1.02: 3.20, 11 | 1.23: 2.67, 5 | 1.53: 1.75, 3 | 2.74: 1.00, 0 | 3.45: 1.00, 0 |
| 10, 4 | 1.01: 6.50, 33 | (1.05: 5.80, 24)† | 1.52: 1.50, 3 | 2.01: 1.00, 0 | 3.02: 1.00, 0 |
| 12, 4 | 1.02: 13.7, 76 | (1.08: 8.0, 35)† | (1.03: 9.6, 43)† | (1.04: 16, 90)† | 4.00: 1.00, 0 |
| 16, 3 | — | — | (1.27: 5.29, 30)† | 2.07: 1.00, 0 | 3.14: 1.00, 0 |
| 20, 3 | — | — | (1.05: 10.4, 85)† | 2.00: 1.00, 0 | (1.18: 5.9, 38)† |
| 16/20, 4 | — | — | †(margin ≤ 1.04) | † | † |
† = the climber could not reach the target margin while keeping off-path expansions; the row shows the margin it settled at. **In every table it found with margin ≥ 2.0 (nine cells), n_off = 0; with margin ≥ 1.5, exp/D ≤ 1.75.**

Objective (a): maximise R over expanded off-path nodes (any margin): R_max = 2.28 (T=10, W=3), **3.08** (12, 3; margin 1.08, K_u = 4, completions at 0.49–0.62·p*), 2.96 (16, 3), 2.79 (20, 3), 2.99 (12, 4), 2.97 (16, 4). The climber cannot push R above ≈ 3 and cannot combine R ≥ 2 with margin ≥ 2: raising the mode's dominance makes the suffix modes on the support compatible with each other (they become suffixes/truncations of one string), which collapses R.

### 4.4 The T-dependence of R (all off-path expanded nodes, all experiments)
| T | 10 | 12 | 16 | 20 | 24 | 32 | 48 | 64 | 80 |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| max R, structured grids (§4.1–4.2, §3) | 1.38 | — | 1.91 | — | 2.61 | 2.65 | 3.10 | 3.42 | 2.38 |
| max R, adversarial (§4.3) | 2.28 | 3.08 | 2.96 | 2.79 | — | — | — | — | — |
| max K_u on those nodes | 4 | 6 | 11 | 10 | 13 | 18 | 34 | 34 | 17 |
(T = 80 covers only the pinned family of §3; the T = 80 rows of scan2/scan3 were still running at write-up time and append to their logs.)
Within the blank-dominant grid alone R − 1 grows like T^{0.45} (1.66, 1.85, 2.01, 2.25, 2.47 at T = 16…64), but only at margin ≈ 1.0–1.1; the peaky conf-0.5 tables give the overall maximum 3.10 at margin 1.00. R is far below K_u everywhere (Proposition D is loose by 5–15×).

### 4.5 Real posteriors (`real_run_*.log`, `real_rows.log`)
Plain (non-certifying) final search with this report's diagnostics on the four T = 112, W = 32 wav2vec2 tables (P14 at clean / 10 dB / 5 dB / 0 dB); p* checked against `ctc_forward`; margin by the exact second-best search:

| table | D | p* | margin | K (=max_d K_d) | exp_final | n_off | max K_u / R on off-path nodes | Theorem A fires? |
|---|--:|--:|--:|--:|--:|--:|---|---|
| clean/P14 | 21 | 0.896 | 30.87 | 22 | 21 = D | 0 | — | **yes** (30.9 > 22) |
| 10dB/P14 | 20 | 7.6e-3 | 1.704 | 21 | 20 = D | 0 | — | no |
| 5dB/P14 | 22 | 1.4e-3 | 1.120 | 23 | 22 = D | 0 | — | no |
| 0dB/P14 | 19 | 3.0e-5 | 1.025 | 20 | 20 = D+1 | 1 | K_u = 20, support 102 frames, **R = 1.12** | no |
K_d = D+1 for every symbol d (one suffix-mode string per inter-segment gap: d followed by the transcript from the next segment), so on real tables the a-priori certificate is "margin > D+1". Among the 70 certified real tables of the certified-exact-decoder report §(f) (their `exp_final` includes the runner-up certification and is ≈ 1.7·D regardless of margin, so it cannot be used for n_off) the margin exceeds D+1 on four: T4/clean/P14 (30.9 > 22), torgo_ctl_3 (82 > 73), T4/clean/P0 (333 > 91), T4/clean/P12 (718 > 53) — assuming K = D+1 as measured on P14. The one off-path node seen on real data (0 dB, margin 1.025) has R = 1.12 with twenty distinct suffix modes over a 102-frame support: on real posteriors the prefix-end distribution λ is concentrated on one segment and the suffix modes are the transcript suffixes, so R ≈ 1 even when K_u is large.

### 4.6 Summary table — max exp_final/D over every table measured, by true-margin band
| band | T ≤ 12 (adversarial) | T = 16 | 24 | 32 | 48 | 64–80 | real T=112 |
|---|--:|--:|--:|--:|--:|--:|--:|
| m ≥ 1.00 | 16.0 | 10.8 | 77.9 | 213 | 6507 | 1465 (W=3, T=64); 894 (peaky, T=64); 616 (T=80, §3) | 1.05 (m=1.025) |
| m ≥ 1.05 | 13.7 (m=1.02)/5.8 | 5.00 | 19.3 | 43.3 | 471 | 1465 | 1.00 (m=1.12) |
| m ≥ 1.20 | 2.83 | 2.50 | 5.11 | 3.75 | 5.40 | 1.44 (peaky T=64) | 1.00 (m=1.70) |
| m ≥ 1.50 | 1.75 | 1.00 | 1.09 | 1.00 | 1.00 | 1.00 (19 cells) | 1.00 |
| m ≥ 2.0 | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** | **1.00** (18) | 1.00 (m=30.9, Theorem A) |
| m ≥ 4.0 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 (11) | 1.00 |
| m ≥ T | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | — |
gen/T² is 0.3–3.6 in every cell with m ≥ 1.5 (it is the backward pass, ≈ (W−1)·Σ_{t,c}(|v_{c,t}|+1)·O(1)), 2–20 in the 1.2 band, and 20–2000 (exponential in T) in the m ≈ 1 band.

## 5. The gap, stated exactly

Write λ_t := ok_d(t−1)H_d(t)/S_d(u) (a distribution over the support) and M[s][t] := g_{v_s}(t)/H_d(t) ∈ [0,1] (the suffix mode of frame s, started at frame t; M[t][t] = 1). Then exactly
  R_d(u) = 1 / max_s Σ_t λ_t·M[s][t].
Theorem A′ says: **off-path u is expanded ⇒ max_s Σ_t λ_t M[s][t] ≤ 1/m.** The margin also forces λ_s ≤ 1/m for every s (each single completion is ≤ p*/m while S_d(u) ≥ p*). So a counterexample to C0 at margin m needs a prefix whose end-frame distribution λ is spread over ≥ m frames whose suffix modes are pairwise incompatible (M ≈ identity on the support), while every completion stays ≤ p*/m and the mode keeps p*.

**Open Lemma (would close C0 and give "margin > c₀ ⇒ optimal").** There is a constant c₀ such that for every table, every prefix u and every d with S_d(u) ≥ p*: max_s Σ_t λ_t M[s][t] ≥ 1/c₀.
What is known: c₀ ≤ K_u ≤ T (Lemma 2). The two mechanisms that make R large pull against the margin: (i) spreading λ needs the prefix to be alignable across frames that separate different suffix modes, which in every family found means either skipping rigid symbols (each skip is itself a competitor, cost ≥ m, so λ decays geometrically across the support and R = O(1/(1−1/m)) — this is why the "clock + free insertion" designs I tried give R < m) or living in a blank-dominant region, where the suffix modes are the truncations of one string and the margin is forced to 1 + O(1/D) (§3); (ii) making the suffix modes incompatible needs rigid frames, which concentrate λ. I could not turn this into a proof; the adversarial search (T ≤ 20) finds R ≤ 3.1, never together with m ≥ 2.

**If C0 fails, the next-best target** is the quasi-polynomial statement exp_final ≤ (T²W)^{O(log_m R_max)} (an off-path node with e "edits" has max_v p(u·v) ≲ p*/m^e, so R ≥ m^e forces e ≤ log_m R_max, and there are ≤ (T²W)^e such prefixes); its missing ingredient is the near-mode count under a margin, which the cost-theorem report showed is not polynomial in general (T^{Θ(log T/log m)} on the alternating family, where the decoder is nevertheless exact).

## 6. What the margin lemma means for the decoder on real posteriors

On clean audio (margins 1.3–80, K = D+1 ≈ 20–90) the *proven* certificate (Theorem A) fires only when the margin exceeds D+1 — 4 of 70 tables — and there it guarantees the plain final search is exactly the D-node walk down the mode; for the other clean tables the measured plain search is D nodes (margins 1.12 and 1.70 on the T = 112 tables: zero off-path expansions) but the guarantee is empirical, resting on C0 (R ≤ 3.5 measured): if C0 is proven, every table with margin > c₀ ≈ 3.5 — most clean audio — gets a free a-priori certificate "exp_final ≤ D+1" from the backward pass alone, and margin 1.3–3.5 tables are covered by the measured R ≈ 1.1 on real data, not by a theorem. On hard audio (margins 1.001–1.1) no margin lemma of any kind can help — the runner-up is within 10 % of the mode by definition — but neither is one needed for the final search: the observed cost there is D to 2·D (one off-path node at margin 1.025 on 0 dB/P14; the certified-exact-decoder report's 70-table sweep has one 57·D outlier in its certifying count), because real tables are rigid (R ≈ 1.1 even with 20 suffix modes over 100 frames). The blow-ups of the cost-theorem report §4 (exp/D = 600–6500, gen/T² up to 2000 at T ≤ 80) need margin ≤ 1.1 *and* a blank-dominant tie structure (R growing with T), a combination real posteriors do not exhibit. The cost that a margin cannot touch is the backward pass, 0.3–10·T² generations in every cell of this report regardless of margin.

## 7. File index
- `../code/margin-lemma/r1core.py` — `backward_modes` (H and argmax strings), `final_instrumented` (per-node B, p, d, support, K_u, Σ/max completion masses, on-path flag), `second_best` (exact p₂), `enumerate_above` (all labellings ≥ θ), `analyse`, families (`fam_pinned`, `fam_tworate`, `fam_blankdom`, `fam_alt`).
- `../code/margin-lemma/gate1.py` → `gate1.log` (G1a–g); `../code/margin-lemma/gate2.py` → `gate2.log` (G2a–c, sub-search form).
- `../code/margin-lemma/scan1.py` → `scan1.log` (true margins of the cost-theorem report's pinned family, §3); `../code/margin-lemma/scan2.py` → `scan2_w3.log`, `scan2_w4.log` (rates grid, §4.1); `../code/margin-lemma/scan3.py` → `scan3.log` (peaky + alternating bands, §4.2).
- `../code/margin-lemma/hunt.py` → `hunt.log`, `../code/margin-lemma/hunt2.py` → `hunt2_off.log`, `hunt2_R.log` (adversarial, §4.3–4.4).
- `../code/margin-lemma/real_run.py` → `real_run_a.log`, `real_run_b.log` (four T = 112 real tables, §4.5); `../code/margin-lemma/real_rows.py` → `real_rows.log` (70 certified margins from `../code/certified-exact-decoder/real_*.jsonl`).

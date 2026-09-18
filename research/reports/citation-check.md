# Adversarial citation check for the exact-CTC-decoder quantum claims

Date: 2026-09-18. Adversarial verification thread. All papers body-read from the arXiv PDFs
in `citation-check/pdfs/` (versions listed per item). All numbers come from runs in `citation-check/` (`genmin_sim.py`,
`checks.py`; logs `genmin_run.log`, `checks.log`, `genmin_results.json`). Python: `citation-check/.venv` (uv, numpy 2.5.3).

## Headline

| # | Citation | Verdict | One line |
|---|---|---|---|
| 1 | vAGGdW 1705.01843v4, App. C, Lemma 47/48, Thm 49 | **HOLDS-WITH-CAVEATS** | Proof reproduced step by step, no gap; every inequality verified numerically; empirical constant 1.0–4.9 vs stated C≈25. Caveats: (i) it is a *fixed-budget* algorithm — you must know a lower bound on p* to set M, and there is no stopping certificate; (ii) "expected O(1/√p*) uses" is only true in the Lemma 48 sense; the theorem's algorithm always spends exactly M. Ties are handled by the statement itself. |
| 2 | Belovs 1904.02192v1, Thm 4 (Θ(1/d_H)) | **HOLDS-WITH-CAVEATS** | Theorem is fine, but it is a *distinguishing* bound in models whose lower bound is worst-case over garbage; it does not by itself state a mode-finding bound and does not cover an oracle whose garbage reveals p_l (ours does). A two-line reduction plus the hybrid argument on the specific state (Claim 5's proof) gives T ≥ 1/(6√p*) for any black-box (state-preparation) algorithm, including ones that see |p_l⟩. Constant verified numerically (0.167/√p*). Not a lower bound for algorithms that open the CTC circuit. |
| 3a | Jarret–Wan 1711.05295v2, Thm 5 | **HOLDS-WITH-CAVEATS** | Bounded-degree rooted tree, oracles f/h, η_max ≤ depth (their Thm 10) ⇒ Õ(√(T n)). Prefix tree satisfies the hypotheses *once a threshold θ is fixed*. It returns *a* marked vertex, not the argmax: with θ ≤ p* the marked set can be large; argmax needs θ ∈ (p₂, p*] (unknown) or k repeats. |
| 3b | Aaronson–Ambainis (quant-ph/0303041 Thm 7) Ω(√(nδ)) as cited via Montanaro | **HOLDS-WITH-CAVEATS (does not apply to us)** | Source located and verified: starfish graph, C-/Z-local robot model. It lower-bounds *local* tree search on worst-case trees. Our prefix tree has known labels and a directly evaluable f, so locality is not forced; the bound says nothing about our problem. |
| 4 | Rall 2103.09717v4 "rounding promise unavoidable" vs Guo et al. 2606.06316v1 | **HOLDS (Rall's claim is informal but correct); NO CONTRADICTION** | Rall's statement is prose ("we claim … impossible in principle"), no theorem number; the continuity argument is nevertheless a valid one-paragraph proof for the exact-for-all-λ task. Guo et al. evade it exactly as Rall says one must: a constant-relative-width ambiguity band [Δ,(1+α)Δ] with α≈0.44–0.5 in the actual proof, error ζ charged to the output; degree O((1/Γ)log 1/ε) with Γ=0.1√Δ. For our exact construction (value computed reversibly into a register) the issue does not arise at all. |
| 5 | de la Higuera–Oncina W11-2904, Property 2 | **HOLDS; transfer valid; but does NOT give ǀT_{p*}ǀ ≈ c/p*** | Proof is the disjointness of {uΣ*} over u ∈ Σⁿ; transfers verbatim to CTC (prefix probability is a genuine event probability, Σ_l p(l\|y)=1). Provable bound is ≤ 1/p* *per length*, hence ǀT_{p*}ǀ ≤ L_max/p*, and this is tight (explicit family). c/p* is empirical. |
| 6 | Chakrabarti et al. 2210.03210v1, Thm 1.5 | **GAP-FOUND (external + internal)** | Only v1 exists; nothing fixed. Proof of Thm 1.5 is arithmetically consistent with its own statement (both Õ(√Q·d)), but rests on Primitive 1 ("Apers et al.: O(√T·d log d log 1/δ)") and Primitive 3 (log²(1/δ) "follows from [22, Thm 1]", which has 1/δ²). AGJ Thm 13 (verbatim below) gives, for a tree from the root, O(√(Tn) log(Tn) log log(Tn)) — √(Tn), not √T·n — so the attribution is not what AGJ proved. Proof also references a `cost'` oracle that does not exist in Thm 1.5. |

Survived for our purposes: 1 (with the budget caveat), 2 (via the explicit reduction, not by bare citation), 5 (as a per-length bound only), 4 (Rall/Guo consistent; irrelevant to the exact evaluator).
Did not survive as cited: 3b (wrong model for our problem), 6 (attribution chain), and the *inference* "Property 2 ⇒ |T_{p*}| = O(1/p*)".

---

## 1. van Apeldoorn, Gilyén, Gribling, de Wolf — arXiv:1705.01843v4 (12 Feb 2020; "This version will appear in Quantum" = Quantum 4, 230 (2020)). Appendix C, pp. 58–63. Body-read.

Version note: arXiv has v1–v4; v4 is the journal version and contains Appendix C (pp. 58–63, "C Generalized minimum-finding algorithm"). The FOCS 2017 extended abstract is not the reference of record for Appendix C; cite the Quantum/arXiv v4 version.

### (a) Exact statements with every hypothesis

Meta-Algorithm 2 (from DH96): "Input A discrete random variable X with finite range. Output The minimal value x_min in the range of X. Init t ← 0; s_0 ← ∞. Repeat until s_t is minimal in the range of X: 1. t ← t+1 2. Sample a value s_t according to the conditional distribution Pr(X = s_t | X < s_{t−1})."

Lemma 47 (verbatim): "Let X be a finite discrete random variable whose range of values is x_1 < x_2 < … < x_N. Let S(X) = {s_1, s_2, …} denote the random set of values obtained via sampling during a run of Meta-Algorithm 2 with input random variable X. If k ∈ [N], then Pr(x_k ∈ S(X)) = Pr(X = x_k)/Pr(X ≤ x_k)."

Algorithm 3 (verbatim input/output): "Input A number M and a unitary U, acting on q qubits, such that U|0⟩ = Σ_{k=1}^N |ψ_k⟩|x_k⟩, where x_k is a binary string representing some number and |ψ_k⟩ is an unnormalized quantum state on the first register. Let x_1 < x_2 < … < x_N and define X to be the random variable with Pr(X = x_k) = ‖ψ_k‖². Output Some |ψ_k⟩|x_k⟩ for a (hopefully) small k. Init t ← 0; s_0 ← ∞. While the total number of applications of U and U⁻¹ does not exceed M: 1. t ← t+1 2. Use the exponential search algorithm with amplitude amplification on states such that x_k < s_{t−1} to obtain a sample |ψ_k⟩|x_k⟩. 3. s_t ← x_k".

Lemma 48 (verbatim): "There exists C ∈ ℝ₊, such that if we run Algorithm 3 indefinitely (setting M = ∞), then for every U and x_k the expected number of uses of U and U⁻¹ before obtaining a sample x ≤ x_k is at most C/√Pr(X ≤ x_k)." Followed by: "It is not too hard to work out the constant by following the proof of [BBHT98] providing something like C ≈ 25."

Theorem 49 (verbatim): "(Generalized Minimum-Finding). If we run Algorithm 3 with input satisfying M ≥ 4C/√Pr(X ≤ x) for C as in Lemma 48 and a unitary U that acts on q qubits, then at termination we obtain an x_i from the range of X that satisfies x_i ≤ x with probability at least 3/4. Moreover the success probability can be boosted to at least 1 − δ with O(log(1/δ)) repetitions. This uses at most M applications of U and U⁻¹ and O(qM) other gates."

Hypotheses, made explicit (the checklist from the brief):
- **Distinctness:** the x_k in the statement are *distinct* by construction — but |ψ_k⟩ is an arbitrary unnormalized state on the first register, so *all* first-register content sharing value x_k (many labels, garbage, paths) is lumped into |ψ_k⟩. Ties in the value register are therefore handled by the statement itself; Pr(X = x_k) = total mass of the tie class. Nothing in the proof uses that |ψ_k⟩ is a single basis state. DH96 needed a separate remark for non-distinct values (their p(t,r) ≤ 1/r); vAGGdW do not, because Lemma 47 is about values, not indices.
- **Register:** x_k is a finite binary string; comparison "x_k < s_{t−1}" is exact string comparison (needs O(q) gates — that is where "O(qM) other gates" comes from).
- **Access:** U and U⁻¹ (explicit), reflection about |0⟩ on q qubits, and a comparator oracle on the value register. Controlled-U is not needed.
- **Failure/expectation:** Lemma 48 is an *expectation* statement for the unbounded run. Theorem 49 is a *fixed-budget* Monte-Carlo statement: with M ≥ 4C/√Pr(X ≤ x), Markov gives success ≥ 3/4. Boosting: repeat, take the minimum.
- **Knowledge required:** to set M you need a lower bound on Pr(X ≤ x) for the target x. There is no self-certifying stop: the last round searches for x < x_min, which has zero good amplitude, and runs until the budget is exhausted. The algorithm therefore *always* costs exactly M.
- **"At most M":** the while-guard is checked at round boundaries; strictly, the final round can overshoot M unless you truncate it. Truncation does not affect the success claim (the sample ≤ x_k, if obtained within M uses, has already been recorded).
- Pr(X ≤ x) > 0 is implicit (x in the range).

### (b) Proof reproduction, step by step

**Lemma 47.** Fix a value x = x_k. Claim (25): Pr(s_t = x | s_t ≤ x ∧ s_{t−1} > x) = Pr(X=x)/Pr(X≤x). Their chain: condition additionally on s_{t−1} = x_ℓ for each x_ℓ > x; given s_{t−1} = x_ℓ, s_t ~ X | X < x_ℓ, so Pr(s_t = x | s_{t−1}=x_ℓ)/Pr(s_t ≤ x | s_{t−1}=x_ℓ) = [Pr(X=x)/Pr(X<x_ℓ)]/[Pr(X≤x)/Pr(X<x_ℓ)] = Pr(X=x)/Pr(X≤x), independent of ℓ; averaging over ℓ with weights Pr(s_t ≤ x ∧ s_{t−1}=x_ℓ)/Pr(s_t ≤ x ∧ s_{t−1} > x) (which sum to 1) gives (25). I checked each of the six displayed equalities; they are bookkeeping, with the 0/0 := 0 convention of footnote 13 covering unreachable thresholds. Then Pr(x ∈ S) = Σ_t Pr(s_t = x) = Σ_t Pr(s_t = x | s_t ≤ x ∧ s_{t−1} > x)·Pr(s_t ≤ x ∧ s_{t−1} > x); the events {s_t ≤ x ∧ s_{t−1} > x} over t are disjoint and exhaust "the first time the threshold drops to ≤ x", which happens with probability 1 within N rounds because thresholds strictly decrease. So Pr(x ∈ S) = Pr(X=x)/Pr(X≤x). **No gap.** (Numerical: `checks.py`, Meta-Algorithm 2 with 12 distinct values and heavy ties, 40 000 runs: max deviation 0.0015 vs MC noise 0.005.)

**Lemma 48.** Round 0 costs 1 use (s_0 = ∞, all good). Round i+1 starts from s_i; its cost is the cost of the exponential search on the good set {x < s_i}, which is a fresh run whose distribution depends only on s_i (Markov). So E[cost until a sample ≤ x_k] = 1 + Σ_{ℓ>k} Σ_i Pr(s_i = x_ℓ)·E[cost of QSearch on X_{<x_ℓ}] = 1 + Σ_{ℓ>k} Pr(x_ℓ ∈ S)·E[…] (each value appears at most once in S since thresholds strictly decrease) = 1 + Σ_{ℓ>k} [Pr(X=x_ℓ)/Pr(X≤x_ℓ)]·O(1/√Pr(X<x_ℓ)) by Lemma 47 and BBHT/BHMT. Two things must be true for this line: (1) the output of a successful exponential-search round is distributed as X | X < s — true because every Grover iterate acts inside span{|good⟩,|bad⟩} with |good⟩ ∝ Π_good U|0⟩, so conditional on measuring a good element the relative amplitudes inside the good subspace are those of U|0⟩, independently of j (and j=0 rounds are plain samples); (2) the expected cost of QSearch with good amplitude a is O(1/√a) — BHMT02 Theorem 3 ("QSearch finds a good solution using an expected number of applications of A and A⁻¹ which are in Θ(1/√a) if a > 0, and otherwise runs forever"), whose proof is BBHT98 Theorem 3 with 1/sin(2θ) in place of √(N/t). Neither is spelled out in vAGGdW ("we will skip the details here, which are straightforward modifications of [BBHT98]"); both are correct, and (1) is confirmed by the simulation: E[#rounds] matched the Lemma 47 prediction Σ_v Pr(X=v)/Pr(X≤v) in all 14 distributions (e.g. uniform-256: 6.113 vs 6.124; Dirichlet: 3.823 vs 3.807; uniform-4096: 8.974 vs 8.895).

Equation (30): Σ_{j=1}^{N−k} p_j/(Σ_{i≤j} p_i)·(Σ_{i≤j−1} p_i)^{−1/2} ≤ 2/√p_0. Their route: (27)/(28) show that splitting any p_ℓ (ℓ ≥ 1) into two halves does not decrease the sum. I verified (28) algebraically: multiplying by (a+b)(a+2b)√a√(a+b)/b gives (a+2b)√(a+b) + (a+b)√a − 2(a+b)√(a+b) = √a·√(a+b)·(√(a+b) − √a) ≥ 0; numerically min over 2·10⁵ random (a,b) = +5.4·10⁻¹³. Refining until all p̃_j ≤ δ, (29) gives (P_{j−1})^{−1/2} ≤ (P_j)^{−1/2}·√(1+δ/p_0) (they then use 1+δ/p_0 ≥ √(1+δ/p_0), harmless); the refined sum is ≤ (1+δ/p_0)·Σ_j p̃_j/P_j^{3/2} ≤ (1+δ/p_0)∫_{p_0}^{1} z^{−3/2}dz = (1+δ/p_0)(2/√p_0 − 2); δ → 0 gives (30). Every step checks. Numerically (`checks.py`): sup over 2·10⁴ random distributions of sum·√p_0/2 = 0.903; for a fine uniform tail the ratio converges to exactly 1 − √p_0 (0.98587 at p_0 = 10⁻⁴; 0.89996 at 10⁻²; 0.29289 at 0.5), i.e. the integral bound is asymptotically tight and never exceeded. **No gap.**

Constant: BBHT98 Theorem 3 (body-read): λ = 6/5, j uniform in [0,m), expected Grover iterations ≤ (9/2)m_0, m_0 = 1/sin 2θ ≈ 1/(2√a) for a ≤ 3/4. Each iteration uses U and U⁻¹, so ≈ 4.5/√a uses plus one preparation per round (≈ log_λ m_0 rounds). Through (30) this gives C ≈ 9 asymptotically plus O(log²(1/p_0)) lower-order terms; "C ≈ 25" is conservative. Consistent with what we measured.

**Theorem 49.** Markov on Lemma 48: Pr(cost ≥ 4·E) ≤ 1/4. Boosting by repetition and taking the minimum is valid because every output is a genuine value from the range. Gate count is comparator + reflection per iterate. **No gap** — but note the theorem gives a *fixed-M* algorithm, not an "expected O(1/√p*)" stopping algorithm (see caveats).

**Origin of the non-uniform extension.** DH96 (quant-ph/9607014v2, body-read) is uniform start only: Lemma 1 there is "probability that the element of rank r is ever chosen = 1/r", and their Theorem 1 gives success ≥ 1/2 in time 22.5√N + 1.4 lg²N using BBHT with the √N cap. The exponential search over an arbitrary start state is BHMT02 Thm 3 (QSearch). The threshold-sampling analysis for a non-uniform X (Lemma 47) and the integral bound (30) are vAGGdW's own; the "generalization" is theirs, inherited from nothing.

### (c) Numerical test

`citation-check/genmin_sim.py 1000` (exact statevector, N ≤ 256 plus two N = 4096 scaling runs; BBHT schedule λ=6/5, no cap on m because the amplitude-amplification version has none and a √N cap is only valid for uniform amplitudes; cost = 1 + 2j uses per round). Value register x_k = −p_k (value = probability, so ties are exactly our setting); two Dürr–Høyer rows use distinct values with uniform amplitude. Metric: uses of U^{±1} until the first sample with the minimum value; p_0 = mass of the tie class of maximisers. Output (`genmin_run.log`):

| distribution | N | p_0 | E[uses] | E·√p_0 (= C_emp) | q75·√p_0 | q95·√p_0 | max·√p_0 | E[rounds] | Lemma-47 pred | Eq.30 sum | 2/√p_0 | trials |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A uniform, distinct values (DH) | 256 | 0.00391 | 64.0 | 4.000 | 5.375 | 8.378 | 15.0 | 6.113 | 6.124 | 27.76 | 32.0 | 1000 |
| B p* = 0.5, flat rest | 256 | 0.5 | 2.5 | 1.783 | 2.121 | 5.657 | 15.6 | 1.501 | 1.500 | 0.71 | 2.83 | 1000 |
| C p* = 0.99 | 256 | 0.99 | 1.0 | 1.005 | 0.995 | 0.995 | 1.99 | 1.010 | 1.010 | 0.01 | 2.01 | 1000 |
| D 50 near-ties (0.0105 vs 50×0.0100) | 256 | 0.0105 | 25.3 | 2.593 | 3.510 | 5.226 | 9.43 | 2.453 | 2.469 | 10.24 | 19.52 | 1000 |
| E heavy runner-up (0.30 vs 0.29) | 256 | 0.30 | 3.7 | 2.036 | 2.739 | 5.505 | 19.2 | 1.869 | 1.902 | 1.43 | 3.65 | 1000 |
| F p* = 2/N, flat tail | 256 | 0.00781 | 29.7 | 2.625 | 3.624 | 5.303 | 8.31 | 1.995 | 1.992 | 11.2 | 22.6 | 1000 |
| G Zipf 1/k | 256 | 0.163 | 6.8 | 2.732 | 3.637 | 7.273 | 30.3 | 2.754 | 2.699 | 2.83 | 4.95 | 1000 |
| H one distinct value | 256 | 1.0 | 1.0 | 1.000 | 1.000 | 1.000 | 1.0 | 1.000 | 1.000 | 0 | 2.0 | 1000 |
| I two values, 10 tied maximisers (mass 0.2) | 256 | 0.20 | 4.1 | 1.826 | 2.236 | 3.578 | 17.0 | 1.794 | 1.800 | 1.79 | 4.47 | 1000 |
| J mode 0.005 vs 199×0.00497 | 256 | 0.005 | 37.3 | 2.639 | 3.606 | 5.374 | 11.2 | 2.003 | 2.001 | 14.1 | 28.3 | 1000 |
| K Dirichlet(0.3) seed 1 | 256 | 0.0459 | 14.1 | 3.025 | 4.123 | 7.068 | 21.4 | 3.823 | 3.807 | 6.86 | 9.34 | 1000 |
| K Dirichlet(0.3) seed 2 | 256 | 0.0366 | 16.2 | 3.095 | 4.210 | 7.080 | 18.6 | 4.000 | 3.969 | 7.80 | 10.45 | 1000 |
| L p* = 2/N, flat tail (scaling) | 4096 | 0.00049 | 129.3 | 2.857 | 3.845 | 5.593 | 9.02 | 2.000 | 2.000 | 45.2 | 90.5 | 500 |
| M uniform, distinct values (DH, scaling) | 4096 | 0.00024 | 312.4 | 4.881 | 6.656 | 10.13 | 29.2 | 8.974 | 8.895 | 117.0 | 128.0 | 500 |

Readings:
- Empirical constant C_emp = E[uses]·√p_0 is 1.0–3.1 for value-register distributions and 4.0–4.9 in the Dürr–Høyer (all-distinct) regime, vs the stated C ≈ 25 and the analytic ≈ 9 from BBHT. The theorem's constant is loose by 5–25×, never violated. The mild growth 4.0 → 4.9 from N=256 to 4096 in the uniform case is the O(log²(1/p_0)) lower-order term (many rounds, each with a log-length exponential-search ramp), not a change in the √ scaling.
- Theorem 49's budget M = 4C/√p_0 = 100/√p_0 contained 100% of runs in every distribution (`frac_within_4C25` = 1.000 everywhere). The budget actually needed for 3/4 success is q75·√p_0 ≈ 2.1–6.7 (in units of 1/√p_0); M = 4·E[uses] contained ≥ 97.7% of runs (Markov guarantees 75%).
- Adversarial cases behave as the theorem predicts: near-ties (D, J) and a heavy runner-up (E) do not hurt — the cost is governed by p_0 alone; the Eq. (30) sum is ≤ 2/√p_0 in every row.
- Boundary cases: p* → 1 gives ≈ 1 use (C: 1.005); one distinct value (H): exactly 1 use, then the algorithm would search a zero-amplitude set until M — the fixed-budget nature is visible here.

### (d) Application to our setting

U|0⟩ = Σ_π √p(π)|π⟩|B(π)⟩|p(B(π)|y)⟩: first register = (π, B(π)), value register = the fixed-point bitstring of p(l|y). Then Pr(X = v) = Σ_{l: p(l|y)=v} p(l|y), the tie class of the maximum has mass p_0 = D·p*, and Theorem 49 with x = −p* returns one of the D tied argmax labels with probability ≥ 3/4 using M ≥ 4C/√(D p*) uses of U^{±1}. This is exactly the theorem's setting; no adaptation needed. Caveats:
1. **M requires a lower bound on p*.** Unknown in decoding. Doubling M gives total cost O(1/√p*) *by the time the guarantee kicks in*, but nothing tells you it has. Any practical use is "best label within budget B, correct w.p. ≥ 3/4 if B ≥ 4C/√(Dp*)". A first plain sample gives a valid lower bound p(l_1) ≤ p*, but E[1/√p(l_1)] = Σ_l √p_l can be ≫ 1/√p* (e.g. p* = 1/2 with a flat tail over N: Σ√p ≈ √(N/2) vs √2).
2. **Precision of the value register.** Rounding merges near-ties into ties; the output is a maximiser of the *rounded* value. Needs enough bits to separate p* from the runner-up, unknown a priori. Not the theorem's problem, but it is our construction's.
3. **U⁻¹ is required** — fine for a reversible circuit, but every use of U⁻¹ is a full un-computation of the forward recursion (the quantum-argmax-construction report's cost model).
4. The theorem's output is a measured sample, so D > 1 gives a uniformly-weighted (by p) random member of the tie class, not the set.

### (e) Verdict: **HOLDS-WITH-CAVEATS.** Proof correct; constant loose; ties handled; budget must be set from a lower bound on D·p*; no expected-time stopping algorithm is provided by the theorem.

---

## 2. Belovs — arXiv:1904.02192v1 (3 Apr 2019; ESA 2019). Body-read.

### (a) What is proven

Models (Sec. 3, verbatim): "(iii) A quantum procedure that generates the state µ_p = Σ_a √p_a |a⟩ … (iv) A quantum procedure that generates a state of the form Σ_a √p_a |a⟩|ψ_a⟩ where ψ_a are arbitrary unit vectors." Plus (i) frequency-string oracle and (ii) i.i.d.-sample-string oracle. State-generating oracle convention (Sec. 2.2, verbatim): "the input to the algorithm is given by a state ψ ∈ ℂ^m, and the algorithm should work equally well for any unitary performing the transformation O: |0⟩ ↦ |ψ⟩."

Theorem 4 (verbatim): "For any two probability distributions p and q on the same space A, and any model of accessing them from Section 3, the quantum query complexity of distinguishing p and q is Θ(1/d_H(p,q))." with d_H(p,q) = √(½Σ_a(√p_a − √q_a)²).

Proof structure (Sec. 4, body-read): upper bound in model (iv) (implies all); lower bound in model (ii) via the adversary bound (Theorem 7, Γ = G^{⊗n} with G a rotation by the angle α between µ_p and µ_q, ‖G∘Δ‖ ≤ 2 sin α), which implies (i) and (iv) through Proposition 3(b) ("Model (iv) is more general than model (i)" — a model-(i) string oracle yields a model-(iv) oracle in one query, with garbage ψ_a ∝ Σ_{i: x_i = a}|i⟩); model (iii) separately by Claim 5's hybrid argument: "Let O_p be the input oracle exchanging |0⟩ and |µ_p⟩ and leaving the vectors orthogonal to them intact … ‖O_p − O_q‖ = O(α) … ‖A^{O_p} − A^{O_q}‖ ≤ t‖O_p − O_q‖ = O(tα). As this must be Ω(1), we get that t = Ω(1/α)."

### (b) Does it imply Ω(1/√p*) for "find the mode given U"? Gap analysis

It does not *state* it, and two gaps must be closed:

**Gap 1 (distinguish vs. argmax).** Closed by a reduction. Take p with mode A of mass p*, all other labels < p* (mass 1 − p* spread over ≥ (1−p*)/p* labels), and q identical except the mass p* sits on a fresh label B and A has mass 0. Then d_H² = ½(p* + p*) = p*, so d_H = √p*. Any algorithm that outputs the argmax with probability ≥ 2/3 on both distinguishes them, hence needs Ω(1/d_H) = Ω(1/√p*) queries in every model of Theorem 4. (Models (i)/(ii) need p* to be a multiple of 1/n — fine for large n.)

**Gap 2 (which oracle class).** The model-(iv) lower bound is *worst-case over garbage*: it is inherited from the string model, whose garbage ψ_a ∝ Σ_{i:x_i=a}|i⟩ reveals nothing about p_a. Our U has garbage |π⟩|p(l|y)⟩ — the value register is a *known function of p*, which no string oracle can produce in one query. So Theorem 4/Proposition 3 do **not** cover our oracle as a member of a class, and a bare citation "Belovs Thm 4, model (iv)" for our lower bound is incomplete. Closing it: apply Claim 5's argument to the *specific* state ψ_p = Σ_a √p_a|a⟩|g_a(p)⟩ under the state-generating-oracle convention ("work equally well for any unitary performing |0⟩ ↦ |ψ⟩"; Proposition 9: the canonical choice R_ψ is "the reflection through the orthogonal complement of e_0 − ψ"). For our pair, garbage agrees on all shared labels (p_a = q_a there), so ‖ψ_p − ψ_q‖ = √(2p*) exactly as without garbage. Then ‖R_p − R_q‖ ≤ √2‖ψ_p − ψ_q‖ (numerically the ratio is 1.32–1.41, `checks.py`), a T-query black-box algorithm has ‖final states‖ difference ≤ T‖R_p − R_q‖, and a correct argmax finder needs total-variation ≥ 1/3 between its outputs, so T ≥ (1/3)/(2√p*) = 1/(6√p*). Run output: `hybrid: p*=0.0100 ||psi_p-psi_q||=0.1414 ||O_p-O_q||_op=0.1997 => T >= 0.167/sqrt(p*)` (same constant at p* = 0.5, 0.1, 1/64).

Result: **Ω(1/√p*) holds for every algorithm that uses U (and U⁻¹, controlled-U) as a black box that prepares the given state — including algorithms that exploit the |p_l⟩ register — because the hybrid argument only uses the state, not the garbage's meaning.** Theorem 49 is such an algorithm, so its 1/√p* is optimal among black-box methods up to the constant (empirical C ≈ 2–5 vs the bound 1/6). Note the bound is in terms of p*, not D·p*; the tie-class version follows by the same pair with D copies.

### (c) Numbers: see `checks.log` (hybrid block).

### (d) Caveats for our setting
- It is a black-box bound. An algorithm that opens the circuit (uses the CTC structure — the per-frame product form, the collapsing map, the forward recursion) is not bounded by it. No structural lower bound for exact CTC decoding of this form exists in the literature we hold; classically the problem is NP-hard in general (Casacuberta–de la Higuera), which says nothing about the p*-parametrised regime.
- The hard pair (p, q) need not be realisable as two CTC tables; irrelevant for a black-box bound, relevant if someone tries to state it as a bound on "CTC decoding".

### (e) Verdict: **HOLDS-WITH-CAVEATS.** The paper is correct; the mode-finding bound is not in it and must be cited as "Belovs Thm 4 (Claim 5 argument) + the two-line reduction above", stated for black-box state-preparation access.

---

## 3. Jarret–Wan Theorem 5 and the Aaronson–Ambainis lower bound

### 3a. Jarret & Wan — arXiv:1711.05295v2 (8 May 2018). Body-read.

Theorem 5 (verbatim): "Let T, f, h, T, n, and η be defined as in Theorem 4. Let η(v) denote the effective resistance of the subtree rooted at v, and define η_max = sup_{v∈V(T), η(v)<∞} η(v). (1) Then, for any 0 < δ < 1, there is a quantum algorithm which returns a v ∈ V(T) such that f(v) = 1 or 'none' if no such v exists using O(√(T η_max) log⁴(kη) log(1/δ)) queries to f and h. The algorithm requires O(1) auxiliary operations per query and poly(n) space, and fails with probability at most δ."

Hypotheses (from Theorems 1/4 and Sec. 2, body-read): rooted tree; T an upper bound on |V(T)|; n an upper bound on the depth; **bounded degree with a known upper bound d** (Sec. 2: "We consider a tree T of bounded degree … an upper bound d on the degree of each vertex"); f(v) ∈ {0,1} marks; h(v) returns the set of children; η(v) = effective resistance (unit resistors) between v and the marked set inside T(v); η_max is the sup over subtrees that contain a marked vertex; k = number of marked vertices. Theorem 10 (verbatim): "Let n denote the depth of the tree, k ≡ |M| the number of leaves, and d_r the degree of the root vertex r. Then η ∈ [max(1/k, 1/d_r), n]." Hence η_max ≤ n and Theorem 5 is Õ(√(T n)). The output is *a* marked vertex; finding all k costs O(k√(Tn) log⁴(kn) log(k/δ)) (their remark after Thm 5).

Prefix tree check: fix a threshold θ. Nodes = prefixes u with P(uΣ*|y) ≥ θ; h(u) = {ua : P(uaΣ*) ≥ θ} (one forward-recursion extension per child); degree ≤ |Σ|(+1); depth ≤ T_frames; f(u) = [u is a complete label with p(u|y) ≥ θ]; T := |T_θ| ≤ T_frames/θ (item 5). All hypotheses satisfied **given θ**. Caveats:
- θ must be supplied. With θ ≤ p* the marked set is {l : p(l) ≥ θ}, and Theorem 5 returns an arbitrary member — not the argmax. The argmax is guaranteed only if θ ∈ (p₂, p*] (p₂ = runner-up), which is unknown; otherwise you find all k marked (cost ×k, and k can be ~1/θ) or combine with a max-finding step.
- The polylog is log⁴(kη), and T, n, d must be given as inputs.

Verdict: **HOLDS-WITH-CAVEATS** — supports "find some label with p ≥ θ in Õ(√(|T_θ| n))", not "find the mode" without a threshold schedule and a tie-breaking step.

### 3b. Aaronson–Ambainis — quant-ph/0303041 (Theory of Computing 1 (2005)), Theorem 7. Body-read. Cited via Montanaro arXiv:1509.02374 Sec. 5.

Montanaro (verbatim): "it was shown by Aaronson and Ambainis [1] that for each pair T and n, there is a tree containing T vertices and with depth O(n) such that determining the existence of a marked vertex requires Ω(√(Tn)) queries. This holds even if we know the tree in advance and are allowed to perform arbitrary 'local' operations to search within it."

Source, Theorem 7 (verbatim): "For all δ, there exists a graph G with diameter δ_G = δ such that Q(OR, G) = Ω(√(nδ))." Proof: "Let G be a 'starfish' with central vertex v_1 and M = 2(n−1)/δ legs L_1, …, L_M, each of length δ/2 … We use the hybrid argument of Bennett et al." Model (Definitions 1–2, Sec. 3): a quantum robot on a *known* graph whose steps are C-local (or Z-local) unitaries — amplitude moves only along edges — and a query reads the mark at the robot's current vertex. Montanaro's paraphrase is accurate: the starfish is a tree of depth δ/2 with n vertices, and the bound is for local algorithms.

Does it constrain us? No. The Ω(√(nδ)) is a statement about the *local* model on worst-case trees. In the standard query model with vertex labels known (or with an f that can be evaluated on any label), a known tree of size T is searched by Grover in O(√T) with no depth factor; the √n arises only because the robot must physically traverse legs. Our prefix tree has known labels (strings) and f/p(·|y) evaluable on any prefix directly, so locality is not forced and the bound does not apply. What it does say: any *quantum-walk-backtracking-style* (local) algorithm cannot beat √(Tn) on worst-case trees; it does not say our problem needs the √n.

Verdict: **HOLDS-WITH-CAVEATS (as a statement); does not apply to our setting as a lower bound.**

---

## 4. Rall — arXiv:2103.09717v4 (12 Dec 2022; Quantum, accepted 2021-10-14) vs Guo et al. — arXiv:2606.06316v1 (4 Jun 2026). Both body-read.

### Rall: theorem or heuristic?

The claim appears only in prose (Sec. 2, p. 5–6). Verbatim: "Consider phase estimation using a quantum circuit composed of elementary unitaries and controlled-e^{2πiλ_j}. Following an argument related to the polynomial method, we see that the resulting state must be of the form Σ_x Σ_y α_{x,y}(e^{2πiλ_j})|x⟩|garbage_{x,y}⟩ (7) where α_{x,y}(e^{2πiλ_j}) is some polynomial of e^{2πiλ_j}. … This is impossible: α_{x,y}(e^{2πiλ_j}) is a continuous function of λ_j, but the desired amplitude indicating x = floor(2^n λ_j) is discontinuous. … This argument even holds in the approximate case when we demand that α_{x,y} ≤ δ or ≥ 1−δ for some small δ". And: "We claim that all of these attempts fail, and furthermore that achieving coherent phase estimation without some kind of promise is impossible in principle." The α⁻¹ optimality: "we informally argue that the α⁻¹ dependence is optimal, via a reduction to approximate counting." The numbered results (Definition 1 = (n,α)-rounding promise; Theorems 12, 15, 19) are the *algorithms* under the promise; **no theorem states the impossibility**. So: heuristic as presented.

Is the heuristic correct? Yes, and it is a one-paragraph proof for the task as Rall poses it: on the invariant subspace |ψ_j⟩ ⊗ (ancillas), every controlled-U^{±1} acts as a fixed diagonal with entries in {1, e^{±2πiλ_j}}, all other gates are λ-independent, so each output amplitude is a Laurent polynomial in e^{2πiλ_j} of degree ≤ #queries, hence continuous in λ_j. Requiring |α_{floor(2^n λ)}(λ)|² ≥ 1 − δ for *all* λ ∈ [0,1) forces the amplitude on |x⟩ to jump from ≥ 1−δ to ≤ δ across λ = (x+1)/2^n; impossible for δ < 1/2. Hence an exclusion zone around every rounding boundary (his Definition 1) is necessary for any coherent rounding protocol with constant confidence at every λ. Ta-Shma-style random shifts move the zone but do not remove it (his "dense spectrum" remark). Verdict on the claim: correct, provable, but cite it as "Rall 2021, Sec. 2, informal argument", not as a theorem.

### Guo et al. 2606.06316v1

Problem S2 (verbatim, App. B): "Define the ambiguous region S_Δ := {x ∈ Ω : Δ < P(x) ≤ (1+α)Δ}, with α > 0 a constant and total mass p_Δ := P(S_Δ). We write ζ := p_Δ/p_rare for the relative near-threshold ambiguity. Given a precision parameter ε > 0, the task is to construct a sampler whose output distribution P̃_R satisfies D_tv(P̃_R, P_R) = O(ε + ζ)." Theorem S4 (verbatim): "There exists a quantum algorithm that solves Problem S1 using O(max{1/√(p_1−p_2), 1/√p_rare}·(1/√Δ) log(1/ε)) queries to U_P …". Proof (verbatim): "we choose the ambiguity range as 0.2√Δ such that (√Δ + 0.2√Δ)² = 1.44Δ < 1.5Δ … approximated to error ε by an even polynomial P with degree O((1/√Δ) log(1/ε)), with t = 1.1√Δ and Γ = 0.1√Δ", and Lemma S2: "degree d scales as O((1/Γ) log(1/ε))". Theorem S5 (verbatim): "For any 0 < Δ < 1/4, any quantum algorithm that solves Problem S1 … requires Ω(1/√Δ) queries to U_P and U_P†". Guo et al. do not cite Rall (no occurrence of "Rall" in the text).

Contradiction? **No.** Guo et al. state "no promise" but their *problem definition* contains the promise's twin: arbitrary behaviour is allowed on S_Δ and its mass is charged to the output error ζ ("unavoidable ambiguity from near-threshold events", Fig. 2). This is precisely Rall's exclusion zone moved from an input promise to an output error term. The band is of constant relative width (α = 0.44–0.5 in the proof; the intro's "e.g., α = 0.001" would cost a factor 1/α in degree through Lemma S2's O(1/Γ)), and the O(1/√Δ) cost is the QSVT degree for a step of width Γ = 0.1√Δ in amplitude. Consistent with, indeed an instance of, Rall's argument.

Relevance to us: **none for the exact construction.** Our p(l|y) is computed by a reversible forward-recursion evaluator into a register; the comparison x < s in Theorem 49 is exact bit-string comparison, and there is no amplitude/phase estimation anywhere, hence no rounding promise. Rall/Guo become relevant only if someone replaces the evaluator by amplitude estimation of p(l|y); then near-ties within the estimation resolution form the ambiguity band and a runner-up in the band may be returned — the same effect as D > 1.

Verdict: **HOLDS (Rall, as an informal-but-valid argument); Guo et al. do not contradict it; neither bears on the exact-evaluator construction.**

---

## 5. de la Higuera & Oncina, ACL W11-2904 ("Computing the most probable string with a probabilistic finite state machine"), Property 2. Body-read (`pdfs/W11-2904.txt`).

Property 2 (verbatim): "For each n ≥ 0 there are at most 1/p strings u in Σⁿ such that Pr_A(uΣ*) ≥ p." Property 3 (verbatim): "If X is a set of strings such that (1) ∀u ∈ X, Pr_A(uΣ*) ≥ p and (2) no string in X is a prefix of another different string in X, then |X| ≤ 1/p." The paper: "Both proofs are straightforward and hold not only for PFA but for all distributions."

Proof (mine, since the paper omits it): for fixed n the events {uΣ*}, u ∈ Σⁿ, are pairwise disjoint (a string has exactly one length-n prefix, or none if shorter), so Σ_{u∈Σⁿ} Pr(uΣ*) ≤ 1 and at most 1/p of the terms can be ≥ p. Property 3: a prefix-free X gives pairwise-disjoint events, same argument. Both need only that Pr is a probability measure on Σ*.

Transfer to CTC: the label distribution p(·|y) is a probability measure on Σ* because B is a total map on paths and Σ_π ∏_t y[t][π_t] = ∏_t Σ_s y[t][s] = 1 (per-frame columns sum to 1). The CTC prefix probability P(uΣ*|y) = Σ_{π: B(π) ∈ uΣ*} p(π) is a genuine event probability, and it is exactly the quantity Graves' prefix search computes (the γ totals for a prefix). So Property 2 and 3 hold verbatim for CTC. **The transfer is valid.**

What the transfer does *not* give: |T_{p*}| = O(1/p*). The prefix tree T_{p*} = {u : P(uΣ*) ≥ p*} contains, at each depth, an antichain of size ≤ 1/p* (Property 2), so |T_{p*}| ≤ L_max/p* with L_max ≤ T_frames; its leaves number ≤ 1/p* (Property 3). The depth factor is tight: with |Σ| ≥ 1/p*, first symbol uniform over 1/p* symbols and the next L symbols deterministic, every depth ≤ L+1 carries 1/p* prefixes of probability p*, so |T_{p*}| = (L+1)/p*. The measured |T_{p*}| ≈ c/p* is therefore an empirical property of peaky CTC posteriors (the chain of the mode's own prefixes plus few competitors per depth), not a theorem; the provable statement is 1/p* ≤ |T_{p*}| ≤ L_max/p* and both ends are attainable. Graves' ≈ c/p* expansions inherit the same status.

Verdict: **HOLDS; transfer valid; the O(1/p*) tree-size claim must be labelled empirical (provable bound is L_max/p*).**

---

## 6. Chakrabarti et al. — arXiv:2210.03210v1 (6 Oct 2022; only version). Theorem 1.5. Body-read; pages 6–9 and 13 also inspected as rendered images.

Statement (page 6–7, verbatim): "Theorem 1.5 (Universal Speedup for Heuristic Tree Search). Consider a tree T rooted at r that is specified by a branch oracle, and a marking function f that marks at least one node. Suppose a classical algorithm A uses a Branch-Local heuristic h and returns a marked node n such that f(n) = 1, using Q(ε) queries to branch and f. Then there exists a quantum algorithm Incremental-Quantum-Tree-Search_A that offers the same guarantee with probability at least 1 − δ, using Õ(√(Q(ε)) d log(h_max) log²(log(T)/δ)) queries to branch and f, where d is the depth of T, T is an upper bound on the size of T, and h_max is an upper bound on the heur function associated with h." (d is *outside* the square root — confirmed on the rendered page.)

Proof (page 9, verbatim): "At each m we make Õ(d√(2^m) log(h_max) log²(log T/δ)) queries for QSubtree_A(·) and Õ(d√(4·2^m) log²(log T/δ)) queries for QuantumTreeSearch(·); leading to a total of Õ(d√(2^m) log(h_max) log²(log T/δ)). Across iteration the number of queries made is therefore Õ(d log(h_max) log²(log T/δ) Σ_{m=0}^{m_Q} √(2^m)) = Õ(d√(2^{m_Q}) log(h_max) log²(log T/δ)) (2.1)".

What is and is not wrong:
1. The arithmetic of the proof matches the statement (both Õ(√Q·d)); the geometric sum, the iteration count m_Q = ⌈log Q⌉, and the failure budget (2m_Q calls at δ/(4 log T) each, ≤ δ/2) are correct. The proof refers to "branch', cost'" — there is no cost oracle in Theorem 1.5 (copy-paste from Theorem 1.3); cosmetic.
2. **The chain rests on Primitive 1 (page 7, verbatim): "The first, due to Apers, et al. [27] makes O(√T d log(d) log(1/δ)) queries to branch and f. This is an improvement of an earlier algorithm due to Montanaro [20] makes O(√T d^{3/2} log(d) log(1/δ)) queries".** [27] = Apers, Gilyén, Jeffery, arXiv:1912.04233. Its Theorem 13 (verbatim, body-read): "(Electric network framework). Let P be any reversible Markov chain on a finite state space X, M ⊂ X a marked set, σ a distribution on X, and C a known upper bound on C_{σ,M}. There is a quantum algorithm that finds a marked element from M, or decides that it is empty, with bounded error in complexity O(√(log C) S(σ) + √(C log C) log log C (U(σ) + C))." with C_{σ,M} = W·R_{σ,M}. For a tree with T vertices, unit weights and root start, W = T − 1 and R ≤ depth n, so C ≤ Tn and the bound is O(√(Tn)·log(Tn) log log(Tn)) — the depth enters as √n, and C must be *known* (a doubling schedule adds a log). Chakrabarti's quote (√T·d) is neither AGJ's form nor its log factors; it is a different (weaker in d, different in logs) statement attributed to [27]. Their Remark 14 (verbatim): "A similar result, but restricted to the special case where the graph is a tree, can be found in the quantum algorithm for backtracking by Montanaro [Mon18] … this algorithm incurs an additional log factor for actually finding a solution". So the "Apers improvement to √T·d" is not what Apers et al. state; what they state is *stronger* in d. Theorem 1.5's d-dependence is therefore mis-sourced (it would follow, with √d instead of d, from AGJ Thm 13 plus a known C).
3. **Internal inconsistency in Primitive 3 (page 8, verbatim):** "Given a Branch-and-Bound tree … there exists an algorithm QuantumMinimumLeaf … that makes Õ(√T d log(c_max) log²(1/δ)) oracle calls … The guarantee follows from [22, Theorem 1]." But their own Theorem 1.1 (quoting [22, Theorem 1]) has failure dependence 1/δ², not log²(1/δ), and depth d^{3/2}; the reduction to d and log²(1/δ) is asserted via Primitive 1 (the mis-sourced item above) and never argued. Theorem 2.1 (Õ(d√(2^m) log(h_max) log²(1/δ))), hence Theorem 1.5, inherit this.
4. No later arXiv version exists (listing: "Submitted on 6 Oct 2022", [v1] only), so nothing has been fixed.

Verdict: **GAP-FOUND.** Theorem 1.5's proof is consistent with its own statement but its d- and δ-dependence are inherited from Primitive 1/3, whose attribution to [27]/[22] does not match those sources' theorems. Do not cite Theorem 1.5's bound as established; the underlying AGJ Theorem 13 gives Õ(√(Tn)) for tree search from the root with a known resistance bound, which is the citable statement.

---

## Files
- `citation-check/genmin_sim.py`, `citation-check/genmin_run.log`, `citation-check/genmin_results.json` — Algorithm 3 statevector simulation (command: `.venv/bin/python genmin_sim.py 1000`).
- `citation-check/checks.py`, `citation-check/checks.log` — inequalities (28), (30), Lemma 47 Monte Carlo, hybrid-oracle norm constant.
- `citation-check/pdfs/` — arXiv PDFs + text: 1705.01843v4, quant-ph/9607014v2, quant-ph/9605034, quant-ph/0005055, 1904.02192v1, 1711.05295v2, quant-ph/0303041, 1509.02374, 2103.09717v4, 2606.06316v1, 2210.03210v1, 1912.04233v1; rendered pages `chak-06..15.png`.

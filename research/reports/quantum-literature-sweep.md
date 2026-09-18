# Quantum literature sweep against C1–C6 (exact CTC decoding)

Date: 2026-09-18. Sources: WebSearch, arXiv API (export.arxiv.org, 35 keyword sweeps sorted by date; raw log `quantum-literature-sweep/arxiv_sweep1.txt`), Semantic Scholar citation graphs of 1509.02374, 1906.10375, 2210.03210, 1711.05295, 1912.04196, 2103.09717, 2207.08628, 2403.18927, 2508.06677, 1807.06456, 2208.07544, 1909.05023 (raw log `quantum-literature-sweep/s2_citations.txt`). PDFs saved in `quantum-literature-sweep/`. "Body" = pages read with the Read tool or pdftotext; "abs" = abstract only.

## (a) Headline

1. **Nothing published 2024–26 overturns C1–C6.** No new quantum tree-search bound beats Montanaro / Jarret–Wan / Ambainis–Kokainis / Chakrabarti et al.; no new hardness result for the memoryless-λ-chain mode (C6 stays open); Bausch et al. has zero algorithmic follow-ups.
2. **But an older primitive appears to dominate the C1 route and is not reflected in C3's "trivial classically too":** van Apeldoorn–Gilyén–Gribling–de Wolf, arXiv:1705.01843 App. C, *Generalized Minimum-Finding* (Theorem 49): with the Born-encoded product state + reversible collapse as the state-prep unitary U and the exact forward-recursion evaluator as the comparator, argmax_l p(l|y) costs **O(1/√p\*)** applications of U, U⁻¹ — no prefix tree, no QRAM/shift-register walk, and no √(c·D) factor. Matching Ω(1/√p\*) in the state-preparation model follows from Belovs 1904.02192 (Θ(1/d_H) distinguishing) / Wang–Zhang 2308.01794 lifting. This should be checked against the C1 units-equalised gate (see §2).
3. **C2's *reason* needs rewording, not its conclusion:** Guo et al. arXiv:2606.06316 (June 2026, body-read) implements coherent amplitude *thresholding* with no rounding promise (QSVT Heaviside with a relative ambiguity band [Δ,(1+α)Δ]) at cost O(1/√Δ) per application and proves Ω(1/√Δ) optimal. Nesting it in AA gives O(1/√(p_marked·Δ)) → O(1/p\*) for mode-finding — i.e. the block is *cost*, not impossibility.

---

## (b) Search areas

### 1. Quantum tree search / backtracking / B&B / divide-and-conquer / DP (2023–26)

| arXiv | Year | One-line result | Affects | Read |
|---|---|---|---|---|
| 2505.22405 | 2025 | Variable-time backtracking: O(√(T·D)) with T=Σt_v² (known to us) | C1 (no change) | abs |
| 2606.28452 (Wichert) | 2026 | Grover-style tree search "√(b_avg^m)" instead of √(b_max^m); no O-notation, no comparison to Montanaro; heuristic padding arguments | C1 (none) | body pp.1–12 |
| 2509.07041 (Wichert) | 2025 | Nested Grover for tree search with "partial candidate solution" oracle; no bound beating Montanaro | C1 (none) | abs |
| 2504.15194 (Li–Li–Luo) | 2025 | Quantum phase discrimination; spatial search on any graph in O(1/√ε) queries, ε = marked fraction — for prefix tree this is ≥ Montanaro's √(T·D) | C1 (none) | abs |
| 2504.02115 (Cornelissen) | 2025/26 | Graph-composition framework subsumes part of quantum D&C; shows weighted-decision-tree power ≤ quadratic over deterministic query complexity — a *ceiling*, consistent with C1 | C1 (strengthens the "at most quadratic" framing) | abs |
| 2605.30013 (Apers–Roland–Zhang) | 2026 | Zero-error transducers for electric-flow sampling; improved effective-resistance estimation — engineering of the same O(√(RW)) bound | C1 (none) | abs |
| 2311.15873 / 2401.08355 (Belovs–Jeffery–Yolcu; Jeffery–Pass) | 2023/24 | Time-efficient composition/transducers; time-efficient quantum D&C when subproblems combine via Boolean formula | C1 (removes log factors only) | abs |
| 2311.16401 (Allcock et al.) ICALP'25 | 2023 | Time complexity of quantum D&C; applications: Longest Distinct Substring, k-Increasing Subsequence, Klee — none is a sum-over-alignments DP | C1 (none) | abs |
| 2507.00823 (Caroppo et al.) | 2025 | **Quantum DP framework**: table-driven DP with op∈{min,max,find,findAll} runs in Õ(\|V(G_P)\|·(T'+T_P√δ)), δ = avg dependency degree; Table 1 lists "Viterbi Path Problem O(T·\|S\|²) → Õ(T·\|S\|·√\|S\|)" | C1/C6 (none: CTC forward recursion has δ≈3 and is a *sum*, not min/max; prefix-tree DP has exponential \|V\|) | body pp.1–14 |
| 2403.09187 | 2024 | "Quantum dynamic programming" = coherent recursion-step unitaries from memorised states; not classical DP speedup | none | abs |
| 2412.13274 (Brehm–Weggemans, Quantum 2025) | 2024/26 | Hybrid benchmarking of quantum backtracking vs CaDiCaL on structured k-SAT: "almost all quantum speedups vanish, even asymptotically, when minimal structure is introduced or when T-count is considered instead of T-depth"; explicit constants for Belovs detection (~100× better than prior configs); search adds O(n² log n) | C1 (strengthens the units-equalised pessimism) | body pp.1–8 |
| 1704.06774 (Ambainis–Kokainis) | 2017 | Õ(√T·n^{3/2}) quantum backtracking relative to the classical *explored* tree T, no a-priori T | C1 (already implied by our c/p\* framing; not in our citation list) | abs |
| 2511.19501, 2509.11040, 2407.20185 | 2024–25 | Hybrid/QUBO branch-and-bound; no query-complexity improvements | none | abs |

Quote (2507.00823, Theorem 2, body): "If op ∈ {find, min, max}, then Q_A solves P for I using Õ(|V(G_P(I))|(T' + T_P√δ)) time and Õ(|V(G_P(I))|) space." — inapplicable to the CTC objective (sum over alignments), and the prefix-tree "DP" has |V| exponential, so it does not change C1.

Quote (2412.13274, abstract, body): "when the requirement is for the algorithm to find a solution within a single day, we find that only Grover's algorithm has the potential to outperform classical algorithms, but only in a very limited regime and only when using T-depth."

**Verdict:** C1's exponent stands: best known is still Õ(√(c·D/p\*)) node visits for the *tree* route (Chakrabarti et al.; Ambainis–Kokainis). But see §2: the tree route is not the best quantum route.

### 2. Mode / heavy-hitter / argmax finding from a state-preparation oracle

| arXiv | Year | One-line result | Affects | Read |
|---|---|---|---|---|
| **1705.01843 (vAGGdW), App. C** | 2017 | **Theorem 49 (Generalized Minimum-Finding)**: given U\|0⟩ = Σ_k \|ψ_k⟩\|x_k⟩, finds min x_k with prob ≥ 3/4 using M ≥ 4C/√Pr(X ≤ x) applications of U, U⁻¹ (C ≈ 25), O(qM) other gates | **C1, C3** | body (pdftotext App. C) |
| quant-ph/0005055 (BHMT) Thm 3 | 2000 | QSearch from arbitrary A: expected Θ(1/√a) applications of A, A⁻¹ without knowing a | C3 (the AA-from-biased-state primitive) | body pp.1–8 |
| 1904.02192 (Belovs) | 2019 | Distinguishing p vs q in the state-prep model costs Θ(1/d_H(p,q)) (classical Θ(1/d_H²)) | lower bound for mode-finding: Ω(1/√p\*) | body (abstract+intro) |
| 2308.01794 (Wang–Zhang) | 2023/25 | Sample-to-query lifting: quadratic relation between quantum sample and query complexity for state-prep+inverse access | same lower bound, alternative route | abs |
| **2606.06316 (Guo, Huang, Wang, Thompson, Rebentrost, Gu, Yang)** | 2026 | Rare-event sampling: prepare \|P_R⟩ ∝ Σ_{P(x)≤Δ}√P(x)\|x⟩ with O(1/√(p_rare·Δ)·log 1/ε) uses of U_P, U_P†; Ω(1/√Δ) lower bound; QSVT Heaviside with ambiguity band | **C2 (reason)**, area-2 question | body pp.1–12 |
| 2605.03685 (Chen, Gao, Li, Wang, Wang) | 2026 | Non-destructive singular-value discrimination to bin p_i into geometric intervals with 4 ancillas; functionals Σf(p_i) | C2 (same toolkit; no mode-finder) | body pp.1–6 |
| 1710.06025 (Li–Wu) | 2017 | Quantum min-entropy (α=∞) *estimation* upper bounds — estimates p\*, does not return argmax | none directly | abs |
| 2302.10244 (van Apeldoorn–Gribling–Nieuwboer) | 2023 | Find all k marked in O(√(Nk)) queries with polylog gate overhead | C4 (top-k per level, engineering) | abs |
| 1807.06456 (Hamoudi–Magniez) | 2018 | Quantum Chebyshev: relative-error mean with O(√Var/mean) samples; applications are frequency moments, edge/triangle counting — **no mode application** | none | abs (checked application list) |
| 2504.06940 | 2025 | Multivariate mean estimation w/o polylog | area 6 | abs |

Quotes (1705.01843, body):
> "Suppose we have a unitary U which prepares a quantum state U|0⟩ = Σ_{k=1}^N |ψ_k⟩|x_k⟩, where the |ψ_k⟩ are unnormalized states. Our procedure can find the minimum value x_{k*} among the x_k's that have support in the second register, using roughly O(1/‖ψ_{k*}‖) applications of U and U⁻¹. … Unlike Dürr-Høyer, we need not assume direct query access to the individual values f(k)."
> "Lemma 48. There exists C ∈ ℝ+, such that if we run Algorithm 3 indefinitely (setting M = ∞), then for every U and x_k the expected number of uses of U and U⁻¹ before obtaining a sample x ≤ x_k is at most C/√Pr(X ≤ x_k)."
> "Theorem 49 (Generalized Minimum-Finding). If we run Algorithm 3 with input satisfying M ≥ 4C/√Pr(X ≤ x) for C as in Lemma 48 and a unitary U that acts on q qubits, then at termination we obtain an x_i from the range of X that satisfies x_i ≤ x with probability at least 3/4. … This uses at most M applications of U and U⁻¹ and O(qM) other gates." "… something like C ≈ 25."

**Application to CTC (my derivation, to be checked against the existing analysis):**
- U = (product state ⊗_t Σ_a √y[t][a]|a⟩) ∘ (reversible collapse π ↦ B(π) into a label register) ∘ (reversible forward recursion computing x_l := −p(l|y) into a value register). Then U|0⟩ = Σ_l |ψ_l⟩|−p_l⟩ with ‖ψ_l‖² = p_l, so Pr(X ≤ x_min) = p\*.
- Theorem 49 ⇒ argmax found with O(1/√p\*) applications of U, U⁻¹, each costing O(T·W) (state prep) + O(T) (collapse) + O(T·D) (evaluator, fixed-point) reversible gates. Total **Õ(T·(W+D)/√p\*)**, no tree walk, no QRAM.
- Versus C1's tree route Õ(√(c·D/p\*)) visits × O(T·D): saves the √(c·D) factor (≈6 for D=20) and the 56 % QRAM/shift-register overhead.
- Units-equalised gate vs classical prefix search (c/p\*)·O(T): quantum wins when √p\* < c/(W+D) ⇒ **p\* < (c/(W+D))²** (≈1.3·10⁻³ for c=1.8, W=30, D=20; ≈2·10⁻⁶ if the C≈25 constant is included). Compare C1's gate p\* < c/D³ ≈ 2·10⁻⁴. Advantage remains confined to low-confidence utterances but the route is simpler and D-independent in count.
- Lower bound: in the state-prep model, identifying which of two labels carries mass p\* is distinguishing two distributions with d_H ≍ √p\*, so Θ(1/√p\*) by Belovs (1904.02192): "query complexity of this problem is Θ(1/d_H(p,q))". Hence Õ(1/√p\*) is optimal *for black-box access*; for the white-box CTC table no unconditional bound exists (ties to C6).

Quotes (2606.06316, body):
> "Result 3 (Quantum rare event sampling). Given a quantum sampler U_P for a probability distribution P over N events, for any ε > 0, O(1/√(p_rare Δ) · log(1/ε)) applications of U_P suffice to prepare and measure a quantum state, yielding an event from a distribution O(ζ+ε)-close to P_R in total variation distance, where ζ = p_Δ/p_rare."
> "Result 4 (Optimality of quantum rare event sampling). For Δ > 0, any quantum algorithm requires Ω(1/√Δ) applications of U_P to construct a sampler for P_R."
> "The non-smooth Heaviside function is approximated by a polynomial of degree O(1/√Δ log(1/ε)) … This approximation has a finite transition width of O(α√Δ) around the threshold √Δ, which corresponds directly to the ambiguous set S_Δ."
> "Even multidimensional quantum amplitude estimation [14], while more efficient at identifying multiple outcomes, still requires O(1/Δ) applications of U_P to estimate probabilities with precision O(Δ), which we prove to be suboptimal, and provides no scaling advantage."

Implication for area-2 question: *without* an exact evaluator, coherent amplitude-thresholding at level Δ≈p\* costs O(1/√Δ) per reflection, so mode-finding via nested thresholding is O(1/p\*) — no speedup, and Result 4 shows the thresholding step itself is tight. *With* the exact evaluator (our case), Theorem 49 gives O(1/√p\*).

### 3. Coherent / non-destructive amplitude estimation (2024–26)

| arXiv | Year | One-line result | Affects | Read |
|---|---|---|---|---|
| 2606.06316 | 2026 | Coherent threshold on amplitudes with ambiguity band; no rounding promise; Ω(1/√Δ) | C2 (reason) | body |
| 2605.03685 | 2026 | Non-destructive singular-value discrimination into geometric bins with constant ancillas, replaces VTAE control overhead | C2 (toolkit) | body pp.1–6 |
| 2602.08120 (Sun–Wang–Blanchet) | 2026 | Repeatedly nested *expectation* estimation in Õ(1/ε) via derandomised MLMC; "rMLMC is inherently a variable-time algorithm: its random truncation level induces a random runtime … interacts poorly with amplitude amplification" | C2 (classical-output nesting only; not coherent) | body pp.1–4 |
| 2507.23787 (Tang–Wright) | 2025 | AA/AE need U⁻¹; without inverse access no speedup | none (we have circuits) | abs |
| 2608.24434, 2603.05475, 2609.02715, 2405.14697, 2508.05805 | 2024–26 | Low-depth / ancilla-free AE variants; all measure | C2 (none) | abs |
| 2609.07604 (Bernoulli-oracle counting) | 2026 | QSVT "coherently amplify the bias gap without collapsing the superposition", then AE; Õ(√ρ/(Δε)+1/(Δ√ε)) with near-matching adversary lower bound | C2 (same gap-based coherent-marking pattern; confirms cost ∝ 1/Δ) | abs |
| 2305.04908 (Mande–de Wolf) | 2023 | Tight bounds for phase estimation incl. max-eigenphase with advice states; error reduction costs full log(1/ε) | C2 (lower-bound context) | abs |

**Verdict:** No paper removes the promise for coherent *estimation* into a register; the 2026 papers all route around it with *discrimination/threshold* polynomials and pay the 1/√Δ (or 1/Δ) gap cost. C2's conclusion holds; its stated mechanism should read "threshold marking is possible without a promise (Guo et al. 2606.06316, Chen et al. 2605.03685) but costs O(1/√Δ) per reflection with an unavoidable relative ambiguity band, so nesting inside AA yields O(1/√(p_marked Δ)) ≥ classical".

### 4. Quantum decoding / sequence models (2020–26)

| arXiv | Year | One-line result | Affects | Read |
|---|---|---|---|---|
| 1909.05023 citations (S2: 18) | 2020–26 | All QNLP/lambeq/overview/QNN papers; **zero** algorithmic follow-ups to the quantum search decoder | C5 (unchanged) | list checked |
| 2605.18912 (Accardi et al.) | 2026 | "Quantum Viterbi" for *hidden quantum Markov models*; no complexity statement; not classical decoding | none | abs |
| 1405.7479 | 2014 | Quantum Viterbi for convolutional codes via fanout-dependent AA | none (known class) | abs |
| 2411.04727 | 2024 | Polar ML decoding via Grover adaptive search — pure quadratic over brute force | none (same as C5 pattern) | abs |
| 2304.02292 | 2023 | QAOA for trellis Viterbi | none | abs |
| 2606.30415 | 2026 | Neutral-atom MWIS inside MCTS (heuristic) | none | abs |

arXiv sweeps for "quantum beam search", "quantum CTC/connectionist temporal classification", "quantum A\*/best-first", "quantum MAP inference", "quantum speech recognition decoding" returned nothing new (only 1909.05023 itself).

### 5. Complexity of most-probable-string / trace mode (2015–26)

| ref | Year | One-line result | Affects | Read |
|---|---|---|---|---|
| 1711.05408 (Chen, Gilroy, Maletti, May, Knight) | 2017/18 | Best-string for RNN LMs undecidable; consistent RNN decidable; **Theorem 11: polynomial-length best string in a consistent RNN is NP-complete and APX-hard** (reduction from 0-1 ILP feasibility); Table 1: Nondet. PFSA/PCFG best-string NP-c [Casacuberta–de la Higuera 2000; Sima'an 1996] | C6 (context only; not memoryless) | body pp.1–6 + Thm 11 text |
| 1210.2587 (Nánási–Vinař–Brejová) | 2012 | NP-hardness of most-probable *footprint*/state-set/ball decoding in HMMs — not the most-likely-string | C6 (none) | grep |
| 2004.06581 (Gutiérrez et al.) | 2020 | Restates: weight maximisation undecidable for general WA; "NP-complete … with weights over ℤ and just two alphabet symbols"; probabilistic case NP-hard (Casacuberta–de la Higuera) | C6 (none new) | abs |
| de la Higuera–Oncina, J. Logic & Comput. 2014 | 2013/14 | Pseudo-polynomial algorithm for most probable string, poly in 1/p\* — classical analogue of our c/p\* baseline | C6/C1 (baseline context) | abs (WebSearch) |
| 2005.14388, 2012.06713, 2107.09497 | 2020–21 | Trace reconstruction: ML over deletion channels; hardness only via SCS for many traces | C6 (none) | abs |
| 2603.11332 (Saha et al.) | 2026 | Hardness of *attention computation* (SETH), not decoding | none | abs |

**Verdict:** No 2015–26 result addresses the memoryless λ-chain (product slots + collapse/deletion) specifically. C6 remains open. The tightest neighbours are still Casacuberta–de la Higuera (nondet. PFSA) and the RNN result above — both rely on state/nondeterminism that the memoryless chain lacks.

### 6. Multivariate mean estimation / expected-utility / MBR-style objectives

| arXiv | Year | One-line result | Affects | Read |
|---|---|---|---|---|
| 2208.07544 (Cornelissen–Hamoudi–Jerbi) | 2022 | Near-optimal multivariate mean estimation (known) | reframing lane baseline | abs |
| 2504.06940 (Tang) | 2025 | Removes polylog factors via generalized Grover operator; Õ(n log(d/δ)) samples for ℓ∞ error √tr Σ / n | reframing lane | abs |
| 2602.08120 | 2026 | Õ(1/ε) nested expectations, optimal stopping | reframing lane (MBR = E_l~p[utility] is a *single* nesting: standard QMC) | body pp.1–4 |
| 2609.03625 (Recchia et al.) | 2026 | Quantum quasi-MC: no asymptotic gain, pre-asymptotic window only | reframing lane (caution) | abs |
| 2609.07604 | 2026 | Counting with Bernoulli oracles | — | abs |
| "quantum minimum Bayes risk" | — | **no hits** on arXiv/web | — | — |

---

## (c) What we missed (candidates for the analysis to absorb)

1. **vAGGdW Theorem 49 route** (1705.01843, App. C): argmax via generalized minimum-finding over the Born-encoded state with the exact evaluator as comparator — O(1/√p\*) applications, no tree, no QRAM. C3's "trivial classically too" only covers *sampling*; the quantum version is the Grover-of-sampling and (by my arithmetic above) beats the C1 tree route by √(c·D) and improves the units-equalised gate from p\*<c/D³ to p\*<(c/(W+D))². Needs an independent check of the per-application cost model and of the C≈25 constant.
2. **Ω(1/√p\*) black-box lower bound for mode-finding** from Belovs 1904.02192 (Θ(1/d_H) distinguishing) — answers the area-2 question; not previously cited.
3. **Ambainis–Kokainis 1704.06774** (Õ(√T·n^{3/2}) relative to the classical explored tree) is the origin of the "c/p\*" framing and predates Chakrabarti et al.; worth citing alongside 2210.03210.
4. **Guo et al. 2606.06316** and **Chen et al. 2605.03685**: coherent thresholding without a rounding promise is now standard (QSVT Heaviside with relative band; non-destructive SV discrimination). C2 should cite them and restate the block as a cost bound.
5. **Brehm–Weggemans 2412.13274 (Quantum 2025)**: concrete evidence that quantum backtracking's speedup evaporates under structure/T-count; useful as an external anchor for C1's pessimism and for the QRAM/shift-register overhead argument.
6. **Caroppo et al. 2507.00823**: makes explicit that quantum DP speedups need a min/max/find recurrence with large average dependency degree; CTC's sum-recurrence with δ≈3 gets nothing — a clean citation for why the forward recursion itself cannot be Grover-accelerated.
7. **Chen et al. 1711.05408 Thm 11** (NP-complete, APX-hard best-string for consistent RNNs at polynomial length) — the closest modern hardness neighbour for LM-fused decoding; not applicable to the pure memoryless chain but relevant if an LM is fused.
8. Empty spaces confirmed: no "quantum beam search", "quantum A\*", "quantum MBR", "quantum CTC" literature exists as of 2026-09-18.

## (d) Next reads

- 1705.01843 App. C in full (Algorithm 3, proof of Lemma 48 incl. the constant) and Boyer–Brassard–Høyer–Tapp exponential search (quant-ph/9605034) to pin the constant for the C1-vs-Theorem-49 comparison.
- 2606.06316 App. D.2 (pp. 16–21) and App. E.2 "Related works" — for the exact QSVT degree and whether they discuss the *heavy*-event direction.
- 2605.03685 §3.1 (pp. 12–14) non-destructive singular value discrimination lemma — cheapest coherent threshold primitive if the evaluator is ever replaced by AE.
- 2412.13274 App. A.2–A.3 — explicit constants for Belovs-walk detection/search, reusable for the C1 per-node cost table.
- 2305.04908 (Mande–de Wolf) §on max-eigenphase with advice — potential template for a lower bound on "argmax amplitude with a state-prep oracle".
- 2504.02115 (Cornelissen) §on weighted decision trees vs deterministic query complexity — the formal "at most quadratic" ceiling for C1.
- de la Higuera–Oncina 2014 (JLC) full text — to check whether their pseudo-polynomial algorithm's dependence on 1/p\* is tighter than Graves' c/p\* for the memoryless special case.

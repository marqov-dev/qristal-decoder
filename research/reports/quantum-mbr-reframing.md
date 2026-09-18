# Reframing the QB decoder machinery: quantum Minimum-Bayes-Risk decoding of CTC posteriors

**Date:** 2026-09-18 · **Scope:** conjecture D2 ("right machine, wrong objective") · **Status:** measured, gated, cited.
Code and logs: `quantum-mbr-reframing/` (`mbr.py` gate, `measure.py` synthetic, `measure2.py` real posteriors, `resources.py` resource count, `dump_posteriors.py`). Toolkit used read-only: the validation toolkit `ctc.py` (included as `../code/certified-exact-decoder/ctc.py`).

## (a) Headline

1. **The reframing is technically sound and the query-count claim is genuinely unconditional**: expected edit distance under a CTC posterior has no known polynomial exact evaluator (Calvo-Zaragoza–de la Higuera–Oncina 2016: exact is exponential in |l|, "we conjecture it is NP-hard", the polynomial route is an FPRAS = Monte Carlo), our product-state + collapsing-map sampler is a unitary, a reversible Levenshtein oracle exists, so Montanaro/Kothari–O'Donnell mean estimation gives Õ(σ/ε) vs Θ(σ²/ε²) with no structural assumption — and no paper does this (0 hits in 5 searches).
2. **But the precision it buys is decision-irrelevant on the only objective the machine can serve**: on real wav2vec2 posteriors at 5 dB the MBR winner beats the runner-up by a median 1.6e-4 in normalised utility (≈ 0.01 of a character on a 57-character utterance); the MBR and MAP transcripts differ by ≤ 1 edit and have identical mean CER (0.361 vs 0.361); op-parity crossover needs ε ≈ 2e-5 (0.003 character) while a decision-relevant ε (half a character) needs ~10 classical samples.
3. **Verdict: not a defensible advantage claim.** Where MBR measurably helps ASR (Whisper: −27% rel. WER at 5 dB; Novosad: −0.54 pp on CTC) the reference distribution is non-product (tempered / LM-augmented) or the utility is a neural metric — which removes the cheap sampler or the cheap oracle. Under the bare acoustic posterior with Levenshtein utility — the one case our machine handles — published MBR gains are nil (Novosad: −0.035 pp, p = 0.16) and ours are nil at 5 dB and +1.9 pp CER on 70%-CER garbage at 0 dB.

## (b) MBR-CTC formalised, the classical state of the art, and whether MBR helps on hard audio

### Definition

Given the CTC posterior p(l | y) = Σ_{π∈B⁻¹(l)} ∏_t y[t][π_t] (Graves et al. 2006, doi:10.1145/1143844.1143891), a utility u : Σ* × Σ* → [0,1], and a candidate set C ⊂ Σ*, the MBR / consensus decision is

  l̂_MBR = argmax_{l∈C} μ(l),  μ(l) := E_{l'~p(·|y)}[u(l, l')] = Σ_{l'} p(l'|y) u(l, l').

We use u(l,l') = 1 − ED(l,l')/max(|l|,|l'|,1) (normalised Levenshtein; "1 − CER of l against pseudo-reference l'"). MAP is the special case u = 1{l = l'}, for which μ(l) = p(l|y) (Kumar & Byrne 2004, NAACL N04-1022; Eikema & Aziz 2022 §2, body-read: "for the 'exact match' utility … the expected utility of h is p(h|x,θ), hence MBR and MAP decoding have the same optimum"). With edit-distance utility the objective is neither a product over frames nor prefix-decomposable: ED(l, l') is a min over alignments, so no admissible prefix bound of the Graves prefix-search kind exists. Xu, Povey, Mangu & Zhu 2011 (CSL 25(4):802–828, body-read) say exactly this: "The difficulty is largely due to the non-local nature of the Levenshtein edit distance. When more 'local' risk measures based on counting N-grams are used … efficient exact solutions may be obtained … When the Levenshtein edit distance is the risk measure, a solution to the decoding problem is only easy to describe when working with N-best sentence lists; however, the length of such a list required to cover all word confusions … is expected to grow exponentially with the utterance length."

### Is μ(l) exactly computable? (the fact the whole analysis turns on)

A CTC posterior is a probabilistic finite-state automaton (PFA) with O(T·W) states (frame index × last symbol), so the question "compute μ(l) exactly" is the problem **EDD** of Calvo-Zaragoza, de la Higuera & Oncina, *Computing the expected edit distance from a string to a PFA*, CIAA 2016 (LNCS 9705, pp. 39–50; extended IJFCS 28(5):603–621, 2017, doi:10.1142/S0129054117400093) — **body-read** (Alicante repository copy). Verbatim:

- "The first is exact but has a cost which can be exponential in the length of the input string, whereas the second is a Fpras." (abstract)
- "The construction involves building a multiplicity automaton which can be of size exponential in the length of the string w, but only increases polynomially with the number of states of the Pfa or the size of the alphabet."
- "The exact status of EDD is an open question. We conjecture it is NP-hard." (§2.4)
- Theorem 2: "There exists an Fpras computing the expected distance between a string and a distribution given by a Pfa." — and the FPRAS is plain Monte Carlo: "Algorithm Build Sample … generate a string of length at most L, using AD and add it to S" with N polynomial in 1/ε.

So: **no polynomial exact evaluator for μ(l) is known; the polynomial route is sampling, with classical cost Θ(σ²/ε²).** That is precisely the setting in which quantum mean estimation gives its unconditional quadratic advantage (task 4 criterion). It is also what practice does:

### Classical state of the art and cost

| Method | What it evaluates | Cost | Source |
|---|---|---|---|
| N-best / sampling MBR (MT and modern ASR) | μ̂(l) by Monte Carlo over S pseudo-references, for N candidates | O(N·S·U) utility calls; N = S gives O(N²·U) | Eikema & Aziz 2022 (arXiv:2108.04718, EMNLP 2022, body-read: "MBR_N-by-N runs in time O(N²×U)"; "the quadratic cost prevents us from sufficiently exploring the space"); Jinnai 2025 (arXiv:2510.19471, body-read: "The complexity is O(UN²+GN)"; whisper-large-v3: beam B=20 1.56 s vs MBR N=64 30.18 s per utterance) |
| Lattice consensus (confusion networks) | expected word error via an alignment-clustered approximation | polynomial, biased | Mangu, Brill & Stolcke 2000 (CSL 14:373–400, arXiv:cs/0010012, body-read) |
| Lattice recursion (Xu–Povey) | an **upper bound** on the expected Levenshtein distance | polynomial (Levenshtein DP × forward-backward), deterministic, biased | Xu et al. 2011 (body-read: "We prove that the approximated lattice edit distance L̂ … is an upper bound on the true edit distance averaged over the paths in the lattice") |
| Exact | μ(l) | exponential in |l| (multiplicity-automaton construction) | Calvo-Zaragoza et al. 2016 (body-read) |
| Search over all of Σ* (median string) | argmin over unconstrained l | NP-hard | de la Higuera & Casacuberta 2000, TCS 230:39–48 (abstract-only) |

Practitioners' sample sizes: Mangu et al. N-best cutoff 300 ("increasing … to 1000 did not give significant error reductions"); Eikema & Aziz 1,000 samples for "robust" estimates, 100 in the coarse step; Jinnai 2025 N = 64; Deguchi et al. 2026 |Z| = 64 or 256 CTC-path samples; Novosad 2026 G = 4…128.

### Does MBR beat MAP on hard audio? Numbers

Yes for lattice/HMM systems and for Whisper-class attention models, with the gain concentrated on high-WER conditions; **no measurable gain when the posterior is a peaky CTC posterior used alone.**

- Mangu et al. 2000 (body-read), Switchboard Set I/II: MAP 38.5/42.9 → N-best centre 37.9/42.3 → lattice consensus 37.3/41.6 %WER ("absolute WER reduction of 1.2% … statistically significant at the 0.0001 level"); Broadcast News overall 33.1 → 32.5; noisy F4 22.8 → 22.3, non-native F5 52.3 → 51.8; "the larger gains over the MAP hypothesis come from the longer utterances" (long: 31.5 → 30.8). SER *rises* (65.3 → 65.8) — by design.
- Xu et al. 2011 (body-read), English BN MPE: MAP 24.68 → Consensus 24.37 → proposed 24.28 %WER; Mandarin CER 17.15 → 16.74/16.76; **Arabic at 12.9% WER: no gain** ("in our experience it does not typically help at very low Word Error Rates").
- Jinnai 2025 (arXiv:2510.19471, body-read), whisper-large-v3 on LibriSpeech + MUSAN noise, Table 4 verbatim: SNR −20/−15/−10/−5/0/5/10/15/20 dB — Beam B=20: 0.590/0.444/0.284/0.151/0.082/0.056/0.049/0.048/0.045; MBR N=64: 0.530/0.388/0.235/0.108/0.057/0.041/0.035/0.036/0.034. At 5 dB: 0.056 → 0.041 (−27% rel); at 0 dB: 0.082 → 0.057 (−30% rel). "MBR decoding is more accurate than beam search at any noise level."
- Deguchi, Kano, Chousa & Delcroix 2026 (arXiv:2606.17537, body-read), Mask-CTC NAR + MBR with CTC-path sampling, |Z| = 64: LibriSpeech other 7.4 → 7.1, Switchboard Callhome 15.7 → 14.9, AMI 18.9 → 18.1 (all marked significant at p<0.05). Note this is a *NAR/CTC hybrid* whose samples come from Mask-CTC iterations, not from the raw acoustic CTC posterior alone.
- **The negative result that matters for us.** Novosad 2026, *The Anatomy of the CTC Oracle Gap* (arXiv:2606.23306, body-read via HTML), Zipformer-S CR-CTC on LibriSpeech dev-other, G = 16: greedy 6.022%, oracle 4.442%; **MBR-CER with the CTC posterior alone (best temperature τ = 50): 5.987%, Δ = −0.035 pp, p = 0.163, not significant**; MBR-CER with a RoBERTa pseudo-log-likelihood posterior: 5.79% (p<0.0001); test-other G=128: 5.96 → 5.42%. Verbatim: "CTC posteriors at unit temperature are sharply peaked around the greedy output, so MBR degenerates to the mode of that distribution — which coincides with greedy by construction." And Jinnai 2025 §Limitations verbatim: "We also attempted to apply MBR decoding to Wav2Vec 2.0 (Baevski et al., 2020), a CTC-based model. CTC models produce extremely peaked per-frame probability distributions: random sampling yields the same result as greedy (MAP) decoding unless the temperature is raised to a level that severely degrades output quality. Consequently, MBR decoding is not directly applicable to CTC-based models in their standard configuration."

So the literature says: MBR wins where the posterior is diffuse *and* calibrated (attention/Whisper, HMM lattices with LM); on a bare CTC acoustic posterior the only published attempt (Novosad, G ≤ 128, dev-other) finds nothing significant, and the gain appears only once an external LM is folded into the reference distribution. Our own measurement below (section d) is on noisier audio (5 dB / 0 dB white noise, wav2vec2-base, frame confidence 0.81–0.95), where the posterior is *not* degenerate — 2,000 of 2,000 samples are distinct — and still finds the MBR/MAP difference to be decision-irrelevant.

## (c) The quantum MBR-CTC algorithm, with the coherence boundary drawn

**Inputs.** Posterior table y (T×W), fixed candidate l (classical), utility u, precision ε, failure δ.

**Step 0 — candidates (classical).** Draw N_c paths from the product measure (each frame independently), collapse with B, keep the top-K most frequent; union with the top-K of an exact prefix beam (the MAP side). This is ordinary Born-rule sampling of |Ψ⟩ (or classical sampling of the product measure — identical distribution, and classically trivial: O(T log W) per sample). Nothing coherent is needed here.

**Step 1 — state preparation U (coherent).** |Ψ⟩ = ⊗_t (Σ_s √y[t][s] |s⟩_t) followed by the reversible collapsing map B: |π⟩|0⟩ ↦ |π⟩|B(π)⟩. This is our C3 construction (product state + B; QB's `RyEncoding` + coherent `decoder_kernel` collapse). Measuring the |B(π)⟩ register gives Pr[l'] = p(l'|y) — the Born rule does the preimage sum.

**Step 2 — utility oracle (coherent, reversible).** A circuit computing |l'⟩|0⟩ ↦ |l'⟩|u(l,l')⟩ for the fixed classical l: Wagner–Fischer DP with b-bit cells, min of three b-bit values per cell, symbol equality on log₂W bits. Two choices: (i) run the DP over the *compacted* register |B(π)⟩ — |l|·|l'| cells but needs the pointer-addressed compaction inside B; (ii) run it directly over the path register with a per-frame "emitted" flag — |l|·T cells, no compaction. We cost (ii) in section (f). Then encode u into an ancilla amplitude: |u⟩|0⟩ ↦ |u⟩(√(1−u)|0⟩ + √u|1⟩) via a 2^b-entry QROM of angles. The whole thing is one unitary A = (encode)(ED)(B)(prep) with ⟨1|A|0⟩-amplitude² = μ(l).

**Step 3 — mean estimation (coherent inner loop, classical output).** Amplitude estimation on A (Brassard–Høyer–Mosca–Tapp, arXiv:quant-ph/0005055) or, equivalently, Montanaro's Algorithm 1 for [0,1]-bounded variables (arXiv:1504.06987, Thm 2.3/Alg 1, abstract + prior body-read in this programme: "estimates the mean … up to additive error ε with 99% success probability using the subroutine only Õ(σ/ε) times"), or Kothari & O'Donnell, *Mean estimation when you have the source code; or, quantum Monte Carlo methods* (arXiv:2208.07544, SODA 2023, abstract-read: with "O(n) runs" of the code the estimate satisfies |μ̂ − μ| ≤ σ/n, versus classical σ/√n). Output: a classical number μ̂(l) with |μ̂ − μ| ≤ ε w.p. ≥ 1−δ, using O((σ/ε)·log(1/δ)) applications of A and A†. [Correction to the task brief: arXiv:2208.07544 is Kothari–O'Donnell; the multivariate paper of Cornelissen, Hamoudi & Jerbi is arXiv:2111.09787 (STOC 2022). Univariate suffices here.]

**Better: estimate the difference directly.** The decision only needs sign(μ(l₁) − μ(l₂)). A circuit computing d = u(l₁,l') − u(l₂,l') ∈ [−1,1] on the *same* |l'⟩ (two DPs) turns the pairwise comparison into one mean estimation with the *paired* standard deviation σ_diff, which we measure to be 2–5× smaller than σ_u. Classical Monte Carlo gets the same benefit for free by common random numbers (Eikema & Aziz's "fixed set of S samples … for each candidate"), so we cost both sides with σ_diff.

**Step 4 — outer loop (classical).** Keep the argmax over C classical: |C|−1 pairwise comparisons against the running best (or estimate all |C| means to ε = gap/2). We deliberately do **not** nest Dürr–Høyer minimum finding (arXiv:quant-ph/9607014, O(√|C|)) over the mean estimates: the estimates are measured classical numbers, and using them inside a coherent comparator would require a coherent, exact-rounded mean estimate — the "rounding-promise" obstruction that killed QB's nested AE→search design in our earlier audit. The saving from Dürr–Høyer here would be √|C| with |C| ≈ 40 — a factor 6 — and it is not worth the coherence risk. **Coherence boundary:** everything inside one amplitude-estimation call (prep, B, utility DP, encode, reflections) is coherent; everything that consumes a mean estimate is classical.

**Query complexity.** Quantum: Õ(|C| · σ_diff/ε) applications of A. Classical unbiased: O(|C| · σ_diff²/ε²) samples, shared across candidates. Quadratic in 1/ε, unconditional (it inherits the mean-estimation lower bound of Nayak–Wu and the classical Θ(σ²/ε²) sampling lower bound). What ε has to be is an empirical question — section (d).

## (d) Measurements

All numbers from `mbr.py` / `measure.py` / `measure2.py` (`results_synthetic.json`, `results2_{clean,10dB,5dB,0dB}.json`, logs alongside). Python: numba 0.63 for the DP. Real posteriors regenerated offline from the locally cached `facebook/wav2vec2-base-960h` on the cached LibriSpeech dummy split with the earlier recipe (`dump_posteriors.py`: seed 7, utterances {0,1,6,8,10,12,14}, white noise scaled to per-utterance SNR; utterances 3 and 5 skipped as > 120 000 samples, exactly as before). Frame confidence: clean 0.98, 10 dB 0.94–0.98, 5 dB 0.81–0.95, 0 dB 0.82–0.91 — consistent with N48.

### Gates (printed lines)

```
GATE mbr_A (labelling-dist, iterative ED) vs mbr_B (path-enum, recursive ED): 120 instances, 1162 (l,mu) pairs, worst |mu_A-mu_B| = 4.44e-16, argmax-value mismatches = 0 -> PASS
GATE sampler vs brute_ctc: N=200000, worst |freq - p| = 1.55e-03 (4-sigma bound 4.47e-03) -> PASS
GATE edit distance spot checks: ED(123,13)=1,1 (expect 1,1); ED(eps,11)=2 (expect 2) -> PASS
GATE ed_nb vs ed_iter: 300 pairs, worst diff 0 -> PASS
GATE numba sampler vs brute_ctc: N=200000, worst |freq-p| = 1.35e-03 (4-sigma 4.47e-03) -> PASS
```
Impl A forms p(l'|y) by `brute_ctc` and uses an iterative Wagner–Fischer; Impl B enumerates paths directly (never forms the labelling distribution) and uses a recursive memoised edit distance. 120 instances, half uniform-random tables, half `peaky_table(conf=0.89)`, T ≤ 6, W ≤ 3. The numba DP and the numba product-measure sampler are gated against those.

### Protocol

Candidate set C = top-20 of an exact prefix beam (beam 300) ∪ top-20 most frequent labellings among N_c = 2 000 samples (|C| = 20–40). μ(l) for every l ∈ C estimated on one shared set of N_ref samples (common random numbers; N_ref = 20 000 synthetic, 200 000 at 5/0 dB, 100 000 at 10 dB, 50 000 clean). Reported: whether argmax μ equals the MAP labelling; the MAP labelling's rank under μ; ED(MBR, MAP); gap = μ(top-1) − μ(top-2) with its standard error (paired); σ_u and the paired σ_diff; N90 = smallest N ∈ {10,…,20 000} at which a bootstrap of N samples identifies the top-1 in ≥ 90 % of 100 (200 synthetic) trials; CER of MAP, MBR and the best candidate against the reference transcript; measured throughput of the classical DP.

### Synthetic peaky tables, conf 0.89 (matches the 5 dB regime), 5 tables per cell

| T | W | MBR ≠ MAP | gap median | gap min | gap max | σ_diff median | N90 per table | distinct labellings / 2 000 samples |
|---|---|---|---|---|---|---|---|---|
| 50 | 5 | 2/5 | 8.1e-3 | 6.7e-4 | 1.4e-2 | 0.042 | 20, 100, 100, 20 000, 10 000 | 1 933 |
| 50 | 10 | 1/5 | 1.2e-2 | 1.5e-3 | 1.8e-2 | 0.030 | 10, 20, 50, 50, 5 000 | 1 986 |
| 100 | 5 | 3/5 | 1.4e-3 | 9.6e-5 | 3.4e-3 | 0.022 | 200, 500, >20 000, 5 000, 1 000 | 2 000 |
| 100 | 10 | 1/5 | 5.8e-4 | 3.2e-4 | 3.2e-3 | 0.016 | 2 000, 1 000, 5 000, 5 000, 200 | 2 000 |

MBR ≠ MAP in 7/20; when they differ, ED(MBR, MAP) = 1 in six cases and 2 in one. The gap shrinks roughly as 1/T (median 1e-2 → 1e-3 from T = 50 to 100) while σ_diff shrinks only ~2×, so N90 ≈ (1.28 σ_diff/gap)² grows with T (bootstrap N90 agrees with this analytic estimate within the grid spacing in 19/20 tables). At T = 100 the sampler never repeats: every one of 2 000 samples is a distinct labelling, i.e. the posterior is spread over ≫ 10⁴ labellings and "the candidate set" is whatever the beam and a handful of sample frequencies happen to surface.

### Real wav2vec2-base posteriors (T = 112–292, W = 32; 7 utterances per SNR)

| SNR | p* median | margin p*/p₂ | MBR ≠ MAP | MAP's rank under μ | ED(MBR, MAP) | gap median (resolved) | gap min | σ_diff median | N90 per utterance | mean CER vs reference: MAP / MBR / best candidate | MBR better / worse than MAP (CER) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clean | 0.90 | 30.9 | 0/7 | 1 | 0 | 1.4e-2 | 2.8e-3 | 0.005 | 10,10,10,10,50,10,10 | 0.020 / 0.020 / 0.020 | 0 / 0 |
| 10 dB | 7.6e-3 | 1.70 | 1/7 | 19 (one) | 2 | 2.9e-3 | 2.1e-4 | 0.013 | 1000,50,5000,500,20,50,50 | 0.122 / 0.119 / 0.097 | 1 / 0 |
| 5 dB | 4.7e-11 | 1.04 | 2/7 | 5, 2 | 1, 1 | 5.2e-4 (5/7 resolved) | 1.5e-4; two utterances unresolved at 200 000 samples (gap 3.4e-7 ± 1.7e-5 and 4.5e-5 ± 2.6e-5) | 0.010 | 10000,1000,>20000,100,10000,>20000,200 | 0.361 / 0.361 / 0.319 | 1 / 1 |
| 0 dB | 1.0e-17 | 1.04 | 7/7 | 14,15,11,5,6,4,5 | 3,3,2,1,2,1,1 | 1.8e-3 | 4.9e-4 | 0.018 | 200,5000,20,1000,5000,100,1000 | 0.726 / 0.707 / 0.666 | 6 / 0 |

Per-utterance rows are in `real2_*.log`; the transcripts are in `aggregate.out`. Reading the table:

(i) **MBR-optimal vs MAP.** They coincide on clean audio, differ on 1/7 at 10 dB, 2/7 at 5 dB, 7/7 at 0 dB. Where they differ the edit distance between them is 1–3 characters, and at 0 dB the MAP labelling sits at rank 4–15 under μ — the mode is a poor consensus representative there, as MBR theory predicts. But at 0 dB every hypothesis is garbage (CER 0.67–0.80; e.g. MAP `A|E|ON|O|EO|EBA|OO|IT|O||` vs reference "ON THE GENERAL PRINCIPLES OF ART…"): the 1.9 pp mean CER gain is real and worthless. At 5 dB (CER ≈ 0.36, the "usable window" of N50) MBR wins one utterance by 1.6 pp and loses one by 1.4 pp — mean CER identical to three decimals.

(ii) **The gap that sets ε.** Median resolved gap 5.2e-4 at 5 dB (1.5e-4 if one takes the median over all seven with the two unresolved ones at their point estimates, which is what `resources.py` uses), 1.8e-3 at 0 dB, 2.9e-3 at 10 dB, 1.4e-2 clean. In characters (gap × |l|): 5 dB ≈ 0.01–0.03 char, 0 dB ≈ 0.05 char. Two 5 dB utterances have a top-1/top-2 gap below the 200 000-sample resolution (3σ ≈ 5e-5) — there the "MBR winner" is undefined at any precision anyone would pay for.

(iii) **Classical samples to identify the winner (90 %).** Median N90: clean 10, 10 dB 50, 5 dB 1 000 (range 100 to > 20 000), 0 dB 1 000 (20–5 000). Practitioners' N = 64–300 resolves clean and 10 dB always and roughly half of the hard-audio cases; the rest are ties to within the precision that matters.

(iv) **Implied query counts at that ε** (`resources.py`, `resources.out`; constants stated in the script: C_Q = 10 for the polylog/confidence factor in the quantum estimator, z = 2.58 classical, paired σ_diff on both sides, ε = gap/2):

| Regime | ε | quantum uses of A per pairwise comparison (C_Q σ/ε) | classical samples (z² σ²/ε²) | quantum / classical query ratio |
|---|---|---|---|---|
| 5 dB medians (σ_diff 0.0105, gap 1.55e-4) | 7.7e-5 | 1.4e3 | 1.2e5 | 1 : 90 |
| 0 dB medians (σ_diff 0.0175, gap 1.8e-3) | 9.0e-4 | 2.0e2 | 2.5e3 | 1 : 13 |
| 0 dB smallest resolved gap (4.9e-4) | 2.4e-4 | 7.2e2 | 3.4e4 | 1 : 48 |
| decision-relevant ε = half a character (5 dB) | 8.8e-3 | 12 | 9.5 | ≈ 1 : 1 |

The quadratic query advantage is real and it is worth a factor 13–90 in *queries* at the measured gaps — and a factor ~1 at the precision that changes a transcript.

## (e) Where the mean-estimation advantage is real and where it is fake

The test is one line: **is there a polynomial-time exact evaluator for the expectation?** If yes, classical computes it exactly at zero ε-cost and the "1/ε vs 1/ε²" comparison is against a straw man. If no, the classical baseline is Monte Carlo at σ²/ε² and the quadratic quantum advantage is real (in query count). For an expectation E_{l'~p(·|y)}[f(l')] under a CTC posterior the rule of thumb is: **exact and polynomial iff f is computable by a (weighted) finite automaton of polynomial size**, because then a DP over (frame t, automaton state) — the CTC forward recursion with the automaton in the product — evaluates the expectation exactly in O(T · |automaton|).

| Objective | Exact classical evaluator? | Verdict for quantum mean estimation |
|---|---|---|
| p(l\|y) for a given l ("certification of the MAP answer") | **Yes**, forward recursion O(T·\|l\|) (Graves 2006 §4.1; `ctc_forward`, gated to 4e-16 vs brute force) | **Fake.** Estimating to ε in O(1/ε) is worse than computing exactly in O(T\|l\|). |
| Per-position marginals P(l_k = s), expected length E\|l\|, expected count of symbol s, P(\|l\| = k) | **Yes**, DP over (t, #emitted-so-far, last symbol), O(T·L·W) | **Fake.** |
| Expected n-gram counts / "linearised BLEU" utility (Tromble et al. 2008 lattice MBR) | **Yes**, DP over (t, last n−1 emitted symbols), O(T·W^n) — the "local" risk Xu et al. contrast with Levenshtein | **Fake** for fixed n. |
| Global *regular* constraints (l contains word w; l matches a grammar with a small DFA; l has ≤ k occurrences of x) — P(constraint) or E[u·1{constraint}] | **Yes**, intersect the DFA into the forward recursion | **Fake.** |
| **Expected edit distance to a fixed l** — the MBR/consensus utility; equivalently expected CER/WER of candidate l | **No polynomial exact algorithm known**; exact = multiplicity automaton exponential in \|l\|; "we conjecture it is NP-hard" (Calvo-Zaragoza et al. 2016). Polynomial routes: Monte Carlo (FPRAS, σ²/ε²) or a *biased* deterministic bound (Xu–Povey). | **Real** (conditional only on the absence of a poly exact algorithm — a well-studied open problem, not our assumption) — but only against the *unbiased* classical route; the biased Xu–Povey bound has no ε at all. |
| Expected score under an external non-decomposable rescorer f (a neural LM's PLL, as in Novosad's MBR-CER) — E[f(l')] or E[f(l')·u(l,l')] | **No** (f is a neural network) | **Real in query count, unusable in practice**: the oracle must implement f *reversibly and coherently* — a RoBERTa forward pass inside the amplitude-estimation loop. This is where the actual WER gain lives (Novosad: −0.54 pp only with the LM posterior), and it is exactly what the coherent oracle cannot afford. |
| Expected utility under a *tempered* posterior p^τ (Novosad's τ = 50) | Sampling from p^τ is no longer a product measure over frames — the state prep loses the product structure; exact normaliser Z(τ) is a #P-style sum for τ ≠ 1 | The C3 state-prep advantage evaporates: you need a coherent sampler for a non-product distribution. **Not available.** |

Three consequences. (1) The only decoding objective on this list that is simultaneously (i) non-decomposable, (ii) sample-able by our product-state prep, and (iii) reversible at a sane gate count is the **bare Levenshtein utility under the raw (τ = 1) acoustic posterior**. (2) That is precisely the configuration the ASR literature reports as giving *no significant gain over greedy* (Novosad 2026; Jinnai 2025 could not even make it produce distinct samples on clean audio). (3) The gain in practice comes from a non-product reference distribution (LM-augmented or tempered) — which removes the cheap sampler — or from a non-reversible utility (neural metrics: Freitag et al. 2022, arXiv:2111.09388) — which removes the cheap oracle. The machine and the useful objective do not overlap.


## (f) Verdict, resources, novelty, next experiment

### Absolute resources for one mean estimate

Per application of A (state prep + collapse + Levenshtein DP + encode, and its inverse), from `resources.py` with b = 9-bit cells, 104 Toffoli per DP cell (two b-bit comparators, two selects, three constant adds, one 5-bit equality), DP run over |l| × T cells directly on the path register (no compaction), Möttönen state prep of 31 controlled rotations per 32-way frame at 30 T-gates each, unary-pointer collapse write:

| | 5 dB (T = 268, |l| = 57) | 0 dB (T = 268, |l| = 25) |
|---|---|---|
| Toffoli-equivalents per use of A (compute + uncompute) | 3.9e6 (DP 3.2e6, collapse 2.5e5, prep 5.0e5 T) | 2.0e6 |
| logical qubits, store-all DP rows (no pebbling) | 1.4e5 | 6.2e4 |
| uses per pairwise comparison at ε = gap/2 | 1.4e3 | 2.0e2 |
| Toffolis per pairwise comparison | 5.3e9 | 4.0e8 |
| × (|C| − 1) = 39 comparisons | 2.1e11 | 1.6e10 |
| wall clock at 1 MHz logical Toffoli (optimistic) | 58 h | 4.3 h |
| classical, same ε, 40 candidates, shared samples | 6.4e10 FLOP, **54 s** measured-rate (2–4e8 DP cells/s single core) | 2.5e8 FLOP, **< 1 s** |
| op-parity ratio classical/quantum | 0.31 | 0.016 |
| op-parity crossover gap | 4.7e-5 (0.003 character) | 2.9e-5 (0.0007 character) |

Pebbling the DP rows to cut qubits to O(√T · |l| · b) ≈ 1e4 multiplies the Toffoli count by ~3; it does not change the conclusion. Note also that the classical side here is the *worst* classical baseline: unbiased Monte Carlo at the same ε. The Xu–Povey lattice recursion (polynomial, deterministic, an upper bound) needs no ε at all, and Cheng & Vlachos 2023 (arXiv:2311.14919, EMNLP 2023) prune candidates while growing N, so the classical constant is smaller still.

### Is "quantum MBR decoding of CTC posteriors via Born-rule sampling + quantum mean estimation" a defensible unconditional-quadratic-speedup claim?

**As a statement about query complexity, yes; as a claim of advantage, no.**

- *Unconditional:* yes. It needs no structural assumption on the posterior, only (a) a unitary sampler — ours, C3 — and (b) a reversible bounded utility — Levenshtein. It inherits the Nayak–Wu Ω(1/ε) lower bound (arXiv:quant-ph/9804066, abstract-read) on the quantum side and the classical Θ(σ²/ε²) sampling lower bound on the other, so the quadratic gap in *queries to the sampler* is a theorem, not a conjecture. Its only conditional element is that this is the right classical baseline — i.e. that no polynomial exact evaluator of E[ED(l,·)] exists; that is the open EDD problem, conjectured NP-hard by the people who studied it, and not something we assume.
- *Quadratic:* yes in queries; **no** in operations. Each query costs ~4e6 Toffolis against ~3e3 FLOPs for a classical sample (|l|² cells), a 10³ per-query handicap that a √ advantage only overcomes once σ/ε ≳ 1.5e3 — gaps ≲ 5e-5, a few thousandths of a character.
- *Speedup for anything anyone wants:* no. The measured gaps on hard audio are 1e-4–6e-3; the decision-relevant precision (half a character) is reached classically with ~10 samples; MBR under the raw acoustic posterior does not change mean CER at 5 dB (ours, n = 7) and gives no significant WER gain at G ≤ 128 on dev-other (Novosad 2026, n = 2 864 utterances). The configurations where MBR does help — LM-augmented or tempered reference distributions, neural-metric utilities — are exactly the ones that break the product-state sampler or the cheap reversible oracle (section e). The machine and the useful objective do not overlap; this is the same pincer as the MAP case (N50/N58/N60) in a new coordinate system: quantum wins the query count only where the decision has stopped mattering.

### Novelty

Five searches ("quantum minimum Bayes risk", "quantum MBR decoding", "quantum expected utility decoding", "quantum Monte Carlo speedup decoding", amplitude estimation × {consensus decoding, expected word error, machine translation / text generation decoding}) return nothing that applies amplitude/mean estimation to MBR or consensus decoding. Nearest neighbours: Bausch et al. 2021 (quantum search decoder, best-path objective, no collapse class — N65); the finance/Monte-Carlo QAE literature (option pricing, VaR); Boroujeni et al. 2018 / arXiv:1804.04178 and arXiv:2112.13005 (quantum algorithms for *one* edit distance, not an expectation over a distribution); Calvo-Zaragoza et al. 2016 (classical FPRAS for exactly our expectation). So "quantum mean estimation for MBR under a CTC posterior" would be a **new but small** result: a correct O(σ/ε) statement for a problem whose practical ε is not small enough to matter, publishable as a note or a section, not as a claim of advantage. If written up it must (i) cite Calvo-Zaragoza et al. as the classical baseline it beats and the EDD hardness status it depends on, (ii) report the resource table above, and (iii) say in the abstract that MBR under the bare CTC posterior gives no measurable CER gain.

### The one next experiment

The only way the verdict flips is if a *useful* objective is both non-decomposable and cheaply sample-able by our product-state prep. The single candidate we have not measured: **MBR with an LM folded into the utility rather than into the posterior** — u(l, l') = 1 − ED(l,l')/… evaluated under p(·|y) at τ = 1, with candidates C pre-scored by an external LM (Novosad's PLL) so that the LM enters only the classical outer loop and the coherent inner loop stays exactly our circuit. Run Novosad's configuration (Zipformer/CR-CTC or wav2vec2-large, LibriSpeech test-other, G = 16–128, N_ref = 1 000) with the reference distribution fixed at the raw acoustic posterior and the LM used only to choose C; if that recovers a significant fraction of his −0.54 pp, the coherent primitive has a live use and the gap/ε analysis above should be redone on that objective. If it does not — and Novosad's own τ = 1 result predicts it will not — D2 is closed.

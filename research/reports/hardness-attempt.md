# SUBSEQ-MODE / MOST-FREQUENT-SUBSEQUENCE: hardness attempt (2026-09-18)

Work dir: `hardness-attempt/` (`sm.py`, `mfs.py`, `expA*.py`, `expC.py`, `mfs_conj*.py`, `seplemma.py`).
All counts exact (integers / `fractions.Fraction`).

## Headline (3 lines)
- **Proved:** (i) a *separator-forcing lemma*: in `x = #^M B_1 #^M … B_k #^M` every "honest" word (one non-empty #-free piece per block, non-empty interior # groups) has `emb = ∏C(M,i_j)·∏emb(u_j,B_j)` — fully separable, so any block-product gadget for MFS must have a *cheating* word as its mode; (ii) a matrix-product reformulation `emb(l,x) = 1ᵀ A_{l_n}⋯A_{l_1} e` with `A_c = D_c U` (SUBSEQ-MODE = same with weighted `D_c`); (iii) SUBSEQ-MODE is FPT in the number of non-degenerate slots, `O((|Σ|+1)^k · T²)`.
- **Refuted (machine-checked):** the LCS permutation-block gadget (no δ makes the mode an LCS witness; at k=3,m=5 best is 21/40); *length-unimodality* of `max_{|l|=n} emb(l,x)` for binary x (`x=bababbaababa`: 67,57,71 at n=4,5,6); *greedy single-letter insertion* as an exact algorithm for MFS (fails 11/760 stop-rule, 1/760 full-chain: `x=abbbaaabbbbbaabb`, opt `abbbab`=365, greedy 360); nestedness of per-length optima (22/760 fail).
- **Conjecture (survived to |x|=22, 760 random binary strings):** the *full-chain* greedy insertion (never stop, take the best length) is within 2% of optimum; `|opt| ∈ [0.36T, 0.5T]`; `runs(opt) ≤ runs(x)/2+1` holds on 95%. No exact polynomial characterisation survived. MFS (Fang 2024, Rem. 4.2) remains open in both directions.

## Gates
```
GATE brute-vs-DP: 300 random instances (T<=7, W<=3, exact Fractions, all words), mismatches=0
GATE all_emb-vs-DP: 300 random binary x (|x|<=10), all distinct subsequences, mismatches=0, total mass 2^T ok
GATE separator lemma (interior i_j>=1): 300 random instances (k<=3, M<=4, |Sigma|=3), mismatches=0
```
(`sm.py`: path-enumeration brute force vs. forced-blank forward DP for general slot tables; `mfs.py`: subset-enumeration dictionary vs. direct DP for the deterministic/δ=1/2 case.)

## Primary target: MOST-FREQUENT-SUBSEQUENCE (MFS)
Input `x ∈ Σ^T`, `K`; is there `l` with `emb(l,x) ≥ K`? Equals SUBSEQ-MODE with deterministic source and δ=1/2 (`P(l)=2^{-T} emb(l,x)`). With general δ, `P(l) ∝ ρ^{|l|} emb(l,x)`, `ρ=(1-δ)/δ`.
Pursued: 3(a) block products (→ separator lemma + LCS gadget refutation), 3(b) length-k version (per-length data below), 3(c) exhaustive binary experiments to |x|=24.

## Direction A — reduction from LCS via concatenated blocks
**Construction.** `x = B_1 … B_k`, each `B_i` a permutation of `[m]` (so `emb(u,B_i) ∈ {0,1}`), source deterministic, deletion δ. For a word `l` that is a common subsequence of all blocks, `emb(l,x) = C(|l|+k-1, k-1)` (every split of `l` into k pieces embeds). Hope: tune ρ so that `f(n)=ρ^n C(n+k-1,k-1)` increases up to the LCS length and non-common words lose.

**Why it fails (argument).** `f(n+1)/f(n) = ρ(n+k)/(n+1)`, so the mode among common words sits at `n* ≈ (kρ-1)/(1-ρ)`; to push `n*` to `m` you need `ρ ≥ (m+1)/(m+k) → 1`. But a word common to only `k-1` blocks and of length `m` still has `emb ≥ C(m+k-2,k-2)`, and words with `|l| > m` (subsequences of no block) have `emb ≥ 1`; with `ρ ≈ 1` the exponential length penalty is gone and the only separation between honest and cheating words is *polynomial in m of one degree*, while the LCS threshold is a length gap. The separation is therefore not sharp at any ρ, and the argmax is a short common word (ρ small) or a long non-common word (ρ large) with only a narrow, instance-dependent window in between.

**Machine check** (`expA.py`, 40 random instances per (k,m), exact, argmax over all distinct subsequences; key `(ρ, opt is common, |opt|−LCS)`):
- k=2, m=5, ρ=1: 40/40 opt is a common subsequence of LCS length — but k=2 LCS is in P anyway.
- k=3, m=4: ρ=1/2 → all common, but 33/40 *shorter* than LCS; ρ=3/4 → 21/40 witnesses, 19 non-common longer; ρ=1 → 0/40 (all non-common, +1…+4 longer).
- k=3, m=5: ρ=3/4 → 11/40 witnesses; ρ=1 → 1/40. k=4, m=4: ρ=3/4 → 1/40; ρ=1/2 → 22/40 witnesses but 16 non-common at +1.
Fine ρ-scan (`expA2.py`, 20 instances, ρ=0.40…1.15 step 0.05, counts = witness/short-common/non-common): best window k=3,m=4: ρ∈[0.55,0.60] → 18/2/0; k=3,m=5: ρ=0.65 → 18/1/1; k=4,m=4: ρ=0.40 → 11/9/0, ρ≥0.45 → ≤8 witnesses. The window shrinks and the witness fraction drops as k grows (k=4 never exceeds 55%), as the polynomial-degree argument predicts.
Verdict: **refuted as a reduction** (no ρ separates), consistent with the argument above.

## Direction A′ — block products with separators (briefed direction 3(a)): a barrier lemma
**Lemma 1 (separator forcing).** Let `x = #^M B_1 #^M B_2 … B_k #^M` with `# ∉ alph(B_i)`. Let `l = #^{i_0} u_1 #^{i_1} u_2 … u_k #^{i_k}` with all `u_j` non-empty and #-free and all *interior* `i_1,…,i_{k-1} ≥ 1`. Then
`emb(l,x) = ∏_{j=0}^{k} C(M,i_j) · ∏_{j=1}^{k} emb(u_j, B_j)`.
*Proof.* In any embedding the k non-empty #-free stretches `u_1,…,u_k` are separated by ≥1 `#` each, so they lie in k distinct blocks in increasing order; there are exactly k blocks, so `u_j ↦ B_j`. Interior group `j` then lies strictly between `B_j` and `B_{j+1}`, i.e. inside separator `j`; outer groups lie in separators 0 and k. The embedding thus factorises into independent choices per separator (`C(M,i_j)`) and per block (`emb(u_j,B_j)`). ∎ (Machine-checked, gate above; the hypothesis "interior `i_j ≥ 1`" is necessary — dropping it produced 2/300 mismatches.)

**Corollary (block-product barrier).** Over the honest family the objective is a product of independent per-separator and per-block terms, so its argmax is `i_j = ⌊M/2⌋` and `u_j = argmax emb(·,B_j)` — solved by k independent smaller MFS instances. Hence a gadget of this shape can only be hard if the mode is a *cheating* word (some `u_j` empty or some interior group empty, letting stretches straddle blocks). This sharpens Barrier 2: even with a shared alphabet, forcing structure via separators restores separability; the hardness, if any, must live in the straddling embeddings — which are exactly the terms one cannot control.

## Direction B — number-theoretic weights
For `l = a^n`, `P(l) = ∏r_t · e_n(w)`, `w_t = p_t(a)/r_t`; `e_n` is log-concave in n (Newton), so single-symbol words are trivial. Question was whether two-symbol words give enough structure. Finding: the two-symbol per-length maximum is **not unimodal** (Lemma 2 below), so the "structured symmetric function" is already non-convex at |Σ|=2 — but I found no way to make its maximum *encode* a subset-sum equality: every coefficient is a non-negative sum over embeddings, and an equality test needs a peak that positive sums over monotone index sets do not produce without the injectivity that kills ambiguity (the pincer, Barrier 3). No gadget survived to an instance; nothing to report beyond this negative.

**Lemma 2 (no length-unimodality at |Σ|=2).** For `x = bababbaababa` (T=12, δ=1/2), `max_{|l|=n} emb(l,x)` for n=0..12 is `1,6,22,38,67,57,71,42,29,10,5,2,1`. Machine-checked by exhaustive enumeration. Seven of 760 random binary strings (T=8..22) are non-unimodal; log-concavity fails on 556/760. Consequence: any algorithm that fixes the length by a unimodal search over n is wrong.

## Direction C — polynomial-algorithm attempts (exhaustive data)
**SUBSEQ-MODE, general tables** (`expC.py`, W=2, T=6..11, exact, 200 instances each; opt vs. per-slot argmax collapse `g`):
- uniform-random tables: edit(opt,g) histogram {0:36, 1:102, 2:51, 3:11}; peaky tables (winner mass 0.6–0.95): {0:196, 1:4}; tables with 40% zeros: {0:124, 1:66, 2:10}.
So on realistic (peaky) tables the greedy collapse is the mode 98% of the time at T ≤ 11; on flat tables it is usually not.

**MFS, binary x** (`mfs_conj.py`, 760 random strings, T=8..22, all distinct subsequences enumerated):
| conjecture | holds | note |
|---|---|---|
| per-length max unimodal | 753/760 | refuted (Lemma 2) |
| per-length max log-concave | 204/760 | refuted |
| nested chain of per-length optima up to the mode | 738/760 | refuted |
| greedy insertion (stop at first non-improvement) = mode | 749/760 | refuted, e.g. `x=abbbabab`: opt `bbab`(12), greedy `abb`(11) |
| greedy insertion full chain, best length = mode | 759/760 | refuted: `x=abbbaaabbbbbaabb`, opt `abbbab`(365), greedy `babbab`(360) |
| mode unique | 589/760 | — |
| `runs(opt) ≤ runs(x)/2 + 1` | 723/760 | — |
| `|opt|/T` | 0.36–0.50 | all 760; |opt| tends to be ~0.42T |

No exact polynomial characterisation survived. The surviving *soft* statement: full-chain greedy insertion is a ≥0.98-approximation on every instance tested (not a theorem).

## Direction D — parameterised result
**Lemma 3 (FPT in non-degenerate slots).** Call slot `t` degenerate if its distribution over Σ∪{ε} is a point mass. Let k be the number of non-degenerate slots. Then SUBSEQ-MODE is solvable in `O((|Σ|+1)^k · T²)`.
*Proof.* A word has `P(l)>0` only if it is the collapse of a path that agrees with every degenerate slot, so at most `(|Σ|+1)^k` words have positive probability; enumerate them (via the k free slots) and evaluate each by the forward DP in `O(T·|l|) ≤ O(T²)`. ∎
Note this is tight in spirit: fact 4 (fixed T ⇒ P) is the case k ≤ T. An ε-relaxation ("max mass ≥ 1−ε") does not give FPT by this argument, because ε-slots still create ambiguity across all of T.

## New reformulation (for the next attempt)
**Lemma 4 (matrix form).** With `U` the strictly-upper-triangular all-ones T×T matrix and `D_c = diag([x_t = c])`, `emb(l,x) = 1ᵀ (D_{l_n} U)(D_{l_{n-1}} U)⋯(D_{l_1} U) e_0` (e_0 = a virtual start column). For SUBSEQ-MODE replace `[x_t=c]` by `p_t(c)/r_t` and multiply by `∏r_t`. *Proof:* `f_j(t) = [x_t=l_j] Σ_{t'<t} f_{j-1}(t')` is the row-wise forward recursion. ∎
So MFS is "maximise a fixed entry of a product of matrices drawn from the finite set `{D_c U}`" — the finite-set matrix-product family for which max-norm/JSR problems are NP-hard in general (Tsitsiklis–Blondel 1997). Our matrices are rank-structured (rows are suffix-ones or zero), so that hardness does not transfer, but this is the cleanest place to look for a width-1 gadget: a reduction must show that products of `D_c U` can simulate the transition structure of a hard product problem.

## Most promising next step + first experiment
Use Lemma 4. Take the smallest NP-hard "max-entry matrix product over words" instance family you can state (e.g. 0/1 matrices from a graph, word = vertex sequence, entry = number of walks) and ask whether `x` can be chosen so that `D_c U` products reproduce those matrices on a sub-block, with the straddling terms bounded. First experiment (concrete, ≤ 1 day): for every binary `x` with T ≤ 12, compute the set of all products `A_{l_n}⋯A_{l_1}` restricted to a chosen row/column subset and test whether the map `l ↦ product` can realise a 2×2 matrix semigroup that is not "monotone" (e.g. both `[[1,1],[0,1]]`-like and `[[1,0],[1,1]]`-like generators). If the realisable semigroups are always triangular-monotone, that is a new barrier lemma (and a strong hint the problem is in P); if some `x` realises a non-monotone pair, that is the seed of a gadget.
Secondary: prove the 0.98-approximation of full-chain greedy insertion, or find a counterexample family (search over run-length patterns rather than random strings).

## Direction E — matrix semigroup / straddling seeds
Code: `hardness-attempt/expE.py` (matrix form, two-block coupling scan), `expE2.py` (gap/spread, ternary), `expE3.py` (crossing pairs), `expE4.py` (k-block interface identity). All exact integers.
```
GATE matrix-form vs DP: 300 random (x,l), |x|<=10, |Sigma|<=3, mismatches=0
GATE interface identity (k<=4 blocks, |Sigma|<=3, |B_i|<=4, |l|<=5): 300 random instances, mismatches=0
```
(Every straddle profile below also sums to the reported mode count — the two-block identity checked on each instance.)

**Result: a seed, not a barrier.** There is no monotonicity lemma to prove; instead the experiment gives the minimal coupled instances and pins down the *only* channel through which blocks can interact.

**Lemma 5 (interface identity).** For `x = B_1 B_2 … B_k` and any `l` of length n,
`emb(l,x) = Σ_{0=s_0≤s_1≤…≤s_{k-1}≤s_k=n} ∏_{i=1}^{k} emb(l[s_{i-1}:s_i], B_i)`.
*Proof.* Each embedding of `l` places a contiguous (possibly empty) piece of `l` in each block, in order; the pieces are determined by the cut vector `s`, and given `s` the blocks embed their pieces independently. ∎ (Gate above.)
Consequences for gadget design: (a) two consecutive blocks communicate through a *single integer* — the cut position — so the "transfer" across a block boundary is a 1-D convolution of the prefix-count profile `s ↦ emb(l[:s],B_1)` with the suffix-count profile `s ↦ emb(l[s:],B_2)`; (b) every per-block piece set is the *downward-closed* (under subsequence) set of subsequences of `B_i`, so the empty and short pieces always contribute — "cheating" pieces cannot be excluded, only out-weighed. Any width-1 gadget is a maximisation of a sum over monotone cut vectors of products of downward-closed counts; this is the exact shape a hardness proof must exploit, and the shape Barrier 5 (2-local) already rules out at second order.

**Crossing (non-monotone) pairs inside one string** (`expE3.py`, exhaustive binary): same-length prefixes `l,l'` and continuations `w,w'` with `emb(lw) > emb(l'w)` and `emb(lw') < emb(l'w')` exist from **T = 4** (`x=aaba`: `aa` vs `ab`; continuation `b`: 1>0, continuation `a`: 1<2) and are present in 504/512 binary strings at T = 9. So the "future value" of a prefix is content-dependent, not length-dependent — consistent with fact 7 (exponential dominance frontier); there is no monotone-comparison barrier to state.

**Two-block coupling ("mode of the concatenation ≠ concatenation of per-block modes")** (`expE.py`, exhaustive over all binary `x` and all cut points `x = B_1B_2`; "concatenation of block modes" = any `u·v` with `u` a per-length mode of `B_1` and `v` a per-length mode of `B_2`, lengths free):
- binary T ≤ 8: **0 coupled** out of 2 768 (x, cut) pairs; T = 9: 4/4096; T = 10: 60/9216.
- ternary T ≤ 7: 0 coupled out of 18 045; T = 8: 42/45 927 (e.g. `x=aababcac`, cut@7, mode `abc`=10, straddle `[0,0,5,5]`; `x=aabacbcc`, cut@4, mode `abc`=12, straddle `[0,6,6,0]`).
- **Minimal binary instance (unique up to reversal/complement):** `x = abaabaaab` (runs 1,1,2,1,3,1), cut after position 1: `B_1 = a`, `B_2 = baabaaab`. Mode `aaab` with emb = 21 = 10 (whole word in `B_2`) + 11 (`a` in `B_1`, `aab` in `B_2`). Per-length modes of `B_2` are `baa` (13) and `baab` (14); the best concatenation word scores 20. `aaab` is the per-length mode of neither block at any split, and wins only because two different cuts both contribute. Re-checked independently via the matrix form (21).
- **Coupling strength grows with T:** gap `M − best_concat` at T = 9 is 1 (all 4 cases); at T = 10 the histogram is {1:28, 2:12, 3:8, 4:12}, i.e. up to 40 vs 36 (`x=aaababaaab`, cut@3, mode `aaab`, straddle `[4,18,15,3,0]`). Straddle spread (number of cuts with non-zero mass) at T = 10: {2:40, 3:12, 4:8} — the mass of the mode can be spread over four different cut positions, and can be an exact 50/50 split (`x=aabaaabbab`, cut@9, straddle `[0,0,0,20,20]`).

**Reading.** The straddling mode is the ambiguity mechanism of fact 1 made concrete: a word beats every "honest" concatenation by letting one letter (`a`) be read by either block. The seed is real but weak — at T = 10 the coupled fraction is 0.65% and the relative gain ≤ 11% — and Lemma 5 says the interaction is always a 1-D convolution of downward-closed profiles. A gadget must therefore amplify exactly this: blocks whose count profiles `s ↦ emb(l[:s],B)` are *sharply peaked* at a cut that depends on the content of `l` (so the convolution selects the cut), with the downward-closed cheating mass bounded. The permutation blocks of Direction A have flat profiles (0/1), which is why they failed.

**Next experiment (concrete).** Search, for block pairs `(B_1,B_2)` with `|B_i| ≤ 8` over |Σ| ≤ 3, for the pair maximising `M / best_concat`; then test whether the ratio composes under concatenation `B_1B_2B_3…` (grows geometrically ⇒ an amplifier exists and a reduction from a segmentation-type problem becomes plausible; saturates ⇒ new quantitative barrier, "straddling gain is bounded by a constant per boundary").

## Direction F — does straddling gain compose?
Code: `hardness-attempt/expF1.py` (all block pairs), `bb.py` (certified branch-and-bound mode), `expF2.py` (composition + honest-best search), `expF3.py` (block-length scaling), `expF4.py` (gate). Outputs in `expF1.out`, `expF2.out`.
```
GATE branch-and-bound mode vs exhaustive: 300 random binary x (|x|<=20, suffix table exhaustive only <=6), mismatches=0, max nodes=82
GATE honest_best (bounded DFS) vs brute product-set max: 300 random block tuples (k<=4, |B_i|<=5), mismatches=0
```
The certified search uses the bound `emb(lw,x) = Σ_t f_l(t)·emb(w, x_{>t}) ≤ Σ_t f_l(t)·M(x_{>t})` (Lemma 5 with two pieces; `f_l(t)` = embeddings of the prefix `l` ending exactly at `t`, `M(y)` = mode count of `y`, computed exhaustively for `|y| ≤ 22` and by the same search for longer suffixes). Best-first search stops when the top bound is ≤ the incumbent, so every mode count below is exact; at T = 64 it needed ≤ 1836 nodes. Definitions: `M` = mode count of the concatenation; `honest` = max `emb(u_1⋯u_k, x)` over `u_i` a per-length mode of `B_i` (ties included, lengths free); `r = M/honest`.

### (1) All binary block pairs, |B_i| ≤ 8 (130 050 (x, cut) pairs modulo complement, exhaustive)
r = 1 for every pair with |x| ≤ 8; max r by |x|: 9: 21/20; 10: 39/35; 12: 73/63; 14: 45/37; 16: 30/23. Top 10 (all at |x| = 16; straddle profile = mass per cut position):
| r | M | honest | B_1 | B_2 | mode | straddle |
|---|---|---|---|---|---|---|
| 1.3043 | 600 | 460 | abaaaabb | aabbbbab | aaabbb | [0,50,200,100,200,50,0] |
| 1.2456 | 786 | 631 | aaababab | bababaaa | aababaa | [0,15,150,228,228,150,15,0] |
| 1.2222 | 495 | 405 | abaaaabb | aabbbaba | aaabba | [0,45,180,90,140,40,0] |
| 1.2222 | 495 | 405 | ababbbaa | bbaaaaba | abbaaa | (mirror) |
| 1.2162 | 405 | 333 | aaaabaab | babaaa | aaabaa | [0,0,45,180,144,32,4] |
| 1.2162 | 405 | 333 | aaabab | baabaaaa | aabaaa | (mirror) |
| 1.2000 | 252 | 210 | abaaaa | bbaaaaba | aaaaa | [1,25,100,100,25,1] |
| 1.2000 | 252 | 210 | abaaaabb | aaaaba | aaaaa | (mirror) |
| 1.1990 | 1374 | 1146 | aaaaabab | baabaaaa | aaabaaa | [0,24,120,480,600,150,0,0] |
| 1.1990 | 1374 | 1146 | aaaabaab | babaaaaa | aaabaaa | (mirror) |
Note the mode's mass is genuinely spread over 4–6 cut positions; no single cut carries a majority.

### (2) Composition (certified counts; boundaries = k−1)
| blocks | T | k | M | mode | honest | r | r^{1/(k−1)} | trivial bound C(n+k−1,k−1) |
|---|---|---|---|---|---|---|---|---|
| B_1B_2 (top pair) | 16 | 2 | 600 | aaabbb | 460 | 1.304 | 1.304 | 7 |
| B_1B_2B_1 | 24 | 3 | 21 680 | aaabbbaaab | 18 240 | 1.189 | 1.090 | 66 |
| B_1B_2B_2 | 24 | 3 | 18 000 | aaabbbabbb | 17 600 | 1.023 | 1.011 | 66 |
| B_1B_2B_3, best B_3 (=bbaaba, all |B_3| ≤ 8) | 22 | 3 | 8 316 | aaabbbba | 6 472 | 1.285 | 1.134 | — |
| (B_1B_2)² | 32 | 4 | 636 000 | (aaabbb)² | 510 800 | 1.245 | 1.076 | 455 |
| (B_1B_2)³ | 48 | 6 | 673 814 400 | (aaabbb)³ | 434 784 000 | 1.550 | 1.092 | 33 649 |
| (B_1B_2)⁴ | 64 | 8 | 713 867 251 200 | (aaabbb)⁴ | 462 348 345 600 | 1.544 | 1.064 | 2 629 575 |
| pair 2 (aaababab·bababaaa), m=1,2,3,4 | 16–64 | 2–8 | — | (aababaa)^m | — | 1.246, 1.229, 1.213, 1.212 | 1.246, 1.071, 1.039, 1.028 | 8 … 6.7·10⁶ |
| pair 3 (aaaaabab·baabaaaa), m=1,2,3,4 | 16–64 | 2–8 | — | (aaabaaa)^m | — | 1.199, 1.168, 1.165, 1.165 | 1.199, 1.053, 1.031, 1.022 | 8 … 6.7·10⁶ |
**Verdict: saturates.** Across 1 → 7 boundaries `r` stays in [1.02, 1.55] while the trivial bound grows to 2.6·10⁶; the per-boundary factor `r^{1/(k−1)}` decays toward 1 (1.30 → 1.06; 1.25 → 1.03; 1.20 → 1.02). No amplifying triple exists among the tested compositions (best B_3 gives 1.285 < 1.304 for the pair alone). Single-boundary `r` grows only slowly with block length (`expF3.py`, 150 random pairs each: max r = 1.00, 1.17, 1.29, 1.30 at |B_i| = 8, 12, 16, 20; median 1.00; fraction with r > 1: 0, 0.17, 0.26, 0.35).
Two side observations, machine-checked but unproved in general: the mode of `(B_1B_2)^m` was the periodic word `u^m` for all three pairs and m ≤ 4; the honest optimum is the periodic mode with O(1) local defects (e.g. `aaabb·ab·aaabbb·aaabbb·ab·aabbb`), which is *why* r does not compound.

### (3) What can be proved, and what the saturation actually says
**Lemma 6 (straddling gain is polynomial, not constant).** Let `x = B_1⋯B_k`, `l` a mode of `x` with `|l| = n`, and `M_i(j)` the length-j mode count of `B_i`. Then
`M(x) ≤ Σ_{cuts s} ∏_i M_i(s_i − s_{i−1}) ≤ C(n+k−1, k−1) · honest(x)`, and for k = 2, `M(x) ≤ (n+1)·honest(x)`.
*Proof.* Lemma 5 gives `M(x) = Σ_s ∏_i emb(l[s_{i−1}:s_i], B_i) ≤ Σ_s ∏_i M_i(s_i−s_{i−1})`. Each summand is attained by the honest word `u_1⋯u_k` (`u_i` a length-`(s_i−s_{i−1})` mode of `B_i`) through its own cut `s`, so each summand is ≤ `honest(x)`; there are `C(n+k−1,k−1)` cut vectors. ∎
A *constant* per-boundary bound (`M ≤ c^{k−1}·honest` with an absolute c) is **not** what I can prove, and I do not believe it is the right statement: (i) the single-boundary maximum grows with block length (1.05 at |x|=9 to 1.30 at |x|=16–40), so any constant would have to be shown independent of n, which the convolution form does not give — the profiles `s ↦ emb(l[:s],B_1)` are not unimodal in general (Lemma 2), so the standard "convolution of log-concave sequences is dominated by its peak times a constant" argument is unavailable; (ii) more importantly, the honest baseline is the wrong yardstick for hardness: the honest set is a product set that contains near-copies of the mode, so `r` measures how well *per-block* modes cover the global mode, not how much ambiguity straddling creates. Against the *diagonal* baseline `∏_i M(B_i)` (the value a separable/cut-respecting algorithm would compute) the gain is trivially exponential: `x = a^m` as m blocks gives `M(x)/∏M(B_i) = C(m,⌊m/2⌋)` (6, 70, 12 870 at m = 4, 8, 16 — exact). That exponential gain is fact 1 (all hardness is in the aggregation) restated, and it is symmetric across words, which is why it does not by itself yield a gadget.

**What the saturation rules out.** An "amplifier" built by *repeating* a coupled pair does not exist: repetition drives the mode periodic and the honest set tracks it up to a bounded number of defects. A width-1 gadget therefore cannot get a super-constant separation between a "good" and a "bad" word merely by chaining copies of a straddling block pair; the separation must come from a block sequence whose per-block modes *change* with the choice made earlier in the word — i.e. from crossing pairs (Direction E) arranged so that their effects do not average out. The trivial bound of Lemma 6 (`C(n+k−1,k−1)`) leaves exponential room for that, so this is not a barrier lemma against hardness; it is a negative result about one specific gadget template (repetition), stated with certified counts.

**Smallest instance to hand a gadget-designer.** `B_1 = abaaaabb, B_2 = aabbbbab` (r = 1.304, straddle `[0,50,200,100,200,50,0]`): a 16-letter string whose mode `aaabbb` is the per-length mode of neither block at any cut and whose mass is spread over five cuts.

**Next step.** Drop the repetition template. Search block *triples* `B_1B_2B_3` (|B_i| ≤ 6, exhaustive, ternary alphabet allowed) for the largest ratio `M(x) / max_l Σ_{single cut vector} ∏ emb(pieces)`, i.e. mode vs. the best *single-cut* decomposition — the quantity a separable DP would optimise — and check whether it can exceed the two-block maximum by more than a constant when the middle block's modes depend on the outer choices; if that ratio grows with k on some family, that family is the seed of a reduction.

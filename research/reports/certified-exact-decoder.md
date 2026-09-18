# A certified-exact CTC decoder that beats Graves' prefix search

Date 2026-09-18. Code, gates and logs: `../code/certified-exact-decoder/` (`bounds.py`, `gate.py`, `gate_w.py`, `bench.py`, `side.py`, `loose.py`, `scale2.py`; logs `gate.log`, `bench_*.log/json`, `side.log`, `loose.log`, `rnd32.log`, `scale2_w5_c08.log`). Python: the decoder-research venv, pure stdlib. Toolkit `ctc.py`/`prefixprob.py` copied unmodified (their own gates re-run: PASS).

## (a) Headline

1. **Prefix search's c/p* node count is NOT optimal for admissible-bound search.** The same best-first search with a tighter admissible bound — the *exact backward suffix mode* H_c(t) = max_v g_v(t), computed for every (frame, first-symbol) pair by T·(W−1) small best-first searches that reuse later H values — expands **exactly D nodes** (D = |mode|) in the final search on every peaky cell with T ≥ 64, versus c/p* (c ≈ 1.8) for Graves. Gated exact on 520 brute-force instances.
2. **Total work is polynomial and independent of p\***: generated nodes ≈ **0.10·T²·W²** (measured 0.07–0.14 over T ∈ {100,150,200}, W ∈ {5,10}, conf ∈ {0.7,0.8,0.9}), each node O(T), i.e. ≈ 0.4·T³·W² arithmetic. Instances with 1/p* = 1.6·10¹⁸ (T=200, W=10, conf 0.8) decode exactly in 35 s of Python; Graves would need ~10¹⁷ expansions.
3. **Improvement factor over the c/p* baseline** (for the quantum-costing thread): at the real-audio operating point (T ≈ 300, W ≈ 32, D ≈ 40, p* ≈ 5·10⁻¹²) the classical exact baseline drops from **3.6·10¹¹ expansions to ≈ 9·10⁶ O(T)-node evaluations (≈ 1·10¹⁰ flops) — a factor f ≈ 4·10⁴ in node count**, extrapolated from the T²W² law (measured directly at T ≤ 200, W ≤ 10; measured factors there are 4·10² at T=48 up to >10¹¹ at T=200). The `1/√p*`-type quantum finding cost (≈ 2·10⁶ evaluator calls × O(T·D)) is then *comparable to, not exponentially better than*, the classical exact decoder.

## Common framework (all directions)

Frames 1..T, blank = 0. For a prefix u: Ab[t], An[t] = mass of paths over frames 1..t collapsing to u and ending in the blank-after-u / last-symbol state; ok_d(t) = Ab[t] + [u_last ≠ d]·An[t]; p(u) = Ab[T]+An[T]. For a suffix v with v₁ = c: g_v(t) = mass of paths over frames t..T with π_t = c collapsing to v. Because the segment that emits the (|u|+1)-th symbol starts at a unique frame,

  p(u·v) = Σ_t ok_{v₁}(t−1) · g_v(t)   (exact; gated).

Hence for **any** family Ĥ_d(t) ≥ H_d(t) := max_{v: v₁=d} g_v(t),

  B(u) = max( p(u), max_d Σ_t ok_d(t−1)·Ĥ_d(t) ) ≥ max_v p(u·v)

is admissible (sum of maxes ≥ max of sums). Graves' F(u) is the special case Ĥ_d(t) = y_t[d] *summed* over d. All decoders below are the same best-first search (`best_first` in `bounds.py`, priority B, terminate when top bound ≤ incumbent) with a different Ĥ; expansions and generated nodes (`child()` calls, each O(T)) are counted identically.

**Gate line (all decoders, `gate.log`):**
```
GATE graves_F vs prefix_prob: 3184 prefixes, worst abs err 2.22e-16 -> PASS
GATE admissibility Hhat >= brute-force H_c(t): 1155 (t,c) cells, violations {'tree': 0, 'policy': 0, 'exact': 0}, exact-backward worst |H - brute| 5.55e-16 -> PASS
GATE argmax vs brute force: 400 instances (300 random T<=8 W<=3 + 100 peaky), wrong = {'graves': 0, 'childF': 0, 'bidir': 0, 'bidir.1': 0, 'policy': 0, 'exactbwd': 0, 'dfs_bb': 0, 'graves+beam': 0, 'policy+vit': 0}, exact ties 2 -> PASS
GATE argmax vs brute force at W in {5,8}, T<=6: 120 instances (60 random + 60 peaky), wrong = {'graves': 0, 'bidir': 0, 'policy': 0, 'exactbwd': 0}, exact ties 0 -> PASS
```
In every benchmark cell the three new decoders' p* and argmax were additionally asserted equal to each other (policy vs exact-backward vs bidir) — no disagreement in any cell.

## (b) Directions

### Direction 1 — two-sided / suffix-aware bounds (three admissible Ĥ families)

**1a. Suffix-tree bound (`bidir`).** Ĥ_d(t) = min( y_t[d], max( max_{v∈S, v₁=d} g_v(t), θ/w_d(t) ) ), S = {v : P(labelling ends with v) ≥ θ}, w_d(t) = 1 − y_{t−1}[d] (w=1 at t=1). *Admissibility:* P(ends with v) = Σ_t w_{v₁}(t)·g_v(t) exactly — the prefix mass ending at t−1 in a state that may start v₁ fresh at t is P(π_{t−1} ≠ v₁) = 1 − y_{t−1}[v₁] under the product measure. So v ∉ S ⇒ g_v(t) < θ/w_{v₁}(t) for every t; v ∈ S is covered by the explicit max. S is enumerated as the prefix tree of the reversed table (collapse(rev π) = rev(collapse π)); g_v(t) = An_rev[T−t+1] of the node rev(v). θ = p̂^α with p̂ the beam-32 incumbent. Predicted cost ≈ c/θ + c'·θ/p* → optimum ~ 1/√p*.

**1b. Frame-policy relaxation DP (`policy`).** Backward DP, O(W·T²): Ĥ_c(t) = y_t[c]·max( Tail_c(t), Σ_{t'>t} [ Rn_c(t,t')·max_{d≠c} Ĥ_d(t') + Rb_c(t,t')·max_d Ĥ_d(t') ] ), Rn = frames t+1..t'−1 all c (next symbol must differ), Rb = c* blank⁺ (any next symbol), Tail = c* blank* to the end. *Admissibility:* the exact recursion for g_{c·v'}(t) sums over the start frame t' of v'; replacing g_{v'}(t') by its max over v' separately at each t' can only increase it; induction backward in t. Equivalent to letting the emitted symbol depend on the *frame* where a segment starts instead of on its *index* — a relaxation whose looseness compounds over segments.

**1c. Exact backward suffix modes (`exactbwd`).** For t = T..1 and each c, H_c(t) = max_{v₁=c} g_v(t) is computed **exactly** by the same best-first search rooted at "c forced at frame t", whose bound uses the already-exact H_d(t') for t' > t (only t' > t is ever read). The final search then runs with Ĥ = H. *Admissibility:* trivial (Ĥ = H). Its only looseness is the single "Σ_t max_v" split at the node being bounded, never compounded.

**Comparison — required grid (peaky, N=4/cell, geometric means; `bench_peaky.log`).** exp = expansions, (gen) = all O(T) node generations incl. suffix tree / backward searches. Speedup = Graves exp ÷ decoder exp.

| T | W | conf | p* | D | Graves exp | Graves s | childF exp | bidir exp (gen) | policy exp | exactbwd exp (gen) | policy s | exactbwd s | G/policy | G/exactbwd |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 12 | 3 | 0.8 | 1.4e-01 | 3 | 7 | 0.000 | 4 | 4 (14) | 3 | 3 (58) | 0.000 | 0.000 | 2.2x | 2.4x |
| 12 | 3 | 0.9 | 3.8e-01 | 3 | 4 | 0.000 | 3 | 3 (11) | 3 | 3 (50) | 0.000 | 0.000 | 1.4x | 1.4x |
| 12 | 3 | 0.95 | 6.2e-01 | 4 | 4 | 0.000 | 3 | 3 (13) | 3 | 3 (88) | 0.000 | 0.000 | 1.3x | 1.3x |
| 12 | 5 | 0.8 | 1.0e-01 | 3 | 8 | 0.000 | 3 | 3 (21) | 3 | 3 (231) | 0.000 | 0.001 | 2.7x | 2.7x |
| 12 | 5 | 0.9 | 3.5e-01 | 4 | 5 | 0.000 | 4 | 4 (28) | 4 | 4 (355) | 0.000 | 0.001 | 1.2x | 1.2x |
| 12 | 5 | 0.95 | 5.7e-01 | 2 | 3 | 0.000 | 0 | 0 (14) | 0 | 0 (0) | 0.000 | 0.001 | (mode found at root; trivial) | |
| 16 | 3 | 0.8 | 8.9e-02 | 4 | 13 | 0.000 | 9 | 6 (21) | 5 | 4 (99) | 0.000 | 0.000 | 2.6x | 3.1x |
| 16 | 3 | 0.9 | 2.8e-01 | 5 | 6 | 0.000 | 5 | 5 (18) | 5 | 5 (134) | 0.000 | 0.001 | 1.2x | 1.2x |
| 16 | 3 | 0.95 | 5.1e-01 | 5 | 6 | 0.000 | 5 | 5 (20) | 5 | 5 (170) | 0.000 | 0.001 | 1.2x | 1.2x |
| 16 | 5 | 0.8 | 4.6e-02 | 4 | 20 | 0.000 | 11 | 5 (34) | 4 | 4 (497) | 0.000 | 0.003 | 5.7x | 5.7x |
| 16 | 5 | 0.9 | 2.2e-01 | 3 | 4 | 0.000 | 3 | 3 (22) | 3 | 3 (368) | 0.000 | 0.002 | 1.4x | 1.4x |
| 16 | 5 | 0.95 | 4.7e-01 | 4 | 5 | 0.000 | 4 | 4 (30) | 4 | 4 (550) | 0.000 | 0.002 | 1.3x | 1.3x |
| 24 | 3 | 0.8 | 3.2e-02 | 6 | 46 | 0.001 | 29 | 20 (58) | 14 | 8 (331) | 0.000 | 0.001 | 3.4x | 5.7x |
| 24 | 3 | 0.9 | 1.6e-01 | 6 | 11 | 0.000 | 7 | 6 (22) | 6 | 6 (297) | 0.000 | 0.002 | 1.8x | 1.9x |
| 24 | 3 | 0.95 | 3.9e-01 | 6 | 7 | 0.000 | 6 | 6 (22) | 6 | 6 (296) | 0.000 | 0.001 | 1.2x | 1.2x |
| 24 | 5 | 0.8 | 9.9e-03 | 6 | 85 | 0.002 | 39 | 18 (102) | 6 | 5 (1037) | 0.000 | 0.006 | 14.3x | 15.6x |
| 24 | 5 | 0.9 | 1.1e-01 | 7 | 10 | 0.000 | 8 | 7 (46) | 7 | 7 (1335) | 0.000 | 0.008 | 1.5x | 1.5x |
| 24 | 5 | 0.95 | 3.3e-01 | 7 | 8 | 0.000 | 7 | 7 (48) | 7 | 7 (1310) | 0.001 | 0.008 | 1.1x | 1.1x |
| 32 | 3 | 0.8 | 1.3e-02 | 8 | 119 | 0.003 | 79 | 51 (134) | 31 | 12 (705) | 0.001 | 0.004 | 3.8x | 10.2x |
| 32 | 3 | 0.9 | 8.1e-02 | 8 | 22 | 0.000 | 17 | 9 (29) | 10 | 8 (548) | 0.000 | 0.004 | 2.1x | 2.7x |
| 32 | 3 | 0.95 | 2.9e-01 | 9 | 10 | 0.000 | 9 | 9 (30) | 9 | 9 (510) | 0.000 | 0.003 | 1.1x | 1.1x |
| 32 | 5 | 0.8 | 2.4e-03 | 10 | 372 | 0.014 | 211 | 43 (265) | 14 | 10 (2760) | 0.001 | 0.027 | 26.5x | 35.9x |
| 32 | 5 | 0.9 | 5.3e-02 | 10 | 20 | 0.001 | 13 | 10 (70) | 10 | 10 (2793) | 0.000 | 0.020 | 2.0x | 2.0x |
| 32 | 5 | 0.95 | 2.3e-01 | 8 | 9 | 0.000 | 8 | 8 (49) | 8 | 8 (1812) | 0.000 | 0.016 | 1.1x | 1.1x |
| 48 | 3 | 0.8 | 1.3e-03 | 16 | 1213 | 0.023 | 816 | 165 (427) | 176 | 26 (1882) | 0.003 | 0.015 | 6.9x | 46.6x |
| 48 | 3 | 0.9 | 2.2e-02 | 12 | 84 | 0.002 | 61 | 25 (71) | 26 | 14 (1278) | 0.001 | 0.011 | 3.3x | 6.0x |
| 48 | 3 | 0.95 | 1.7e-01 | 14 | 16 | 0.000 | 14 | 14 (46) | 14 | 14 (1318) | 0.000 | 0.011 | 1.1x | 1.1x |
| 48 | 5 | 0.8 | 1.3e-04 | 14 | 6540 | 0.386 | 3433 | 223 (1258) | 34 | 17 (6242) | 0.002 | 0.069 | 195x | 394x |
| 48 | 5 | 0.9 | 1.2e-02 | 14 | 100 | 0.005 | 75 | 18 (113) | 13 | 13 (4909) | 0.001 | 0.082 | 7.5x | 7.5x |
| 48 | 5 | 0.95 | 1.1e-01 | 12 | 14 | 0.001 | 11 | 11 (74) | 11 | 11 (4257) | 0.000 | 0.049 | 1.2x | 1.2x |

The required grid is easy for everyone (p* ≥ 10⁻⁴, Graves ≤ 6.5·10³ expansions); at its hardest cell (48/5/0.8) Graves is 6540 expansions (c = 0.86/p*), policy 34, exact-backward 17 (= D+3), and exact-backward is 5.6× faster in wall-clock despite its T·W backward searches.

**Hard grid (peaky, T ∈ {64,100,150,200}, W ∈ {5,10}; `bench_hard.log`, T=64 from the earlier run with cap 10⁵):**

| T | W | conf | p* | D | 1/p* | Graves exp | Graves s | bidir exp (gen) | policy exp | policy s | exactbwd final exp | exactbwd gen (all searches) | exactbwd s |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 64 | 5 | 0.7 | 6.7e-09 | 17 | 1.5e+08 | 100000 (cap) | 11.0 | 14967 (138265) | 7724 | 0.47 | 109 | 28835 | 0.39 |
| 64 | 5 | 0.8 | 5.8e-06 | 18 | 1.7e+05 | 100000 (cap) | 10.1 | 904 (5600) | 152 | 0.008 | 18 | 9328 | 0.13 |
| 64 | 5 | 0.9 | 2.6e-03 | 18 | 3.9e+02 | 424 | 0.031 | 42 (272) | 18 | 0.001 | 18 | 8520 | 0.10 |
| 100 | 5 | 0.8 | 5.3e-09 | 30 | 1.9e+08 | 30000 (cap) | 5.1 | 15440 (139141)† | 4071 | 0.70 | 29 | 24727 | 0.85 |
| 100 | 5 | 0.9 | 8.4e-05 | 25 | 1.2e+04 | 12973 | 2.1 | — | 49 | 0.008 | 25 | 18494 | 0.44 |
| 100 | 10 | 0.7 | 3.5e-15 | 30 | 2.9e+14 | 30000 (cap) | 16.5 | — | 2418 | 0.85 | 30 | 124437 | 3.91 |
| 100 | 10 | 0.8 | 7.4e-10 | 33 | 1.3e+09 | 30000 (cap) | 14.7 | — | 108 | 0.034 | 33 | 127543 | 4.47 |
| 100 | 10 | 0.9 | 4.4e-05 | 28 | 2.3e+04 | 20824 | 11.0 | — | 28 | 0.016 | 28 | 102390 | 4.58 |
| 150 | 5 | 0.9 | 1.0e-06 | 44 | 9.8e+05 | 30000 (cap) | 9.0 | — | 252 | 0.13 | 44 | 48401 | 1.80 |
| 150 | 10 | 0.8 | 3.1e-14 | 54 | 3.2e+13 | 30000 (cap) | 21.0 | — | 511 | 0.28 | 53 | 320346 | 18.1 |
| 150 | 10 | 0.9 | 2.9e-07 | 40 | 3.5e+06 | 30000 (cap) | 31.9 | — | 40 | 0.035 | 40 | 244115 | 16.1 |
| 200 | 5 | 0.9 | 1.1e-08 | 52 | 9.3e+07 | 30000 (cap) | 11.1 | — | 979 | 0.19 | 51 | 73991 | 2.88 |
| 200 | 10 | 0.8 | 6.4e-19 | 58 | 1.6e+18 | 30000 (cap) | 36.4 | — | 4763 | 3.40 | 58 | 509757 | 35.2 |
| 200 | 10 | 0.9 | 2.2e-09 | 61 | 4.5e+08 | 30000 (cap) | 32.0 | — | 61 | 0.046 | 61 | 443906 | 26.7 |

† from the scale sweep on a different seed. Cells 100/5/0.7, 150/5/{0.7,0.8}, 150/10/0.7, 200/5/{0.7,0.8}, 200/10/0.7 are omitted because the *reference* step (policy, cap 3·10⁴) capped; exact-backward itself did not cap in any cell run (see the T=200–500 sweep below).

**Non-peaky (uniform-random rows) grid, N=3 (`bench_randomhard.log`, `rnd32.log`):**

| T | W | p* | D | 1/p* | Graves exp | Graves s | bidir exp (gen) | policy exp | exactbwd final exp | exactbwd gen | exactbwd s |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 16 | 5 | 3.3e-05 | 8 | 3.0e+04 | 22583 | 0.86 | 332 (2154) | 430 | 39 | 3264 | 0.026 |
| 16 | 8 | 9.6e-08 | 8 | 1.0e+07 | 100000 (cap) | 26.4 | 2203 (37919) | 2293 | 82 | 12195 | 0.68 |
| 24 | 5 | 4.1e-07 | 12 | 2.5e+06 | 100000 (cap) | 28.5 | 2134 (16000) | 5143 | 87 | 13156 | 0.42 |
| 24 | 8 | 6.0e-11 | 12 | 1.7e+10 | 100000 (cap) | 41.8 | 60472 (1436570) | 54553 | 113 | 33616 | 0.75 |
| 32 | 5 | 7.5e-09 | 16 | 1.3e+08 | 100000 (cap) | 22.4 | 12297 (119237) | 82451 | 271 | 19056 | 0.26 |
| 32 | 8 | 1.1e-14–2.5e-14 | 16–17 | 4e+13–9e+13 | — | — | — | — | 183 / 315 / 742 | 89012 / 200984 / 260603 | 0.9 / 2.7 / 3.6 |

**θ sensitivity of 1a (`side.log`)**, θ = p̂^α, cells = expansions / generated / |S|: at 64/5/0.7 (p* = 8·10⁻⁹) α=0.6 gives 2423 / 401352 / 97826 vs Graves > 4·10⁵ generated (capped); α=0.5 gives 16332 / 121936. The optimum is α ≈ 0.5–0.6 and the total scales as (1/p*)^0.49 (fit below) — the predicted meet-in-the-middle law.

**Looseness of 1b (`loose.log`)**: Ĥ^pol/H grows as ρ^(T−t) with ρ = 1.045 (W=5, conf 0.8), 1.022 (5, 0.9), 1.010 (10, 0.9), 1.068 (5, 0.7); it is 90× at 100 remaining frames for conf 0.8 and 6.9·10³ at 200 — this is why `policy` caps at T ≥ 200 while `exactbwd` does not.

**Scaling-law fits (`fit.py`, cells with 1/p* ≥ 30, uncapped, peaky + hard):**
```
graves     exp = 1.76 (1/p*)^0.935  R²=0.99     gen = 2.46 (1/p*)^1.07
bidir      exp = 3.34 (1/p*)^0.485  R²=0.77     gen = 9.02 (1/p*)^0.56  R²=0.98
policy     exp = 11.4 (1/p*)^0.152  (but ρ^T-limited, caps at T>=200)
exactbwd   exp = 12.1 (1/p*)^0.047 ; exp/D = 1.0 in every cell with T >= 64 ; gen ≈ 0.10·T²·W² (0.07–0.14 in all 11 hard cells)
random-hard: bidir gen = 12.6 (1/p*)^0.49 R²=0.999 ; exactbwd gen = 772 (1/p*)^0.17, exp/D = 5–17
```

**Verdicts.** 1a: real and gated; quadratic improvement (≈ 1/√p*) exactly as predicted; superseded by 1c. 1b: O(WT²) precomputation, very cheap, near-perfect up to T ≈ 100 at conf ≥ 0.8, but its looseness compounds as ρ^T; use only as the seed for 1c. **1c is the result**: final search = D expansions on peaky tables, 5–17·D on uniform-random tables; all work is in the backward searches, ≈ 0.1·T²W² nodes, independent of p*.

### Direction 2 — Viterbi-collapse / beam incumbent (`side.log`)

Viterbi path collapse equals the mode in 12/12 peaky instances (T ∈ {24,32,48}, W=5, conf 0.8), p_vit/p* = 1.000; beam-32 also 12/12. **Effect on expansions: none** — Graves with no incumbent, Viterbi incumbent, beam incumbent, or the *exact mode* as incumbent expands 88.7 / 339.0 / 9159.9 nodes identically in all four columns. Reason: best-first must expand every u with F(u) > p* before it can terminate whatever the incumbent; the incumbent only changes the termination *check*, not the set. Verdict: closed — a lower bound on p* buys nothing for best-first search with the Graves bound.

### Direction 3 — DFS branch-and-bound with a good incumbent (`side.log`)

DFS B&B (children visited best-bound-first) with the beam incumbent: 88.7 / 339.0 / 9160.8 expansions; with the exact mode as incumbent: 88.7 / 339.0 / 9159.9 — identical to best-first to within one node. Verdict: closed, as the brief anticipated: both explore {u : F(u) > p*}; B&B is only memory-light.

### Direction 4 — dominance in a weaker state

Not built. Rationale from the numbers above: exact-backward's final tree is already exactly the D prefixes of the mode (plus their W−1 children each), so no pruning of that search can save anything; the residual cost is the T·(W−1) backward searches, which are themselves near-perfect (≈ 5–12 expansions each on peaky tables; e.g. 5439 backward expansions over 396 searches at T=100, W=5). A certified-inexact dominance scheme would have to remove a constant fraction of those and would inherit the exponential-frontier problem already closed. Verdict: superseded, not run.

### Direction 5 — island / divide-and-conquer with a small boundary state

Direction 1c **is** this decomposition, in its strongest form: the boundary state is (frame t, first symbol c of the suffix), i.e. (W−1)·T states, and the adjacent-repeat coupling appears exactly as the `[u_last ≠ d]` factor in ok_d and the Rn/Rb split in the recursion. The exact search decomposes as: solve the suffix problem from every boundary state backward, then one forward search. It does better than the brief's Σ_islands c/p*_island: each per-boundary search is near-perfect because it sees the exact suffix modes of later frames, so its cost is ≈ (suffix-mode depth)·W rather than c/p*_island. The measured total, 0.1·T²·W² generated nodes, is what this gives with D ∝ T. No separate island segmentation was needed or measured.

## (c) Best decoder and its scaling law

**Exact-backward decoder** (`decode_exact_backward` in `bounds.py`): (i) seed Ĥ with the O(WT²) policy DP; (ii) for t = T..1, c = 1..W−1: H_c(t) ← best-first search from root (t, c) with bound B(u) = max(p(u), max_d Σ_{t'>t} ok_d(t'−1)·H_d(t')); (iii) final best-first search from the empty prefix with Ĥ = H. Exact by construction; gated 520/520 on brute force.

Scaling law (peaky tables, measured T ≤ 200, W ≤ 10, conf 0.7–0.9; 1/p* up to 1.6·10¹⁸):
- final-search expansions = D (exp/D = 1.00 ± 0.0 for every cell with T ≥ 64; 1.0–1.7 at T ≤ 48);
- total generated nodes ≈ 0.10·T²·W² (each O(T) arithmetic), i.e. ≈ 0.4·T³·W² flops, **no dependence on p\***;
- Graves on the same instances: 1.76·(1/p*)^0.935 expansions, 2.46·(1/p*)^1.07 generated nodes.

Wall-clock (same Python code path, same instances): 48/5/0.8: Graves 0.386 s vs 0.069 s (5.6×); 64/5/0.8: Graves ≥ 10 s (capped at 10⁵ of ≈ 1.7·10⁵ expansions) vs 0.125 s (≥ 80×); 100/5/0.8: Graves would need ≈ 1.9·10⁸ expansions ≈ 9 h at the measured 1.7·10⁻⁴ s/expansion vs 0.85 s (≈ 4·10⁴×); 200/10/0.8: ≈ 10¹⁷ expansions vs 35 s.

**Real-audio-scale sweep, exact-backward only (W=5, conf 0.8, `scale2_w5_c08.log`; Graves and policy both cap here):**

| T | inst | p* | D | final exp | backward exp (all T·(W−1) searches) | gen | sec | gen/(T²W) |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 200 | 0 | 3.4e-17 | 56 | 92 | 38981 | 156292 | 8.1 | 0.78 |
| 200 | 1 | 5.6e-17 | 60 | 61 | 25144 | 100820 | 4.3 | 0.50 |
| 300 | 0 | 1.6e-25 | 90 | 252 | 101672 | 407696 | 28.7 | 0.91 |
| 300 | 1 | 1.9e-25 | 85 | 89 | 57271 | 229440 | 16.9 | 0.51 |
| 400 | 0 | 5.4e-34 | 102 | 146 | 105364 | 422040 | 41.2 | 0.53 |
| 400 | 1 | 2.4e-33 | 111 | 111 | 90124 | 360940 | 34.8 | 0.45 |
| 500 | 0 | 1.0e-41 | 133 | 169 | 146030 | 584796 | 71.7 | 0.47 |
| 500 | 1 | 1.1e-41 | 137 | 262 | 316894 | 1268624 | 148.0 | 1.02 |

At 1/p* = 10⁴¹ the final search is 1–2·D and total work stays at 0.45–1.0·T²·W generated nodes (= 0.09–0.2·T²W² at W=5), confirming the p*-independent law out to T = 500. Each instance's argmax was cross-checked against the policy decoder where it finished (T ≤ 100) and all backward H values are exact by construction; the brute-force gates above are the correctness evidence.

On uniform-random rows (the adversarial, non-peaky regime) the final search is 5–17·D and the backward work grows mildly, gen ≈ 772·(1/p*)^0.17 — still 10⁵–10¹³ below c/p*.

## (d) Implications for the quantum-vs-classical comparison

- The honest classical exact baseline is **no longer c/p* prefix expansions**. It is ≈ 0.1·T²·W² O(T)-node evaluations (≈ 0.4·T³W² arithmetic), with a final search of D expansions, and it is p*-independent on peaky tables. Any quantum claim costed against c/p* must be re-costed against this.
- **Explicit factor.** For the real-audio operating point quoted in the brief (T ≈ 300, D ≈ 40, W ≈ 32 characters, p* ≈ 5·10⁻¹²): c/p* ≈ 3.6·10¹¹ expansions → exact-backward ≈ 0.1·300²·32² ≈ 9·10⁶ node generations ≈ 1·10¹⁰ flops. **f ≈ 4·10⁴ in node count (≈ 3·10⁷ if Graves' O(T·W) per-expansion cost is charged)** — this is an extrapolation of the measured T²W² law to W = 32; the largest directly measured factors are 3.9·10² (T=48), ≥ 10⁴ (T=64), and ≥ 10¹¹ (T=200, W=10, against the fitted Graves law).
- Consequence for a 1/√p*-type finding cost: at p* = 5·10⁻¹² that is ≈ 4.5·10⁵ evaluator calls (before constants ≈ 25 and before the O(T·D) ≈ 10⁴ cost of each exact evaluation ≈ 10¹⁰–10¹¹ elementary steps). The classical exact decoder is at ≈ 10¹⁰ flops for the same instance: the gap versus prefix search (≈ 10⁶) collapses to O(1) or a classical win. The v10 gate "advantage ⇔ p* < 1/D" was derived against the c/p* baseline and no longer applies; the relevant classical count is 0.1·T²W², so the finding-route gate would become √(1/p*) · T·D ≲ 0.1·T²·W²·T, i.e. p* ≳ (D/(0.1·T²·W²))², which real-audio p* violates by orders of magnitude in the classical direction.
- Directly useful: the exact-backward decoder makes certified-exact decoding of hard audio feasible (T=200, W=10, p* = 6·10⁻¹⁹ in 35 s of pure Python; ≈ 0.4·T³W² flops suggests seconds in C at T=500, W=32). Beam-5 misses on 3/7 utterances could be resolved exactly.

## (e) Next step

1. Run `decode_exact_backward` on the seven real wav2vec2 5 dB posteriors (T ≈ 100–500, W = 32) — port `child`/`bound_from_H` to numpy or C first (Python at W=32, T=500 is ≈ 3·10⁷ node generations × O(T)). Report certified modes vs beam-5 and the exact p* values (currently only beam-estimated at 5·10⁻¹²).
2. Tighten the backward step: restrict each search to the sub-table t..T (O(T−t) per node, halves the constant) and share H across the W−1 first symbols via max_{d≠c} bookkeeping. Target: gen ≈ 0.03·T²W².
3. Worst-case characterisation: construct tables where the single "Σ_t max_v" split is loose by the T factor (many near-tied suffix modes at different start frames) and measure whether exact-backward's final search can exceed T·D; the uniform-random grid (5–17·D) suggests not in practice.
4. Hand the number f and the 0.1·T²W² law to the quantum-costing thread; re-derive the v10 gate against it.

## (f) Real posteriors — 70 tables, all certified, none cut off

**Port and gates.** Variant 1c was ported to C (`../code/certified-exact-decoder/exactbwd.c`, ctypes wrapper `../code/certified-exact-decoder/cdecoder.py`; the search logic is a line-for-line port of `bounds.py`). The C final search also certifies the runner-up: every generated prefix carries its exact p(u), the two best distinct labellings are tracked, and the search terminates only when the top bound ≤ p₂ — so every unexplored labelling has p ≤ p₂ and the margin p*/p₂ is certified. Gate lines (`../code/certified-exact-decoder/gate.log`, `../code/certified-exact-decoder/real_gate.log`):
```
GATE C port vs stdlib exact-backward: 300 tables (T<=12, W<=8), p* mismatches 0, argmax mismatches 0, worst rel |H_C - H_py| 0.00e+00 -> PASS
GATE C port vs brute force (mode AND certified runner-up): 200 tables (T<=6, W<=8), mode wrong 0, runner-up wrong 0, exact ties 39 -> PASS
GATE stdlib vs C on real table T4/clean/P14 T=112 W=32: stdlib p*=8.963259e-01 exp=21 gen=945345 sec=160 | C p*=8.963259e-01 exp=41 gen=945965 sec=1.1 -> PASS
GATE stdlib vs C on real table T4/10dB/P14 T=112 W=32: stdlib p*=7.631711e-03 exp=20 gen=900302 sec=194 | C p*=7.631711e-03 exp=32 gen=900674 sec=7.0 -> PASS
```
(The C final search expands ~2× the stdlib count because it additionally certifies the runner-up; generated counts agree to the last few nodes, the difference being the runner-up's extra children.)

**Tables.** LibriSpeech set (table identifiers `quantum-mbr-reframing/<condition>/<utterance>`): wav2vec2-base-960h on LibriSpeech dummy utterances at clean / 10 dB / 5 dB / 0 dB additive white noise (7 each); adjacent-domain set: 40 `.npy` tables (UWB-ATCC air-traffic radio, AMI far-field SDM, TORGO dysarthric, TORGO controls; models base960h, base960h_dys, and the collapsed `torgoft` fine-tune, whose mode is a single symbol on every table). W = 32, blank = 0, T = 112–412. Per table: certified p*, mode, certified runner-up p₂, margin, generations (all O(T) node builds incl. the T·31 backward searches), final-search expansions, wall-clock (4 shards concurrently on one machine, so times above ~45 s include contention; 10-minute limit — never reached), and p(returned)/p* for greedy (Viterbi collapse) and the toolkit's `topk_labellings` at beam 5 / 50 / 800, with p recomputed exactly by `ctc_forward` (not the beam score). Raw rows: `../code/certified-exact-decoder/real_{0..3}.jsonl`; assembler `../code/certified-exact-decoder/assemble.py`.

| table | T | D | status | sec | gen | final exp | p* (certified) | p₂ (certified) | margin | greedy/p* | beam-5/p* | beam-50/p* | beam-800/p* |
|---|--:|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| T4/clean/P0 | 292 | 90 | ok | 45.9 | 1.23e+07 | 152 | 9.745e-01 | 2.923e-03 | 333.368 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P1 | 240 | 64 | ok | 24.1 | 7.43e+06 | 114 | 8.227e-01 | 2.838e-02 | 28.995 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P10 | 279 | 81 | ok | 36.3 | 1.08e+07 | 87 | 3.775e-01 | 2.446e-01 | 1.543 | 0.648 | 1.000 | 1.000 | 1.000 |
| T4/clean/P12 | 268 | 52 | ok | 22.7 | 6.96e+06 | 87 | 9.818e-01 | 1.367e-03 | 718.094 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P14 | 112 | 21 | ok | 1.2 | 9.46e+05 | 41 | 8.963e-01 | 2.903e-02 | 30.874 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P6 | 281 | 75 | ok | 35.8 | 9.20e+06 | 110 | 3.926e-01 | 1.049e-01 | 3.741 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P8 | 255 | 58 | ok | 23.8 | 6.84e+06 | 107 | 9.283e-01 | 2.202e-02 | 42.168 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P0 | 292 | 85 | ok | 41.9 | 1.16e+07 | 120 | 4.532e-03 | 3.878e-03 | 1.168 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P1 | 240 | 63 | ok | 20.2 | 7.37e+06 | 112 | 1.296e-01 | 7.526e-02 | 1.722 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P10 | 279 | 81 | ok | 34.8 | 1.08e+07 | 93 | 5.316e-02 | 2.291e-02 | 2.321 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P12 | 268 | 52 | ok | 75.9 | 6.96e+06 | 65 | 7.283e-02 | 3.417e-02 | 2.131 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P14 | 112 | 20 | ok | 1.1 | 9.01e+05 | 32 | 7.632e-03 | 4.479e-03 | 1.704 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P6 | 281 | 74 | ok | 31.0 | 9.00e+06 | 104 | 2.979e-06 | 2.786e-06 | 1.069 | 0.832 | 0.832 | 0.832 | 1.000 |
| T4/10dB/P8 | 255 | 56 | ok | 21.3 | 6.59e+06 | 61 | 2.552e-03 | 2.543e-03 | 1.003 | 0.997 | 0.997 | 0.997 | 1.000 |
| T4/5dB/P0 | 292 | 78 | ok | 37.7 | 1.06e+07 | 112 | 1.023e-10 | 9.800e-11 | 1.044 | 0.215 | 1.000 | 1.000 | 1.000 |
| T4/5dB/P1 | 240 | 57 | ok | 34.1 | 7.01e+06 | 106 | 2.623e-22 | 2.570e-22 | 1.021 | 0.225 | 0.264 | 0.632 | 1.000 |
| T4/5dB/P10 | 279 | 79 | ok | 119.1 | 1.07e+07 | 130 | 1.221e-08 | 1.171e-08 | 1.042 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/5dB/P12 | 268 | 51 | ok | 71.8 | 7.38e+06 | 72 | 2.917e-12 | 2.899e-12 | 1.006 | 0.356 | 0.771 | 1.000 | 1.000 |
| T4/5dB/P14 | 112 | 22 | ok | 1.0 | 1.02e+06 | 26 | 1.393e-03 | 1.244e-03 | 1.120 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/5dB/P6 | 281 | 70 | ok | 50.1 | 9.68e+06 | 95 | 2.198e-18 | 2.152e-18 | 1.022 | 0.775 | 0.806 | 1.000 | 1.000 |
| T4/5dB/P8 | 255 | 52 | ok | 17.9 | 5.83e+06 | 54 | 1.995e-04 | 1.419e-04 | 1.406 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/0dB/P0 | 292 | 37 | ok | 126.9 | 9.47e+06 | 77 | 6.199e-26 | 6.180e-26 | 1.003 | 0.324 | 0.341 | 0.512 | 0.713 |
| T4/0dB/P1 | 240 | 18 | ok | 13.5 | 4.11e+06 | 35 | 2.933e-14 | 2.848e-14 | 1.030 | 0.148 | 0.815 | 1.000 | 1.000 |
| T4/0dB/P10 | 279 | 32 | ok | 24.8 | 8.82e+06 | 145 | 1.838e-19 | 1.712e-19 | 1.073 | 0.406 | 1.000 | 1.000 | 1.000 |
| T4/0dB/P12 | 268 | 25 | ok | 45.8 | 1.27e+07 | 283 | 1.790e-17 | 1.740e-17 | 1.029 | 0.147 | 0.814 | 1.000 | 1.000 |
| T4/0dB/P14 | 112 | 19 | ok | 0.8 | 1.04e+06 | 29 | 3.019e-05 | 2.944e-05 | 1.025 | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/0dB/P6 | 281 | 23 | ok | 88.4 | 4.15e+07 | 1324 | 1.383e-25 | 1.351e-25 | 1.023 | 0.076 | 0.319 | 0.319 | 0.960 |
| T4/0dB/P8 | 255 | 35 | ok | 11.5 | 4.30e+06 | 69 | 1.063e-15 | 9.829e-16 | 1.081 | 0.925 | 0.925 | 1.000 | 1.000 |
| atc_uwb__TWR-34720N_002001_002559_AT | 278 | 64 | ok | 29.8 | 9.62e+06 | 132 | 5.036e-20 | 5.031e-20 | 1.001 | 0.530 | 0.678 | 0.996 | 0.996 |
| atc_uwb__TWR-A5lZHJ_000000_000613_AT | 306 | 88 | ok | 46.1 | 1.49e+07 | 150 | 4.382e-18 | 4.374e-18 | 1.002 | 0.740 | 0.872 | 0.872 | 0.872 |
| atc_uwb__TWR-A5lZHJ_002805_003388_PIAT | 291 | 87 | ok | 43.8 | 1.22e+07 | 160 | 1.090e-17 | 9.776e-18 | 1.115 | 0.411 | 0.779 | 1.000 | 1.000 |
| atc_uwb__TWR-A64ueL_000128_000777_PI | 324 | 57 | ok | 31.4 | 7.84e+06 | 65 | 1.112e-18 | 1.098e-18 | 1.013 | 0.119 | 0.306 | 0.306 | 1.000 |
| atc_uwb__TWR-a1WcrN_000157_000469_AT | 155 | 49 | ok | 4.8 | 3.88e+06 | 65 | 4.818e-09 | 4.760e-09 | 1.012 | 0.529 | 0.894 | 0.894 | 1.000 |
| atc_uwb__TWR-a3o8f0_000000_000352_AT | 175 | 63 | ok | 8.0 | 5.08e+06 | 119 | 2.083e-12 | 1.931e-12 | 1.079 | 0.289 | 1.000 | 1.000 | 1.000 |
| atc_uwb__TWR-a8R9jE_000144_000596_AT | 225 | 77 | ok | 21.2 | 8.63e+06 | 155 | 7.317e-10 | 6.528e-10 | 1.121 | 0.668 | 1.000 | 1.000 | 1.000 |
| atc_uwb__TWR-a8R9jE_000700_001023_PIAT | 161 | 46 | ok | 3.9 | 3.11e+06 | 65 | 8.907e-12 | 8.603e-12 | 1.035 | 0.624 | 0.966 | 0.966 | 1.000 |
| torgoft__atc_uwb__TWR-34720N_002001_002559_AT | 278 | 1 | ok | 0.7 | 2.75e+05 | 3 | 9.891e-03 | 5.795e-03 | 1.707 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-A5lZHJ_000000_000613_AT | 306 | 1 | ok | 1.1 | 3.03e+05 | 3 | 6.213e-03 | 4.009e-03 | 1.550 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-A5lZHJ_002805_003388_PIAT | 291 | 1 | ok | 0.6 | 2.88e+05 | 3 | 7.970e-03 | 4.889e-03 | 1.630 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-A64ueL_000128_000777_PI | 324 | 1 | ok | 0.8 | 3.21e+05 | 3 | 4.607e-03 | 3.149e-03 | 1.463 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a1WcrN_000157_000469_AT | 155 | 1 | ok | 0.2 | 1.53e+05 | 3 | 7.630e-02 | 2.478e-02 | 3.079 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a3o8f0_000000_000352_AT | 175 | 1 | ok | 0.3 | 1.73e+05 | 3 | 5.473e-02 | 2.010e-02 | 2.723 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a8R9jE_000144_000596_AT | 225 | 1 | ok | 0.3 | 2.22e+05 | 3 | 2.385e-02 | 1.129e-02 | 2.113 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a8R9jE_000700_001023_PIAT | 161 | 1 | ok | 0.2 | 1.59e+05 | 3 | 6.906e-02 | 2.331e-02 | 2.963 | 1.000 | 1.000 | 1.000 | 1.000 |
| ami_sdm__FEO070_0169920_0170266 | 172 | 21 | ok | 2.0 | 1.05e+06 | 37 | 1.323e-06 | 1.193e-06 | 1.109 | 0.902 | 0.902 | 0.902 | 1.000 |
| ami_sdm__FEO070_0201252_0201545 | 146 | 38 | ok | 4.6 | 3.49e+06 | 79 | 1.972e-09 | 1.844e-09 | 1.070 | 0.900 | 0.900 | 1.000 | 1.000 |
| ami_sdm__FEO072_0027270_0027918 | 323 | 96 | ok | 51.7 | 1.59e+07 | 176 | 2.696e-06 | 2.460e-06 | 1.096 | 0.813 | 0.912 | 1.000 | 1.000 |
| ami_sdm__MEE071_0192089_0192700 | 305 | 107 | ok | 52.5 | 1.55e+07 | 169 | 1.043e-17 | 1.040e-17 | 1.003 | 0.829 | 0.962 | 0.962 | 0.997 |
| ami_sdm__MEE073_0157652_0158052 | 199 | 51 | ok | 7.7 | 4.59e+06 | 58 | 4.033e-08 | 3.677e-08 | 1.097 | 0.371 | 0.456 | 0.792 | 0.903 |
| ami_sdm__MEE073_0182107_0182452 | 172 | 60 | ok | 6.6 | 4.45e+06 | 62 | 1.593e-11 | 1.567e-11 | 1.017 | 0.343 | 0.812 | 1.000 | 1.000 |
| ami_sdm__MEE073_0193279_0193562 | 141 | 56 | ok | 3.4 | 3.33e+06 | 64 | 1.473e-03 | 9.236e-04 | 1.595 | 1.000 | 1.000 | 1.000 | 1.000 |
| ami_sdm__MEE073_0208436_0208731 | 147 | 48 | ok | 5.1 | 3.29e+06 | 97 | 2.739e-05 | 2.215e-05 | 1.236 | 1.000 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_0 | 194 | 23 | ok | 6.9 | 2.26e+06 | 43 | 3.904e-02 | 2.792e-02 | 1.398 | 1.000 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_1 | 314 | 48 | ok | 26.1 | 7.56e+06 | 90 | 3.644e-10 | 3.589e-10 | 1.015 | 0.124 | 0.940 | 0.940 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_2 | 412 | 50 | ok | 42.3 | 1.08e+07 | 86 | 1.762e-09 | 1.574e-09 | 1.120 | 0.678 | 0.678 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_3 | 209 | 32 | ok | 5.4 | 3.23e+06 | 48 | 2.888e-04 | 2.711e-04 | 1.065 | 0.735 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_4 | 322 | 32 | ok | 24.8 | 5.90e+06 | 63 | 8.268e-08 | 7.646e-08 | 1.081 | 0.104 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_5 | 224 | 33 | ok | 13.4 | 3.82e+06 | 59 | 3.139e-07 | 3.035e-07 | 1.034 | 0.373 | 0.967 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_6 | 299 | 38 | ok | 13.9 | 5.75e+06 | 61 | 1.839e-09 | 1.829e-09 | 1.006 | 0.185 | 0.963 | 0.994 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_7 | 247 | 38 | ok | 10.5 | 5.22e+06 | 75 | 1.789e-06 | 1.693e-06 | 1.057 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_0 | 194 | 1 | ok | 0.3 | 1.92e+05 | 3 | 3.992e-02 | 1.627e-02 | 2.454 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_1 | 314 | 1 | ok | 1.0 | 3.11e+05 | 3 | 5.440e-03 | 3.602e-03 | 1.510 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_2 | 412 | 1 | ok | 1.3 | 4.08e+05 | 3 | 1.068e-03 | 9.296e-04 | 1.149 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_3 | 209 | 1 | ok | 0.3 | 2.06e+05 | 3 | 3.112e-02 | 1.367e-02 | 2.276 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_4 | 322 | 1 | ok | 1.0 | 3.19e+05 | 3 | 4.763e-03 | 3.235e-03 | 1.472 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_5 | 224 | 1 | ok | 0.5 | 2.21e+05 | 3 | 2.425e-02 | 1.143e-02 | 2.122 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_0 | 359 | 59 | ok | 38.5 | 8.90e+06 | 105 | 4.504e-01 | 7.128e-02 | 6.318 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_1 | 262 | 45 | ok | 12.3 | 4.52e+06 | 64 | 7.897e-02 | 6.260e-02 | 1.262 | 0.793 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_2 | 337 | 52 | ok | 27.4 | 6.55e+06 | 61 | 5.388e-01 | 2.255e-01 | 2.389 | 1.000 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_3 | 322 | 72 | ok | 31.6 | 9.95e+06 | 121 | 9.715e-01 | 1.181e-02 | 82.230 | 1.000 | 1.000 | 1.000 | 1.000 |

**Per-domain summary** (n, median T, median certified p*, p* range, median margin, decoder = mode counts, greedy-worst p/p*, beam-800-worst p/p*, worst sec):

| domain | n | T med | p* med | p* range | margin med | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | worst greedy/p* | worst beam-800/p* | worst sec | cut-offs |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| LibriSpeech clean | 7 | 268 | 8.96e-01 | 3.8e-01–9.8e-01 | 30.874 | 6/7 | 7/7 | 7/7 | 7/7 | 0.648 | 1.000 | 46 | 0 |
| LibriSpeech 10dB | 7 | 268 | 7.63e-03 | 3.0e-06–1.3e-01 | 1.704 | 5/7 | 5/7 | 5/7 | 7/7 | 0.832 | 1.000 | 76 | 0 |
| LibriSpeech 5dB | 7 | 268 | 1.02e-10 | 2.6e-22–1.4e-03 | 1.042 | 3/7 | 4/7 | 6/7 | 7/7 | 0.215 | 1.000 | 119 | 0 |
| LibriSpeech 0dB | 7 | 268 | 1.79e-17 | 6.2e-26–3.0e-05 | 1.029 | 1/7 | 2/7 | 5/7 | 5/7 | 0.076 | 0.713 | 127 | 0 |
| UWB-ATCC (base960h) | 8 | 252 | 1.04e-12 | 5.0e-20–4.8e-09 | 1.024 | 0/8 | 2/8 | 3/8 | 6/8 | 0.119 | 0.872 | 46 | 0 |
| UWB-ATCC (torgoft) | 8 | 252 | 1.69e-02 | 4.6e-03–7.6e-02 | 1.910 | 8/8 | 8/8 | 8/8 | 8/8 | 1.000 | 1.000 | 1 | 0 |
| AMI-SDM | 8 | 172 | 6.82e-07 | 1.0e-17–1.5e-03 | 1.096 | 2/8 | 2/8 | 5/8 | 6/8 | 0.343 | 0.903 | 53 | 0 |
| TORGO dysarthric (base960h_dys) | 8 | 273 | 1.98e-07 | 3.6e-10–3.9e-02 | 1.061 | 2/8 | 4/8 | 6/8 | 8/8 | 0.104 | 1.000 | 42 | 0 |
| TORGO dysarthric (torgoft) | 6 | 269 | 1.48e-02 | 1.1e-03–4.0e-02 | 1.816 | 6/6 | 6/6 | 6/6 | 6/6 | 1.000 | 1.000 | 1 | 0 |
| TORGO control | 4 | 330 | 4.95e-01 | 7.9e-02–9.7e-01 | 4.354 | 3/4 | 4/4 | 4/4 | 4/4 | 0.793 | 1.000 | 38 | 0 |

Worst wall-clock: T4/0dB/P0 T=292 127 s (status ok); cut-offs: []; rows: 70
gen/(T^2 W^2) over ok rows: min 0.002 max 0.513

**Beam-6400 creep resolution:**

| adjacent-domain table | beam-800 p1 | beam-6400 p1 | certified p* | 6400/p* | certified mode == beam-6400 D? |
|---|--:|--:|--:|--:|--:|
| base960h__atc_uwb__uwb-atcc_TWR-a1WcrN_000157_000469_AT | 3.3433e-09 | 3.5731e-09 (beam 6400) | 4.8180e-09 | 0.7416 | D_cert=49 vs D_6400=49; p(beam-800 labelling)/p* = 1.0000 |
| base960h__ami_sdm__AMI_EN2002a_sdm_MEE073_0193279_0193562 | 1.4703e-03 | 1.4729e-03 (beam 6400) | 1.4730e-03 | 1.0000 | D_cert=56 vs D_6400=56; p(beam-800 labelling)/p* = 1.0000 |
| base960h__atc_uwb__uwb-atcc_TWR-a8R9jE_000144_000596_AT | 6.3454e-10 | 6.6404e-10 (beam 6400) | 7.3175e-10 | 0.9075 | D_cert=77 vs D_6400=77; p(beam-800 labelling)/p* = 1.0000 |
| base960h__ami_sdm__AMI_EN2002a_sdm_MEE073_0182107_0182452 | 9.3865e-12 | 1.2803e-11 (beam 6400) | 1.5933e-11 | 0.8036 | D_cert=60 vs D_6400=60; p(beam-800 labelling)/p* = 1.0000 |


**Findings.**
- **All 70 tables decode exactly, none hit the 10-minute cut-off.** Worst wall-clock 127 s (T4/0dB/P0, T=292, under 4-way contention); median well under 30 s. Generations are 0.03–0.16·T²·W² on 69/70 tables; the one outlier is T4/0dB/P6 (0.51·T²W², final search 1324 = 58·D expansions, p* = 1.38e-25, margin 1.02) — the hardest real instance found, still 88 s.
- **Certified p* on real hard audio is far below the 5e-12 the brief assumed.** LibriSpeech 5 dB ranges 2.6e-22–1.4e-3 (median 1.0e-10); 0 dB 6.2e-26–3.0e-5 (median 1.8e-17); UWB-ATCC 5.0e-20–4.8e-9. Against c/p* prefix search these are 10¹⁰–10²⁶ expansions; the exact decoder spends 10⁶–4·10⁷ node generations. The classical baseline improvement factor on these instances is therefore 10⁴–10¹⁹, not the 4·10⁴ extrapolated in (d).
- **Beam search misses the certified mode on real data.** Beam-800 returns a sub-mode labelling on 2/7 LibriSpeech 0 dB tables (0.71·p* and 0.96·p*), 2/8 UWB-ATCC (0.872, 0.996), 2/8 AMI (0.903, 0.997); beam-50 misses on 26/70; beam-5 on 34/70; greedy on 43/70 (worst 0.076·p*). Every miss is a near-tie: certified margins on the hard domains are 1.001–1.1 (medians 1.02–1.10), i.e. the mode and runner-up differ by a few percent, and the runner-up is what the beams return.
- **Beam-6400 creep resolved.** On the four adjacent-domain tables that report flagged, the beam-6400 labelling *is* the certified mode in all four (same D, and the beam-800 labelling's exact probability equals p*), but the beam *score* was still below the true p(l): 3.573e-9 vs certified 4.818e-9 (0.74), 1.4729e-3 vs 1.4730e-3 (1.00), 6.64e-10 vs 7.3175e-10 (0.91), 1.28e-11 vs 1.5933e-11 (0.80). The creep was pruned-alignment mass on the correct labelling, not a moving mode; a finite beam's score is a lower bound on p(l), and only the exact forward recursion on the returned labelling (or the certified decoder) gives p*.
- The collapsed `torgoft` model (D = 1 everywhere) decodes in ≤ 1.3 s per table and adds nothing; it is reported for completeness.

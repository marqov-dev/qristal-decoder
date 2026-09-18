# certctc — RESULTS (2026-09-18)

Machine: this workstation, `cc` = Apple clang, C backend (`-O2 -ffp-contract=off`), Python 3.13. All commands were run from the `research/` directory.

## 1. Test suite (every gate of the two decoder reports as a test)

```
.venv/bin/python -m pytest certctc/tests -s -q
```

Gate lines (full log: 13 passed in 7.3 s):

```
GATE (a) argmax AND p_mode vs brute force, random T<=8 W<=3: 300 instances, wrong = {'python': 0, 'c': 0}, exact ties at p* 0 -> PASS
GATE (b) runner-up AND p_runner_up vs brute force (second largest, ties explicit), random T<=8 W<=3: 300 instances, wrong = {'python': 0, 'c': 0}, exact ties at p2 0 -> PASS
GATE (f) verify() on every certificate, random T<=8 W<=3: 600 certificates, failures {'python': 0, 'c': 0} -> PASS
GATE (a) argmax AND p_mode vs brute force, peaky conf 0.5-0.9 T<=8 W<=4: 100 instances, wrong = {'python': 0, 'c': 0}, exact ties at p* 9 -> PASS
GATE (b) runner-up AND p_runner_up vs brute force (second largest, ties explicit), peaky conf 0.5-0.9 T<=8 W<=4: 100 instances, wrong = {'python': 0, 'c': 0}, exact ties at p2 33 -> PASS
GATE (f) verify() on every certificate, peaky conf 0.5-0.9 T<=8 W<=4: 200 certificates, failures {'python': 0, 'c': 0} -> PASS
GATE (a) argmax AND p_mode vs brute force, W in {5,8} T<=6: 100 instances, wrong = {'python': 0, 'c': 0}, exact ties at p* 3 -> PASS
GATE (b) runner-up AND p_runner_up vs brute force (second largest, ties explicit), W in {5,8} T<=6: 100 instances, wrong = {'python': 0, 'c': 0}, exact ties at p2 44 -> PASS
GATE (f) verify() on every certificate, W in {5,8} T<=6: 200 certificates, failures {'python': 0, 'c': 0} -> PASS
GATE (c) admissibility, exact Fractions, conf in {0.5,0.6,0.8} + random, W<=5: 74 tables, 1123 (t,c) cells H != brute-force max_v g_v(t): 0; 3517 prefixes with B(u) < max_v p(u.v): 0 -> PASS
GATE (d) decomposition p(u.v) == sum_t ok_{v1}(t-1) g_v(t), exact Fractions: 300 triples, mismatches 0 -> PASS
GATE (e) C backend vs Python backend bit-identical (p*, p2, mode, runner-up, H, expansions, generations): 100 tables (T<=12, W<=8), mismatches 0 -> PASS
GATE (f) verify() on 3 larger certificates (T up to 64, W up to 32): PASS; 4 mutations x 3 certificates rejected: PASS
GATE (g) flat rows W=5, T=8,10,12,14 [python]: final expansions [53, 161, 485, 1457] (T9: [53, 161, 485, 1457]), generations [788, 2500, 7668, 23204], growth per 2 frames ['3.038', '3.012', '3.004'] (law: W-2 = 3) -> PASS
GATE (g) flat rows W=5, T=8,10,12,14 [c]: final expansions [53, 161, 485, 1457] (T9: [53, 161, 485, 1457]), generations [788, 2500, 7668, 23204], growth per 2 frames ['3.038', '3.012', '3.004'] (law: W-2 = 3) -> PASS
GATE (g) flat rows W=4, T=8..14: final expansions [22, 46, 94, 190], growth per 2 frames ['2.091', '2.043', '2.021'] (law: W-2 = 2) -> PASS
GATE (h) final expansions <= |prefixes of labellings with p >= p2/T| (T9 theorem, p2 for the runner-up-certifying search): 48 instances, violations 0 -> PASS
GATE (i) vs T2b bounds.py (H bit-identical, p*, mode) and T9 t9core (H bit-identical, p*, mode): 20 tables, mismatches T2b 0, T9 0 -> PASS; backward expansion counts differ from T9 on 0/20 tables (0 of them peaky: exact-tie ordering, see README)
GATE (j) blank != 0 handled by column permutation (20 tables, 1 exact runner-up ties reported in permuted order), budgets raise BudgetExceeded instead of returning a certificate -> PASS
13 passed in 7.31s
```

Notes.
- (a)/(b) run every instance through both backends; "exact ties" are instances where several labellings share p* (resp. p₂) to 1e-12 — the decoder's answer is accepted iff its labelling attains that value.
- (g) pins the adversarial-decoder-check report's worst case: on flat rows the final search expands exactly 53/161/485/1457 nodes at T = 8/10/12/14 (W = 5), i.e. ×3 = W−2 per two frames, with `margin == 1` (exact ties). The generation counts 788/2500/7668/23204 are the adversarial-decoder-check report's `grow_flat5.log` to the node.
- (i): H, p* and the mode are bit-identical to `../code/certified-exact-decoder/bounds.py` and `../code/adversarial-decoder-check/t9core.py`; the backward-search expansion counts equal the adversarial-decoder-check report's on 20/20 tables.
- Two test-side corrections were made while writing the suite (no decoder change): the comparison against the adversarial-decoder-check code initially subtracted the adversarial-decoder-check report's *mode-only* final-search generations from this package's *runner-up-certifying* total (wrong quantity; backward generations are exactly `expansions_backward·(W−1)`), and the blank-permutation test initially rejected an exact runner-up tie reported in a different symbol order. A third fix replaced a time-limit test instance that the C backend finished before the deadline (flat T=20 → T=28).

## 2. Synthetic scaling bench (the worst case, reproducible)

```
.venv/bin/python -m certctc bench --gen-cap 5000000 --time-limit 60 --out certctc/bench.jsonl > certctc/bench.log
```

One instance per cell, seed 7, toolkit `peaky_table` (≈70 % blank frames, winner mass = conf, rest uniform) and flat rows (every entry 1/W).
`gen` = all node generations (T·(W−1) backward searches + final), each O(W·T); `law` = gen / (0.1·T²·W²); `(W−2)^(T/2)` = the flat-row growth law for the final search. CAP = the 5·10⁶-generation budget was exhausted (`BudgetExceeded`, no certificate). Total bench wall-clock ≈ 20 s.

| family | W | T | status | D | p* | p2 | margin | expF | expF/D | gen | gen/(0.1 T²W²) | (W-2)^(T/2) | sec | backend |
|---|--:|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| peaky0.5 | 5 | 16 | ok | 4 | 3.434e-04 | 3.434e-04 | 1 | 60 | 15.00 | 2708 | 4.23 | 6.56e+03 | 0.00 | c |
| peaky0.5 | 5 | 32 | ok | 9 | 1.653e-07 | 1.652e-07 | 1.001 | 726 | 80.67 | 54300 | 21.21 | 4.3e+07 | 0.01 | c |
| peaky0.5 | 5 | 64 | CAP (gen_cap) | - | - | - | - | - | - | >5000000 | >488.28 | 1.85e+15 | 0.89 | c |
| peaky0.5 | 5 | 128 | CAP (gen_cap) | - | - | - | - | - | - | >5000000 | >122.07 | 3.43e+30 | 1.13 | c |
| peaky0.5 | 32 | 16 | ok | 3 | 1.891e-05 | 3.773e-06 | 5.014 | 96 | 32.00 | 30752 | 1.17 | 6.56e+11 | 0.00 | c |
| peaky0.5 | 32 | 32 | ok | 11 | 3.738e-10 | 8.577e-11 | 4.358 | 100 | 9.09 | 132525 | 1.26 | 4.3e+23 | 0.04 | c |
| peaky0.5 | 32 | 64 | ok | 10 | 1.139e-19 | 6.407e-20 | 1.778 | 11 | 1.10 | 221061 | 0.53 | 1.85e+47 | 0.11 | c |
| peaky0.5 | 32 | 128 | ok | 35 | 1.901e-38 | 9.405e-39 | 2.021 | 53 | 1.51 | 2036948 | 1.21 | 3.43e+94 | 1.95 | c |
| peaky0.6 | 5 | 16 | ok | 4 | 1.530e-03 | 1.455e-03 | 1.052 | 5 | 1.25 | 316 | 0.49 | 6.56e+03 | 0.00 | c |
| peaky0.6 | 5 | 32 | ok | 10 | 4.976e-06 | 4.914e-06 | 1.013 | 47 | 4.70 | 6348 | 2.48 | 4.3e+07 | 0.00 | c |
| peaky0.6 | 5 | 64 | ok | 21 | 1.811e-11 | 1.807e-11 | 1.002 | 311 | 14.81 | 111112 | 10.85 | 1.85e+15 | 0.03 | c |
| peaky0.6 | 5 | 128 | ok | 38 | 4.575e-22 | 4.570e-22 | 1.001 | 3336 | 87.79 | 3450184 | 84.23 | 3.43e+30 | 0.98 | c |
| peaky0.6 | 32 | 16 | ok | 3 | 3.115e-04 | 6.782e-05 | 4.593 | 94 | 31.33 | 36456 | 1.39 | 6.56e+11 | 0.00 | c |
| peaky0.6 | 32 | 32 | ok | 12 | 1.194e-07 | 1.520e-08 | 7.85 | 22 | 1.83 | 202089 | 1.93 | 4.3e+23 | 0.04 | c |
| peaky0.6 | 32 | 64 | ok | 18 | 1.087e-14 | 2.814e-15 | 3.861 | 88 | 4.89 | 599912 | 1.43 | 1.85e+47 | 0.23 | c |
| peaky0.6 | 32 | 128 | ok | 35 | 1.358e-28 | 5.597e-29 | 2.426 | 59 | 1.69 | 2436848 | 1.45 | 3.43e+94 | 2.23 | c |
| peaky0.8 | 5 | 16 | ok | 3 | 4.509e-02 | 1.911e-02 | 2.359 | 4 | 1.33 | 356 | 0.56 | 6.56e+03 | 0.00 | c |
| peaky0.8 | 5 | 32 | ok | 11 | 2.460e-03 | 9.524e-04 | 2.583 | 34 | 3.09 | 3304 | 1.29 | 4.3e+07 | 0.00 | c |
| peaky0.8 | 5 | 64 | ok | 16 | 7.599e-06 | 5.482e-06 | 1.386 | 25 | 1.56 | 8076 | 0.79 | 1.85e+15 | 0.00 | c |
| peaky0.8 | 5 | 128 | ok | 36 | 3.138e-11 | 1.906e-11 | 1.646 | 61 | 1.69 | 39368 | 0.96 | 3.43e+30 | 0.02 | c |
| peaky0.8 | 32 | 16 | ok | 2 | 2.888e-02 | 2.806e-03 | 10.29 | 4 | 2.00 | 21204 | 0.81 | 6.56e+11 | 0.00 | c |
| peaky0.8 | 32 | 32 | ok | 7 | 8.625e-04 | 5.595e-05 | 15.42 | 66 | 9.43 | 111383 | 1.06 | 4.3e+23 | 0.03 | c |
| peaky0.8 | 32 | 64 | ok | 18 | 7.799e-07 | 5.675e-08 | 13.74 | 19 | 1.06 | 538191 | 1.28 | 1.85e+47 | 0.22 | c |
| peaky0.8 | 32 | 128 | ok | 41 | 6.692e-13 | 5.967e-14 | 11.22 | 51 | 1.24 | 2228838 | 1.33 | 3.43e+94 | 2.30 | c |
| peaky0.9 | 5 | 16 | ok | 6 | 2.409e-01 | 2.055e-02 | 11.72 | 19 | 3.17 | 868 | 1.36 | 6.56e+03 | 0.00 | c |
| peaky0.9 | 5 | 32 | ok | 13 | 5.038e-02 | 9.816e-03 | 5.132 | 26 | 2.00 | 3572 | 1.40 | 4.3e+07 | 0.00 | c |
| peaky0.9 | 5 | 64 | ok | 18 | 3.075e-03 | 6.132e-04 | 5.015 | 79 | 4.39 | 10160 | 0.99 | 1.85e+15 | 0.00 | c |
| peaky0.9 | 5 | 128 | ok | 32 | 5.836e-06 | 2.409e-06 | 2.422 | 57 | 1.78 | 32084 | 0.78 | 3.43e+30 | 0.02 | c |
| peaky0.9 | 32 | 16 | ok | 6 | 1.887e-01 | 4.066e-03 | 46.43 | 123 | 20.50 | 49755 | 1.90 | 6.56e+11 | 0.01 | c |
| peaky0.9 | 32 | 32 | ok | 12 | 3.638e-02 | 7.842e-04 | 46.39 | 19 | 1.58 | 207824 | 1.98 | 4.3e+23 | 0.04 | c |
| peaky0.9 | 32 | 64 | ok | 20 | 1.306e-03 | 3.752e-05 | 34.8 | 37 | 1.85 | 614606 | 1.47 | 1.85e+47 | 0.27 | c |
| peaky0.9 | 32 | 128 | ok | 35 | 1.692e-06 | 7.298e-08 | 23.18 | 55 | 1.57 | 2128274 | 1.27 | 3.43e+94 | 2.10 | c |
| flat | 5 | 16 | ok | 7 | 5.356e-06 | 5.356e-06 | 1 | 4373 | 624.71 | 69844 | 109.13 | 6.56e+03 | 0.00 | c |
| flat | 5 | 32 | CAP (gen_cap) | - | - | - | - | - | - | >5000000 | >1953.12 | 4.3e+07 | 0.41 | c |
| flat | 5 | 64 | CAP (gen_cap) | - | - | - | - | - | - | >5000000 | >488.28 | 1.85e+15 | 0.53 | c |
| flat | 5 | 128 | CAP (gen_cap) | - | - | - | - | - | - | >5000000 | >122.07 | 3.43e+30 | 0.67 | c |
| flat | 32 | 16 | CAP (gen_cap) | - | - | - | - | - | - | >5000021 | >190.74 | 6.56e+11 | 0.20 | c |
| flat | 32 | 32 | CAP (gen_cap) | - | - | - | - | - | - | >5000021 | >47.68 | 4.3e+23 | 0.26 | c |
| flat | 32 | 64 | CAP (gen_cap) | - | - | - | - | - | - | >5000021 | >11.92 | 1.85e+47 | 0.31 | c |
| flat | 32 | 128 | CAP (gen_cap) | - | - | - | - | - | - | >5000021 | >2.98 | 3.43e+94 | 0.37 | c |

Reading. (i) Peaky conf ≥ 0.8: `gen/(0.1·T²W²)` = 0.56–1.98 at every T and W, final search 1.1–1.8·D at T ≥ 64 — the certified-exact-decoder law, seconds in C at T=128, W=32 (p* down to 6·10⁻¹³). (ii) At conf 0.6 and W=5 the exponent bends up (law ratio 0.5 → 2.5 → 11 → 84 as T doubles; final search 88·D at T=128) — the adversarial-decoder-check report's α = 0.17 regime. (iii) At conf 0.5, W=5 the search exhausts 5·10⁶ generations already at T=64 (the adversarial-decoder-check report: 1.4·10⁶–>3·10⁶ on other seeds) — the α ≈ 0.3 regime. (iv) Flat rows: T=16, W=5 finishes with 4373 final expansions (= the adversarial-decoder-check report), everything larger caps: the `(W−2)^{T/2}` lower bound is the wall. (v) At W=32 the conf-0.5/0.6 cells are *easy* (law 0.5–1.9) because the per-symbol competitor mass is (1−conf)/(W−1) ≈ 1/62: what matters is the ratio r = (1−c)/((W−1)c) of the adversarial-decoder-check report's argument, not conf alone.

## 3. Real posteriors — 70 tables, regenerated with certctc

The tables were still on disk (the LibriSpeech `posteriors_{clean,10dB,5dB,0dB}.npz` archives, 7 utterances each, and the adjacent-domain `.npy` tables, 42 tables; none are redistributed; W = 32, blank = 0, T = 112–412), so the certified columns below are **this package's output** (C backend, 4 shards concurrently on one machine — times above ~30 s include contention; 600 s limit, never reached). The greedy column is recomputed here (`ctc_prob` of the Viterbi collapse); the beam-5/50/800 columns are the certified-exact-decoder report's (`../code/certified-exact-decoder/real_*.jsonl`, toolkit `topk_labellings` with p recomputed exactly), merged by table name. The last line is the cross-check gate: every certified p*, p₂, mode, generation count and final-expansion count equals the certified-exact-decoder report's run.

```
for i in 0 1 2 3; do .venv/bin/python -m certctc real --nshards 4 --shard $i --out certctc/real_rows_$i.jsonl > certctc/real_rows_$i.log & done; wait
.venv/bin/python -m certctc assemble --rows 'certctc/real_rows_*.jsonl' --t2b T2b
```

| table | T | D | status | sec | gen | final exp | p* (certified) | p2 (certified) | margin | verify | greedy/p* | beam-5/p* | beam-50/p* | beam-800/p* |
|---|--:|--:|---|--:|--:|--:|--:|--:|--:|---|--:|--:|--:|--:|
| T4/clean/P0 | 292 | 90 | ok | 40.1 | 1.23e+07 | 152 | 9.745e-01 | 2.923e-03 | 333.368 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P1 | 240 | 64 | ok | 18.4 | 7.43e+06 | 114 | 8.227e-01 | 2.838e-02 | 28.995 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P10 | 279 | 81 | ok | 33.5 | 1.08e+07 | 87 | 3.775e-01 | 2.446e-01 | 1.543 | PASS | 0.648 | 1.000 | 1.000 | 1.000 |
| T4/clean/P12 | 268 | 52 | ok | 21.4 | 6.96e+06 | 87 | 9.818e-01 | 1.367e-03 | 718.094 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P14 | 112 | 21 | ok | 1.0 | 9.46e+05 | 41 | 8.963e-01 | 2.903e-02 | 30.874 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P6 | 281 | 75 | ok | 29.1 | 9.20e+06 | 110 | 3.926e-01 | 1.049e-01 | 3.741 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/clean/P8 | 255 | 58 | ok | 19.0 | 6.84e+06 | 107 | 9.283e-01 | 2.202e-02 | 42.168 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P0 | 292 | 85 | ok | 38.2 | 1.16e+07 | 120 | 4.532e-03 | 3.878e-03 | 1.168 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P1 | 240 | 63 | ok | 19.2 | 7.37e+06 | 112 | 1.296e-01 | 7.526e-02 | 1.722 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P10 | 279 | 81 | ok | 32.6 | 1.08e+07 | 93 | 5.316e-02 | 2.291e-02 | 2.321 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P12 | 268 | 52 | ok | 21.4 | 6.96e+06 | 65 | 7.283e-02 | 3.417e-02 | 2.131 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P14 | 112 | 20 | ok | 1.0 | 9.01e+05 | 32 | 7.632e-03 | 4.479e-03 | 1.704 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/10dB/P6 | 281 | 74 | ok | 28.9 | 9.00e+06 | 104 | 2.979e-06 | 2.786e-06 | 1.069 | PASS | 0.832 | 0.832 | 0.832 | 1.000 |
| T4/10dB/P8 | 255 | 56 | ok | 18.9 | 6.59e+06 | 61 | 2.552e-03 | 2.543e-03 | 1.003 | PASS | 0.997 | 0.997 | 0.997 | 1.000 |
| T4/5dB/P0 | 292 | 78 | ok | 35.3 | 1.06e+07 | 112 | 1.023e-10 | 9.800e-11 | 1.044 | PASS | 0.215 | 1.000 | 1.000 | 1.000 |
| T4/5dB/P1 | 240 | 57 | ok | 17.9 | 7.01e+06 | 106 | 2.623e-22 | 2.570e-22 | 1.021 | PASS | 0.225 | 0.264 | 0.632 | 1.000 |
| T4/5dB/P10 | 279 | 79 | ok | 31.9 | 1.07e+07 | 130 | 1.221e-08 | 1.171e-08 | 1.042 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/5dB/P12 | 268 | 51 | ok | 22.1 | 7.38e+06 | 72 | 2.917e-12 | 2.899e-12 | 1.006 | PASS | 0.356 | 0.771 | 1.000 | 1.000 |
| T4/5dB/P14 | 112 | 22 | ok | 1.0 | 1.02e+06 | 26 | 1.393e-03 | 1.244e-03 | 1.120 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/5dB/P6 | 281 | 70 | ok | 31.0 | 9.68e+06 | 95 | 2.198e-18 | 2.152e-18 | 1.022 | PASS | 0.775 | 0.806 | 1.000 | 1.000 |
| T4/5dB/P8 | 255 | 52 | ok | 17.1 | 5.83e+06 | 54 | 1.995e-04 | 1.419e-04 | 1.406 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/0dB/P0 | 292 | 37 | ok | 29.9 | 9.47e+06 | 77 | 6.199e-26 | 6.180e-26 | 1.003 | PASS | 0.324 | 0.341 | 0.512 | 0.713 |
| T4/0dB/P1 | 240 | 18 | ok | 8.6 | 4.11e+06 | 35 | 2.933e-14 | 2.848e-14 | 1.030 | PASS | 0.148 | 0.815 | 1.000 | 1.000 |
| T4/0dB/P10 | 279 | 32 | ok | 15.8 | 8.82e+06 | 145 | 1.838e-19 | 1.712e-19 | 1.073 | PASS | 0.406 | 1.000 | 1.000 | 1.000 |
| T4/0dB/P12 | 268 | 25 | ok | 42.2 | 1.27e+07 | 283 | 1.790e-17 | 1.740e-17 | 1.029 | PASS | 0.147 | 0.814 | 1.000 | 1.000 |
| T4/0dB/P14 | 112 | 19 | ok | 0.9 | 1.04e+06 | 29 | 3.019e-05 | 2.944e-05 | 1.025 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| T4/0dB/P6 | 281 | 23 | ok | 73.8 | 4.15e+07 | 1324 | 1.383e-25 | 1.351e-25 | 1.023 | PASS | 0.076 | 0.319 | 0.319 | 0.960 |
| T4/0dB/P8 | 255 | 35 | ok | 12.3 | 4.30e+06 | 69 | 1.063e-15 | 9.829e-16 | 1.081 | PASS | 0.925 | 0.925 | 1.000 | 1.000 |
| atc_uwb__TWR-34720N_002001_002559_AT | 278 | 64 | ok | 30.1 | 9.62e+06 | 132 | 5.036e-20 | 5.031e-20 | 1.001 | PASS | 0.530 | 0.678 | 0.996 | 0.996 |
| atc_uwb__TWR-A5lZHJ_000000_000613_AT | 306 | 88 | ok | 46.6 | 1.49e+07 | 150 | 4.382e-18 | 4.374e-18 | 1.002 | PASS | 0.740 | 0.872 | 0.872 | 0.872 |
| atc_uwb__TWR-A5lZHJ_002805_003388_PIAT | 291 | 87 | ok | 32.7 | 1.22e+07 | 160 | 1.090e-17 | 9.776e-18 | 1.115 | PASS | 0.411 | 0.779 | 1.000 | 1.000 |
| atc_uwb__TWR-A64ueL_000128_000777_PI | 324 | 57 | ok | 24.2 | 7.84e+06 | 65 | 1.112e-18 | 1.098e-18 | 1.013 | PASS | 0.119 | 0.306 | 0.306 | 1.000 |
| atc_uwb__TWR-a1WcrN_000157_000469_AT | 155 | 49 | ok | 5.3 | 3.88e+06 | 65 | 4.818e-09 | 4.760e-09 | 1.012 | PASS | 0.529 | 0.894 | 0.894 | 1.000 |
| atc_uwb__TWR-a3o8f0_000000_000352_AT | 175 | 63 | ok | 8.1 | 5.08e+06 | 119 | 2.083e-12 | 1.931e-12 | 1.079 | PASS | 0.289 | 1.000 | 1.000 | 1.000 |
| atc_uwb__TWR-a8R9jE_000144_000596_AT | 225 | 77 | ok | 15.2 | 8.63e+06 | 155 | 7.317e-10 | 6.528e-10 | 1.121 | PASS | 0.668 | 1.000 | 1.000 | 1.000 |
| atc_uwb__TWR-a8R9jE_000700_001023_PIAT | 161 | 46 | ok | 3.5 | 3.11e+06 | 65 | 8.907e-12 | 8.603e-12 | 1.035 | PASS | 0.624 | 0.966 | 0.966 | 1.000 |
| torgoft__atc_uwb__TWR-34720N_002001_002559_AT | 278 | 1 | ok | 0.6 | 2.75e+05 | 3 | 9.891e-03 | 5.795e-03 | 1.707 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-A5lZHJ_000000_000613_AT | 306 | 1 | ok | 0.8 | 3.03e+05 | 3 | 6.213e-03 | 4.009e-03 | 1.550 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-A5lZHJ_002805_003388_PIAT | 291 | 1 | ok | 0.8 | 2.88e+05 | 3 | 7.970e-03 | 4.889e-03 | 1.630 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-A64ueL_000128_000777_PI | 324 | 1 | ok | 1.1 | 3.21e+05 | 3 | 4.607e-03 | 3.149e-03 | 1.463 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a1WcrN_000157_000469_AT | 155 | 1 | ok | 0.2 | 1.53e+05 | 3 | 7.630e-02 | 2.478e-02 | 3.079 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a3o8f0_000000_000352_AT | 175 | 1 | ok | 0.2 | 1.73e+05 | 3 | 5.473e-02 | 2.010e-02 | 2.723 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a8R9jE_000144_000596_AT | 225 | 1 | ok | 0.4 | 2.22e+05 | 3 | 2.385e-02 | 1.129e-02 | 2.113 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__atc_uwb__TWR-a8R9jE_000700_001023_PIAT | 161 | 1 | ok | 0.2 | 1.59e+05 | 3 | 6.906e-02 | 2.331e-02 | 2.963 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| ami_sdm__FEO070_0169920_0170266 | 172 | 21 | ok | 2.1 | 1.05e+06 | 37 | 1.323e-06 | 1.193e-06 | 1.109 | PASS | 0.902 | 0.902 | 0.902 | 1.000 |
| ami_sdm__FEO070_0201252_0201545 | 146 | 38 | ok | 3.9 | 3.49e+06 | 79 | 1.972e-09 | 1.844e-09 | 1.070 | PASS | 0.900 | 0.900 | 1.000 | 1.000 |
| ami_sdm__FEO072_0027270_0027918 | 323 | 96 | ok | 52.7 | 1.59e+07 | 176 | 2.696e-06 | 2.460e-06 | 1.096 | PASS | 0.813 | 0.912 | 1.000 | 1.000 |
| ami_sdm__MEE071_0192089_0192700 | 305 | 107 | ok | 46.2 | 1.55e+07 | 169 | 1.043e-17 | 1.040e-17 | 1.003 | PASS | 0.829 | 0.962 | 0.962 | 0.997 |
| ami_sdm__MEE073_0157652_0158052 | 199 | 51 | ok | 7.8 | 4.59e+06 | 58 | 4.033e-08 | 3.677e-08 | 1.097 | PASS | 0.371 | 0.456 | 0.792 | 0.903 |
| ami_sdm__MEE073_0182107_0182452 | 172 | 60 | ok | 6.8 | 4.45e+06 | 62 | 1.593e-11 | 1.567e-11 | 1.017 | PASS | 0.343 | 0.812 | 1.000 | 1.000 |
| ami_sdm__MEE073_0193279_0193562 | 141 | 56 | ok | 3.9 | 3.33e+06 | 64 | 1.473e-03 | 9.236e-04 | 1.595 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| ami_sdm__MEE073_0208436_0208731 | 147 | 48 | ok | 3.3 | 3.29e+06 | 97 | 2.739e-05 | 2.215e-05 | 1.236 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_0 | 194 | 23 | ok | 4.2 | 2.26e+06 | 43 | 3.904e-02 | 2.792e-02 | 1.398 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_1 | 314 | 48 | ok | 24.6 | 7.56e+06 | 90 | 3.644e-10 | 3.589e-10 | 1.015 | PASS | 0.124 | 0.940 | 0.940 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_2 | 412 | 50 | ok | 51.6 | 1.08e+07 | 86 | 1.762e-09 | 1.574e-09 | 1.120 | PASS | 0.678 | 0.678 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_3 | 209 | 32 | ok | 6.9 | 3.23e+06 | 48 | 2.888e-04 | 2.711e-04 | 1.065 | PASS | 0.735 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_4 | 322 | 32 | ok | 17.2 | 5.90e+06 | 63 | 8.268e-08 | 7.646e-08 | 1.081 | PASS | 0.104 | 1.000 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_5 | 224 | 33 | ok | 8.2 | 3.82e+06 | 59 | 3.139e-07 | 3.035e-07 | 1.034 | PASS | 0.373 | 0.967 | 1.000 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_6 | 299 | 38 | ok | 16.9 | 5.75e+06 | 61 | 1.839e-09 | 1.829e-09 | 1.006 | PASS | 0.185 | 0.963 | 0.994 | 1.000 |
| base960h_dys__torgo_dys__torgo_dys_7 | 247 | 38 | ok | 13.5 | 5.22e+06 | 75 | 1.789e-06 | 1.693e-06 | 1.057 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_0 | 194 | 1 | ok | 0.3 | 1.92e+05 | 3 | 3.992e-02 | 1.627e-02 | 2.454 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_1 | 314 | 1 | ok | 0.9 | 3.11e+05 | 3 | 5.440e-03 | 3.602e-03 | 1.510 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_2 | 412 | 1 | ok | 1.7 | 4.08e+05 | 3 | 1.068e-03 | 9.296e-04 | 1.149 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_3 | 209 | 1 | ok | 0.4 | 2.06e+05 | 3 | 3.112e-02 | 1.367e-02 | 2.276 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_4 | 322 | 1 | ok | 0.8 | 3.19e+05 | 3 | 4.763e-03 | 3.235e-03 | 1.472 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgoft__torgo_dys__torgo_dys_5 | 224 | 1 | ok | 0.4 | 2.21e+05 | 3 | 2.425e-02 | 1.143e-02 | 2.122 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_0 | 359 | 59 | ok | 39.8 | 8.90e+06 | 105 | 4.504e-01 | 7.128e-02 | 6.318 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_1 | 262 | 45 | ok | 14.6 | 4.52e+06 | 64 | 7.897e-02 | 6.260e-02 | 1.262 | PASS | 0.793 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_2 | 337 | 52 | ok | 26.1 | 6.55e+06 | 61 | 5.388e-01 | 2.255e-01 | 2.389 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |
| torgo_ctl__torgo_ctl_3 | 322 | 72 | ok | 38.4 | 9.95e+06 | 121 | 9.715e-01 | 1.181e-02 | 82.230 | PASS | 1.000 | 1.000 | 1.000 | 1.000 |

**Per-domain summary** (n, median T, median certified p*, p* range, median margin, decoder = mode counts, worst greedy/p*, worst beam-800/p*, worst sec, cut-offs):

| domain | n | T med | p* med | p* range | margin med | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | worst greedy/p* | worst beam-800/p* | worst sec | cut-offs |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| LibriSpeech clean | 7 | 268 | 8.96e-01 | 3.8e-01-9.8e-01 | 30.874 | 6/7 | 7/7 | 7/7 | 7/7 | 0.648 | 1.000 | 40 | 0 |
| LibriSpeech 10dB | 7 | 268 | 7.63e-03 | 3.0e-06-1.3e-01 | 1.704 | 5/7 | 5/7 | 5/7 | 7/7 | 0.832 | 1.000 | 38 | 0 |
| LibriSpeech 5dB | 7 | 268 | 1.02e-10 | 2.6e-22-1.4e-03 | 1.042 | 3/7 | 4/7 | 6/7 | 7/7 | 0.215 | 1.000 | 35 | 0 |
| LibriSpeech 0dB | 7 | 268 | 1.79e-17 | 6.2e-26-3.0e-05 | 1.029 | 1/7 | 2/7 | 5/7 | 5/7 | 0.076 | 0.713 | 74 | 0 |
| UWB-ATCC (base960h) | 8 | 252 | 1.04e-12 | 5.0e-20-4.8e-09 | 1.024 | 0/8 | 2/8 | 3/8 | 6/8 | 0.119 | 0.872 | 47 | 0 |
| UWB-ATCC (torgoft) | 8 | 252 | 1.69e-02 | 4.6e-03-7.6e-02 | 1.910 | 8/8 | 8/8 | 8/8 | 8/8 | 1.000 | 1.000 | 1 | 0 |
| AMI-SDM | 8 | 172 | 6.82e-07 | 1.0e-17-1.5e-03 | 1.096 | 2/8 | 2/8 | 5/8 | 6/8 | 0.343 | 0.903 | 53 | 0 |
| TORGO dysarthric (base960h_dys) | 8 | 273 | 1.98e-07 | 3.6e-10-3.9e-02 | 1.061 | 2/8 | 4/8 | 6/8 | 8/8 | 0.104 | 1.000 | 52 | 0 |
| TORGO dysarthric (torgoft) | 6 | 269 | 1.48e-02 | 1.1e-03-4.0e-02 | 1.816 | 6/6 | 6/6 | 6/6 | 6/6 | 1.000 | 1.000 | 2 | 0 |
| TORGO control | 4 | 330 | 4.95e-01 | 7.9e-02-9.7e-01 | 4.354 | 3/4 | 4/4 | 4/4 | 4/4 | 0.793 | 1.000 | 40 | 0 |

Rows: 70 (ok 70, cut-offs []). Worst wall-clock: T4/0dB/P6 T=281 73.8 s. gen/(T^2 W^2): min 0.002, median 0.094, max 0.513. verify() PASS on 70/70.
GATE certctc vs T2b real_*.jsonl (p*, p2, mode, generations, final expansions all identical): 70/70 agree, disagreements 0 -> PASS

Findings (unchanged from the certified-exact-decoder report §(f), now reproduced independently of its code path): all 70 tables certify, none cut off, worst 74 s (T4/0dB/P6, the 0.51·T²W² outlier with a 1324 = 58·D final search); certified p* on hard audio is 10⁻²⁶–10⁻⁹ with margins 1.001–1.1; beam-800 misses the certified mode on 6/70 tables, beam-50 on 26/70, beam-5 on 34/70, greedy on 43/70 — every miss a near-tie in which the beam returns the certified runner-up.

# certctc — certified-exact CTC decoding (mode, runner-up, margin)

`certctc` takes a CTC posterior table `y` (T frames × W symbols, blank column, rows need not sum
to 1) and returns a **certificate**: the labelling of maximum probability `p(l | y)`, the
second-best labelling, both probabilities exactly, and their ratio — computed by an admissible
best-first search that never discards a labelling it has not bounded. It is the
"exact backward suffix modes" decoder (variant 1c) of the certified-exact-decoder report, as
independently re-implemented and adversarially checked in the adversarial-decoder-check report, packaged with every gate from both threads as a test.

```
from certctc import decode, verify
cert = decode(table, blank=0)          # numpy (T, W) array or list of rows
assert verify(table, cert)             # independent forward-recursion check
print(cert.summary()); print(cert.to_json(indent=1))
```

## What it computes and certifies

For a table `y` let `p(l) = Σ_{π: collapse(π) = l} Π_t y_t[π_t]` (Graves 2006). The certificate states

| field | meaning |
|---|---|
| `mode`, `p_mode` | a labelling with `p(mode) = max_l p(l)`, and that maximum |
| `runner_up`, `p_runner_up` | a labelling `≠ mode` with `p(runner_up) = max_{l ≠ mode} p(l)`, and that value |
| `margin` | `p_mode / p_runner_up` (`inf` if every other labelling has probability 0) |
| `pruned_mass_bound` | **always 0** — see below |
| `T, W, D` | table shape and `len(mode)` |
| `expansions_final`, `expansions_backward`, `generations_total` | search-effort counters (accounting of the two decoder reports: generations = `child()` calls, each O(W·T)) |
| `wall_seconds`, `backend` | `"c"` (compiled on demand with `cc`) or `"python"` (bit-identical fallback) |

**Exactness.** The search maintains the two best distinct labellings seen (`b1 ≥ b2`) and stops
only when the largest remaining bound is `≤ b2`. Every labelling is either generated (so its
probability was compared with `b1, b2`) or lies in a pruned subtree whose admissible bound — an
upper bound on every probability in it — was `≤ b2` at the time. Hence on termination
`b1 = max_l p(l)` and `b2 = max_{l ≠ mode} p(l)`, with nothing approximated. `pruned_mass_bound`
is the field an *inexact* decoder (a beam) would use to report "no discarded labelling exceeds
this"; here it is identically 0 because nothing is discarded uncertified, and `verify()` rejects
any certificate with a non-zero value. The only approximation is IEEE-754 rounding of the bound
sums (relative ≈ T·ε); the test suite gates the same code in exact rational arithmetic
(`fractions.Fraction`) for admissibility and the decomposition identity, and against brute force
in float.

**Ties.** If several labellings share the maximum, `mode` is one of them and `runner_up` is
another (so `margin = 1`). If several share the second-largest value, `runner_up` is one of them.
Which one is reported depends on the symbol order (the flat-row test asserts `margin == 1`
exactly; the blank-permutation test shows a tie reported in a different order).

**What `verify()` checks.** It recomputes `p(mode)` and `p(runner_up)` by the standard forward
recursion over the extended label sequence (no code shared with the search) and checks the
certificate's internal consistency (`runner_up ≠ mode`, `margin`, shape, `pruned_mass_bound == 0`).
It cannot check *maximality* — that is the admissibility argument below, gated against brute
force in the tests — and it is mutation-tested: perturbing `p_mode`, swapping the runner-up for
the mode, or claiming a different labelling all fail.

## The algorithm in ten lines

Frames `1..T`, blank `= 0`. For a prefix `u`, `Ab[t]`/`An[t]` = mass of paths over frames `1..t`
collapsing to `u` and ending in the blank-after-`u` / last-symbol state; `ok_d(t) = Ab[t] + [u_last ≠ d]·An[t]`
is the mass that can start a fresh symbol `d` at frame `t+1`; `p(u) = Ab[T] + An[T]`.
For a suffix `v` with `v₁ = c`, `g_v(t)` = mass of paths over frames `t..T` with `π_t = c`
collapsing to `v`.

1. **Decomposition** (exact; the segment emitting the `(|u|+1)`-th symbol starts at a unique frame): `p(u·v) = Σ_t ok_{v₁}(t−1)·g_v(t)`.
2. **Suffix modes**: `H_c(t) = max_{v: v₁ = c} g_v(t)`.
3. **Bound**: `B(u) = max( p(u), max_d Σ_t ok_d(t−1)·H_d(t) )`.
4. **Admissibility**: for any `v` with `v₁ = d`, `p(u·v) = Σ_t ok_d(t−1)·g_v(t) ≤ Σ_t ok_d(t−1)·H_d(t) ≤ B(u)` (a sum of per-frame maxima dominates every single sum). So `B(u) ≥ max_v p(u·v)` — the best completion of `u`.
5. **Backward phase**: for `t = T..1` and each `c ≠ 0`, compute `H_c(t)` *exactly* by the same best-first search rooted at "`c` forced at frame `t`", whose bound reads only `H_d(t')` for `t' > t` — already exact. (`T·(W−1)` small searches; the trivial seed `H_d(t) = y_t[d]` is never read.)
6. **Forward phase**: best-first search from the empty prefix with `B`, priority = bound, children = `u·d` for `d = 1..W−1`, each child's `Ab/An` in O(T) from the parent's, its bound in O(W·T).
7. Track the two best distinct labellings generated; push a child only if its bound exceeds the current second-best; stop when the top of the heap does not.
8. Return `mode = b1`-holder, `runner_up = b2`-holder, `margin = b1/b2`.
9. Correctness given termination: every popped-or-pruned subtree carries an admissible bound, so no labelling with probability `> b2` can remain unexpanded (step 4). Termination: the prefix tree is finite and every subtree of zero mass has bound 0.
10. Each `H_c(t)` is itself the value of an admissible search over a smaller problem, so by backward induction the whole `H` table is exact (gate (c): equality with brute force in exact rationals).

Graves' prefix search is the special case `Ĥ_d(t) = y_t[d]` *summed* over `d`; the certified-exact-decoder report showed that
using the exact `H` instead turns the final search from `≈ c/p*` expansions into `≈ D` on peaky
tables.

## Complexity — proven vs empirical

**Proven.**
- *Admissible and exact on termination* (above). Exactness does not depend on the table family.
- *Upper bound* (the adversarial-decoder-check report §4, adapted to the runner-up-certifying search; test (h)): an expanded node has `B(u) ≥ p₂` (an ancestor of the runner-up is in the heap until it is generated; afterwards the threshold is `p₂`), and `B(u) ≤ n_u · max_v p(u·v)` with `n_u ≤ T` (each frame term `ok_d(t−1)·H_d(t) ≤ p(u·v_t)` for that frame's arg-max suffix). Hence **`expansions_final ≤ |{u : max_v p(u·v) ≥ p₂/T}|`**, the number of prefixes of labellings within a factor `T` of the runner-up; the same holds for each backward search with its own mode. Total arithmetic `≤ (W−1) · Σ_searches (that count) · O(W·T)`.
- *Lower bound / worst case* (the adversarial-decoder-check report §2, test (g)): on flat rows (`y_t = 1/W` for every `t`) `p(l) = W^{−T}·N(l)` depends only on the equal-adjacent pattern of `l`, so the `(W−1)(W−2)^{D−1}` repeat-free relabellings of the mode are exactly tied, and every *proper* prefix of a tied labelling has `B(u) > p*` strictly (the `Σ_t max_v` split adds best suffixes of different lengths). Best-first must expand all of them: **`expansions_final ≥ (W−1)(W−2)^{D−2}` with `D ≈ 0.45·T`, i.e. `(W−2)^{Ω(T)}`**, and the same blow-up occurs in the backward searches. Perturbing the rows by `±10⁻³` leaves the counts unchanged (near-ties suffice), so the family is open, not measure-zero. The decoder is therefore exponential in the worst case, in the same class as Graves' `c/p*` (`≈ (1/p*)^{0.8}` on flat rows, Graves `1.5–4×` more nodes on the same instances).

**Empirical** (the certified-exact-decoder report §(c), the adversarial-decoder-check report §2; reproduced by `python -m certctc bench`, see `RESULTS.md`).
- On the peaky generator at confidence `≥ 0.7` and on real wav2vec2 posteriors: `generations_total ≈ 0.1·T²·W²` (the certified-exact-decoder report: 0.07–0.14 on 11 hard cells; real tables: median 0.09, one outlier 0.51), final search `≈ D` expansions (1.0–1.25·D), independent of `p*` down to `p* = 10⁻⁴¹`. Each generation costs **O(W·T)** (a length-T dot product per next symbol — the adversarial-decoder-check report's correction of the certified-exact-decoder report's "O(T)"), so ≈ `0.1·T³·W³` arithmetic.
- The cost interpolates with confidence (the adversarial-decoder-check report fits, `gen ∝ (1/p*)^α`, `gen ∝ T^β`):

  | family (W=5) | α | β | max expF/D |
  |---|--:|--:|--:|
  | peaky conf 0.8 | 0.08 | 2.5 | 1.25 |
  | peaky conf 0.6 | 0.17 | 3.2 | 128 |
  | peaky conf 0.5 | 0.31 | 4.6 | 621 |
  | uniform-random rows | 0.24 | 3.5 | 15 |
  | near-tie, 3-frame spread (W=3) | 0.50 | 3.7 | 123 |
  | flat | 0.82 | 7.3 | 11810 (= 3^{T/2}) |

  The reason (the adversarial-decoder-check report): with per-symbol confidence `c` a one-symbol-different labelling is ≈ `(1−c)/((W−1)c)` times less likely than the mode, so the number of labellings within a factor `T` of the mode is ≈ `Σ_{j ≤ log T / log(1/r)} C(D,j)(W−1)^j` — quasi-polynomial at fixed confidence, unbounded as `r → 1`. **No argument bounds the backward-search cost by a polynomial on peaky tables**; the "`0.1·T²·W²`" law is a measurement on that family, not a theorem.

## Real posteriors — 70 tables, regenerated with this package

The 70 tables of the certified-exact-decoder report §(f) (LibriSpeech clean/10/5/0 dB via wav2vec2-base-960h, 7 each; UWB-ATCC
air-traffic radio, AMI far-field, TORGO dysarthric/control, 42 tables; `W = 32`, blank `= 0`,
`T = 112–412`) were still on disk (the LibriSpeech `.npz` archives and the adjacent-domain `.npy` tables; not redistributed) and were **re-decoded with `certctc` (C backend)** by
`python -m certctc real`; the greedy column is recomputed here and the beam-k columns are taken
from the certified-exact-decoder report's `real_*.jsonl` (toolkit `topk_labellings`, unchanged). The full per-table table, the
per-domain summary and the cross-check gate against the certified-exact-decoder report's rows are in **`RESULTS.md`**.
Headline: all 70 certified, `verify()` passes on all, and every certified `p*`, `p₂`, mode,
generation count and final expansion count is identical to the certified-exact-decoder report's run (the algorithm is
deterministic).

## How to run

Everything below uses a Python 3 environment; the package needs only
the standard library and numpy (numpy only for `.npy` I/O and the C backend's buffer). Run from the
directory containing `certctc/` (or put it on `PYTHONPATH`).

```
# decode one table (.npy, .npz --key K, .json, or whitespace text); prints the certificate and verify()
python -m certctc decode table.npy --blank 0 --json cert.json [--backend auto|c|python] [--time-limit S] [--gen-cap N]

# synthetic scaling table: peaky conf {0.5,0.6,0.8,0.9} + flat, W {5,32}, T {16,32,64,128}
python -m certctc bench [--gen-cap 5000000] [--time-limit 60] [--out bench.jsonl]

# the real tables (paths given with --t4/--t7; the posterior tables are not redistributed), then the markdown table + cross-check against ../code/certified-exact-decoder/real_*.jsonl
python -m certctc real --shard 0 --nshards 4 --out certctc/real_rows_0.jsonl
python -m certctc assemble --rows 'certctc/real_rows_*.jsonl'

# the gates (print the GATE lines with -s)
python -m pytest certctc/tests -s -q
```

The C core (`_core/certctc.c`) is compiled on first use with `cc -O2 -ffp-contract=off -shared -fPIC`
into `_core/build/`; if that fails the pure-Python mirror (`_pysearch.py`) is used. The two are
gated bit-identical (probabilities, `H`, labellings, node counts) — the Python mirror performs every
floating-point operation in the same order and uses the same binary-heap algorithm, so tie-breaking
is identical too. Budgets (`time_limit`, `max_generations`) raise `BudgetExceeded`; a `Certificate`
is only ever returned for a completed search.

Relation to the two decoder reports' code: the search logic is `../code/certified-exact-decoder/exactbwd.c` (= `../code/certified-exact-decoder/bounds.py::decode_exact_backward`
plus the runner-up certification of `../code/certified-exact-decoder/real.py`) with two memory-only changes (node arrays are
freed once a node can no longer be expanded; the node pool grows on demand). Test (i) checks `H`,
`p*` and the mode bit-identical against `../code/certified-exact-decoder/bounds.py` and `../code/adversarial-decoder-check/t9core.py`, and the backward
expansion counts against the adversarial-decoder-check report (20/20 identical). Nothing in `../code/certified-exact-decoder/`, `../code/adversarial-decoder-check/` or the toolkit was modified.

## Tests (`certctc/tests/test_gates.py`)

| gate | what | source |
|---|---|---|
| (a) | argmax **and** `p_mode` vs brute force: 300 random T≤8 W≤3, 100 peaky conf 0.5–0.9, 100 at W∈{5,8}; both backends | the certified-exact-decoder report `gate.py`/`gate_w.py` + the adversarial-decoder-check report (c1–c3); the adversarial-decoder-check report noted the certified-exact-decoder report skipped the `p*` check when the label matched |
| (b) | runner-up **and** `p_runner_up` vs brute force (second largest with multiplicity; exact ties counted) on the same sets | the certified-exact-decoder report `gate_c.py` (C port only) — now on both backends |
| (c) | `H_c(t)` == brute-force `max_v g_v(t)` and `B(u) ≥ max_v p(u·v)` in exact `Fraction`s, conf ∈ {0.5, 0.6, 0.8} + random, W ≤ 5 | the adversarial-decoder-check report (b); the certified-exact-decoder report's gate covered only conf ≥ 0.8, W ≤ 3 |
| (d) | decomposition identity on 300 `Fraction` triples | the adversarial-decoder-check report (a) |
| (e) | C backend bit-identical to Python backend on 100 tables (T ≤ 12, W ≤ 8) | the certified-exact-decoder report `gate_c.py` |
| (f) | `verify()` on every certificate produced (1000+), on T=64/W=32, JSON round trip, and 4 mutations rejected | new |
| (g) | flat rows W=5, T ∈ {8,10,12,14}: final expansions exactly 53/161/485/1457 (the adversarial-decoder-check report `grow_flat5.log`), growth ×3 = W−2 per 2 frames, `margin == 1`; W=4 growth ×2 | the adversarial-decoder-check report §2 — asserted, not footnoted |
| (h) | `expansions_final ≤ |prefixes of labellings with p ≥ p₂/T|` on 48 brute-forced instances | the adversarial-decoder-check report `t9theory.py` |
| (i) | vs `../code/certified-exact-decoder/bounds.py` and `../code/adversarial-decoder-check/t9core.py` (read-only) | the certified-exact-decoder report `gate_c.py`, the adversarial-decoder-check report `diff.log` |
| (j) | `blank ≠ 0`, budgets raise | new |

## Credits

- A. Graves, S. Fernández, F. Gomez, J. Schmidhuber, *Connectionist Temporal Classification*, ICML 2006 — the CTC model, the forward recursion used by `verify()`, and prefix search (the bound family's `Σ_d y_t[d]` special case).
- the certified-exact-decoder report thread (`../reports/certified-exact-decoder.md`, `../code/certified-exact-decoder/`): the decomposition, the exact-backward bound (variant 1c), the C port and the runner-up certification, the 70-table real-audio run.
- the adversarial-decoder-check report thread (`../reports/adversarial-decoder-check.md`, `../code/adversarial-decoder-check/`): the independent re-implementation, the flat-row worst case and its exact-arithmetic proof, the prefix-count upper bound, the O(W·T)-per-node correction, and the audit of the certified-exact-decoder report's gates that this package's tests close.
- Validation toolkit (`ctc.py`, also at `../code/certified-exact-decoder/ctc.py`, copied verbatim as `_toolkit_ctc.py`): `brute_ctc`, `collapse`, `peaky_table`, `topk_labellings`, used by the tests and the bench.

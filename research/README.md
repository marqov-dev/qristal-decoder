# Exact CTC decoding: an independent analysis of the Qristal Decoder, a minimal correct quantum decoder, and a certified-exact classical one

*Technical note, September 2026. Reports, code and the `certctc` package are in this directory: see the
[reports index](reports/README.md), [`certctc/README.md`](certctc/README.md) and
[`LICENSE-NOTICE.md`](LICENSE-NOTICE.md).*

## 1. What this fork contains and why

`marqov-dev/qristal-decoder` is a fork of Quantum Brilliance's `qbrilliance/qristal-decoder`, the
"quantum decoder" of their Qristal SDK, public under Apache-2.0 since 2022. The Decoder takes a
table of per-timestep symbol probabilities — the output of a CTC-trained acoustic model — and
searches for the most probable *labelling*: the string left after collapsing repeats and removing
blanks, whose probability is the sum over every path that collapses to it (Graves et al., ICML
2006). Three merged pull requests (#1–#3) add input and register validation, a caller-visible
result contract and a comparator bit-order fix; they change nothing algorithmic.

We then asked a different question: what does the full Decoder compute, is there a quantum
advantage anywhere in exact CTC decoding, and what is the honest classical baseline? Two things
belong at the front. Quantum Brilliance shipped this code publicly, four years ago, without
claiming a speedup — their README presents the simplified decoder as a demonstration and the full
decoder as complicated and slow to test. And their central idea is right and, as far as we can
find, unpublished elsewhere: a *coherent collapsing map* that turns a path register into a
labelling register reversibly (`src/decoder_kernel.cpp:168–280`), so that the Born rule performs
the preimage sum. We verified it as a bijection on hundreds of tables and use it, unchanged, in §3.

## 2. What the Decoder computes, and the located issues

Line numbers refer to this fork's `main`.

1. **State preparation enumerates the strings classically.** In Qristal core the
   `SuperpositionAdder` that prepares the beam-metric register loops over every string
   configuration and emits, for each, a comparison oracle, a full `MeanValueFinder` and its
   inverse (core `src/superposition_adder.cpp`; core is a separate repository, and its line
   numbers are not re-verified here). The prepared circuit is Ω(W^T) in size before any Grover
   iteration — asymptotically larger than classical enumeration of the same strings. This is what
   the circuit builder emits, not a simulator artefact.
2. **The implemented arithmetic is not p(l|y).** Per-letter metrics are combined by a
   `RippleCarryAdder` (`src/quantum_decoder.cpp:338–364`), so a path's value is a *sum* of
   per-frame probabilities. The log₂ conversion that would turn addition into multiplication is
   commented out (`src/quantum_decoder.cpp:211–221`), the `Exponent` block that would invert it is
   commented out (`src/decoder_kernel.cpp:157–165`), and if enabled it would read a misspelled
   option key, `"total_metric_exponenet"` (`src/decoder_kernel.cpp:127`). The beam aggregation in
   core divides by the class size (`ProperFractionDivision`, `mean_value_finder.cpp`) although the
   register is sized for a sum over W^T strings (`src/quantum_decoder.cpp:191`) and the README
   says "adds them" (`README.md:12`); and the amplitude-estimation read-out squares each per-bit
   estimate before weighting (`ae_to_metric.cpp`). The emitted integer is a mean of squared
   bit-marginals of a sum of probabilities: a different objective, not an approximation of
   p(l|y). PR #2's result contract records this (result kind `quantized-search-observation`).
3. **A ceiling near 28 bits of string.** The signed-integer score implementation limits register
   widths to 30 bits (`include/qristal/decoder/register_validation.hpp:15`, PR #2), so m_b ≤ 30
   and, with m_b ≈ m_s + L·log₂W, L·log₂W ≲ 28 — independent of simulator speed.

None of this is unusual for a research prototype; it only means correctness and advantage must be
assessed on a *correct* construction, which is what we built.

## 3. The minimal correct quantum decoder

Keep the two components the Decoder already has and replace everything else
([`reports/quantum-argmax-construction.md`](reports/quantum-argmax-construction.md)):

- **Product Born state.** U_prod = ⊗_t R_t with R_t|0⟩ = Σ_s √y[t][s]|s⟩. The CTC path measure
  is a product measure, so U_prod|0⟩ = Σ_π √p(π|y)|π⟩ exactly, one W-dimensional rotation per frame.
- **Coherent collapse.** Quantum Brilliance's B: |π⟩|0⟩ ↦ |π⟩|B(π)⟩. The label register is then
  Σ_l √p_l |l⟩⊗|φ_l⟩ and measuring it returns l with probability p(l|y). Gate: worst
  |marginal − p(l|y)| = 8.9×10⁻¹⁶ over 248,232 labellings.
- **Exact comparator.** The forward recursion (Graves §4.1) run reversibly on |l⟩ into a b-bit
  fixed-point register, compared with a classical threshold θ, then uncomputed.
- **Generalized minimum-finding.** Threshold raising by capped amplitude-amplification search:
  Theorem 49 of van Apeldoorn, Gilyén, Gribling and de Wolf (arXiv:1705.01843, App. C), whose
  proof we reproduced and simulated ([`reports/citation-check.md`](reports/citation-check.md)).
  New here: the CTC instantiation; a *self-certifying* cap — the marked mass is ≥ θ whenever
  non-empty, so each round is capped at ⌈2/√θ⌉ with no prior bound on p* and the loop ends on an
  explicit emptiness test; and E[rounds] ≤ 1 + ln(1/p*).

Verified end to end: 272/272 tables return a labelling with p = p*; expected search cost ≤ 9/√p*
(worst measured 1.756 against the bound 2 in normalised units), certification ≈ 12/√p*, ≈ 21/√p*
Grover iterations in all; failure probability 3.5×10⁻³.

**Cost in equal units** (one b-bit multiply-add = one Toffoli; generous to quantum). The margin
m = p*/p₂ forces the register width b ≥ log₂(2TS/(p*(1−1/m))): 57 bits at 5 dB, 79 at 0 dB.
Against Graves' prefix search at c/p* expansions:

| point | T, D | b | Toffolis | speedup | logical qubits |
|---|---|---|---|---|---|
| 10 dB, p* = 1.2e-2 | 300, 40 | 25 | 2.5e10 | 1.6e-4× | 7.3e4 |
| 5 dB, p* = 5e-12 | 300, 40 | 57 | 5.3e15 | **1.9×** (1.2–4×) | 1.7e5 |
| 0 dB, p* = 6e-18 | 300, 40 | 79 | 8.9e18 | ~940× | 2.3e5 |

The crossover is p* ≲ 2×10⁻¹¹ and the speedup grows only as √(p*_x/p*); at 1 MHz logical
Toffoli rate the 5 dB point is ~170 years of wall clock. §5 shows even this is too kind.

**Why no sample-only route escapes the margin.** Belovs (arXiv:1904.02192, Thm 4) bounds
distinguishing two distributions from a state-preparation oracle by Θ(1/d_H). A mode-finder must
distinguish p from p with its top two masses swapped, d_H² = p*(1−1/√m)², so any black-box user
of U needs Ω(1/(√p*(1−1/√m))) queries: 18× more than 1/√p* at m = 1.12, 101× at m = 1.02 (the
step from Belovs' statement to this claim is a hybrid argument on the specific state, T ≥ 1/(6√p*),
constant verified numerically). Only a white-box exact evaluator avoids paying the margin
multiplicatively, and then it reappears as register width, logarithmically. Coherent thresholding
without a rounding promise (Guo et al., arXiv:2606.06316) nested inside amplification costs O(1/p*).

## 4. The certified-exact classical decoder

[`certctc/`](certctc/README.md) solves the Decoder's target problem exactly, on a laptop, and
returns a certificate: mode, runner-up, both probabilities and their ratio
([`reports/certified-exact-decoder.md`](reports/certified-exact-decoder.md)).

*Algorithm in ten lines.* Frames 1..T, blank 0. For a prefix u let ok_d(t) be the mass of paths
over frames 1..t collapsing to u that can start a fresh symbol d at t+1; for a suffix v with first
symbol c let g_v(t) be the mass over frames t..T with π_t = c collapsing to v. (1) The segment
emitting the next symbol starts at a unique frame, so p(u·v) = Σ_t ok_{v₁}(t−1)·g_v(t) exactly.
(2) Suffix modes H_c(t) = max_{v₁=c} g_v(t). (3) Bound B(u) = max(p(u), max_d Σ_t ok_d(t−1)·H_d(t)).
(4) B is admissible: a sum of per-frame maxima dominates every single sum. (5) Compute every
H_c(t) exactly, for t = T..1, by the same best-first search rooted at "c forced at frame t", which
reads only later, already-exact H — T·(W−1) small searches. (6) One forward best-first search from
the empty prefix with B. (7) Keep the two best distinct labellings; push a child only if its bound
exceeds the second-best; stop when the top of the heap does not. (8) Return mode, runner-up, margin.
(9) On termination nothing above the runner-up is unexpanded. (10) Each H is the value of an
admissible search, so by backward induction the whole table is exact. Graves' prefix search is the
special case Ĥ_d(t) = y_t[d] summed over d.

*What it certifies.* `pruned_mass_bound` is identically zero — nothing is discarded without a
bound — and `verify()` recomputes both probabilities by an independent forward recursion and
rejects tampered certificates. Thirteen tests carry every gate: argmax and p_mode against brute
force (500 instances, both backends), runner-up against brute-force second-largest with explicit
ties, admissibility and the decomposition identity in exact rationals, C and Python bit-identical.

*Real audio.* All **70/70** real posterior tables (W = 32, T = 112–412: LibriSpeech at clean / 10 /
5 / 0 dB, air-traffic radio, far-field meetings, dysarthric speech) certify in 1–127 s, at
certified p* down to **6.2×10⁻²⁶**, where prefix search at c/p* expansions would need ~10¹⁸–10²⁶.
Certified margins on the hard domains are 1.001–1.1.

*Independent reproduction.* A second implementation, written from the description without
reading the code, agrees node-for-node on 20 shared instances and passes every gate
([`reports/adversarial-decoder-check.md`](reports/adversarial-decoder-check.md)). It found the
worst case: on flat rows the (W−1)(W−2)^{D−1} repeat-free relabellings of the mode tie exactly and
every proper prefix is strictly over-bounded, so the final search expands **(W−2)^{T/2}** nodes —
53 / 161 / 485 / 1457 at T = 8..14, W = 5, pinned as a test. The decoder is exponential in the
worst case, in Graves' class, with 1.5–4× fewer nodes.

*The theorem* ([`reports/cost-theorem.md`](reports/cost-theorem.md)). With P_g = ∏_t max_s y_t[s]
the greedy path's mass and Λ = −ln P_g its log-loss, total node generations are at most
(W−1)·[T(T+1) + (W−1)(T³/3 + T²/2)]/P_g = **O(W²T³·e^Λ)**, each O(W·T) arithmetic; the final
search alone expands ≤ T(T+1)/p*. With k arbitrary frames and the rest at max ≥ 1−ε the bound is
O(W²T³)·W^k·e^{εT/(1−ε)}: decoding is fixed-parameter tractable in strictly ambiguous frames
(≤ W^k(T+1) expansions per search when the others are point masses), without the decoder knowing
k. Both parameters are necessary, and no bound in the per-frame confidence ρ exists: rows
[ρ, q, …, q] have no ambiguous frame at any threshold and exponential cost. On peaky and real
posteriors the measured cost is ≈ 0.1·T²·W² generations (median 0.094 on the 70 tables, one
outlier at 0.51) — a measurement, not a theorem.

## 5. Quantum versus classical, per real utterance

Costing §3 against `certctc`'s measured generations on the 56 non-degenerate real tables, same
units and same model ([`reports/quantum-vs-classical-baseline.md`](reports/quantum-vs-classical-baseline.md)):
the classical cost is 10¹⁰–3.5×10¹¹ multiply-adds on every row and essentially independent of p*,
so the picture inverts. The quantum route is cheaper only at p* ≥ 2.6×10⁻³ (18/56 rows, up to 115×
on clean speech) — rows where greedy already returns the certified mode on 15/18 and beam-5 on
17/18, and where a single 10⁵-operation forward pass certifies the mode whenever p* > ½, at
10⁴–10⁶× less than the quantum circuit. On the **38 rows with p* ≤ 1.5×10⁻³**, holding 25 of the
26 beam-5 misses — every row where an exact decoder is wanted — **quantum loses by 1.1× to
5×10¹¹×**. Median ratio by domain: clean 83, 10 dB 3.2, 5 dB 1.4×10⁻⁴, 0 dB 1.2×10⁻⁷, UWB-ATCC
5×10⁻⁶, AMI 7×10⁻³, TORGO 10⁻². In wall clock the quantum route beats the measured classical
seconds on **0/56 rows at 1 MHz** and 15/56 at 1 GHz, all at high p*. No operating point on real
audio survives.

## 6. What the real-data measurements showed

With a generic model (`wav2vec2-base-960h`) on air-traffic radio, far-field meetings and
dysarthric speech, the low-confidence regime is the default with no noise added: frame confidence
0.86 / 0.89 / 0.94, converged p* medians 7.5×10⁻¹³ / 6.7×10⁻⁷ / 1.6×10⁻⁷, margins ≈ 1.04–1.09
([`reports/adjacent-domains.md`](reports/adjacent-domains.md)). Against the certified mode,
greedy misses on 43/70 tables, beam-5 on 34/70, beam-50 on 26/70 and **beam-800 on 6/70**; every
miss is a near-tie in which the beam returns the certified runner-up.

The field's in-domain checkpoint on the same eight air-traffic clips removes the regime
([`reports/atc-in-domain.md`](reports/atc-in-domain.md)): confidence 0.857 → 0.976, p* median
10⁻¹² → 0.45, greedy = mode 0/8 → 7/8, WER of the mode 1.02 → 0.13. On cross-corpus ATCO2 clips
half still pass the gate, but beam-50 recovers the certified mode 8/8. On 24/24 certified decodes
the runner-up is a **one-character edit** of the mode: the margin certifies spelling entropy, not
an alternative reading. The exact decoder's role on real audio is therefore *validation* — it
proved beam-50 exact on 16/16 in-domain tables and beam-5 not — rather than transcription. A
minimum-Bayes-risk reframing of the quantum machinery is unconditional in query count (Õ(σ/ε)
versus Θ(σ²/ε²)) but decision-irrelevant: on real 5 dB posteriors the MBR winner leads by a median
1.6×10⁻⁴ in normalised utility and MBR and MAP have identical CER
([`reports/quantum-mbr-reframing.md`](reports/quantum-mbr-reframing.md)).

### 6b. Follow-ups: the margin theorem, the word-class posterior, hard audio

*Margin* ([`reports/margin-lemma.md`](reports/margin-lemma.md)): if the top-2 margin p*/p₂ exceeds
K, the number of distinct suffix-mode strings per symbol returned by the backward pass (K ≤ T, known
before the final search; K = D+1 on real tables), the final search expands exactly D or D+1 nodes —
sharpening §4's "margin > T" and firing on 4 of the 70 real tables. Conjecture C0, that the
per-node over-approximation ratio is bounded by a constant c₀ ≈ 3–4 so that margin > c₀ suffices,
is open: in ≈ 2,300 tables none with margin ≥ 2.1 has an off-path expansion and the measured ratio
never exceeds 3.4. *Word classes* ([`reports/word-class-certificate.md`](reports/word-class-certificate.md)):
the object §6 pointed to is computable exactly — for a regular class L (a callsign, a flight
level) P(L|y) = Σ_{l∈L} p(l|y) is one forward recursion over the product of the CTC collapse and a
DFA, 0.06–0.18 s per slot, where a beam-50 class sum is a lower bound loose by up to 0.94. It
certifies the reference class at ≥ 0.9 on 21/33 air-traffic slots, and on the two safety-relevant
misreads it correctly reports the true class at near-zero mass (3.4×10⁻⁹ and 1.4×10⁻⁷): the model
is wrong and the certificate says so, as a refusal rather than a rescue. *Hard audio*
([`reports/hard-atc-audio.md`](reports/hard-atc-audio.md)): on 24 real ATCO2-test clips at an
estimated 4–14 dB the in-domain model's beam-50 returns the certified mode on only 14/24 (16/16 at
≥ 15 dB), yet the exact mode is not a better transcript — its WER ties greedy on 18/24 and beam-50
on 22/24, and the reference is never in the certified top-2. The runner-up stays a one-character
edit of the mode (51/56 here, the other five a two-symbol spelling variant): 80/80 certified
decodes in which the margin is a spelling margin.

## 7. The open complexity question

Whether exact CTC decoding is NP-hard or polynomial is, as far as we can establish, open — and
so is its simplest sub-case. With forced blanks between symbols, p(l|y) is the probability that T
independent slots, each emitting a symbol or deleting, output l. For a deterministic source x and
deletion probability ½, p(l) = 2^{−T}·emb(l, x), the number of embeddings of l as a subsequence
of x, so the mode is the **most frequent subsequence of a word** — stated open in print by Fang
(AofA 2024, arXiv:2406.02971, Remark 4.2: "we don't know whether there is a polynomial time
algorithm to compute a most frequent subword of a given word"). Every published hardness proof for
most-probable-string (Casacuberta–de la Higuera 2000, Goodman 1998 §3.6.1, Lyngsø–Pedersen 2001)
builds a *mixture* of position-indexed chains with a satisfied/unsatisfied memory bit; a product
measure has neither, and the gadgets do not transplant
([`reports/hardness-literature.md`](reports/hardness-literature.md)).

Our attempt ([`reports/hardness-attempt.md`](reports/hardness-attempt.md)) proved three lemmas any
proof must respect: **separator forcing** (with block separators every honest word's count
factorises, so a hard gadget's mode must straddle blocks); the **interface identity**
emb(l, B₁…B_k) = Σ over monotone cut vectors of ∏ emb(piece_i, B_i), so adjacent blocks interact
only through one integer; and a **repetition bound** M(x) ≤ C(n+k−1, k−1)·honest(x), with the
straddling gain measured to saturate (r ≤ 1.55 over seven boundaries). It refuted, with
machine-checked counterexamples, the LCS permutation-block gadget, length-unimodality
(x = bababbaababa: 67, 57, 71 at lengths 4, 5, 6) and greedy insertion as exact
(x = abbbaaabbbbbaabb: 365 vs 360), and showed the problem is FPT in the number of non-degenerate
slots, O((|Σ|+1)^k·T²). No theorem either way; the question stays the prize.

## 8. How to reproduce

```
cd research
python -m pytest certctc/tests -s -q        # 13 tests, every gate printed; ~10 s
python -m certctc bench --out bench.jsonl   # synthetic scaling incl. the flat-row worst case
python -m certctc decode table.npy --blank 0 --json cert.json
```

`certctc` needs Python 3 and numpy; the C core is compiled on first use with `cc`, with a
bit-identical pure-Python fallback. Every number in the reports traces to a script and a log under
`code/`. The posterior tables and audio are not redistributed; `certctc/RESULTS.md` lists all 70
certified rows.

## 9. Licensing and credits

Upstream code © Quantum Brilliance Pty Ltd, Apache-2.0. Additions in this directory © Marqov,
Apache-2.0. Datasets and models are listed in [`LICENSE-NOTICE.md`](LICENSE-NOTICE.md); nothing
from them is redistributed. Credit where due: the coherent collapsing map is Quantum Brilliance's;
the CTC model, forward recursion and prefix search are Graves et al.'s; the minimum-finding
primitive is van Apeldoorn, Gilyén, Gribling and de Wolf's; the lower-bound technique is Belovs'.

## 10. Corrections to our own claims

Part of the result is what we got wrong on the way; it is recorded, not removed. (i) Our earlier
speedup figures — ~8×10⁴× at 5 dB and ~10⁸× at 0 dB — compared quantum oracle calls with
classical node expansions; in equal units they are 1.9× and ~940× against prefix search, and
1.4×10⁻⁴ and 1.2×10⁻⁷ against the certified-exact decoder. (ii) The first decoder report called
its cost "independent of p*"; that is a property of the peaky test generator, not the algorithm —
flat rows cost (W−2)^{T/2}. (iii) A literature review put the per-oracle cost at Õ(T·(W+D)) and
the advantage gate at p* < (c/(W+D))²; it omitted the b² multiplier term and the multiplicative
symbol fetch and was wrong by ~10⁷. (iv) The same decoder report costed one node at O(T); it is
O(W·T). (v) "The low-confidence regime is the default on air-traffic radio" held only for a
generic model. (vi) A cited universal tree-search speedup (Chakrabarti et al., arXiv:2210.03210,
Thm 1.5) rests on attributions that do not match its sources; the citable statement is
Apers–Gilyén–Jeffery's Õ(√(Tn)). Each correction came from a gate or an adversarial
re-derivation, which is the method this work recommends.

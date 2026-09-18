# Certified posterior mass of a word class under a CTC posterior: the object for an ATC readback safety argument

Date: 2026-09-18. One research-engineering experiment. Code and logs under `../code/word-class-certificate/` (`fsa.py`, `classctc.py`, `atc_classes.py`, `gate.py` → `gate.log`, `measure.py` → `measure_a4.log` / `measure_generic.log` / `results__{a4,generic}.json`, `breakdown.log`, `gate_generic_mode.log`, `tables.py` → `tables.md`). No other directory was modified; the toolkit `ctc.py` was copied verbatim from `certctc/_toolkit_ctc.py`.

## Headline

**Class-level mass does *not* rescue the information the top-k loses on the two safety-relevant errors — and that is the right answer.** For the two atc-in-domain misreads the exact posterior mass of the *correct semantic class* is:

| clip | reference slot | certified mode | **P(correct class \| y)** exact | P(competing class) | P(residual: slot unparseable) | what the mass went to |
|---|---|---|---|---|---|---|
| ATCO2 `151125-G` | flight level **100** ("one hundred") | "flight level one on eight" | **3.4 × 10⁻⁹** | **0.954** | 0.046 | FL **1** 0.871, FL 11 0.076, FL 118 0.006, FL 18 5e-4 |
| ATCO2 `145941-G` | callsign **OK-HHH** ("oscar kilo triple hotel") | "oscar kilo kio hotel" | **1.4 × 10⁻⁷** | 0.006 (OK-KH 0.004) | **0.994** | "oscar kilo" 0.79 and "hotel" 0.80 each present, but no valid registration between them |

The atc-in-domain point estimate p(ref)/p\* ≈ 2.6e-7 / 7.1e-9 was therefore not an artefact of comparing one spelling against one spelling: summing over *every* labelling that reads as "FL100" (12 ICAO spellings × all delimiter placements) or as "OK-HHH" (4 tokenisations incl. "hotel hotel hotel", "double hotel hotel") leaves the truth at 10⁻⁷–10⁻⁹. The acoustic model is wrong, and the class certificate says so exactly: a verifier built on it would output *"P(readback level = FL100) < 10⁻⁸; readback reads FL 1 with certified probability 0.87"* — a certifiable **refusal / alarm**, which is what a safety argument needs from the machine on these two clips.

**Where class mass *does* change the picture is spelling entropy, which is exactly what the top-two margin measured.** On 9/33 in-domain slots the exact class mass exceeds the beam-50 class sum by more than 0.1 absolute (max 0.94): callsign AUSTRIAN 706P is **0.985 exact vs 0.330 beam-50 vs 0.565 beam-800** (p\* = 0.073); waypoint TB402 is **0.948 vs 0.004 vs 0.019** (p\* = 2e-4, margin 1.04 — the clip the argmax certificate called "maximally ambiguous"); SKY-TRAVEL 1102 is 0.927 vs 0.119 vs 0.364; SID "one hotel departure" is 0.972 vs 0.181 vs 0.448. A beam-rescored class sum is a *lower bound* that is loose by up to 0.94 and, for the risk side, underestimates the competing-class mass of the FL error by 7× (0.130 beam-50 vs 0.954 exact). The exact sum needs no argmax, no pruning, and costs 0.06–0.18 s per slot (three DFAs of ≤ 380 states, T ≤ 324, W = 31, numpy).

**Overall on the in-domain model:** 21/33 slots certify the reference class at ≥ 0.9; 12/33 do not, and every one of those 12 is either a genuine model misread (7: FL100, OK-HHH, stand 22A at 1.6e-20, OK-ELA at 8.6e-5, EUROWINGS 1TK twice at 0.02/0.016, "one hotel" after confirmation at 0.031) or a misspelt number/letter word inside the slot (wind 160 → "one six zro": P(160) = 0.040, P(16) = 0.906; OK-FAO → "foxtrot alf oscar": 0.33; CSA 71 → "seven onee": 0.65) — plus runway 27 at 0.87 and NOR-SHUTTLE 1515 at 0.85 where the residual is honest spelling mass outside the lexicon. **On the generic model** every one of the 18 slots has P(correct) ≤ 3.4e-3 (median ~1e-12): the certificate refuses everything, which is correct — the generic model cannot read ATC.

## 1. Formalisation

Frames t = 1..T, posterior rows y_t over W symbols with blank ∅; Σ = the W−1 non-blank symbols, including the word delimiter `|`. For a labelling l ∈ Σ\*, p(l | y) = Σ_{π : B(π) = l} Π_t y_t[π_t] (Graves et al. 2006, eq. 3). For a regular L ⊆ Σ\* given by a DFA (Q, q₀, δ, F) over Σ (missing transitions = dead),

  P(L | y) := Σ_{l ∈ L} p(l | y) = Σ_{π ∈ (∅∪Σ)^T : B(π) ∈ L} Π_t y_t[π_t].

**Product recursion.** The collapse B is a transducer whose state is the *symbol of the previous frame* (not the last emitted label): frame t emits a new label c iff π_t = c ≠ ∅ and π_{t−1} ≠ c. Track α_t(q, s) = mass of paths over frames 1..t with π_t = s and δ\*(q₀, B(π_{1..t})) = q:

```
α₁(q₀, ∅)        = y₁[∅]
α₁(δ(q₀,c), c)   = y₁[c]                                            c ≠ ∅
α_{t+1}(q, ∅)    = y_{t+1}[∅] · m_t(q)                              m_t(q) := Σ_s α_t(q, s)
α_{t+1}(q, c)    = y_{t+1}[c] · ( α_t(q, c)                          repeat of c: no emission, DFA stays
                              + Σ_{q' : δ(q',c) = q} ( m_t(q') − α_t(q', c) ) )   new emission of c after ∅ or after a different symbol
P(L | y)         = Σ_{q ∈ F} m_T(q)
```

Paths that hit the dead state are dropped. Cost **O(T · |Q| · W)** time, O(|Q| · W) memory (the inner sum is the per-state total m_t(q') minus one entry; the numpy version does the "new emission" scatter with one `bincount` per symbol per frame). Two places where naive versions go wrong, both hit by the gates: (i) tracking only the DFA state and treating every non-blank frame as an emission double-counts repeats ("aa" is one label, "a∅a" two); (ii) tracking only "last emitted label" without the blank loses the ∅-between-repeats case — the state must be the previous *frame* symbol, W values.

**Word classes.** A labelling's *text* is its `|`-split with empty words dropped. A word-level pattern is compiled on the boundary-extended string `| l |`: every word token is `|⁺ w`, the pattern gets a trailing `|⁺`, and the DFA on plain labellings takes start = δ(q₀, `|`) and accept = {q : δ(q, `|`) ∈ F}. Then leading/trailing/repeated delimiters are all accepted (same text) and patterns compose as ordinary regexes (Thompson NFA → subset construction → Moore minimisation; products for ∩, ∪, −, complement). Slot targeting: `anywhere(anchor · C)` minus `anywhere(anchor · C · NUMWORD)` says "the maximal number-word run after the anchor is in C". Number semantics: VALUE(v) = every ≤ 4-token ICAO number-word sequence (zero…nine, niner, hundred, thousand) whose digit-run/multiplier parse equals v ("one hundred" = "one zero zero" = 100, 12 spellings); NUMLIKE = DIGIT(DIGIT|hundred|thousand)^{≤3}, a conservative superset. Callsign suffix identity: every tokenisation of the alphanumeric string into digit words / NATO letters (alfa|alpha, juliett|juliet, xray) / "double X" / "triple X". Three DFAs per slot: correct, competing = NUMLIKE-slot − correct, residual = complement of both; they partition Σ\*, so the three masses sum to 1 (checked to 1e-12 on every slot).

## 2. Gate lines (`gate.log`, `measure_*.log`, `gate_generic_mode.log`; exact arithmetic where stated)

```
GATE (a) class_posterior vs brute force over all W^T paths (exact Fractions): 192 (table,DFA) instances, 237120 paths summed, 148 with nonzero mass, 0 mismatches -> PASS
GATE (b) class_posterior vs sum of ctc_forward over enumerated L (|l|<=T, exact Fractions): 192 instances, 57756 labellings summed, 148 with nonzero mass, 0 mismatches -> PASS
GATE (c) L=Sigma* gives exactly 1 and L={l} gives exactly ctc_forward(l) (+ toolkit float forward to 1e-12): 160 checks, 0 mismatches -> PASS  [0.5s]
GATE numpy / float implementations vs exact Fractions (T<=40, W<=8, |Q|<=30): 60 checks, worst rel err 1.00e-15 -> PASS
GATE word-pattern DFAs (+ intersect/union/difference/complement) vs Python re on rendered text: 44000 checks, 0 mismatches, sizes [5, 5, 6, 4, 6, 7] -> PASS
GATE generic tables: P({certified mode}) by class_posterior vs certctc certified p* (l1/p1 rows): 8 tables, worst rel err 2.42e-15 -> PASS
REAL-TABLE GATES PASS   (A4: 16/16 tables P(Σ*)=1 to 1e-14 and P({mode}) = ctc_forward(mode) = A4 p* to 1e-12 rel; 33/33 slots correct+competing+residual = 1 to 1e-12)
```

Gate (a)/(b) tables: T ≤ 7, W ∈ {2,3,4}, blank at column 0 or W−1 (the atc-in-domain layout), rows random or peaky, DFAs random (1–4 states, partial transitions) and hand-built word classes ("contains word", "2nd word is", "last word is", "only words from {w1,w2}"). Mismatch means non-identical `Fraction`s. Gate (c) also covers blank ≠ 0 against the toolkit's float `ctc_forward`. (The word-pattern gate failed on the first design — a mandatory separator between optional parts — and passed after the boundary-extended convention above; the failing version is not in the deliverable.)

## 3. ATC classes built (`atc_classes.py`)

(i) **Numbers**: `number_slot(anchor, v)` — anchors used: "flight level", "runway", "wind", "degrees", "ground"→frequency, utterance-initial. (ii) **Callsigns**: `callsign_slot(prefix, suffix)` with prefix an airline/registration literal (alternatives allowed, e.g. "euro wings" | "eurowings") and suffix an alphanumeric string ("37A", "1DZ", "HHH", "1515"); the same builder serves SIDs, stands ("22A"), taxiways ("AC") and waypoints ("TB 402"). (iii) **Frequencies**: `freq_slot("ground", "121.9")` = "one two one decimal nine|niner" with optional trailing zeros vs DIGIT^{1–3} decimal DIGIT^{1–3}. (iv) **Phrases**: `phrase_slot("cleared for takeoff", ["cleared for landing", "cleared to land", "line up", "hold short", "hold position"])`, likewise "line up", "descend" vs "climb"/"maintain", "taxi to holding point". Representation: hand-composed NFAs per class → minimal DFAs (regex string parsing was not needed). Sizes 10–380 states; build 0.05–1.0 s per slot (4 s for the prefix-free SID). Per-clip specs (`SPECS`) are the clearance a verifier would be handed; 33 slots over the 16 atc-in-domain clips, the same 18 UWB slots for the generic model.

## 4. Measurement — in-domain model (atc-in-domain posteriors), all 33 slots

Columns: exact P(correct | y), P(competing | y), P(residual), the conditional P(correct | slot parseable), the class sums over the beam-50 and beam-800 hypothesis lists (toolkit prefix beam, each hypothesis re-scored exactly by `ctc_forward`, membership by DFA), the gap, which class the certified mode falls in (C/K/Z), and the highest-probability competing hypothesis in the beam-800 list.

### In-domain model `Jzuluaga/...-uwb-atcc-and-atcosim` (atc-in-domain posteriors, 16 clips, 33 slots)

| clip | T | p* | slot | P(correct) exact | P(competing) exact | P(residual) | P(correct \| parseable) | beam-50 Σ correct | beam-800 Σ correct | exact − beam-50 | mode ∈ | top competing hypothesis (p) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 34720N_002001_002559_AT | 278 | 0.021 | SID "one hotel departure" | **0.972** | 0.013 | 0.016 | 0.987 | 0.181 | 0.448 | 0.791 | C | — |
| a1WcrN_000157_000469_AT | 155 | 0.824 | callsign NOR-SHUTTLE 1515 | **0.848** | 7.36e-03 | 0.144 | 0.991 | 0.837 | 0.845 | 0.011 | C | `nor shuttle one fiv one five line up runway three one` (4.0e-04) |
|  |  |  | runway 31 | **0.985** | 1.29e-03 | 0.013 | 0.999 | 0.956 | 0.976 | 0.030 | C | `nor shuttle one five one five line up runway three ne` (2.9e-04) |
|  |  |  | phrase "line up" | **0.993** | 7.52e-24 | 6.70e-03 | 1.000 | 0.959 | 0.983 | 0.034 | C | — |
| a3o8f0_000000_000352_AT | 175 | 0.378 | callsign OPERA-JET 300 | **0.961** | 5.04e-03 | 0.034 | 0.995 | 0.869 | 0.932 | 0.091 | C | `opera jet three zero zerojust for confirmation vo one hotel` (3.9e-04) |
|  |  |  | "one hotel" after confirmation | **0.031** | 2.51e-04 | 0.968 | 0.992 | 0.028 | 0.029 | 3.45e-03 | Z | `opera jet three zero zero just for confirmation one htel` (4.2e-05) |
| A5lZHJ_000000_000613_AT | 306 | 0.775 | callsign CSA 37A | **0.986** | 4.17e-03 | 9.99e-03 | 0.996 | 0.893 | 0.950 | 0.093 | C | `csa three seve alfa runway three one cleared for takeoff win` (1.5e-04) |
|  |  |  | runway 31 | **0.987** | 2.12e-03 | 0.011 | 0.998 | 0.893 | 0.949 | 0.094 | C | `csa three seven alfa runway three ne cleared for takeoff win` (3.8e-04) |
|  |  |  | phrase "cleared for takeoff" | **0.929** | 2.20e-22 | 0.071 | 1.000 | 0.859 | 0.902 | 0.070 | C | — |
|  |  |  | wind 160 | **0.040** | 0.949 | 0.010 | 0.041 | 0.035 | 0.038 | 5.35e-03 | K | `csa three seven alfa runway three one cleared for takeoff wi` (7.8e-01) |
|  |  |  | knots 5 (after degrees) | **0.979** | 7.89e-09 | 0.021 | 1.000 | 0.888 | 0.942 | 0.091 | C | — |
| A5lZHJ_002805_003388_PIAT | 291 | 0.073 | callsign AUSTRIAN 706P | **0.985** | 0.011 | 4.38e-03 | 0.989 | 0.330 | 0.565 | 0.655 | C | `ruzyne austrian seven zero six papa one lima austrian seven ` (5.8e-04) |
| a8R9jE_000144_000596_AT | 225 | 0.937 | callsign CSA 731 | **0.992** | 3.37e-03 | 4.44e-03 | 0.997 | 0.966 | 0.986 | 0.026 | C | `csa seven three onecontact ruzyne ground one two one decimal` (3.0e-04) |
|  |  |  | frequency 121.9 (after ground) | **0.966** | 2.19e-08 | 0.034 | 1.000 | 0.949 | 0.962 | 0.017 | C | — |
| a8R9jE_000700_001023_PIAT | 161 | 0.530 | callsign CSA 71 | **0.650** | 0.102 | 0.249 | 0.864 | 0.628 | 0.646 | 0.022 | C | `one nine csa seven onee` (1.8e-02) |
|  |  |  | leading number 19 | **0.923** | 0.016 | 0.061 | 0.983 | 0.832 | 0.897 | 0.091 | C | `one ninet csa seven one` (1.1e-03) |
| A64ueL_000128_000777_PI | 324 | 6.40e-03 | callsign SKY-TRAVEL 1102 | **0.927** | 0.056 | 0.017 | 0.943 | 0.119 | 0.364 | 0.808 | C | `ruzyne tower sky travel one one zero twostand die due to alf` (2.5e-04) |
|  |  |  | stand 22A (after standing) | **1.64e-20** | 6.84e-16 | 1.000 | 2.40e-05 | 0.00e+00 | 0.00e+00 | 1.64e-20 | Z | — |
| BRNO_Tower_119_605MHz_028_185619-A__000000-000536 | 267 | 0.232 | callsign OK-FAO | **0.326** | 0.519 | 0.154 | 0.386 | 0.272 | 0.299 | 0.055 | C | `oscar kilo foxtrot alf oscar taxi to holding point runway tw` (1.4e-01) |
|  |  |  | runway 27 | **0.872** | 2.84e-03 | 0.125 | 0.997 | 0.577 | 0.724 | 0.294 | C | — |
|  |  |  | phrase "taxi to holding point" | **0.938** | 2.74e-17 | 0.062 | 1.000 | 0.604 | 0.767 | 0.335 | C | — |
|  |  |  | taxiway A C (after via) | **0.923** | 0.010 | 0.067 | 0.989 | 0.589 | 0.748 | 0.334 | C | `oscar kilo foxtrot alfa oscar taxi to holding point runway t` (3.9e-04) |
| BRNO_Approach-Radar_127_350MHz_026_111634-A__000000-000395 | 197 | 1.96e-04 | callsign OK-ELA | **8.58e-05** | 5.18e-06 | 1.000 | 0.943 | 0.00e+00 | 0.00e+00 | 8.58e-05 | Z | — |
|  |  |  | waypoint TB402 | **0.948** | 6.49e-03 | 0.046 | 0.993 | 3.72e-03 | 0.019 | 0.944 | C | `kilo echo lima alfa com irm froceeding to tango bravo four z` (4.7e-08) |
| Radar_120_520MHz_028_151125-A__000000-000444 | 221 | 0.877 | callsign CSA 1DZ | **0.990** | 6.11e-03 | 4.09e-03 | 0.994 | 0.961 | 0.981 | 0.029 | C | `csa one delta zulo descend flight level one hundred no speed` (2.3e-04) |
|  |  |  | flight level 100 | **0.981** | 8.82e-03 | 0.010 | 0.991 | 0.956 | 0.972 | 0.025 | C | `csa one delta zulu descend flight level one hudred no speed ` (2.2e-03) |
|  |  |  | phrase "descend" | **0.982** | 1.85e-22 | 0.018 | 1.000 | 0.949 | 0.971 | 0.034 | C | — |
| Radar_120_520MHz_028_151125-G__000444-000934 | 244 | 8.79e-03 | flight level 100  [ERROR CASE: mode "one on eight"] | **3.41e-09** | 0.954 | 0.046 | 3.57e-09 | 0.00e+00 | 0.00e+00 | 3.41e-09 | K | `descending flight level one on eight free speed csa one delt` (8.8e-03) |
|  |  |  | callsign CSA 1DZ | **0.944** | 0.042 | 0.014 | 0.958 | 0.129 | 0.356 | 0.815 | C | `descending flight level one on eight free speed csa one delt` (5.2e-05) |
| Radar_120_520MHz_026_145941-G__000000-000349 | 174 | 1.35e-04 | callsign OK-HHH  [ERROR CASE: mode "kio hotel"] | **1.39e-07** | 5.84e-03 | 0.994 | 2.38e-05 | 0.00e+00 | 0.00e+00 | 1.39e-07 | Z | `oscar kilo kilo hotel please confirm one er holding` (5.9e-05) |
| Tower_134_560MHz_025_144043-B__000000-000332 | 165 | 8.09e-03 | callsign EUROWINGS 1TK | **0.020** | 2.17e-03 | 0.978 | 0.903 | 0.00e+00 | 0.012 | 0.020 | Z | `ruzyne tower hello an eurowings one tango klo` (3.8e-05) |
| Tower_134_560MHz_025_144043-A__000334-000742 | 203 | 0.047 | callsign EUROWINGS 1TK | **0.016** | 1.19e-03 | 0.983 | 0.929 | 0.015 | 0.015 | 8.94e-04 | Z | `eurowings one tango kil ruzyne tower good afternoon go ahead` (2.2e-04) |
| Tower_134_560MHz_025_144043-B__000744-001212 | 233 | 0.168 | runway 24 | **0.957** | 7.40e-03 | 0.036 | 0.992 | 0.614 | 0.777 | 0.343 | C | `just requested do you think there is a chance for us to get ` (2.3e-04) |

| clip | Σ p over beam-50 hypotheses | Σ p over beam-800 hypotheses | beam-50 s | beam-800 s |
|---|---|---|---|---|
| 34720N_002001_002559_AT | 0.1810 | 0.4480 | 0.2 | 4.0 |
| a1WcrN_000157_000469_AT | 0.9613 | 0.9872 | 0.1 | 1.9 |
| a3o8f0_000000_000352_AT | 0.8730 | 0.9534 | 0.1 | 2.3 |
| A5lZHJ_000000_000613_AT | 0.8946 | 0.9558 | 0.2 | 4.8 |
| A5lZHJ_002805_003388_PIAT | 0.3303 | 0.5661 | 0.2 | 4.5 |
| a8R9jE_000144_000596_AT | 0.9667 | 0.9913 | 0.1 | 3.2 |
| a8R9jE_000700_001023_PIAT | 0.8652 | 0.9578 | 0.1 | 1.7 |
| A64ueL_000128_000777_PI | 0.1191 | 0.3644 | 0.2 | 4.7 |
| BRNO_Tower_119_605MHz_028_185619-A__000000-000536 | 0.6037 | 0.7824 | 0.2 | 3.6 |
| BRNO_Approach-Radar_127_350MHz_026_111634-A__000000-000395 | 0.0037 | 0.0188 | 0.1 | 2.3 |
| Radar_120_520MHz_028_151125-A__000000-000444 | 0.9616 | 0.9868 | 0.1 | 2.9 |
| Radar_120_520MHz_028_151125-G__000444-000934 | 0.1301 | 0.3598 | 0.1 | 2.9 |
| Radar_120_520MHz_026_145941-G__000000-000349 | 0.0020 | 0.0091 | 0.1 | 2.1 |
| Tower_134_560MHz_025_144043-B__000000-000332 | 0.1241 | 0.3174 | 0.1 | 1.9 |
| Tower_134_560MHz_025_144043-A__000334-000742 | 0.3021 | 0.5535 | 0.1 | 2.2 |
| Tower_134_560MHz_025_144043-B__000744-001212 | 0.6205 | 0.7916 | 0.2 | 3.2 |

### Generic `facebook/wav2vec2-base-960h` (adjacent-domains posteriors), same 8 UWB-ATCC clips, 18 slots

| clip | T | p* | slot | P(correct) exact | P(competing) exact | P(residual) | P(correct \| parseable) | beam-50 Σ correct | beam-800 Σ correct | exact − beam-50 | mode ∈ | top competing hypothesis (p) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 34720N_002001_002559_AT | 278 | 6.03e-21 | SID "one hotel departure" | **9.44e-06** | 8.72e-04 | 0.999 | 0.011 | 0.00e+00 | 0.00e+00 | 9.44e-06 | Z | — |
| a1WcrN_000157_000469_AT | 155 | 3.34e-09 | callsign NOR-SHUTTLE 1515 | **4.42e-10** | 2.43e-08 | 1.000 | 0.018 | 0.00e+00 | 0.00e+00 | 4.42e-10 | Z | — |
|  |  |  | runway 31 | **2.99e-24** | 2.15e-14 | 1.000 | 1.39e-10 | 0.00e+00 | 0.00e+00 | 2.99e-24 | Z | — |
|  |  |  | phrase "line up" | **3.45e-03** | 3.28e-13 | 0.997 | 1.000 | 0.00e+00 | 0.00e+00 | 3.45e-03 | Z | — |
| a3o8f0_000000_000352_AT | 175 | 1.51e-12 | callsign OPERA-JET 300 | **3.99e-23** | 9.75e-12 | 1.000 | 4.09e-12 | 0.00e+00 | 0.00e+00 | 3.99e-23 | Z | — |
|  |  |  | "one hotel" after confirmation | **8.00e-20** | 1.08e-05 | 1.000 | 7.42e-15 | 0.00e+00 | 0.00e+00 | 8.00e-20 | Z | — |
| A5lZHJ_000000_000613_AT | 306 | 7.79e-19 | callsign CSA 37A | **3.90e-12** | 2.41e-06 | 1.000 | 1.62e-06 | 0.00e+00 | 0.00e+00 | 3.90e-12 | Z | — |
|  |  |  | runway 31 | **5.42e-18** | 7.23e-14 | 1.000 | 7.50e-05 | 0.00e+00 | 0.00e+00 | 5.42e-18 | Z | — |
|  |  |  | phrase "cleared for takeoff" | **5.36e-31** | 7.62e-13 | 1.000 | 7.03e-19 | 0.00e+00 | 0.00e+00 | 5.36e-31 | Z | — |
|  |  |  | wind 160 | **9.79e-21** | 7.64e-11 | 1.000 | 1.28e-10 | 0.00e+00 | 0.00e+00 | 9.79e-21 | Z | — |
|  |  |  | knots 5 (after degrees) | **9.34e-06** | 1.94e-11 | 1.000 | 1.000 | 0.00e+00 | 0.00e+00 | 9.34e-06 | Z | — |
| A5lZHJ_002805_003388_PIAT | 291 | 5.47e-18 | callsign AUSTRIAN 706P | **4.23e-20** | 1.34e-14 | 1.000 | 3.16e-06 | 0.00e+00 | 0.00e+00 | 4.23e-20 | Z | — |
| a8R9jE_000144_000596_AT | 225 | 6.35e-10 | callsign CSA 731 | **9.74e-07** | 3.15e-05 | 1.000 | 0.030 | 0.00e+00 | 0.00e+00 | 9.74e-07 | Z | — |
|  |  |  | frequency 121.9 (after ground) | **1.09e-12** | 2.65e-14 | 1.000 | 0.976 | 0.00e+00 | 0.00e+00 | 1.09e-12 | Z | — |
| a8R9jE_000700_001023_PIAT | 161 | 5.91e-12 | callsign CSA 71 | **6.53e-12** | 1.10e-06 | 1.000 | 5.94e-06 | 0.00e+00 | 0.00e+00 | 6.53e-12 | Z | — |
|  |  |  | leading number 19 | **1.38e-05** | 0.103 | 0.897 | 1.34e-04 | 0.00e+00 | 0.00e+00 | 1.38e-05 | Z | — |
| A64ueL_000128_000777_PI | 324 | 6.57e-19 | callsign SKY-TRAVEL 1102 | **8.75e-38** | 1.76e-15 | 1.000 | 4.98e-23 | 0.00e+00 | 0.00e+00 | 8.75e-38 | Z | — |
|  |  |  | stand 22A (after standing) | **1.55e-29** | 1.75e-15 | 1.000 | 8.86e-15 | 0.00e+00 | 0.00e+00 | 1.55e-29 | Z | — |

| clip | Σ p over beam-50 hypotheses | Σ p over beam-800 hypotheses | beam-50 s | beam-800 s |
|---|---|---|---|---|
| 34720N_002001_002559_AT | 0.0000 | 0.0000 | 0.2 | 4.3 |
| a1WcrN_000157_000469_AT | 0.0000 | 0.0000 | 0.1 | 1.9 |
| a3o8f0_000000_000352_AT | 0.0000 | 0.0000 | 0.1 | 2.4 |
| A5lZHJ_000000_000613_AT | 0.0000 | 0.0000 | 0.2 | 4.7 |
| A5lZHJ_002805_003388_PIAT | 0.0000 | 0.0000 | 0.2 | 4.6 |
| a8R9jE_000144_000596_AT | 0.0000 | 0.0000 | 0.2 | 3.2 |
| a8R9jE_000700_001023_PIAT | 0.0000 | 0.0000 | 0.1 | 2.0 |
| A64ueL_000128_000777_PI | 0.0000 | 0.0000 | 0.2 | 4.7 |

## 5. Exact class mass vs beam-k class rescoring

| model | slots | exact − beam-50 > 0.01 | > 0.1 | median gap | max gap | beam-50 total mass (median over clips) | beam-800 total mass (median) |
|---|---|---|---|---|---|---|---|
| in-domain (the atc-in-domain report) | 33 | **26** | **9** | 0.034 | **0.944** (TB402) | 0.47 (range 0.002–0.967) | 0.67 (0.009–0.991) |
| generic (the adjacent-domains report) | 18 | 0 | 0 | 1e-12 | 3.4e-3 | 0.000 | 0.000 |

The beam sum is always a lower bound (every hypothesis it contains is a genuine labelling with its exact probability) and it is loose precisely where the argmax certificate was weakest: on the 7 atc-in-domain clips with p\* < 0.05 the beam-50 list carries 0.2–30 % of the posterior, so the class mass it can see is a fraction of the truth (TB402: 0.4 % of 94.8 %; CSA 1DZ on the FL-error clip: 12.9 % of 94.4 %). Beam-800 halves the gap and costs 2–5 s per clip against 0.1–0.2 s for the exact sum. For the *risk* side the beam is worse: it reports the competing mass of the FL error as 0.13 (beam-50) / 0.36 (beam-800) where the exact value is 0.954. Conclusion: a class-constrained rescoring of an N-best list is materially different from the exact class posterior on in-domain ATC audio whenever spelling entropy is high, i.e. exactly on the clips where a certificate is wanted.

## 6. Per-value breakdown of the error slots (`breakdown.log`)

Flight-level slot on the error clip: P(FL=1) 0.871, P(FL=11) 0.076, P(FL=118) 0.0060, P(FL=18) 5.4e-4, P(FL=100) 3.4e-9, P(FL=108) 3.4e-9, P(FL=10) 4.3e-8, P(any number-like after "flight level") 0.954; spelling level: "one on eight" 0.0134, "one oneight" 0.0119, "one one eight" 0.0060, "one hundred" 3.4e-9 (certified mode p\* = 8.8e-3 — the *class* "reads as FL 1" has 100× the mode's mass). On the correct clip the same slot gives P(FL=100) 0.981, P(FL=1) 0.0088 (the truncation "one" + non-number), every other value ≤ 1e-12. The callsign slot on the OK-HHH clip: P(text contains "oscar kilo") 0.789, "hotel" 0.799, "kio hotel" 0.0116, "tio hotel" 0.0096, "triple hotel" 1.6e-7, OK-KH 0.0044, OK-H 3.0e-5, OK-HH 1.0e-9, OK-HHH 1.4e-7. Wind slot on the "zro" clip: P(160) 0.040, P(16) 0.906, P(1) 0.043; "wind one six zro" 0.895 — the model's spelling, not a misread, and a verifier defined on ICAO words will alarm on it (a false alarm relative to the reference; see §7 on what is *not* certified).

## 7. The safety object, in one page

**What is computed.** For a clearance item (level, heading, runway, frequency, callsign, phrase) the verifier is handed the *expected* value v and a slot definition; it returns three numbers that partition the posterior exactly: P_ok = P(readback states v | y), P_other = P(readback states a different well-formed value | y), P_unparseable = 1 − P_ok − P_other. Output: *"certified P(readback matches clearance) = P_ok; certified risk = 1 − P_ok, of which P_other is a certified different value and P_unparseable is a certified non-reading."* On the 16 in-domain clips this yields P_ok ≥ 0.9 on 21/33 items, P_ok ≤ 0.05 on 9/33 (7 genuine misreads + 2 in-slot misspellings), and 3 in between (0.33, 0.65, 0.85).

**What is certified.** (1) The three numbers are the *exact* sums over all (W)^T alignment paths — no beam, no lattice, no N-best, nothing pruned; the only approximation is IEEE-754 rounding (relative ≈ T·ε ≈ 1e-13; gated to 1e-15 against exact rationals). (2) They are probabilities of the model's own distribution p(· | y), so "P_ok ≥ 1 − 10⁻⁶" is a statement about a well-defined measure, and P_ok + P_other + P_unparseable = 1 is an identity, not a calibration assumption. (3) Class membership is a DFA over the model's characters, so the semantic mapping (which strings mean "FL100") is explicit, finite and auditable — the ICAO number grammar (SERA.14035 / Annex 10 §5.2.1.4: digits pronounced separately, whole hundreds/thousands with HUNDRED/THOUSAND, DECIMAL) is 13 words and compiles to ≤ 210 states. (4) Cost is O(T·|Q|·W) — 0.1 s per item here — with no worst-case blow-up (contrast the argmax certificate, exponential on near-tie tables, `certctc/README.md`).

**What is NOT certified.** (a) *Calibration of the acoustic model*: P_ok is the model's belief. The FL100 clip shows the model at 0.87 for FL 1 and 3e-9 for the truth — a confidently wrong posterior. The certificate makes such errors *visible* (P_ok ≈ 0 → alarm) but it cannot make a wrong model right, and a confidently wrong posterior that lands on a *different well-formed* value (here "FL 1", ungrammatical for a level, but "FL 118" at 0.006 is not) is the failure mode a safety case must bound empirically, per model and per domain, e.g. by the readback-error-detection / false-alarm rates the ATC community already reports (Helmke et al. 2022: 80 % detection / 11 % false alarm on Isavia en-route audio at 5 %/10 % WER). (b) *Domain shift*: the generic model gives P_ok ≤ 3e-3 on every slot — an honest "unverifiable", but a deployment that is always unverifiable is useless, so the certificate needs the in-domain model (or the checkpoint's shipped 4-gram LM folded into the class posterior — an LM is just another automaton in the product, and would collapse "zro"-type residual mass). (c) *The class definition itself*: "zro" ≠ "zero", "alf" ≠ "alfa", "onee" ≠ "one" under the lexicon used; the exact sum is over the class *as specified*, and spelling tolerance is a specification choice (enumerate variants, or add an edit-distance-1 automaton) that trades false alarms against missed misreads. (d) *Reference-style effects*: ATCO2 references contain disfluencies; the certificate is about the acoustic evidence, not the transcript convention.

**Relation to the literature.** The object is the word-posterior confidence measure of Wessel, Schlüter, Macherey & Ney (IEEE TSAP 2001) — "estimate the confidence of a hypothesized word directly as its posterior probability, given all acoustic observations of the utterance … computed on word graphs using a forward–backward algorithm", where "the posterior probability [of a word hypothesis] can be computed by summing up the posterior probabilities of all sentences which contain the hypothesis" and "a word graph can thus be regarded as a limited representation" of the search space — computed here over the *unlimited* CTC path space instead of a pruned word graph, with the hypothesis generalised from "word w at this position" to any regular class. The machinery is the CTC-over-WFST composition of EESEN (Miao, Gowayyed & Metze 2015: "S = T ∘ min(det(L ∘ G))", where T "allows occurrences of the blank label ∅, as well as repetitions of any non-blank labels" and the forward variable "represents the total probability of all CTC paths that end with label l_u at frame t") and of Laptev, Majumdar & Ginsburg (Interspeech 2022: "the CTC loss as forward-backward score computation of an intersection between a supervision graph and the acoustic outputs of a neural network", topology T.fst "a directed complete graph with self-loops … N states and N² arcs"): here G is the class DFA, L is the character-level lexicon (trivial), and the forward score of T ∘ (class DFA) against the dense posteriors is P(L | y) — in k2 terms `intersect_dense` + total scores. Constrained *decoding* (Graves' token passing, TPAMI 2009; Scheidl, Fiel & Sablatnig's word beam search, ICFHR 2018, which "constrains words to those contained in a dictionary" but keeps only "the best beams … at each time-step") is the argmax cousin: it finds one grammatical string and is approximate; the class posterior sums all of them and is exact. CTC keyword spotting (Fernández, Graves & Schmidhuber 2007 — detection by per-timestep spikes; Zhuang et al. 2016 — phone-lattice matching with a threshold) uses the same posteriors but, as far as the body reads found, never states the keyword confidence as the exact forward sum over Σ\*·k·Σ\*; that formulation appears to be new in this exact form, although it is an immediate consequence of the WFST view. On the ATC side, readback verification is compared at the level of "ATC concepts", not words (Helmke et al. 2021: "'nineteen eight' is the same as 'one one nine decimal eight' … the presented approach transforms recognized word sequences into so-called ATC concepts"), which is exactly what VALUE(v) and the suffix tokenisations implement; the field's accuracy lever is contextual callsign boosting via lattice rescoring (Nigmatulina et al. ICASSP 2022: "Lattices′ = Lattices ∘ biasing FST", callsign accuracy 42.8 → 88.5 % on LiveATC; Zuluaga-Gomez et al. 2023: 86.7 → 96.1 %), which is a *prior* over the callsign class — it composes with this object as another weight in the product and would be certified in the same sum. Mandatory readback items are fixed by regulation (SERA.8015(e)(1) = ICAO Doc 4444 §4.5.7.5.1: route clearances, runway clearances, runway-in-use, altimeter settings, SSR codes, communication channels, level, heading and speed instructions, transition levels) — a finite list of slot types, each a small regular class.

**Verdict on the "certificate" programme.** The exact-argmax certificate certified spelling; this object certifies meaning, is polynomial, and on the decisive cases returns the honest answer (refusal at 10⁻⁷–10⁻⁹). It is classical and seconds of CPU; nothing here needs an exact decoder, a beam, or anything quantum. It does not remove the acoustic model from the safety case — it moves the burden to where it belongs: calibration of P_ok on in-domain audio.

## 8. Next step

1. Calibration study on ATCO2-test (871 rows) and UWB-ATCC test with the in-domain checkpoint: bin P_ok for the reference slot, measure the empirical correctness per bin (reliability diagram) and the two operating numbers a safety case needs — P(misread | P_ok ≥ τ) and P(alarm | correct readback) as functions of τ — for levels, headings, runways, frequencies and callsigns separately; compare to Helmke et al.'s 80 %/11 %.
2. Fold the checkpoint's shipped 4-gram LM into the product (it is a WFST) and re-measure the residual mass and the "zro"/"alf" false alarms; add an edit-distance-1 spelling automaton as the alternative and report both.
3. Surveillance-context prior: the callsign class weighted by the traffic list (Nigmatulina's biasing FST) — the certified quantity becomes P(callsign = c | y, context) with the same recursion.
4. Adversarial check of the class specification with a second agent: random ICAO-grammatical strings through `VALUE`/`suffix_tokenisations` vs an independent parser, and a mutation test that a wrong anchor or a missing alias changes the certified numbers by a detectable amount.
5. The generic-model column says a certificate on an out-of-domain model is an "always unverifiable" oracle: if a product needs to run on a general model, the honest number is the class posterior's *coverage* (P_ok + P_other), which here is < 1e-4 on every slot.

## Citations (body-read unless marked; verbatim quotes above; pulled by a delegated literature agent this session, URLs listed)

- Graves, Fernández, Gomez, Schmidhuber, "Connectionist Temporal Classification", ICML 2006 — eq. 3 and §3 ("we do not know of a general, tractable decoding algorithm … the following two approximate methods"). https://www.cs.toronto.edu/~graves/icml_2006.pdf
- Graves et al., IEEE TPAMI 31(5), 2009 (CTC token passing) — cited from search only, not fetched.
- Miao, Gowayyed, Metze, "EESEN: End-to-End Speech Recognition using Deep RNN Models and WFST-based Decoding", ASRU 2015, arXiv:1507.08240 — §2.2, §3.1, eq. 8.
- Laptev, Majumdar, Ginsburg, "CTC Variations Through New WFST Topologies", Interspeech 2022, arXiv:2110.03098 — §1, §2.1.
- Scheidl, Fiel, Sablatnig, "Word Beam Search: A CTC Decoding Algorithm", ICFHR 2018, doi:10.1109/ICFHR-2018.2018.00052 — §I, §II.B (also local `adjacent-domains/papers/scheidl_wbs.txt`).
- Fernández, Graves, Schmidhuber, "An application of recurrent neural networks to discriminative keyword spotting", ICANN 2007, doi:10.1007/978-3-540-74695-9_23 — §2.1, §2.3.
- Zhuang, Chang, Qian, Yu, "Unrestricted Vocabulary Keyword Spotting Using LSTM-CTC", Interspeech 2016, doi:10.21437/Interspeech.2016-753 — §2, §2.3.
- Wessel, Schlüter, Macherey, Ney, "Confidence Measures for Large Vocabulary Continuous Speech Recognition", IEEE TSAP 9(3):288–298, 2001 — abstract, §II, §II.A.
- Helmke, Ondřej, Shetty, Arilíusson, Simiganoschi, Kleinert, Ohneiser, Ehr, Zuluaga-Gomez, Smrz, "Readback Error Detection by Automatic Speech Recognition and Understanding — Results of HAAWAII project for Isavia's Enroute Airspace", SESAR Innovation Days 2022 — abstract, Table II. https://www.sesarju.eu/sites/default/files/documents/sid/2022/paper_3.pdf
- Helmke et al., "Readback Error Detection by ASR to Increase ATM Safety", ATM Seminar 2021 — abstract.
- Nigmatulina, Zuluaga-Gomez, Prasad, Sarfjoo, Motlicek, "A two-step approach to leverage contextual data: speech recognition in air-traffic communications", ICASSP 2022, arXiv:2202.03725 — §3.1, §5, Table 3.
- Zuluaga-Gomez et al., "A Virtual Simulation-Pilot Agent for Training of Air Traffic Controllers", Aerospace 2023, arXiv:2304.07842 — §4.1.4; ATCO2 corpus arXiv:2211.04054 — §6; [Z22] arXiv:2203.16822 as in the atc-in-domain report.
- SERA.14035 (transmission of numbers; transposes ICAO Annex 10 Vol II §5.2.1.4) and SERA.8015(e) (read-back; = ICAO Doc 4444 §4.5.7.5.1), UK CAA regulatory library HTML; CAP 413 cited from search only.

## Files

`../code/word-class-certificate/fsa.py` (NFA/DFA/products/word patterns), `../code/word-class-certificate/classctc.py` (`class_posterior`, exact references), `../code/word-class-certificate/atc_classes.py` (classes + per-clip specs), `../code/word-class-certificate/gate.py` + `gate.log`, `../code/word-class-certificate/measure.py` + `measure_a4.log`, `measure_generic.log`, `results__a4.json`, `results__generic.json`, `../code/word-class-certificate/breakdown.log`, `../code/word-class-certificate/gate_generic_mode.log`, `../code/word-class-certificate/tables.py` + `tables.md`, `../code/word-class-certificate/ctc.py` (toolkit copy).

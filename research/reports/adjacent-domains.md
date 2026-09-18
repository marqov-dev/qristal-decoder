# Adjacent domains for exact / certified CTC decoding

Date: 2026-09-18. Status: measured + literature triage. Nothing committed, posted, or spent.
Working dir: `adjacent-domains/` (venv, scripts, 28 posterior tables as `.npy`, JSON results, extracted paper texts).

## (a) Headline

**The low-confidence regime we could only reach with additive noise on LibriSpeech is the *default* for a deployed CTC model on three real hard domains — air-traffic-control radio (UWB-ATCC), far-field meeting speech (AMI single-distant-mic) and dysarthric speech (TORGO) — with no noise added: frame confidence 0.86/0.89/0.94 (vs 0.979 clean), converged-beam p\* median 7.5e-13 / 6.7e-7 / 1.6e-7, the gate `p* < 1/D` passes 24/24, greedy finds the mode in only 4/24, beam-5 in 9/24, and in 4/24 utterances beam-800 returns a labelling *less* probable than greedy's (up to 4.4× less) — beam search demonstrably misses the mode.**
**But the top-two margin is 1.00–1.62 (median 1.04–1.09) and the mode itself has WER 0.7–1.0 — the exact mode is garbage; what is certifiable is *ambiguity*, not the transcript. The domain where that is worth money is ATC readback / safety-critical speech verification (Zuluaga-Gomez et al. 2022: ATC channels "usually below 15 dB SNR", 23–31 % WER on noisy accented sets even after in-domain fine-tuning).**
**No CTC domain with an open model has W ≥ 10⁴ (largest found: sign-language glosses, W≈1.3k); nanopore's current models are CTC-CRF (k-mer transition scores, globally normalised), not a product measure — so the √W beam route and the nanopore angle are both closed on the evidence below.**

## (b) Triage table

Legend: *product measure* = per-frame softmax, all Wᵀ paths admissible, collapse map B (our theorems' premise). *Conf* = typical max-softmax per frame. *Gap evidence* = published or measured beam-vs-greedy / beam-vs-exact. *Cert value* = does anyone pay for a certified mode or a provable margin? *Open CPU model* = runnable here ≤400 MB.

| Domain | Product measure? | Alphabet W | Typical confidence | Beam-vs-exact gap evidence | Certification value | Open CPU model | Verdict |
|---|---|---|---|---|---|---|---|
| **Speech, ATC radio** (UWB-ATCC, ATCOSIM, ATCO2, LiveATC) | Yes (wav2vec2-CTC chars) | 32 | **Measured here: 0.857 mean / 0.934 median; 33–52 % of frames < 0.9** (generic model, domain shift only — UWB-ATCC is ≥ 20 dB SNR [Z22 Tab.1]) | **Measured: greedy=mode 0/8, beam-5 3/8, beam-50 5/8; p\* 6e-21–3e-9; margin 1.00–1.12** | **High**: "the 'ideal ASR engine' should aim at preventing error propagation to the fullest extent" [Z22, body]; readback-error detection is the standard ATC use-case; safety-critical | Yes — `facebook/wav2vec2-base-960h` (cached) used; in-domain `Jzuluaga/wav2vec2-*-atc-*` exist but are 1.26 GB | **Best fit for the certification framing.** Small W kills the √W route. |
| **Speech, far-field meetings** (AMI SDM) | Yes | 32 | **Measured: 0.887 / 0.975; 18–48 % frames < 0.9** | **Measured: greedy 2/8, beam-5 2/8, beam-50 5/8; p\* 2e-18–1.5e-3; margin 1.01–1.62** | Low (nobody certifies meeting minutes); MBR/LM route dominates | Yes (same) | Regime present; value absent. |
| **Speech, dysarthric** (TORGO) | Yes | 32 | **Measured: 0.937 / 0.994; 6–25 % frames < 0.9** (healthy controls same setup: 0.978 / 1.000) | **Measured: greedy 2/8, beam-5 4/8, beam-50 6/8; p\* 3e-10–4e-2; margin 1.01–1.40** | Medium (AAC, clinical assessment) but users want *accuracy*; severity-specific fine-tuning still leaves WER 40–52 % [SAFT26, abstract] | Generic model yes; the only ≤400 MB TORGO checkpoint (`sulde/torgo-wav2vec2-dysarthric`) is **degenerate** (emits blank only on 12/12 inputs; see §c) | Regime present; the fix is fine-tuning/LM, not search. |
| Speech, clean read (LibriSpeech; TORGO healthy controls here) | Yes | 32 | 0.979 / 1.000 (prior E7); **0.978 / 1.000 here** | beam-5 = exact 11/11 (E7); **4/4 here**, p\* 0.08–0.97, margin 1.3–82 | — | Yes | Moot (control reproduces E7 — pipeline parity confirmed). |
| **Nanopore DNA/RNA basecalling** — current ONT (Bonito/Dorado, all `fast/hac/sup` models) | **No.** CTC-CRF: per-timestep *transition* scores between 4^state_len k-mer states, `n_score = len(alphabet)·n_base**state_len`, loss `logz = logZ_cu(stay_scores, move_scores, …)` — global normalisation over a *constrained* path space [Bonito `crf/model.py`, body] | 5 emissions but ~1k–4k k-mer states | Not reported per-frame; read-level: median match rate 90 %, homopolymer error 14.9 % (Bonito) [PG23, body]; "each model has its own PhredQ score offset … not directly numerically comparable" [PG23] | CRF +4 % match rate over CTC [PG23]; for CTC basecallers "beam sizes of 10 are usually sufficient" [Boža21, body]; "beam search or Viterbi search can in practice be used to find reasonably good solutions" [SR21, body] | Consensus-over-reads, not single-read exactness, is how the field buys certainty ("lifts Bonito's median accuracy from 94.7 % to 98.1 %") [SR21] | Bonito needs CUDA/koi; Dorado has Apple-silicon builds but emits bases + move tables, not posteriors [Dorado README, body] | **Closed** for our theorems (not a product measure); legacy pure-CTC basecallers (Bonito ≤ v0.3, RODAN RNA "beam search size of 5" [RODAN, search-summary only]) are product-measure but W=5 and D≈10³–10⁵ make p\* vanish trivially and the √W route worthless. |
| **Handwritten text recognition** (PyLaia, Kraken, Scheidl CRNN) | Yes (chars) | 79 (IAM), 93 (Bentham) [Sch18, body] | Not reported per-frame; CER 4.6–9.7 % line-level [TK24, body; Ret24, body] | **Best-path vs vanilla beam (BW 15–50): IAM 8.77→8.49 CER, Bentham 5.60→5.55 (Tr+L) / 5.35 (Te)** [Sch18 Tab., body]; LM matters more: PyLaia IAM 8.44→7.50 CER with char LM, NorHand 9.72→8.23 [TK24, body]; Ret24 uses greedy only | Medium (archives/legal/genealogy want verified transcripts; historical HTR is a human-in-loop product) | PyLaia models on HF (Teklia) — not run (budget spent) | Product measure + medium value; gap small on modern models; degraded manuscripts unmeasured. **Runner-up.** |
| **Sign language (CSLR)** (PHOENIX-2014) | Yes (gloss CTC) | **≈1,295 glosses** — the largest CTC alphabet found | Not reported | "having a higher beam value did not improve performance"; beam 4–5 standard [search-summary of CSLR papers, abstract-level] | None | No CPU-cheap path checked | Closest to "large W" but still 10× short of 10⁴; beam 5 suffices. |
| **Lip reading / VSR** (LRS2/3, LiteVSR2) | Yes (chars) | ~30 | Low by construction (visual ambiguity; WER 20–30 % range) [search-summary] | Greedy S=26.2 % vs char-beam 16.5 % *audio* (Switchboard, LM in beam) [Zen17, body] — no clean beam-only gap found for VSR | Niche (forensic lip-reading) | Not checked | Regime plausible, value low. |
| **Brain-to-text / silent speech** (CTC phonemes) | Yes | 41 phonemes | Low; PER 7.9 %, WER 26.6 % only via "WFST beam search (beam=128)" + phoneme LM [iPh26, abstract] | WER hinges on LM, not acoustic search | Users are patients: accuracy, not certification | Not open | MBR/LM route; not ours. |
| **De novo peptide sequencing** (π-PrimeNovo) | CTC training, but decoding is a **mass-constrained knapsack DP over per-position probabilities**, selecting "the most probable sequence at d_{t,|A|} cell" — a constrained best-path, not collapsed-sum argmax [PN24 bioRxiv, body] | ~20 AA + PTMs | Low (peptide recall 64–75 %) [PN24] | No beam; exact under constraint | Medium (mass constraint is itself a certificate); T is small (≤ ~40) so classical exact search is cheap | Yes (GitHub) but out of scope | Interesting analogue of "certified constrained decoding"; no quantum angle. |
| Optical music recognition (PrIMuS CRNN-CTC) | Yes | agnostic/semantic symbol alphabets (sizes not extracted from text; hundreds–~2k) | High: "error rates at symbol level below 2 %" [CZ18, body] | Greedy used | Low | Yes (tf-deep-omr) | Moot (peaky). |
| Keyword spotting; chemical/math OCR (DECIMER, im2latex) | KWS is not sequence decoding; DECIMER/im2latex are attention seq2seq, not CTC | — | — | — | — | — | Out of scope. |
| **Acoustic-to-word CTC** (Soltau et al. 2016 arXiv:1610.09975; Audhkhasi et al. 2017 arXiv:1703.07754) | Yes | **10⁴–10⁵ words** | unknown | unknown | — | No open checkpoints found | The *only* product-measure CTC family with W ≥ 10⁴ — the natural home of the √W result. Title-level pointer only; not read. |

## (c) Measurement

### Setup
- Venv: `uv venv --python 3.12` at `adjacent-domains/.venv`; torch 2.14.0 (CPU), transformers 5.17.0, datasets 5.0.1, numpy 2.5.3, soundfile. Never system python; toolkit imported read-only (the validation toolkit `ctc.py`, included as `../code/certified-exact-decoder/ctc.py`).
- Models: `facebook/wav2vec2-base-960h` (already in HF cache — zero download; W=32, blank=`<pad>`=0). `sulde/torgo-wav2vec2-dysarthric` (377.6 MB, the one permitted download; W=33, blank=32): **degenerate** — softmax is the identical blank-dominated row on every frame (conf 0.984 constant), D=0 on 12/12 inputs. Discarded; all other TORGO/ATC/CHiME CTC checkpoints on HF are XLS-R/large (1.26 GB) and over budget.
- Data (handful of samples via HF datasets-server row API, 4.8 MB total): 8× UWB-ATCC test (`Jzuluaga/uwb_atcc`, 3–6.5 s, ≥5 words), 8× AMI SDM test (`edinburghcstr/ami` config `sdm`), 8× TORGO dysarthric (`abnerh/TORGO-database`, rows 12000–16100, `speech_status='dysarthria'`, ≥4 words, ≥3 s), 4× TORGO healthy controls (same corpus, same mic).
- Pipeline: `measure.py` → softmax in float64 → `posteriors/*.npy` (T×W) → toolkit `topk_labellings` at beam 5/50/100/200/400/800, `ctc_forward(greedy)`, `collapse`.

### Gate / convergence lines
```
GATE ctc_forward vs brute force: 1361 labellings, worst rel err 4.17e-16 -> PASS
GATE prefix beam vs brute force: 300 instances, 0 wrong argmax, worst score err 3.33e-16 -> PASS
```
(re-run inside every measurement run; toolkit's own T ≤ 6 brute-force gates.)

Beam convergence at real T (cannot brute-force; `converge.py`, 4 hard-domain tables, beams 200→6400):

| table | T | D | p\* @200 | @800 | @1600 | @3200 | @6400 | mode stable from | margin @6400 |
|---|---|---|---|---|---|---|---|---|---|
| ATC a1WcrN | 155 | 49 | 2.12e-9 | 3.34e-9 | 3.57e-9 | 3.573e-9 | 3.573e-9 | beam 400 | 1.016 |
| AMI MEE073_0193279 | 141 | 56 | 1.39e-3 | 1.470e-3 | 1.471e-3 | 1.4713e-3 | 1.4729e-3 | beam 200 | 1.595 |
| ATC a8R9jE | 225 | 77 | 5.49e-10 | 6.35e-10 | 6.49e-10 | 6.495e-10 | 6.64e-10 | beam 200 | 1.121 |
| AMI MEE073_0182107 | 172 | 60 | 6.91e-12 | 9.39e-12 | 1.24e-11 | 1.26e-11 | 1.28e-11 | beam 200 | 1.053 |

Reading: the **mode identity** is stable from beam 200–400 on all four, but **p\* is still creeping by 1–2 % between beam 3200 and 6400** on two of four (mass in the preimage arriving through late-pruned prefixes). So every p\* below is a lower bound, good to within ~×1.1–1.8 of the beam-200 value; margins are stable to three decimals from beam 400. The `rel Δp* 400→800` column in the main table (up to 0.47) is therefore *mass* convergence, not mode instability — except the two rows flagged `400=800 mode = N`.

### Per-sample table (generic model `wav2vec2-base-960h`; p\* at beam 800; gate `p* < c/D` with c = 1)

| domain | T | D | conf mean/med | frames conf<0.9 | p\* | margin p\*/p₂ | p(greedy)/p\* | greedy=mode | beam-5 | beam-50 | 400=800 mode | WER(mode) | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| atc_uwb | 278 | 65 | 0.844/0.920 | 0.44 | 6.0e-21 | 1.00 | **4.43** | N | N | Y | Y | 1.10 | PASS |
| atc_uwb | 155 | 49 | 0.857/0.934 | 0.41 | 3.3e-09 | 1.02 | 0.76 | N | N | N | Y | 0.64 | PASS |
| atc_uwb | 175 | 63 | 0.830/0.898 | 0.50 | 1.5e-12 | 1.11 | 0.40 | N | Y | Y | Y | 0.80 | PASS |
| atc_uwb | 306 | 87 | 0.866/0.933 | 0.42 | 7.8e-19 | 1.02 | **4.16** | N | Y | Y | Y | 1.00 | PASS |
| atc_uwb | 291 | 87 | 0.865/0.951 | 0.39 | 5.5e-18 | 1.12 | 0.82 | N | N | Y | Y | 0.74 | PASS |
| atc_uwb | 225 | 77 | 0.884/0.956 | 0.36 | 6.3e-10 | 1.12 | 0.77 | N | Y | Y | Y | 0.83 | PASS |
| atc_uwb | 161 | 46 | 0.838/0.896 | 0.52 | 5.9e-12 | 1.05 | 0.94 | N | N | N | Y | 2.20 | PASS |
| atc_uwb | 324 | 57 | 0.874/0.962 | 0.33 | 6.6e-19 | 1.03 | 0.20 | N | N | N | **N** | 0.83 | PASS |
| ami_sdm | 172 | 60 | 0.839/0.915 | 0.48 | 9.4e-12 | 1.06 | 0.58 | N | N | Y | Y | 0.67 | PASS |
| ami_sdm | 146 | 38 | 0.850/0.922 | 0.42 | 1.4e-09 | 1.07 | **1.30** | N | N | Y | Y | 1.14 | PASS |
| ami_sdm | 141 | 56 | 0.913/0.979 | 0.28 | 1.5e-03 | 1.62 | 1.00 | Y | Y | Y | Y | 0.38 | PASS |
| ami_sdm | 147 | 48 | 0.897/0.970 | 0.33 | 2.5e-05 | 1.27 | 1.08 | Y | Y | Y | Y | 0.80 | PASS |
| ami_sdm | 199 | 47 | 0.902/0.987 | 0.31 | 3.4e-08 | 1.08 | 0.44 | N | N | N | Y | 0.64 | PASS |
| ami_sdm | 323 | 96 | 0.936/0.997 | 0.18 | 2.3e-06 | 1.59 | 0.93 | N | N | Y | Y | 0.45 | PASS |
| ami_sdm | 172 | 21 | 0.910/0.993 | 0.24 | 1.3e-06 | 1.11 | 0.91 | N | N | N | Y | 1.00 | PASS |
| ami_sdm | 305 | 107 | 0.850/0.941 | 0.44 | 2.4e-18 | 1.01 | **3.67** | N | N | N | Y | 0.78 | PASS |
| torgo_dys | 194 | 23 | 0.977/1.000 | 0.06 | 3.9e-02 | 1.40 | 1.00 | Y | Y | Y | Y | 0.14 | PASS |
| torgo_dys | 314 | 48 | 0.914/0.989 | 0.25 | 3.3e-10 | 1.02 | 0.14 | N | N | N | Y | 1.25 | PASS |
| torgo_dys | 412 | 50 | 0.945/0.996 | 0.16 | 1.5e-09 | 1.11 | 0.82 | N | N | Y | Y | 1.00 | PASS |
| torgo_dys | 209 | 32 | 0.946/0.996 | 0.17 | 2.9e-04 | 1.07 | 0.74 | N | Y | Y | Y | 1.00 | PASS |
| torgo_dys | 322 | 32 | 0.939/0.996 | 0.17 | 7.4e-08 | 1.09 | 0.12 | N | Y | Y | Y | 1.00 | PASS |
| torgo_dys | 224 | 33 | 0.920/0.990 | 0.21 | 2.4e-07 | 1.05 | 0.49 | N | N | Y | Y | 1.50 | PASS |
| torgo_dys | 299 | 38 | 0.918/0.988 | 0.24 | 1.3e-09 | 1.01 | 0.26 | N | N | N | **N** | 1.00 | PASS |
| torgo_dys | 247 | 38 | 0.939/0.992 | 0.18 | 1.6e-06 | 1.06 | 1.10 | Y | Y | Y | Y | 0.67 | PASS |
| torgo_ctl | 359 | 59 | 0.983/1.000 | 0.06 | 4.5e-01 | 6.32 | 1.00 | Y | Y | Y | Y | 0.00 | fail |
| torgo_ctl | 262 | 45 | 0.970/0.997 | 0.08 | 7.9e-02 | 1.26 | 0.79 | N | Y | Y | Y | 0.10 | fail |
| torgo_ctl | 337 | 52 | 0.984/1.000 | 0.06 | 5.4e-01 | 2.39 | 1.00 | Y | Y | Y | Y | 0.00 | fail |
| torgo_ctl | 322 | 72 | 0.976/1.000 | 0.07 | 9.7e-01 | 82.2 | 1.00 | Y | Y | Y | Y | 0.00 | fail |

**p(greedy)/p\* > 1 (bold)** means the greedy labelling has *higher* CTC probability than the labelling beam-800 returned: prefix beam search pruned the true mode's prefix. That is a direct, gate-backed demonstration that beam-800 is not exact on these tables (4/24 hard-domain utterances; up to 4.4×).

### Per-domain summary and comparison to the speech baseline

| condition | n | conf mean | conf median | p\* median | p\* range | margin median (range) | greedy=mode | beam-5=mode | beam-50=mode | WER(mode) |
|---|---|---|---|---|---|---|---|---|---|---|
| LibriSpeech clean (prior E7) | 11 | 0.979 | 1.000 | ~0.1–0.7 | — | 29 (1.54–719) | 10/11 | 11/11 | — | low |
| LibriSpeech +noise 5 dB (prior N47–N50) | 7 | 0.893 | — | ~5e-12 | — | 1.12 | — | 4/7 | — | — |
| LibriSpeech +noise 0 dB (prior) | 7 | — | — | ~6e-18 | — | 1.02 | — | 1/7 | — | — |
| **TORGO healthy control (this run)** | 4 | 0.978 | 1.000 | 4.9e-1 | 7.9e-2–9.7e-1 | 4.4 (1.26–82) | 3/4 | 4/4 | 4/4 | 0.03 |
| **UWB-ATCC (ATC radio, ≥20 dB SNR, accented)** | 8 | **0.857** | 0.934 | **7.5e-13** | 6.0e-21–3.3e-9 | **1.04 (1.00–1.12)** | **0/8** | 3/8 | 5/8 | 1.02 |
| **AMI SDM (far-field meetings)** | 8 | 0.887 | 0.975 | 6.7e-7 | 2.4e-18–1.5e-3 | 1.09 (1.01–1.62) | 2/8 | 2/8 | 5/8 | 0.73 |
| **TORGO dysarthric** | 8 | 0.937 | 0.994 | 1.6e-7 | 3.3e-10–3.9e-2 | 1.06 (1.01–1.40) | 2/8 | 4/8 | 6/8 | 0.94 |

Reading against the settled speech numbers: **ATC radio with a generic model sits between the 5 dB and 0 dB synthetic-noise rows on every statistic (conf 0.857 vs 0.893; p\* 7.5e-13 vs 5e-12/6e-18; margin 1.04 vs 1.12/1.02) with no noise added** — the domain shift (accent + VHF channel + phraseology) alone produces the regime. AMI and dysarthric sit near the 10 dB crossover. The healthy TORGO controls reproduce the clean-LibriSpeech numbers exactly (0.978/1.000, beam-5 4/4), so the pipeline is at parity with E7 and the effect is the audio, not the code.

Two caveats that cut against the application, both visible in the table: (i) the mode is *wrong* (WER 0.7–1.0) — certifying it certifies garbage; (ii) margins of 1.00–1.12 mean the mode is within the beam's own convergence noise of its runner-up, which is exactly the "acoustic exhaustion" Novosad 2026 describes: "no reweighting or recombination of acoustic signals can close the oracle gap" (arXiv:2606.23306, HTML body-read via fetch; their MBR-with-RoBERTa gain is 5.96→5.42 % WER on test-other). What is certifiable in this regime is **that the utterance is ambiguous** — a provable margin ≈ 1 is an abstention certificate.

## (d) Which of our results each domain favours

| route | needs | domain that fits | verdict |
|---|---|---|---|
| **Exact-argmax (Graves prefix search / amplitude-amplified tree search)** | product measure, tiny p\*, users who want the *mode* | ATC / far-field / dysarthric speech pass the gate 24/24 with p\* down to 1e-21, and beam-800 provably misses the mode 4/24. But the mode is wrong (WER ≈ 1) and margins ≈ 1 — nobody wants it. Nanopore (huge D → tiny p\*) fails the product-measure premise. | **Regime real, product absent.** The only sellable output is the certificate of ambiguity (margin), i.e. the *complement* of exact decoding. |
| **√W per-level beam speedup** | W ≥ 10⁴ | No open CTC domain qualifies: chars 32–94, phonemes 41, glosses ≈1.3k, k-mer CRF states ~1k–4k (and not a product measure). Only acoustic-to-word CTC (10⁴–10⁵ words; Soltau 2016 / Audhkhasi 2017, closed models, title-level) fits. | **No domain with an open model.** |
| **MBR route** | posterior mass spread over near-duplicates, external utility/LM | Exactly the AMI / ATC / dysarthric posteriors measured here (margin ≈ 1, mass in near-duplicates); Novosad shows MBR + masked-LM is what recovers WER; brain-to-text and VSR likewise live on LM+beam. | **Every hard domain favours MBR over argmax.** Our MBR result is the one with a customer; ATC readback verification is the customer with a safety budget. |
| **Certification (margin proof)** | converged p\*, p₂, and a bound on pruned mass | ATC (safety-critical: readback error detection; ATC audio "usually below 15 dB SNR" [Z22]); clinical/legal per RAS 2026 ("plausible-but-wrong transcriptions … especially acute in high-stakes applications … medical documentation and legal records", arXiv:2604.24278, PDF body-read). Note the certificate is classical: once the beam has converged, p\*/p₂ is a number; the quantum part would only speed up *finding* it. | **Real value, small W, classical cost is seconds** (beam 6400 on T=225 took 160 s in pure python). |

## (e) Next step

1. **If the certification angle is pursued:** fine-tune-free demonstration on ATC. Run the 1.26 GB `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim` (in-domain; needs one approved download) on the same 8 UWB-ATCC clips plus 8 ATCO2-test clips (open 1.1 h set, 10–15 dB SNR, WER 21–23 % even in-domain [Z22 Tab.2]) and re-measure. Prediction from Z22's WERs: in-domain UWB-ATCC will look like LibriSpeech-clean (moot), ATCO2/LiveATC will stay in the regime. That single run decides whether "certified readback" survives an in-domain model.
2. **If the √W route is pursued:** the only product-measure CTC family with W ≥ 10⁴ is acoustic-to-word CTC; read Soltau et al. 2016 (arXiv:1610.09975) and Audhkhasi et al. 2017 (arXiv:1703.07754) for their reported beam/greedy gaps before spending anything — no open checkpoints were found, so a demonstration would require training one.
3. **Drop nanopore** from the programme on the evidence: the production head is CTC-CRF (transition scores, global Z), not a product measure; W=5; and the field's route to certainty is consensus over reads.
4. Toolkit note (not modified — read-only): `topk_labellings` is O(T·beam·W) pure python; beam 6400 on T≈225 is ~3 min. Converged p\* on these domains needs beam ≥ 3200; report beam-800 numbers as lower bounds, as done above.

## Citations (body-read unless marked)

- [Z22] Zuluaga-Gomez et al., "How does pre-trained wav2vec 2.0 perform on domain-shifted ASR? An extensive benchmark on air traffic control communications", arXiv:2203.16822 (SLT 2022). **PDF body-read** (`adjacent-domains/zuluaga.txt`). Quotes: "the communications are mostly carried over noisy audio channels, usually below 15 dB SNR, which is the default in ATC environments"; Table 1 SNR: UWB-ATCC ≥ 20 dB, ATCO2-Test 10–15 dB, LiveATC-Test 5–15 dB; Table 2 (greedy / +4-gram LM): w2v2-L-60k+ (132 h ATC fine-tune) NATS 9.3/7.4, ISA VIA 11.2/9.1, ATCO2-Test 23.3/21.2, LiveATC-Test 31.1/27.2; w2v2-B (32 h) ATCO2 45.6/40.1.
- [Nov26] Novosad, "The Anatomy of the CTC Oracle Gap: Acoustic Exhaustion and Linguistic Recovery", arXiv:2606.23306 (2026-06-22). **HTML body fetched (two passes)**. Quotes: greedy 6.02 % vs oracle 4.44 % at G=16 (dev-other), oracle 3.53 % at G=128; "no reweighting or recombination of acoustic signals can close the oracle gap"; "MBR-CER decoding with a RoBERTa pseudo-log-likelihood posterior (τ=10, G=128) achieves 5.42% WER on held-out LibriSpeech test-other (greedy 5.96%)"; "VoxPopuli (coverage collapse: 91.5% of utterances already greedy-optimal)"; model is a 22M Zipformer-S CR-CTC.
- [RAS26] "RAS: a Reliability Oriented Metric for Automatic Speech Recognition", arXiv:2604.24278. **PDF body-read** (`adjacent-domains/ras.txt`): "forced decoding under weak acoustic evidence, yielding errors that appear confident rather than explicitly uncertain … especially acute in high-stakes applications with stringent transcription requirements, such as medical documentation and legal records."
- [PG23] Pagès-Gallego & de Ridder, "Comprehensive benchmark and architectural analysis of deep learning models for nanopore sequencing basecalling", Genome Biology 2023, PMC10088207. **HTML body fetched**: "using a CRF decoder leads to a general improvement of performance with a mean increase in match rate of 4%"; Bonito "highest median match rate (90%)"; homopolymer "lowest median error rate (14.9% …)"; "each model has its own PhredQ score offset … not directly numerically comparable".
- [Bonito crf] `nanoporetech/bonito` `bonito/crf/model.py` (master). **Raw source fetched**: class `CTC_CRF`, `n_score = len(self.alphabet) * self.n_base**(self.state_len)`, stay/move score gathers, `logz = logZ_cu(stay_scores, move_scores, …)`, `loss = -(logz / target_lengths)`; `bonito/cli/download.py` model list contains only `fast/hac/sup` DNA/RNA models, none named CTC.
- [SR21] Silvestre-Ryan & Holmes, "Pair consensus decoding improves accuracy of neural network basecallers for nanopore sequencing", Genome Biology 2021, PMC7814537. **HTML body fetched**: "While perfectly optimal decoding requires an intractably exhaustive search over sequences, heuristic algorithms (such as beam search or Viterbi search) can in practice be used to find reasonably good solutions"; "lifts Bonito's median accuracy from 94.7% to 98.1%".
- [Boža21] Boža et al., "Dynamic Pooling Improves Nanopore Base Calling Accuracy", arXiv:2105.07520. **PDF body-read** (`adjacent-domains/papers/boza2021.txt`): "inference of the best sequence Z in a trained network is hard, and consequently beam search heuristic is typically used"; "Compared to CTC, where beam sizes of 10 are usually sufficient, we need to use a much higher beam size with recurrent neural aligners (we use k = 50)".
- [Dorado] `nanoporetech/dorado` README (release-v1.0). **Raw fetched**: Apple Silicon (M-series, macOS 13+) supported; `--emit-moves` move tables; no posterior emission documented.
- [RODAN] Neumann et al., BMC Bioinformatics 2022, doi:10.1186/s12859-022-04686-y. **Search-summary only** ("basecalling is performed with a beam search size of 5"); README fetched (torch 1.4–1.8, Zenodo test data); full text behind Springer redirect — not body-read.
- [Sch18] Scheidl, Fiel, Sablatnig, "Word Beam Search: A Connectionist Temporal Classification Decoding Algorithm", ICFHR 2018. **PDF body-read** (`adjacent-domains/papers/scheidl_wbs.txt`): IAM 79 chars, Bentham 93, T=100; Table (CER/WER/ms): Best Path IAM 8.77/29.07/12, VBS BW=50 8.49/28.27/168; Bentham Best Path 5.60/17.06/15, VBS BW=15 5.55/16.39 (Tr+L), 5.35/16.02 (Te).
- [TK24] Tarride & Kermorvant, "Revisiting N-gram Models: Their Impact in Modern Neural Networks for Handwritten Text Recognition", arXiv:2404.19317. **PDF body-read** (`adjacent-domains/ngramhtr.txt`): "for PyLaia there is no such token (CTC model)"; Table 3 PyLaia CER no-LM / char-LM: NorHand 9.72/8.23, RIMES 4.57/3.79, IAM 8.44/7.50.
- [Ret24] Retsinas et al., "Best Practices for a Handwritten Text Recognition System", arXiv:2404.11339. **HTML body fetched**: greedy decoding only; IAM 4.62 % CER / 15.89 % WER line-level.
- [Zen17] Zenkel et al., "Comparison of Decoding Strategies for CTC Acoustic Models", arXiv:1708.04469 (Interspeech 2017). **PDF body-read** (`adjacent-domains/papers/zenkel2017.txt`): Table 1 Eval2000 WER greedy 37.2 % vs char-RNN beam 25.1 %; Table 2 substitutions greedy 26.2 % vs char beam 16.5 % (beam includes a character LM — not a pure search gap).
- [CZ18] Calvo-Zaragoza & Rizo, "Camera-PrIMuS", ISMIR 2018. **PDF body-read** (`adjacent-domains/papers/primus2018.txt`): CTC softmax "over the alphabet of music symbols"; "error rates at symbol level below 2%". Alphabet sizes not extractable from the text layer.
- [PN24] π-PrimeNovo, Nature Communications 2024, doi:10.1038/s41467-024-55021-3; **bioRxiv full text fetched** (10.1101/2024.05.17.594647): "knapsack-like dynamic programming (DP) solver that carefully selects the amino acids based on prediction probability while satisfying the precise mass constraint"; "the most probable sequence at d_{t,|A|} cell as our final result"; 64 % / 75 % peptide recall.
- [Zey21] Zeyer, Schlüter, Ney, "Why does CTC result in peaky behavior?", arXiv:2105.14849. **Abstract fetched**: "The peaky behavior of CTC models is well known experimentally."
- [SAFT26] "Addressing Dysarthric Speech Variability with Severity-Aware Fine-Tuning of Transformer-Based Wav2vec2 ASR Models", Circuits, Systems, and Signal Processing 2026, doi:10.1007/s00034-026-03515-4. **Search-summary/abstract only**: WER 40.48 % (TORGO) / 51.79 % (UASpeech) after severity-specific fine-tuning.
- [iPh26] "iPhoneme: Brain-to-Text Communication for ALS Using ConformerXL Decoding", arXiv:2604.16441. **Abstract fetched**: 7.86 % PER, 26.61 % WER via phoneme LM + "WFST beam search (beam=128)".
- CSLR beam-width statements (PHOENIX-2014, 1,295 glosses; "having a higher beam value did not improve performance"; beam 4–5): **search-summary only** over arXiv:2101.04632 / 2004.00588 — not body-read.
- Acoustic-to-word CTC: Soltau, Liao, Sak, arXiv:1610.09975; Audhkhasi et al., arXiv:1703.07754. **Title-level pointers only.**
- Earlier programme numbers (clean 0.979/1.000, beam-5 = exact 11/11, SNR sweep) from the programme's earlier internal claims ledger, entries N41, N43, N44, N47–N50 (not published).

## Files
- `adjacent-domains/measure.py`, `adjacent-domains/converge.py`, `adjacent-domains/select_samples.py`, `adjacent-domains/summarize.py` — pipeline.
- `adjacent-domains/posteriors/*.npy` — 28 float64 T×W softmax tables (20 generic-model + 8 dysarthric; the 8 degenerate `torgoft__atc_*` tables are also present and should be ignored).
- `adjacent-domains/results__base960h.json`, `adjacent-domains/results__base960h_dys.json`, `adjacent-domains/convergence.json`, `adjacent-domains/summary_tables.md`, run logs `run_*.log`, `converge.log`.
- `adjacent-domains/samples/*.wav` (28 clips, 4.8 MB), `adjacent-domains/manifest.json`.
- `adjacent-domains/zuluaga.txt`, `adjacent-domains/ngramhtr.txt`, `adjacent-domains/ras.txt`, `adjacent-domains/papers/*.txt` — extracted paper texts used for the body-read quotes.

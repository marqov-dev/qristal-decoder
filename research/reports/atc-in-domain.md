# Does the certification regime survive an in-domain ATC model?

Date: 2026-09-18. One measurement experiment. All artefacts under `atc-in-domain/` (all other directories untouched).

## Headline verdict

**On UWB-ATCC the regime was a domain-shift artefact of the generic model. It does not survive an in-domain model.** On the same 8 test clips, swapping `facebook/wav2vec2-base-960h` for `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim` moves every statistic to the clean-LibriSpeech column: frame confidence 0.857 → 0.976, certified p\* median 1.0e-12 → 0.45, gate `p* < 1/D` 8/8 → 1/8, top-two margin median 1.02 → 5.2, greedy = certified mode 0/8 → 7/8, beam-5/50/800 = mode 8/8 (generic beam-800 missed it on 2/8), WER of the certified mode 1.02 → 0.13 (corpus 0.135; the model card reports 17.5 % on this test split).

**On ATCO2-test (10–15 dB SNR, cross-corpus for this checkpoint) the *gate* half-survives but the *consequences* do not.** 4/8 clips pass `p* < 1/D` (p\* down to 1.3e-4), 4/8 have margin 1.03–1.10, greedy misses the certified mode 3/8 and beam-5 misses it 2/8 — but **beam-50 and beam-800 recover the certified mode 8/8**, so the exact decoder adds nothing over a beam of 50 on any of the 16 utterances. The certified mode is now a mostly-correct transcript (WER 0.19, corpus 0.188 — matching Zuluaga-Gomez et al. 2022 Table 2's 21–23 % on ATCO2-test after ATC fine-tuning [Z22]), not garbage.

**The certified runner-up differs from the certified mode by exactly one character on 16/16 in-domain clips (and on 8/8 generic clips).** The margin p\*/p₂ is therefore a certificate about the nearest *spelling variant* of the same hypothesis, not about a word-level or readback-level alternative. That breaks the "certificate of ambiguity for ATC readback verification" idea as stated: the two safety-relevant errors in this set — callsign `triple hotel` → `kio hotel` / `tio hotel` (margin 1.03) and `one hundred` → `one on eight` / `oneight` (margin 1.10) — have *both* top-two hypotheses wrong and agreeing on the wrong words; the correct transcript sits at p(ref)/p\* = 7.1e-9 and 2.6e-7 respectively. Conversely the worst transcript in the set (WER 0.38, "just requested … there is a chance for us") carries a comfortable margin of 1.60, and the wrong spelling `zro` beats the correct `zero` by a margin of 22. The margin does not track correctness in either direction.

## Setup

- Model: `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim` (exact repo id exists; snapshot `abeadc1d…`, `pytorch_model.bin` 1.26 GB, downloaded into `~/.cache/huggingface/hub`, no LM used). Base `facebook/wav2vec2-large-960h-lv60-self`, fine-tuned on UWB-ATCC-train + ATCOSIM-train (model card; paper [Z22]). Card-reported greedy WER: UWB-ATCC test 17.48 %, ATCOSIM test 1.85 %. ATCO2 is **not** in its fine-tuning data.
- Vocab / table: `W = 31` (`vocab.json` 29 entries + `<s>`=29, `</s>`=30), **blank = `[PAD]` = 28**, word delimiter `|` = 0, letters a–z = 1–26, `[UNK]` = 27. Because the certified-exact-decoder report decoder and the toolkit assume blank = column 0, columns 0 and 28 are swapped before decoding and labels mapped back (the permutation is an involution; text is rendered from the un-permuted labels). Posteriors saved in the model's native column order as float64 `atc-in-domain/posteriors/atcindom__<domain>__<id>.npy`; the generic model had `W = 32`, blank 0.
- Audio: the 8 UWB-ATCC test clips already in `adjacent-domains/samples/` (8 kHz WAV, resampled to 16 kHz with `torchaudio.functional.resample`, identical to adjacent-domains/measure.py) plus 8 ATCO2 test-set clips from `Jzuluaga/atco2_corpus_1h` (split `test`, 871 rows) fetched one-by-one via the datasets-server `/rows` API (16 kHz WAV, 106–172 KB each; `atc-in-domain/samples/`), selected with the same rule as the adjacent-domains report (first 8 rows with 3 s ≤ duration ≤ 8 s and ≥ 5 words). Manifest with references: `atc-in-domain/manifest.json`.
- Inference: `adjacent-domains/.venv/bin/python` (torch 2.14 CPU, transformers 5.17), `Wav2Vec2FeatureExtractor` + `Wav2Vec2CTCTokenizer` (the card's `Wav2Vec2ProcessorWithLM` is not needed for raw posteriors), float64 softmax of the logits. Whole 16-clip run incl. decoding: ~5 min wall-clock.
- Decoder: `../code/certified-exact-decoder/exactbwd.c` (unmodified copy) compiled in the atc-in-domain report (`cc -O2 -shared -fPIC`) → `atc-in-domain/libexactbwd.so`; `atc-in-domain/cdec.py` is ../code/certified-exact-decoder/cdecoder.py pointing at it. Greedy / beam-k from the validation toolkit `ctc.py` (`collapse`, `ctc_forward`, `topk_labellings` with k = 2; the same file byte-for-byte as `../code/certified-exact-decoder/ctc.py`). Certified p\* re-checked against `ctc_forward` on every clip (max rel err 1.0e-15). WER = simple word-level Levenshtein on lowercase whitespace-split text (jiwer is not in the venv), no further normalisation.
- Scripts: `atc-in-domain/select_atco2.py`, `atc-in-domain/measure_a4.py` (log `run_atcindom.log`, output `results__atcindom.json`), `atc-in-domain/analyse.py` (adds edit distances and p(ref); `results__atcindom_annot.json`), `atc-in-domain/gate_a4.py` (log `gate_a4.log`), `atc-in-domain/generic_paired.json` (generic values pulled from `adjacent-domains/results__base960h.json` + `../code/certified-exact-decoder/real_*.jsonl`).

## Gate lines

Rebuilt `.so` reproduces the certified-exact-decoder report on known tables: `T4/clean/P14 p*=8.963259e-01` (the certified-exact-decoder report real_gate.log: 8.963259e-01) and the adjacent-domain table `base960h a1WcrN p*=4.818045e-09` (the certified-exact-decoder report real_1.jsonl: 4.818e-09).

Toolkit self-gates (from `run_atcindom.log`):
```
GATE ctc_forward vs brute force: 1361 labellings, worst rel err 4.17e-16 -> PASS
GATE prefix beam vs brute force: 300 instances, 0 wrong argmax, worst score err 3.33e-16 -> PASS
```
Pure-Python reference decoder (`../code/certified-exact-decoder/bounds.py::decode_exact_backward`, unmodified, cap 1e7) vs the C port on the two smallest in-domain tables (`gate_a4.log`); identical p\* to 1e-12 rel and identical mode required:
```
GATE stdlib vs C on atcindom__atc_uwb__uwb-atcc_TWR-a1WcrN_000157_000469_AT T=155 W=31: stdlib p*=8.240881e-01 exp=54 gen=3854190 sec=521.5 | C p*=8.240881e-01 exp=100 gen=3855570 sec=3.67 -> PASS
GATE stdlib vs C on atcindom__atc_uwb__uwb-atcc_TWR-a8R9jE_000700_001023_PIAT T=161 W=31: stdlib p*=5.296036e-01 exp=22 gen=723480 sec=94.2 | C p*=5.296036e-01 exp=26 gen=723600 sec=1.18 -> PASS
```
All 16 C decodes returned `status=ok` (certified, not deadline/cap), 1–33 s each.

## Summary (in-domain model; generic paired values from adjacent-domains/the certified-exact-decoder report in brackets)

| corpus | n | conf mean | frac frames < 0.9 | p\* median (range) | gate p\*<1/D | margin median (range) | margin < 1.2 | greedy = mode | beam-5 | beam-50 | beam-800 | WER mode mean (corpus) | WER greedy | ref ∈ top-2 | C dec s median (max) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UWB-ATCC in-domain | 8 | **0.976** [0.857] | 0.07 [0.42] | **4.5e-1** (6.4e-3 – 0.94) [1.0e-12 (1e-21 – 5e-9)] | **1/8** [8/8] | **5.2** (1.12 – 407) [1.02 (1.00 – 1.12)] | 2/8 [8/8] | **7/8** [0/8] | 8/8 [3/8] | 8/8 [5/8] | 8/8 [6/8] | **0.125** (0.135) [1.02] | 0.132 [1.01] | 4/8 | 13 (33) [26 (46)] |
| ATCO2-test in-domain | 8 | 0.957 | 0.13 | 2.8e-2 (1.3e-4 – 0.88) | 4/8 | 1.35 (1.03 – 16.6) | 4/8 | 5/8 | 6/8 | **8/8** | 8/8 | 0.186 (0.188) | 0.165 | 2/8 | 10 (21) |
| (the adjacent-domains report reference rows) LibriSpeech clean / TORGO control | 11 / 4 | 0.979 / 0.978 | — | ~0.1–0.7 / 0.49 | — | 29 / 4.4 | — | 10/11 / 3/4 | 11/11 / 4/4 | — / 4/4 | — | low / 0.03 | — | — | — |

### Paired table — same 8 UWB-ATCC test clips, generic `facebook/wav2vec2-base-960h` (adjacent-domains/the certified-exact-decoder report) vs in-domain `Jzuluaga/...-uwb-atcc-and-atcosim` (the atc-in-domain report)

| clip | T | model | D | conf mean / frac<0.9 | certified p\* | 1/D | gate p\*<1/D | p₂ | margin p\*/p₂ | greedy/p\* (=mode) | b5 | b50 | b800 | p(ref)/p\* | WER mode | WER greedy | C dec s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 34720N_002001_002559_AT | 278 | generic | 64 | 0.844 / 0.44 | 5.0e-20 | 1.6e-02 | Y | 5.0e-20 | 1.00 | 0.53 (n) | 0.68 | 1.00 | 1.00 | — | 1.10 | 1.10 | 30 |
| | | **in-domain** | 56 | 0.969 / 0.10 | 2.1e-02 | 1.8e-02 | n | 1.5e-02 | 1.35 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 5.7e-10 | 0.30 | 0.30 | 16 |
| a1WcrN_000157_000469_AT | 155 | generic | 49 | 0.857 / 0.41 | 4.8e-09 | 2.0e-02 | Y | 4.8e-09 | 1.01 | 0.53 (n) | 0.89 | 0.89 | 1.00 | — | 0.64 | 0.55 | 5 |
| | | **in-domain** | 54 | 0.977 / 0.07 | 8.2e-01 | 1.9e-02 | n | 8.7e-02 | 9.46 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 4 |
| a3o8f0_000000_000352_AT | 175 | generic | 63 | 0.830 / 0.50 | 2.1e-12 | 1.6e-02 | Y | 1.9e-12 | 1.08 | 0.29 (n) | 1.00 | 1.00 | 1.00 | — | 0.80 | 0.80 | 8 |
| | | **in-domain** | 60 | 0.977 / 0.06 | 3.8e-01 | 1.7e-02 | n | 3.3e-01 | 1.16 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 6.8e-04 | 0.10 | 0.10 | 5 |
| A5lZHJ_000000_000613_AT | 306 | generic | 88 | 0.866 / 0.42 | 4.4e-18 | 1.1e-02 | Y | 4.4e-18 | 1.00 | 0.74 (n) | 0.87 | 0.87 | 0.87 | — | 1.00 | 0.94 | 46 |
| | | **in-domain** | 93 | 0.989 / 0.03 | 7.8e-01 | 1.1e-02 | n | 3.5e-02 | 22.12 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 4.5e-02 | 0.06 | 0.06 | 33 |
| A5lZHJ_002805_003388_PIAT | 291 | generic | 87 | 0.865 / 0.39 | 1.1e-17 | 1.1e-02 | Y | 9.8e-18 | 1.12 | 0.41 (n) | 0.78 | 1.00 | 1.00 | — | 0.74 | 0.74 | 44 |
| | | **in-domain** | 91 | 0.964 / 0.11 | 7.3e-02 | 1.1e-02 | n | 3.9e-02 | 1.86 | 0.54 (n) | 1.00 | 1.00 | 1.00 | 6.7e-43 | 0.21 | 0.26 | 28 |
| a8R9jE_000144_000596_AT | 225 | generic | 77 | 0.884 / 0.36 | 7.3e-10 | 1.3e-02 | Y | 6.5e-10 | 1.12 | 0.67 (n) | 1.00 | 1.00 | 1.00 | — | 0.83 | 0.83 | 21 |
| | | **in-domain** | 66 | 0.985 / 0.04 | 9.4e-01 | 1.5e-02 | n | 2.3e-03 | 406.64 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 11 |
| a8R9jE_000700_001023_PIAT | 161 | generic | 46 | 0.838 / 0.52 | 8.9e-12 | 2.2e-02 | Y | 8.6e-12 | 1.04 | 0.62 (n) | 0.97 | 0.97 | 1.00 | — | 2.20 | 2.20 | 4 |
| | | **in-domain** | 22 | 0.980 / 0.04 | 5.3e-01 | 4.5e-02 | n | 6.3e-02 | 8.47 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 1 |
| A64ueL_000128_000777_PI | 324 | generic | 57 | 0.874 / 0.33 | 1.1e-18 | 1.8e-02 | Y | 1.1e-18 | 1.01 | 0.12 (n) | 0.31 | 0.31 | 1.00 | — | 0.83 | 0.92 | 31 |
| | | **in-domain** | 62 | 0.971 / 0.09 | 6.4e-03 | 1.6e-02 | Y | 5.7e-03 | 1.12 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 2.4e-18 | 0.33 | 0.33 | 22 |

### ATCO2 test-set-1h — in-domain model only (8 clips; the generic model was not run on ATCO2 in the adjacent-domains report)

| clip | T | D | conf mean / frac<0.9 | certified p\* | 1/D | gate | p₂ | margin | greedy/p\* (=mode) | b5 | b50 | b800 | p(ref)/p\* | WER mode | WER greedy | C dec s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LKTB_BRNO_Tower_119_605MHz_028_185619-A__000000-000536 | 267 | 85 | 0.969 / 0.09 | 2.3e-01 | 1.2e-02 | n | 1.4e-01 | 1.67 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 21 |
| LKTB_BRNO_Approach-Radar_127_350MHz_026_111634-A__000000-000395 | 197 | 67 | 0.938 / 0.18 | 2.0e-04 | 1.5e-02 | Y | 1.9e-04 | 1.04 | 0.37 (n) | 0.65 | 1.00 | 1.00 | 5.4e-05 | 0.31 | 0.23 | 8 |
| LKPR_RUZYNE_Radar_120_520MHz_028_151125-A__000000-000444 | 221 | 73 | 0.978 / 0.06 | 8.8e-01 | 1.4e-02 | n | 5.3e-02 | 16.55 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 12 |
| LKPR_RUZYNE_Radar_120_520MHz_028_151125-G__000444-000934 | 244 | 66 | 0.966 / 0.11 | 8.8e-03 | 1.5e-02 | Y | 8.0e-03 | 1.10 | 0.91 (n) | 0.91 | 1.00 | 1.00 | 2.6e-07 | 0.18 | 0.09 | 13 |
| LKPR_RUZYNE_Radar_120_520MHz_026_145941-G__000000-000349 | 174 | 50 | 0.938 / 0.18 | 1.3e-04 | 2.0e-02 | Y | 1.3e-04 | 1.03 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 7.1e-09 | 0.22 | 0.22 | 4 |
| LKPR_RUZYNE_Tower_134_560MHz_025_144043-B__000000-000332 | 165 | 46 | 0.940 / 0.18 | 8.1e-03 | 2.2e-02 | Y | 7.3e-03 | 1.10 | 0.70 (n) | 1.00 | 1.00 | 1.00 | 6.2e-03 | 0.22 | 0.22 | 4 |
| LKPR_RUZYNE_Tower_134_560MHz_025_144043-A__000334-000742 | 203 | 60 | 0.966 / 0.11 | 4.7e-02 | 1.7e-02 | n | 2.8e-02 | 1.69 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 1.2e-01 | 0.18 | 0.18 | 9 |
| LKPR_RUZYNE_Tower_134_560MHz_025_144043-B__000744-001212 | 233 | 89 | 0.963 / 0.11 | 1.7e-01 | 1.1e-02 | n | 1.0e-01 | 1.60 | 1.00 (Y) | 1.00 | 1.00 | 1.00 | 6.9e-49 | 0.38 | 0.38 | 15 |

### Transcripts (in-domain model): reference / certified mode / certified runner-up

**atc_uwb**

- `34720N_002001_002559_AT` margin 1.35, WER(mode) 0.30
  - ref :[reference transcript not redistributed]
  - mode: clearance to otel av via one hotel departure squawk alfa
  - 2nd : clearance to tel av via one hotel departure squawk alfa
- `a1WcrN_000157_000469_AT` margin 9.46, WER(mode) 0.00
  - ref :[reference transcript not redistributed]
  - mode: nor shuttle one five one five line up runway three one
  - 2nd : nor shuttele one five one five line up runway three one
- `a3o8f0_000000_000352_AT` margin 1.16, WER(mode) 0.10
  - ref :[reference transcript not redistributed]
  - mode: opera jet three zero zero just for confirmation vo one hotel
  - 2nd : opera jet three zero zero just for confirmation v one hotel
- `A5lZHJ_000000_000613_AT` margin 22.12, WER(mode) 0.06
  - ref :[reference transcript not redistributed]
  - mode: csa three seven alfa runway three one cleared for takeoff wind one six zro degrees five knots
  - 2nd : csa three seven alfa runway three one cleared for takeoff wind one six zero degrees five knots
- `A5lZHJ_002805_003388_PIAT` margin 1.86, WER(mode) 0.21
  - ref :[reference transcript not redistributed]
  - mode: ruzyne austrian seven zero six papa on lima austrian seven zero six papa tower good morning
  - 2nd : ruzyn austrian seven zero six papa on lima austrian seven zero six papa tower good morning
  - grdy: ruzyn austrian seven zero six papa on lima austrian seven zero six papa tower good morning
- `a8R9jE_000144_000596_AT` margin 406.64, WER(mode) 0.00
  - ref :[reference transcript not redistributed]
  - mode: csa seven three one contact ruzyne ground one two one decimal nine
  - 2nd : csa seven three one contact ruzyne ground one two one decial nine
- `a8R9jE_000700_001023_PIAT` margin 8.47, WER(mode) 0.00
  - ref :[reference transcript not redistributed]
  - mode: one nine csa seven one
  - 2nd : one nine csa seven  one
- `A64ueL_000128_000777_PI` margin 1.12, WER(mode) 0.33
  - ref :[reference transcript not redistributed]
  - mode: ruzyne tower sky travel one one zero two stand die due to alfa
  - 2nd : ruzyne tower sky travel one one zero two tand die due to alfa
**atc_atco2**

- `LKTB_BRNO_Tower_119_605MHz_028_185619-A__000000-000536` margin 1.67, WER(mode) 0.00
  - ref :[reference transcript not redistributed]
  - mode: oscar kilo foxtrot alfa oscar taxi to holding point runway two seven via alfa charlie
  - 2nd : oscar kilo foxtrot alf oscar taxi to holding point runway two seven via alfa charlie
- `LKTB_BRNO_Approach-Radar_127_350MHz_026_111634-A__000000-000395` margin 1.04, WER(mode) 0.31
  - ref :[reference transcript not redistributed]
  - mode: kilo echo lima alfa com irm froceeding to tango bravo four zero two
  - 2nd : kilo echo lima alfa com orm froceeding to tango bravo four zero two
  - grdy: kilo echo lima alfa comim froceeding to tango bravo four zero two
- `LKPR_RUZYNE_Radar_120_520MHz_028_151125-A__000000-000444` margin 16.55, WER(mode) 0.00
  - ref :[reference transcript not redistributed]
  - mode: csa one delta zulu descend flight level one hundred no speed restrictions
  - 2nd : csa one delta zulu descend flight level one hundred no speed restriction
- `LKPR_RUZYNE_Radar_120_520MHz_028_151125-G__000444-000934` margin 1.10, WER(mode) 0.18
  - ref :[reference transcript not redistributed]
  - mode: descending flight level one on eight free speed csa one delta zulu
  - 2nd : descending flight level one oneight free speed csa one delta zulu
  - grdy: descending flight level one oneight free speed csa one delta zulu
- `LKPR_RUZYNE_Radar_120_520MHz_026_145941-G__000000-000349` margin 1.03, WER(mode) 0.22
  - ref :[reference transcript not redistributed]
  - mode: oscar kilo kio hotel please confirm one er holding
  - 2nd : oscar kilo tio hotel please confirm one er holding
- `LKPR_RUZYNE_Tower_134_560MHz_025_144043-B__000000-000332` margin 1.10, WER(mode) 0.22
  - ref :[reference transcript not redistributed]
  - mode: ruzyne tower hello an euro ings one tango kilo
  - 2nd : ruzyne tower hello a euro ings one tango kilo
  - grdy: ruzyne tower hello  euro ings one tango kilo
- `LKPR_RUZYNE_Tower_134_560MHz_025_144043-A__000334-000742` margin 1.69, WER(mode) 0.18
  - ref :[reference transcript not redistributed]
  - mode: erowings one tango kilo ruzyne tower good afternoon go ahead
  - 2nd : ero wings one tango kilo ruzyne tower good afternoon go ahead
- `LKPR_RUZYNE_Tower_134_560MHz_025_144043-B__000744-001212` margin 1.60, WER(mode) 0.38
  - ref :[reference transcript not redistributed]
  - mode: just requested do you think there is a chance for us to get runway two four for departure
  - 2nd : just requested do you think thre is a chance for us to get runway two four for departure

## Verdict, point by point

**(a) UWB-ATCC.** The the adjacent-domains report §e prediction ("in-domain UWB-ATCC will look like LibriSpeech-clean, moot") is confirmed on all eight paired clips. Confidence 0.976 vs the clean-LibriSpeech/TORGO-control 0.978–0.979; margin median 5.2 (TORGO control 4.4); greedy finds the certified mode 7/8 (clean 10/11); beam-5 finds it 8/8. The single gate pass (`A64ueL`, p\* = 6.4e-3 vs 1/D = 1.6e-2, margin 1.12) is the clip where the model mishears "standing two two" as "stand die due to" — a genuine acoustic confusion, and its ambiguity is again a one-character spelling variant ("stand" vs "tand"). The 8/8 gate pass, p\* ≈ 1e-20 and 0/8 greedy hits of the generic run were entirely the generic model being lost on accented VHF audio, not a property of ATC speech.

**(b) ATCO2-test.** Half in the regime by the numbers (4/8 gate, p\* down to 1.3e-4, margins 1.03–1.10, greedy ≠ mode 3/8, beam-5 ≠ mode 2/8 — beam-5 returned labellings at 0.65× and 0.91× p\*), which is what [Z22]'s 10–15 dB SNR and 21–23 % in-domain WER predicted. But: (i) beam-50 returns the certified mode on 8/8, so no exact decoder is needed to *find* it; (ii) the mode has WER 0.19 — a usable transcript, not the WER ≈ 1 garbage of the adjacent-domains report; (iii) on 2 of the 3 clips where greedy ≠ mode, greedy is *closer* to the reference than the certified mode (0.23 vs 0.31; 0.09 vs 0.18) — the exact argmax is, on this evidence, not even a better transcript than greedy.

**(c) Is the certified mode correct?** UWB-ATCC 3/8 exactly right, 5/8 with 1–3 word errors; ATCO2 2/8 exactly right. Aggregate WER 0.135 / 0.188 is consistent with the model card (17.5 %) and [Z22] Table 2 (ATCO2-test 23.3 % greedy for the 132 h fine-tune), so the clips are not unrepresentative. The correct transcript is in the certified top-2 on 6/16; when it is not, the model assigns it p(ref)/p\* from 1.2e-1 down to 6.9e-49 — the truth is not "narrowly missed", it is off the model's support (partly reference-style: ATCO2 references keep disfluencies such as "do you think there any chance").

**(d) What the margin actually certifies.** In 24/24 certified decodes across both models the runner-up is a one-character edit of the mode (`otel av`/`tel av`, `zro`/`zero`, `kio`/`tio`, `com irm`/`com orm`, `an`/`a`, `on eight`/`oneight`, `erowings`/`ero wings`, `restrictions`/`restriction`). That is the structure of CTC posteriors — mass spreads over spelling variants of one acoustic hypothesis — and it is exactly what the checkpoint's shipped 4-gram LM (card: 17.5 → 14.3 % WER) is there to collapse. A margin of 1.03 at p\* = 1.3e-4 therefore says "there are thousands of near-identical spellings of this hypothesis", not "the controller may have said something else". A readback verifier wants the probability that the utterance *reads as* "one hundred" versus "one one eight" — the mass of a word-class, i.e. a CTC forward over a small lattice of alternatives (the quantum-mbr-reframing report MBR / hypothesis-class framing), which is polynomial, needs no argmax, and would have flagged both safety-relevant misreads here (the correct class has 1e-7–1e-9 of the mode's mass — a certifiable *refusal*, not a certifiable ambiguity between two readings).

## Implications for the "certificate of ambiguity for ATC readback verification" idea

1. **Drop the exact-argmax certificate as the product.** With any in-domain model the argmax is found by beam-50 (16/16 here) and the top-two margin certifies spelling, not meaning. The quantity that would carry a safety argument is the certified posterior mass of a *semantic class* (digit string, callsign, clearance), not p\* and p₂ of two character strings.
2. **The regime is a property of model–domain mismatch, not of ATC.** The the adjacent-domains report headline ("the low-confidence regime is the default for a deployed CTC model on ATC radio") should be re-read as "…for a *generic* model on ATC radio"; with the field's own checkpoint the UWB-ATCC numbers are indistinguishable from clean read speech. ATCO2 keeps a flatter posterior (p\* 1e-4–1e-2 on half the clips) but that flatness is spelling entropy an LM removes.
3. **If certification is still wanted, the right object is word-class mass with an LM in the loop**, which is a classical sum, seconds of CPU, and needs neither the exact decoder nor anything quantum. The exact decoder's residual role is what the certified-exact-decoder report already showed: a validation instrument (it proved here that beam-50 is exact on all 16 in-domain tables, and that beam-5 is not on 2 ATCO2 clips).
4. **Evidence limits.** n = 8 per corpus, first-8 selection rather than random; UWB-ATCC test clips share the fine-tuning corpus with the checkpoint (different partition per the model card, but same channels/speakers population) — the fairer "in-domain but unseen" test is the ATCO2 column; LiveATC-test (5–15 dB, 27–31 % WER in [Z22]) was not run and is the one remaining corpus where the gate could fully survive — but on the ATCO2 evidence the consequence (beam misses the mode, mode is garbage) would still not follow.

## Citations

- [Z22] J. Zuluaga-Gomez, A. Prasad, I. Nigmatulina, S. Sarfjoo, P. Motlicek, M. Kleinert, H. Helmke, O. Ohneiser, Q. Zhan, "How Does Pre-trained Wav2Vec 2.0 Perform on Domain Shifted ASR? An Extensive Benchmark on Air Traffic Control Communications", arXiv:2203.16822 (SLT 2022). Body-read in the adjacent-domains report (`adjacent-domains/zuluaga.txt`); used here for Table 1 SNR bands (UWB-ATCC ≥ 20 dB, ATCO2-test 10–15 dB, LiveATC 5–15 dB) and Table 2 WERs (ATCO2-test 23.3 / 21.2 % greedy / +LM; LiveATC 31.1 / 27.2 %). Model card for the checkpoint (read this run): UWB-ATCC test WER 17.48 % (14.26 % +LM), ATCOSIM 1.85 %, fine-tuned on UWB-ATCC + ATCOSIM train partitions; code https://github.com/idiap/w2v2-air-traffic.
- Datasets: `Jzuluaga/uwb_atcc` (test split, rows 2–40 per the adjacent-domains report selection) and `Jzuluaga/atco2_corpus_1h` (test split, 871 rows; the public ATCO2-ASR 1 h test set) via the HF datasets-server row API.
- Prior lane artefacts relied on: `adjacent-domains.md` (§c generic numbers, §e prediction), `../code/certified-exact-decoder/` (exactbwd.c, bounds.py, real_*.jsonl, real_gate.log).

## Files

`atc-in-domain/measure_a4.py`, `atc-in-domain/select_atco2.py`, `atc-in-domain/analyse.py`, `atc-in-domain/gate_a4.py`, `atc-in-domain/cdec.py`, `atc-in-domain/exactbwd.c` (copy) + `atc-in-domain/libexactbwd.so`, `atc-in-domain/manifest.json`, `atc-in-domain/atco2_rows.json`, `atc-in-domain/samples/*.wav` (8 ATCO2), `atc-in-domain/posteriors/atcindom__*.npy` (16 × T×31 float64, native column order), `atc-in-domain/results__atcindom.json`, `atc-in-domain/results__atcindom_annot.json`, `atc-in-domain/generic_paired.json`, `atc-in-domain/tables.md`, logs `atc-in-domain/run_atcindom.log`, `atc-in-domain/gate_a4.log`, `atc-in-domain/download.log`.

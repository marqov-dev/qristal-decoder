# Hard ATC audio (5–15 dB, LiveATC-sourced) with the in-domain model: does beam search still find the certified mode?

Date: 2026-09-18. One measurement question. Extends the atc-in-domain report (UWB-ATCC ≥ 20 dB + 8 ATCO2-test clips). All artefacts under `../code/hard-atc-audio/` (all other directories untouched; certctc was *copied* into `hard-atc-audio/certctc/` and its C core compiled there).

## Headline verdict

**Below 15 dB, beam search stops finding the certified mode — but the certified mode stops being worth finding.** On 24 real ATCO2-test clips at 4.4–14.0 dB (estimated SNR, method below) with `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim`, beam-50 returns the exact mode on **14/24** (the atc-in-domain report at ≥ 15 dB: 16/16), beam-800 on **17/24**, beam-5 on 9/24, greedy on 2/24; the beam-50 misses return labellings at 0.49–0.94 × p\* and the beam-800 misses at 0.85–0.95 × p\*. By band: 10–15 dB beam-50 4/8, beam-800 6/8; 5–10 dB 8/11, 9/11; < 5 dB 2/5, 2/5. The 16 synthetic VHF-degraded clips (band-limit + noise + clipping, nominal 10 / 5 dB) reproduce the same picture: beam-50 6/8 and 5/8, beam-800 7/8 and 7/8.

**The certified quantities below 15 dB are: p\* 1e-5 … 1e-16 (median 9e-8 at 10–15 dB, 9e-9 at 5–10, 2e-13 below 5), margin 1.01–1.12 on 24/24 clips (median 1.04–1.05), frame confidence 0.81–0.97 (mean 0.90, 28–40 % of frames < 0.9), gate p\* < 1/D on 23/24.** The exact decoder itself was never the bottleneck: all 56 decodes certified (`status=ok`, `verify()` passes, max rel err 1.9e-15) in 0.3–45 s (median 8 s), generations 0.015–0.23 · T²W², final expansions ≤ 17.5 · D; no decode approached the 10-minute budget.

**The exact mode is not a better transcript than greedy or beam there.** WER(mode) vs WER(greedy) on the 24 real clips below 15 dB: mode better on 4, equal on 18, worse on 2 — and the 4 "wins" are 0.64 vs 0.73, 0.92 vs 1.00, 0.61 vs 0.72, 0.64 vs 0.73. WER(mode) vs WER(beam-50): mode better on 2, equal on 22. Corpus WER of the certified mode: 0.16 (≥ 15 dB) → 0.38 (10–15) → 0.72 (5–10) → 0.67 (< 5). Below 10 dB the exact argmax is a *shorter* string than the reference (mean 6.0 words vs 11.6; 6/16 clips have WER ≥ 0.9, e.g. mode `eoo klopa a` for "vacate via whiskey cross two six and vacate via the airclub oscar kilo papa india") — the classic CTC deletion bias of the exact argmax on flat posteriors — and the reference is never in the certified top-2 (0/24; p(ref)/p\* between 8.6e-2 and 5e-149, median ≈ 1e-40). The exact decoder certifies which garbage string carries the most posterior mass.

**The one-character-edit pattern persists without exception in kind.** 51/56 runner-ups differ from the mode by exactly one symbol; the other 5 (1 real, 4 synthetic, all ≤ 6 dB or synthetic) differ by two symbols that are still a single spelling variant (`bird` / `bird e`, `fa i` / `fa`). Combined with the atc-in-domain and adjacent-domains reports that is 80/80 certified decodes where p\*/p₂ is a spelling margin.

## Data provenance

### (a) Real audio — ATCO2-ASR public 1 h test set, lowest-SNR clips

- Source: `Jzuluaga/atco2_corpus_1h`, split `test` (871 rows; the ATCO2-test-set-1h released at Interspeech 2021, LiveATC/community-receiver VHF recordings from LKPR, LKTB, LSGS, LSZB, LSZH, LZIB, YSSY [Z22 §3.2; ATCO2 corpus paper Table 2 lists it as "SNR ≤ 15 dB, public"]). Row metadata for all 871 rows via the datasets-server `/rows` API (9 pages, `hard-atc-audio/rows/atco2_test_*.json`); audio fetched clip-by-clip from the signed `audio.wav` URLs. Licence: ATCO2-ASRdataset-v1_beta End-User Data Agreement (card); nothing is redistributed here.
- Candidates: the atc-in-domain/adjacent-domains rule (3 s ≤ duration ≤ 8 s, ≥ 5 words) minus the 8 clips already run in the atc-in-domain report → **501 clips, 77.4 MB** (`hard-atc-audio/samples/atco2_all/`, `atco2_candidates.json`). The original ATCO2 tarball (132 MB, contains per-utterance SNR in its XML) was *not* downloaded — that plus the 77 MB would exceed the ~200 MB budget, and the SNR is estimated from the waveform as instructed.
- Selection: the **16 lowest** by the combined SNR estimate (4.4–8.2 dB; 7 × YSSY Sydney, 5 × LSGS Sion, LKTB, LSZB, LSZH, LZIB) → set `atc_atco2_hard`; plus **8 sampled (numpy seed 0) from the 10–15 dB band** (129 candidates there) → set `atc_atco2_mid`, so the 10–15 band is populated with real audio; plus the **16 atc-in-domain clips re-run** through this pipeline (8 UWB-ATCC test at 21–35 dB, 8 ATCO2 at 20–47 dB; identical p\*, margins and modes to the atc-in-domain report, e.g. `a1WcrN` p\* = 8.240881e-01, `A64ueL` p\* = 6.4e-3) → the ≥ 15 dB band.

### (b) Other LiveATC-derived ASR sets on the Hub — none usable under "openly licensed"

Hub search (`/api/datasets?search=` LiveATC, "ATC speech", ATCOSIM, ATCO2, ATC-ASR, "air traffic", atc, "aviation speech"; ~150 hits, this report's log): `nyuuzyou/liveatc` (21 172 raw LiveATC MP3s, **no transcripts**, LiveATC ToU non-commercial/no redistribution); `k3rb3l/atc-asr-eval` (44 human-verified LiveATC clips, 2–5 s, the closest match — but `license: other`, card says "Private — not for redistribution"); `SAadettin-BERber/liveATC_merged` (827 rows, no card, no licence; a sibling set is AssemblyAI-transcribed, i.e. pseudo-labels); `adityarra07/live_ATC_*` (audio only); `jacktol/ATC-ASR-Dataset` (a re-cut of UWB-ATCC + the same ATCO2 1 h set); `jlvdoorn/atco2-asr`, `rodoggx/ATCO2-ASR-1h`, `luigisaetta/atco2*` (the same ATCO2 1 h set, re-packaged). So **no openly licensed LiveATC-derived set with human references exists on the Hub beyond ATCO2-test itself**; the "8 more" were not taken, and the fallback below was used to reach the 10 and 5 dB points on controlled material.

### (c) Synthetic VHF degradation — clearly synthetic

The 8 atc-in-domain ATCO2 clips (20–47 dB) were degraded (`build_manifest.py::degrade`): band-limit 300–3400 Hz (torchaudio `highpass_biquad` 300 Hz + `lowpass_biquad` 3400 Hz, Q = 0.707, each applied twice = 4th order); additive white Gaussian noise passed through the same band-limit and scaled so that (mean power of speech-active 20 ms frames of the band-limited clip) / (noise power) = nominal SNR (speech-active = frames with power > 10 × the mean of the quietest 20 % of frames); then mild hard clipping at 0.7 × the peak of the noisy signal. The clip's own channel noise counts as "signal", so effective SNR is below nominal. Sets `atc_atco2_synth10` (nominal 10 dB) and `atc_atco2_synth5` (nominal 5 dB), 16 files in `hard-atc-audio/samples/synth/`.

### SNR estimation method

Two waveform-only estimators (`../code/hard-atc-audio/snr.py`), no reference signal:

1. **WADA-SNR** (Kim & Stern, Interspeech 2008, "Robust signal-to-noise ratio estimation based on waveform amplitude distribution analysis"; G-table from the LabROSA `snreval` port). This is the estimator the ATCO2 project itself used for its SNR filtering and its per-airport Table 3 (ATCO2 corpus paper §"Signal-to-noise ratio filtering": "We use WADA-SNR … to estimate the SNR").
2. **Energy-VAD SNR**: 20 ms frames; noise floor N = mean power of the quietest 20 % of frames; speech S = mean power of frames with power > 10 N; SNR = 10 log10((S − N)/N).

**Combined estimate = mean of the two in dB; when WADA saturates at its table floor/ceiling (−20 or 100 dB — the Gamma/Gaussian amplitude model breaks on hard-limited AGC'd LiveATC audio; 10/501 clips) the VAD value alone is used and the clip is flagged (\*).** Selection and band assignment use the combined estimate; both raw values are reported per clip.

Checks on the estimator: (i) correlation WADA–VAD over the 501 candidates 0.71; (ii) **calibration on the synthetic files, where the added noise is known: nominal 10 dB → combined 9.4–11.2 dB; nominal 5 dB → 3.3–6.0 dB**; (iii) the site ranking agrees with the ATCO2 corpus paper's WADA-SNR Table 3 (mean/std per airport: YSSY 3.1/7.0, LKTB 4.1/15.7, LZIB 5.4/8.7, LSZH 7.8/7.7, LSGS 10.0/8.0, LKPR 14.2/8.2, LSZB 15.4/10.7 dB) — our per-site medians of the 501 candidates order LSGS 10.5 < LSZH 18.5 < YSSY 18.9 < LKTB 22.2 < LKPR 22.7 < LZIB 24.3 < LSZB 28.0 (WADA), and the 16 hardest clips come from YSSY/LSGS/LKTB/LSZH/LZIB. Absolute values are not comparable to the paper's (theirs run after a tight SAD; ours on the whole segment). Distribution of the 501 candidates (combined): median 19.7 dB, 158 < 15 dB, 29 < 10 dB, 5 < 5 dB — consistent with "ATCO2-test ≤ 15 dB / 10–15 dB" [ATCO2 corpus Table 2; Z22 Table 1] being a statement about the bulk, with a hard tail. The 16 atc-in-domain clips sit at 20–47 dB (the atc-in-domain report's first-8 selection was, by this measure, the *easy* end of ATCO2-test).

## Setup (as the atc-in-domain report unless stated)

- Model: `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim` from the HF cache (snapshot `abeadc1d…`), no LM; W = 31, blank = `[PAD]` = 28, `|` = 0. `adjacent-domains/.venv` (torch 2.14 CPU, transformers 5.17). Float64 softmax posteriors in native column order, `hard-atc-audio/posteriors/r3__<set>__<id>.npy` (56 tables, T = 149–324).
- Certified decoder: `certctc` (`decode(table, blank=28, backend='c', time_limit=600)`, `verify()`), copied to `hard-atc-audio/certctc/` and compiled there (`cc -O2 -ffp-contract=off`); it permutes the blank column internally. Greedy / beam-k (5, 50, 800; k = 2) from the toolkit `ctc.py` on the column-swapped table (0 ↔ 28) as in the atc-in-domain report; p of every labelling re-computed with `ctc_forward`. WER = word-level Levenshtein on lowercase whitespace-split text. Toolkit self-gates passed (`run_r3.log`: `ctc_forward vs brute force: 1361 labellings, worst rel err 4.17e-16 -> PASS`; `prefix beam vs brute force: 300 instances, 0 wrong argmax, worst score err 3.33e-16 -> PASS`).
- Scripts: `fetch_atco2.py`, `snr.py`, `select_r3.py` + `reselect.py` (logs `select_r3.log`, `reselect.log`), `build_manifest.py` (manifest + synthetic files, `build_manifest.log`), `measure_r3.py` (`run_r3.log`, `results__r3.json`), `gate_r3.py` (`gate_r3.log`), `analyse_r3.py` (`tables_r3.md`). Wall-clock: 56 clips incl. inference, certified decode and three beams ≈ 35 min.

## Gate lines

Pure-Python vs C backend of `certctc` on the two smallest tables new in this report (identical p\*, p₂, mode, expansion and generation counts required; `gate_r3.log`):
```
GATE python vs C on r3__atc_atco2_hard__atco2_test-set-1h_LSGS_SION_Tower_118_3MHz_20210502_065945-D__000012-000312 T=149 W=31 blank=28: python p*=2.653967e-05 p2=2.585245e-05 exp=29 gen=309810 sec=15.7 | C p*=2.653967e-05 p2=2.585245e-05 exp=29 gen=309810 sec=0.32 -> PASS
GATE python vs C on r3__atc_atco2_hard__atco2_test-set-1h_LSGS_SION_Tower_118_3MHz_20210503_082715-D__000606-000907 T=150 W=31 blank=28: python p*=6.222409e-10 p2=5.646963e-10 exp=35 gen=1989390 sec=96.7 | C p*=6.222409e-10 p2=5.646963e-10 exp=35 gen=1989390 sec=1.73 -> PASS
```
`verify()` (independent forward recursion) passes on all 56 certificates, max rel err 1.9e-15. All 56 decodes `status=ok` — **no decode exceeded the 10-minute budget** (max 44.6 s, T = 321, D = 116, 1.8e7 generations); hard audio made the beam wrong, not the exact search slow.

### Per SNR band, REAL audio only (combined WADA/VAD estimate)

| set | n | SNR median (range) | conf mean / frac<0.9 | p\* median (range) | gate p\*<1/D | margin median (range) | margin<1.2 | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | WER mode mean (corpus) | WER greedy mean (corpus) | WER beam-50 mean | runner-up 1-char edit | ref in top-2 | C dec s median (max) | budget-exceeded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| real >=15 dB | 16 | 28.8 (20.4–47.3) | 0.967 / 0.10 | 1.2e-01 (1.3e-04–9.4e-01) | 5/16 | 1.64 (1.03–406.6) | 6/16 | 12/16 | 14/16 | 16/16 | 16/16 | 0.156 (0.161) | 0.149 (0.156) | 0.156 | 16/16 | 6/16 | 11.3 (32) | 0 |
| real 10-15 dB | 8 | 11.5 (10.2–14.0) | 0.907 / 0.28 | 9.0e-08 (5.4e-15–3.7e-02) | 7/8 | 1.05 (1.02–1.1) | 8/8 | 1/8 | 4/8 | 4/8 | 6/8 | 0.363 (0.378) | 0.355 (0.370) | 0.355 | 8/8 | 1/8 | 10.5 (45) | 0 |
| real 5-10 dB | 11 | 6.3 (5.1–8.2) | 0.904 / 0.29 | 8.9e-09 (5.6e-16–6.7e-05) | 11/11 | 1.04 (1.01–1.1) | 11/11 | 1/11 | 3/11 | 8/11 | 9/11 | 0.681 (0.719) | 0.692 (0.734) | 0.681 | 10/11 | 0/11 | 5.9 (21) | 0 |
| real <5 dB | 5 | 4.9 (4.4–4.9) | 0.861 / 0.40 | 1.7e-13 (1.6e-16–2.9e-08) | 5/5 | 1.05 (1.01–1.1) | 5/5 | 0/5 | 2/5 | 2/5 | 2/5 | 0.724 (0.672) | 0.759 (0.705) | 0.759 | 5/5 | 0/5 | 4.6 (38) | 0 |

### Per SNR band, SYNTHETIC VHF degradation of the 8 atc-in-domain ATCO2 clips

| set | n | SNR median (range) | conf mean / frac<0.9 | p\* median (range) | gate p\*<1/D | margin median (range) | margin<1.2 | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | WER mode mean (corpus) | WER greedy mean (corpus) | WER beam-50 mean | runner-up 1-char edit | ref in top-2 | C dec s median (max) | budget-exceeded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| synthetic 10-15 dB | 7 | 10.5 (10.1–11.2) | 0.929 / 0.22 | 1.0e-04 (1.9e-11–7.1e-03) | 7/7 | 1.04 (1.01–1.5) | 6/7 | 2/7 | 4/7 | 5/7 | 6/7 | 0.379 (0.386) | 0.414 (0.422) | 0.379 | 6/7 | 0/7 | 10.1 (17) | 0 |
| synthetic 5-10 dB | 7 | 5.2 (5.1–9.4) | 0.922 / 0.22 | 4.3e-08 (3.9e-12–2.9e-02) | 6/7 | 1.04 (1.00–1.3) | 5/7 | 2/7 | 3/7 | 5/7 | 6/7 | 0.751 (0.759) | 0.753 (0.759) | 0.751 | 6/7 | 0/7 | 7.7 (12) | 0 |
| synthetic <5 dB | 2 | 4.1 (3.3–4.8) | 0.911 / 0.27 | 1.8e-06 (6.7e-08–3.6e-06) | 2/2 | 1.11 (1.03–1.2) | 2/2 | 0/2 | 1/2 | 1/2 | 2/2 | 0.607 (0.636) | 0.662 (0.682) | 0.607 | 0/2 | 0/2 | 1.9 (2) | 0 |

### Per set

| set | n | SNR median (range) | conf mean / frac<0.9 | p\* median (range) | gate p\*<1/D | margin median (range) | margin<1.2 | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | WER mode mean (corpus) | WER greedy mean (corpus) | WER beam-50 mean | runner-up 1-char edit | ref in top-2 | C dec s median (max) | budget-exceeded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| atc_uwb | 8 | 28.8 (21.0–34.9) | 0.976 / 0.07 | 4.5e-01 (6.4e-03–9.4e-01) | 1/8 | 5.17 (1.12–406.6) | 2/8 | 7/8 | 8/8 | 8/8 | 8/8 | 0.125 (0.135) | 0.132 (0.146) | 0.125 | 8/8 | 4/8 | 12.9 (32) | 0 |
| atc_atco2 | 8 | 28.7 (20.4–47.3) | 0.957 / 0.13 | 2.8e-02 (1.3e-04–8.8e-01) | 4/8 | 1.35 (1.03–16.5) | 4/8 | 5/8 | 6/8 | 8/8 | 8/8 | 0.186 (0.188) | 0.165 (0.167) | 0.186 | 8/8 | 2/8 | 11.0 (21) | 0 |
| atc_atco2_mid | 8 | 11.5 (10.2–14.0) | 0.907 / 0.28 | 9.0e-08 (5.4e-15–3.7e-02) | 7/8 | 1.05 (1.02–1.1) | 8/8 | 1/8 | 4/8 | 4/8 | 6/8 | 0.363 (0.378) | 0.355 (0.370) | 0.355 | 8/8 | 1/8 | 10.5 (45) | 0 |
| atc_atco2_hard | 16 | 6.1 (4.4–8.2) | 0.891 / 0.32 | 9.1e-10 (1.6e-16–6.7e-05) | 16/16 | 1.04 (1.01–1.1) | 16/16 | 1/16 | 5/16 | 10/16 | 11/16 | 0.695 (0.704) | 0.713 (0.725) | 0.706 | 15/16 | 0/16 | 5.2 (38) | 0 |
| atc_atco2_synth10 | 8 | 10.4 (9.4–11.2) | 0.925 / 0.23 | 5.7e-05 (1.9e-11–7.1e-03) | 8/8 | 1.04 (1.00–1.5) | 7/8 | 3/8 | 5/8 | 6/8 | 7/8 | 0.380 (0.385) | 0.410 (0.417) | 0.380 | 7/8 | 0/8 | 8.9 (17) | 0 |
| atc_atco2_synth5 | 8 | 5.2 (3.3–6.0) | 0.923 / 0.22 | 1.8e-06 (3.9e-12–2.9e-02) | 7/8 | 1.09 (1.01–1.3) | 6/8 | 1/8 | 3/8 | 5/8 | 7/8 | 0.761 (0.781) | 0.776 (0.792) | 0.761 | 5/8 | 0/8 | 3.2 (12) | 0 |


Notes on the band tables. "gate" = p\* < 1/D. "ref in top-2" = reference word sequence equals the mode or the runner-up. The ≥ 15 dB row is the 16 atc-in-domain clips re-decoded (its per-clip values equal the atc-in-domain report's). The synthetic < 5 dB row has n = 2 (two nominal-5 dB files measured at 3.3 and 4.8 dB); the synthetic 5–10 row includes one nominal-10 dB file measured at 9.4 dB.

### Where the beams miss (real audio below 15 dB; p(beam)/p\*)

| clip (SNR) | greedy | beam-5 | beam-50 | beam-800 | WER mode / greedy / b50 |
|---|---|---|---|---|---|
| LSGS Ground 20210504_152004-A (10.4) | 0.47 | 0.73 | **0.90** | 1.00 | 0.47 / 0.41 / 0.41 |
| LSZH Tower 20210412_155616-B (11.4) | 0.40 | 0.60 | **0.61** | **0.85** | 0.56 / 0.56 / 0.56 |
| LSGS Ground 20210502_065520-A (11.6) | 0.82 | 1.00 | 1.00 | **0.95** | 0.23 / 0.23 / 0.23 |
| LSGS Ground 20210503_151946-A (12.7) | 0.92 | 0.92 | **0.92** | 1.00 | 0.45 / 0.45 / 0.45 |
| LSGS Ground 20210502_152026-A (13.0) | 0.52 | 0.79 | **0.94** | 1.00 | 0.41 / 0.41 / 0.41 |
| YSSY Tower 20210503_083640-A (4.4) | 0.27 | 0.27 | **0.82** | **0.87** | 0.64 / 0.73 / 0.73 |
| YSSY Tower 20210501_014446-A (4.7) | 0.21 | 0.42 | **0.80** | **0.86** | 0.92 / 1.00 / 1.00 |
| LSGS Ground 20210503_140302-B (4.9) | 0.23 | 0.60 | **0.60** | **0.93** | 1.00 / 1.00 / 1.00 |
| YSSY Tower 20210504_213748-A (6.3) | 0.06 | 0.17 | **0.49** | **0.87** | 1.00 / 1.00 / 1.00 |
| LSGS Tower 20210503_082715-D (6.3) | 0.83 | 0.83 | **0.83** | 1.00 | 0.57 / 0.57 / 0.57 |
| LKTB Tower 20201029_102129-B (6.4) | 0.18 | 0.46 | **0.85** | **0.93** | 1.00 / 1.00 / 1.00 |

Beam-50 = mode is predicted by p\* rather than by SNR directly: over all 56 clips the beam-50 hits have median log10 p\* = −3.9 and the misses −10.9 (confidence 0.94 vs 0.89). Real audio thresholds: SNR < 15 dB beam-50 14/24; < 10 dB 10/16; < 7 dB 7/13; < 5 dB 2/5.

### Paired synthetic degradation of the 8 atc-in-domain ATCO2 clips (clean → +VHF 10 dB → +VHF 5 dB)

| clip | clean SNR / p* / margin / greedy=mode / b50=mode / WER mode | 10 dB SNR / p* / margin / greedy / b50 / WER | 5 dB SNR / p* / margin / greedy / b50 / WER |
|---|---|---|---|
| LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536 | 22.3 / 2.3e-01 / 1.67 / Y / Y / 0.00 | 10.2 / 1.9e-11 / 1.01 / n / Y / 0.40 | 5.1 / 1.3e-11 / 1.01 / n / n / 0.93 |
| LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395 | 40.1 / 2.0e-04 / 1.04 / n / Y / 0.31 | 9.4 / 4.3e-08 / 1.00 / Y / Y / 0.38 | 3.3 / 6.7e-08 / 1.03 / n / n / 0.77 |
| LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444 | 30.3 / 8.8e-01 / 16.55 / Y / Y / 0.00 | 10.7 / 7.1e-03 / 1.46 / Y / Y / 0.08 | 5.5 / 2.9e-02 / 1.30 / n / Y / 0.50 |
| LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934 | 20.4 / 8.8e-03 / 1.10 / n / Y / 0.18 | 10.1 / 1.0e-04 / 1.03 / Y / Y / 0.27 | 5.2 / 3.9e-12 / 1.02 / n / n / 0.82 |
| LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349 | 47.3 / 1.3e-04 / 1.03 / Y / Y / 0.22 | 11.2 / 9.6e-06 / 1.05 / n / Y / 0.56 | 6.0 / 2.7e-04 / 1.04 / n / Y / 0.78 |
| LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332 | 27.2 / 8.1e-03 / 1.10 / n / Y / 0.22 | 10.5 / 1.2e-04 / 1.17 / n / Y / 0.44 | 4.8 / 3.6e-06 / 1.20 / n / Y / 0.44 |
| LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742 | 33.4 / 4.7e-02 / 1.69 / Y / Y / 0.18 | 10.5 / 2.9e-03 / 1.04 / n / n / 0.27 | 5.1 / 3.7e-05 / 1.13 / Y / Y / 0.91 |
| LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212 | 26.2 / 1.7e-01 / 1.60 / Y / Y / 0.38 | 10.4 / 7.8e-10 / 1.03 / n / n / 0.62 | 5.2 / 5.8e-12 / 1.26 / n / Y / 0.94 |

Reading: p\* falls 3–10 orders of magnitude per 10 dB, margin collapses to 1.0–1.3, greedy loses the mode on 12/16 degraded files, beam-50 on 5/16, beam-800 on 2/16; WER(mode) 0.19 → 0.38 → 0.76. The paired comparison shows the mechanism is the SNR itself, not a property of the YSSY/LSGS speakers.

### Per clip

| set | clip | SNR (wada/vad) | T | D | conf / frac<0.9 | p\* | 1/D | p₂ | margin | greedy/p\* | b5/p\* | b50/p\* | b800/p\* | p(ref)/p\* | WER mode | WER greedy | WER b50 | 1-char | C dec s | gen | b800 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| atc_uwb | 34720N_002001_002559_AT | 29.4 (31/28) | 278 | 56 | 0.969 / 0.10 | 2.1e-02 | 1.8e-02 | 1.5e-02 | 1.35 | 1.00 | 1.00 | 1.00 | 1.00 | 5.7e-10 | 0.30 | 0.30 | 0.30 | Y | 15.0 | 7.5e+06 | 4.9 |
| atc_uwb | a1WcrN_000157_000469_AT | 21.0 (20/22) | 155 | 54 | 0.977 / 0.07 | 8.2e-01 | 1.9e-02 | 8.7e-02 | 9.46 | 1.00 | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 0.00 | Y | 3.6 | 3.9e+06 | 2.7 |
| atc_uwb | a3o8f0_000000_000352_AT | 25.5 (26/25) | 175 | 60 | 0.977 / 0.06 | 3.8e-01 | 1.7e-02 | 3.3e-01 | 1.16 | 1.00 | 1.00 | 1.00 | 1.00 | 6.8e-04 | 0.10 | 0.10 | 0.10 | Y | 4.9 | 4.3e+06 | 3.3 |
| atc_uwb | A5lZHJ_000000_000613_AT | 31.6 (34/30) | 306 | 93 | 0.989 / 0.03 | 7.8e-01 | 1.1e-02 | 3.5e-02 | 22.12 | 1.00 | 1.00 | 1.00 | 1.00 | 4.5e-02 | 0.06 | 0.06 | 0.06 | Y | 32.3 | 1.4e+07 | 6.2 |
| atc_uwb | A5lZHJ_002805_003388_PIAT | 34.9 (40/30) | 291 | 91 | 0.964 / 0.11 | 7.3e-02 | 1.1e-02 | 3.9e-02 | 1.86 | 0.54 | 1.00 | 1.00 | 1.00 | 6.7e-43 | 0.21 | 0.26 | 0.21 | Y | 27.9 | 1.3e+07 | 5.9 |
| atc_uwb | a8R9jE_000144_000596_AT | 24.7 (26/23) | 225 | 66 | 0.985 / 0.04 | 9.4e-01 | 1.5e-02 | 2.3e-03 | 406.64 | 1.00 | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 0.00 | Y | 10.7 | 6.0e+06 | 4.4 |
| atc_uwb | a8R9jE_000700_001023_PIAT | 32.0 (35/29) | 161 | 22 | 0.980 / 0.04 | 5.3e-01 | 4.5e-02 | 6.3e-02 | 8.47 | 1.00 | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 0.00 | Y | 1.0 | 7.2e+05 | 2.7 |
| atc_uwb | A64ueL_000128_000777_PI | 28.2 (29/28) | 324 | 62 | 0.971 / 0.09 | 6.4e-03 | 1.6e-02 | 5.7e-03 | 1.12 | 1.00 | 1.00 | 1.00 | 1.00 | 2.4e-18 | 0.33 | 0.33 | 0.33 | Y | 22.0 | 7.5e+06 | 6.4 |
| atc_atco2 | LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536 | 22.3 (25/20) | 267 | 85 | 0.969 / 0.09 | 2.3e-01 | 1.2e-02 | 1.4e-01 | 1.67 | 1.00 | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 0.00 | Y | 21.2 | 1.0e+07 | 5.4 |
| atc_atco2 | LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395 | 40.1 (60/20) | 197 | 67 | 0.938 / 0.18 | 2.0e-04 | 1.5e-02 | 1.9e-04 | 1.04 | 0.37 | 0.65 | 1.00 | 1.00 | 5.4e-05 | 0.31 | 0.23 | 0.31 | Y | 8.5 | 6.5e+06 | 3.7 |
| atc_atco2 | LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444 | 30.3 (38/22) | 221 | 73 | 0.978 / 0.06 | 8.8e-01 | 1.4e-02 | 5.3e-02 | 16.55 | 1.00 | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 0.00 | Y | 12.0 | 7.5e+06 | 5.2 |
| atc_atco2 | LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934 | 20.4 (18/22) | 244 | 66 | 0.966 / 0.11 | 8.8e-03 | 1.5e-02 | 8.0e-03 | 1.10 | 0.91 | 0.91 | 1.00 | 1.00 | 2.6e-07 | 0.18 | 0.09 | 0.18 | Y | 15.4 | 7.0e+06 | 5.8 |
| atc_atco2 | LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349 | 47.3 (73/22) | 174 | 50 | 0.938 / 0.18 | 1.3e-04 | 2.0e-02 | 1.3e-04 | 1.03 | 1.00 | 1.00 | 1.00 | 1.00 | 7.1e-09 | 0.22 | 0.22 | 0.22 | Y | 4.5 | 3.0e+06 | 3.9 |
| atc_atco2 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332 | 27.2 (100/27) | 165 | 46 | 0.940 / 0.18 | 8.1e-03 | 2.2e-02 | 7.3e-03 | 1.10 | 0.70 | 1.00 | 1.00 | 1.00 | 6.2e-03 | 0.22 | 0.22 | 0.22 | Y | 4.2 | 3.1e+06 | 3.4 |
| atc_atco2 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742 | 33.4 (35/31) | 203 | 60 | 0.966 / 0.11 | 4.7e-02 | 1.7e-02 | 2.8e-02 | 1.69 | 1.00 | 1.00 | 1.00 | 1.00 | 1.2e-01 | 0.18 | 0.18 | 0.18 | Y | 10.1 | 6.4e+06 | 5.0 |
| atc_atco2 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212 | 26.2 (27/25) | 233 | 89 | 0.963 / 0.11 | 1.7e-01 | 1.1e-02 | 1.0e-01 | 1.60 | 1.00 | 1.00 | 1.00 | 1.00 | 6.9e-49 | 0.38 | 0.38 | 0.38 | Y | 16.6 | 8.9e+06 | 5.5 |
| atc_atco2_mid | LSGS_SION_Tower_118_3MHz_20210503_152021-A__000271-000690 | 10.2 (8/12) | 209 | 50 | 0.919 / 0.23 | 1.3e-06 | 2.0e-02 | 1.2e-06 | 1.12 | 0.77 | 1.00 | 1.00 | 1.00 | 5.3e-43 | 0.53 | 0.53 | 0.53 | Y | 8.0 | 4.9e+06 | 4.2 |
| atc_atco2_mid | LSGS_SION_Ground_Control_121_7MHz_20210504_152004-A__000409-000840 | 10.4 (8/13) | 215 | 86 | 0.884 / 0.36 | 3.4e-09 | 1.2e-02 | 3.0e-09 | 1.12 | 0.47 | 0.73 | 0.90 | 1.00 | 8.9e-26 | 0.47 | 0.41 | 0.41 | Y | 13.0 | 8.5e+06 | 4.4 |
| atc_atco2_mid | LKPR_RUZYNE_Tower_134_560MHz_20201028_103443-C__000468-000839 | 10.5 (8/13) | 185 | 58 | 0.971 / 0.09 | 3.7e-02 | 1.7e-02 | 3.6e-02 | 1.04 | 1.00 | 1.00 | 1.00 | 1.00 | 1.0e+00 | 0.00 | 0.00 | 0.00 | Y | 6.3 | 5.1e+06 | 3.5 |
| atc_atco2_mid | LSZH_ZURICH_Tower_118_1MHz_20210412_155616-B__001006-001398 | 11.4 (7/16) | 195 | 65 | 0.835 / 0.55 | 5.4e-15 | 1.5e-02 | 5.4e-15 | 1.02 | 0.40 | 0.60 | 0.61 | 0.85 | 1.6e-21 | 0.56 | 0.56 | 0.56 | Y | 7.4 | 5.4e+06 | 3.9 |
| atc_atco2_mid | LSGS_SION_Ground_Control_121_7MHz_20210502_065520-A__000018-000661 | 11.6 (9/14) | 321 | 116 | 0.931 / 0.21 | 1.5e-07 | 8.6e-03 | 1.4e-07 | 1.05 | 0.82 | 1.00 | 1.00 | 0.95 | 2.0e-27 | 0.23 | 0.23 | 0.23 | Y | 44.6 | 1.8e+07 | 7.2 |
| atc_atco2_mid | LSGS_SION_Ground_Control_121_7MHz_20210503_151946-A__000012-000584 | 12.7 (11/15) | 285 | 106 | 0.932 / 0.20 | 1.9e-07 | 9.4e-03 | 1.8e-07 | 1.05 | 0.92 | 0.92 | 0.92 | 1.00 | 6.5e-71 | 0.45 | 0.45 | 0.45 | Y | 29.4 | 1.3e+07 | 6.5 |
| atc_atco2_mid | LSGS_SION_Ground_Control_121_7MHz_20210502_152026-A__000025-000608 | 13.0 (12/14) | 291 | 122 | 0.890 / 0.32 | 1.8e-11 | 8.2e-03 | 1.7e-11 | 1.06 | 0.52 | 0.79 | 0.94 | 1.00 | 6.6e-17 | 0.41 | 0.41 | 0.41 | Y | 37.4 | 1.7e+07 | 6.9 |
| atc_atco2_mid | LSZH_ZURICH_ApronS_121_75MHz_20210414_100142-A__000028-000380 | 14.0 (12/16) | 175 | 63 | 0.894 / 0.29 | 3.0e-08 | 1.6e-02 | 3.0e-08 | 1.02 | 0.67 | 1.00 | 1.00 | 1.00 | 1.2e-12 | 0.25 | 0.25 | 0.25 | Y | 6.0 | 5.2e+06 | 3.6 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210503_083640-A__000420-000760 | 4.4 (1/7) | 169 | 45 | 0.827 / 0.47 | 1.7e-13 | 2.2e-02 | 1.7e-13 | 1.04 | 0.27 | 0.27 | 0.82 | 0.87 | 6.0e-37 | 0.64 | 0.73 | 0.73 | Y | 4.2 | 3.5e+06 | 3.1 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210501_014446-A__000444-000799 | 4.7 (2/7) | 177 | 29 | 0.807 / 0.58 | 1.6e-16 | 3.4e-02 | 1.6e-16 | 1.01 | 0.21 | 0.42 | 0.80 | 0.86 | 4.3e-91 | 0.92 | 1.00 | 1.00 | Y | 3.7 | 2.6e+06 | 3.1 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210502_235050-A__000324-000909 | 4.9 (2/8) | 292 | 102 | 0.889 / 0.34 | 1.3e-11 | 9.8e-03 | 1.2e-11 | 1.11 | 0.39 | 1.00 | 1.00 | 1.00 | 1.1e-36 | 0.40 | 0.40 | 0.40 | Y | 30.9 | 1.4e+07 | 6.9 |
| atc_atco2_hard | LSGS_SION_Ground_Control_121_7MHz_20210503_140302-B__000023-000548 | 4.9 (3/7) | 262 | 20 | 0.887 / 0.31 | 7.3e-15 | 5.0e-02 | 7.0e-15 | 1.05 | 0.23 | 0.60 | 0.60 | 0.93 | 4.2e-47 | 1.00 | 1.00 | 1.00 | Y | 38.4 | 1.5e+07 | 4.1 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210430_044251-A__000314-000711 | 4.9 (2/7) | 198 | 35 | 0.895 / 0.31 | 2.9e-08 | 2.9e-02 | 2.7e-08 | 1.06 | 0.45 | 1.00 | 1.00 | 1.00 | 3.5e-49 | 0.67 | 0.67 | 0.67 | Y | 4.6 | 3.4e+06 | 3.3 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210502_062227-A__000356-000785 | 5.1 (2/8) | 214 | 48 | 0.905 / 0.33 | 8.9e-09 | 2.1e-02 | 8.6e-09 | 1.04 | 0.36 | 1.00 | 1.00 | 1.00 | 6.4e-37 | 0.45 | 0.36 | 0.45 | Y | 7.3 | 4.3e+06 | 3.7 |
| atc_atco2_hard | LSGS_SION_Tower_118_3MHz_20210423_093650-D__000016-000381 | 5.4 (1/10) | 182 | 59 | 0.861 / 0.45 | 1.2e-09 | 1.7e-02 | 1.1e-09 | 1.07 | 0.41 | 0.62 | 1.00 | 1.00 | 3.7e-44 | 0.64 | 0.73 | 0.64 | Y | 6.2 | 5.4e+06 | 3.1 |
| atc_atco2_hard | LSGS_SION_Tower_118_3MHz_20210502_065945-D__000012-000312 | 6.0 (4/8) | 149 | 18 | 0.921 / 0.24 | 2.7e-05 | 5.6e-02 | 2.6e-05 | 1.03 | 0.59 | 0.95 | 1.00 | 1.00 | 8.7e-29 | 0.50 | 0.50 | 0.50 | Y | 0.3 | 3.1e+05 | 2.3 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210504_065016-A__000428-000883 | 6.2 (6/7) | 224 | 36 | 0.938 / 0.17 | 2.6e-06 | 2.8e-02 | 2.5e-06 | 1.04 | 0.41 | 1.00 | 1.00 | 1.00 | 3.3e-42 | 0.60 | 0.60 | 0.60 | Y | 5.9 | 3.6e+06 | 3.7 |
| atc_atco2_hard | YSSY_SYDNEY_Tower_120_5MHz_20210504_213748-A__000006-000611 | 6.3 (-20/6) | 302 | 15 | 0.885 / 0.33 | 5.6e-16 | 6.7e-02 | 5.3e-16 | 1.04 | 0.06 | 0.17 | 0.49 | 0.87 | 5.4e-149 | 1.00 | 1.00 | 1.00 | n(2) | 17.6 | 7.9e+06 | 4.8 |
| atc_atco2_hard | LSGS_SION_Tower_118_3MHz_20210503_082715-D__000606-000907 | 6.3 (1/12) | 150 | 25 | 0.873 / 0.40 | 6.2e-10 | 4.0e-02 | 5.6e-10 | 1.10 | 0.83 | 0.83 | 0.83 | 1.00 | 1.7e-11 | 0.57 | 0.57 | 0.57 | Y | 1.7 | 2.0e+06 | 2.5 |
| atc_atco2_hard | LKTB_BRNO_Tower_119_605MHz_20201029_102129-B__000639-001262 | 6.4 (4/9) | 311 | 11 | 0.903 / 0.28 | 1.2e-14 | 9.1e-02 | 1.2e-14 | 1.01 | 0.18 | 0.46 | 0.85 | 0.93 | 1.2e-102 | 1.00 | 1.00 | 1.00 | Y | 20.7 | 9.3e+06 | 4.7 |
| atc_atco2_hard | LSZB_BERN_Approach_127_3MHz_20210424_180809-D__000013-000390 | 6.6 (0/13) | 188 | 19 | 0.940 / 0.17 | 2.6e-05 | 5.3e-02 | 2.3e-05 | 1.11 | 1.00 | 1.00 | 1.00 | 1.00 | 8.3e-75 | 0.90 | 0.90 | 0.90 | Y | 1.0 | 5.9e+05 | 3.1 |
| atc_atco2_hard | LSZH_ZURICH_Tower_118_1MHz_20210414_160105-B__000665-000968 | 7.4 (2/12) | 151 | 48 | 0.924 / 0.21 | 6.7e-05 | 2.1e-02 | 6.6e-05 | 1.02 | 0.79 | 0.98 | 1.00 | 1.00 | 8.6e-02 | 0.22 | 0.22 | 0.22 | Y | 2.8 | 2.8e+06 | 2.7 |
| atc_atco2_hard | LSGS_SION_Tower_118_3MHz_20210503_082715-A__000005-000540 | 8.2 (6/11) | 267 | 58 | 0.873 / 0.39 | 3.0e-13 | 1.7e-02 | 3.0e-13 | 1.03 | 0.58 | 0.97 | 1.00 | 1.00 | 5.8e-51 | 0.61 | 0.72 | 0.61 | Y | 16.9 | 8.4e+06 | 4.7 |
| atc_atco2_hard | LZIB_STEFANIK_Tower_118_3MHz_20210503_203710-B__000488-000941 | 8.2 (7/10) | 226 | 10 | 0.923 / 0.22 | 2.1e-08 | 1.0e-01 | 1.9e-08 | 1.07 | 0.27 | 0.27 | 1.00 | 1.00 | 1.4e-80 | 1.00 | 1.00 | 1.00 | Y | 1.4 | 1.1e+06 | 3.5 |
| atc_atco2_synth10 | LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536__vhf10dB | 10.2 (8/13) | 267 | 70 | 0.889 / 0.34 | 1.9e-11 | 1.4e-02 | 1.9e-11 | 1.01 | 0.43 | 1.00 | 1.00 | 0.99 | 1.6e-20 | 0.40 | 0.53 | 0.40 | Y | 17.1 | 8.6e+06 | 4.9 |
| atc_atco2_synth5 | LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536__vhf5dB | 5.1 (2/8) | 267 | 24 | 0.909 / 0.25 | 1.3e-11 | 4.2e-02 | 1.3e-11 | 1.01 | 0.22 | 0.99 | 0.98 | 1.00 | 3.5e-96 | 0.93 | 0.93 | 0.93 | n(2) | 12.4 | 6.3e+06 | 3.9 |
| atc_atco2_synth10 | LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395__vhf10dB | 9.4 (7/12) | 197 | 57 | 0.898 / 0.29 | 4.3e-08 | 1.8e-02 | 4.2e-08 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 2.7e-18 | 0.38 | 0.38 | 0.38 | Y | 7.8 | 6.0e+06 | 3.6 |
| atc_atco2_synth5 | LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395__vhf5dB | 3.3 (0/7) | 197 | 19 | 0.917 / 0.24 | 6.7e-08 | 5.3e-02 | 6.5e-08 | 1.03 | 0.54 | 0.97 | 0.97 | 1.00 | 8.2e-85 | 0.77 | 0.77 | 0.77 | n(2) | 1.7 | 1.2e+06 | 3.1 |
| atc_atco2_synth10 | LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444__vhf10dB | 10.7 (9/13) | 221 | 66 | 0.961 / 0.12 | 7.1e-03 | 1.5e-02 | 4.9e-03 | 1.46 | 1.00 | 1.00 | 1.00 | 1.00 | 2.5e-17 | 0.08 | 0.08 | 0.08 | n(2) | 10.3 | 6.4e+06 | 4.2 |
| atc_atco2_synth5 | LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444__vhf5dB | 5.5 (3/8) | 221 | 53 | 0.965 / 0.09 | 2.9e-02 | 1.9e-02 | 2.2e-02 | 1.30 | 0.66 | 1.00 | 1.00 | 1.00 | 4.7e-73 | 0.50 | 0.42 | 0.50 | Y | 7.9 | 4.3e+06 | 4.0 |
| atc_atco2_synth10 | LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934__vhf10dB | 10.1 (7/13) | 244 | 50 | 0.939 / 0.19 | 1.0e-04 | 2.0e-02 | 1.0e-04 | 1.03 | 1.00 | 1.00 | 1.00 | 1.00 | 5.2e-16 | 0.27 | 0.27 | 0.27 | Y | 10.1 | 5.3e+06 | 4.3 |
| atc_atco2_synth5 | LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934__vhf5dB | 5.2 (2/8) | 244 | 38 | 0.893 / 0.29 | 3.9e-12 | 2.6e-02 | 3.9e-12 | 1.02 | 0.29 | 0.57 | 0.70 | 0.85 | 5.9e-42 | 0.82 | 0.91 | 0.82 | Y | 7.7 | 4.2e+06 | 4.0 |
| atc_atco2_synth10 | LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349__vhf10dB | 11.2 (9/14) | 174 | 36 | 0.922 / 0.24 | 9.6e-06 | 2.8e-02 | 9.2e-06 | 1.05 | 0.96 | 0.96 | 1.00 | 1.00 | 1.1e-24 | 0.56 | 0.67 | 0.56 | Y | 2.8 | 2.1e+06 | 2.9 |
| atc_atco2_synth5 | LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349__vhf5dB | 6.0 (3/9) | 174 | 15 | 0.951 / 0.12 | 2.7e-04 | 6.7e-02 | 2.6e-04 | 1.04 | 0.50 | 0.96 | 1.00 | 1.00 | 5.5e-74 | 0.78 | 0.78 | 0.78 | Y | 0.5 | 4.8e+05 | 2.6 |
| atc_atco2_synth10 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332__vhf10dB | 10.5 (8/13) | 165 | 39 | 0.923 / 0.23 | 1.2e-04 | 2.6e-02 | 1.0e-04 | 1.17 | 0.32 | 0.67 | 1.00 | 1.00 | 1.2e-17 | 0.44 | 0.44 | 0.44 | Y | 3.0 | 2.7e+06 | 2.8 |
| atc_atco2_synth5 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332__vhf5dB | 4.8 (2/8) | 165 | 30 | 0.906 / 0.30 | 3.6e-06 | 3.3e-02 | 3.0e-06 | 1.20 | 0.83 | 1.00 | 1.00 | 1.00 | 9.0e-25 | 0.44 | 0.56 | 0.44 | n(2) | 2.2 | 2.2e+06 | 2.6 |
| atc_atco2_synth10 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742__vhf10dB | 10.5 (8/13) | 203 | 47 | 0.963 / 0.11 | 2.9e-03 | 2.1e-02 | 2.8e-03 | 1.04 | 0.96 | 1.00 | 0.96 | 1.00 | 1.6e-16 | 0.27 | 0.27 | 0.27 | Y | 7.4 | 5.4e+06 | 3.3 |
| atc_atco2_synth5 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742__vhf5dB | 5.1 (2/8) | 203 | 18 | 0.948 / 0.15 | 3.7e-05 | 5.6e-02 | 3.3e-05 | 1.13 | 1.00 | 1.00 | 1.00 | 1.00 | 5.5e-136 | 0.91 | 0.91 | 0.91 | Y | 2.0 | 1.1e+06 | 3.2 |
| atc_atco2_synth10 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212__vhf10dB | 10.4 (8/13) | 233 | 51 | 0.906 / 0.31 | 7.8e-10 | 2.0e-02 | 7.6e-10 | 1.03 | 0.47 | 0.97 | 0.97 | 1.00 | 1.7e-38 | 0.62 | 0.62 | 0.62 | Y | 11.6 | 6.5e+06 | 3.9 |
| atc_atco2_synth5 | LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212__vhf5dB | 5.2 (3/8) | 233 | 19 | 0.892 / 0.31 | 5.8e-12 | 5.3e-02 | 4.6e-12 | 1.26 | 0.71 | 0.72 | 1.00 | 1.00 | 6.2e-102 | 0.94 | 0.94 | 0.94 | Y | 4.1 | 2.9e+06 | 3.6 |

### Transcripts (ref / certified mode / runner-up; greedy and beam-50 when they differ from the mode)

- `LSGS_SION_Tower_118_3MHz_20210503_152021-A__000271-000690` SNR 10.2, margin 1.12, p* 1.3e-06, WER(mode) 0.53
  - ref :[reference transcript not redistributed]
  - mode: ker five one one  even one zero one seven reportgo
  - 2nd : ker five one one n even one zero one seven reportgo
  - grdy: ker five one one   even one zero one seven reportgo
- `LSGS_SION_Ground_Control_121_7MHz_20210504_152004-A__000409-000840` SNR 10.4, margin 1.12, p* 3.4e-09, WER(mode) 0.47
  - ref :[reference transcript not redistributed]
  - mode: charlie zulu wind two five you tel that one four o s two two five andyg own discretion
  - 2nd : charlie zulu wind two five you tel that one four os two two five andyg own discretion
  - grdy: charlie zulu wind two five you te that one four o two two five andyg own discretion
  - b50 : charlie zulu wind two five you tel that one four os two two five andyg own discretion
- `LKPR_RUZYNE_Tower_134_560MHz_20201028_103443-C__000468-000839` SNR 10.5, margin 1.04, p* 3.7e-02, WER(mode) 0.00
  - ref :[reference transcript not redistributed]
  - mode: taxi delta bravo holding point two four csa nine one eight
  - 2nd : taxi delta bravo holding pont two four csa nine one eight
- `LSZH_ZURICH_Tower_118_1MHz_20210412_155616-B__001006-001398` SNR 11.4, margin 1.02, p* 5.4e-15, WER(mode) 0.56
  - ref :[reference transcript not redistributed]
  - mode: clear to land runway one four an vack ig on discretion  one to to
  - 2nd : clear to land runway one four an vack eig on discretion  one to to
  - grdy: clear to land runway one four n vack eig o discretion  one tot o
  - b50 : clear to land runway one four an vack ig on discretion  one tot o
- `LSGS_SION_Ground_Control_121_7MHz_20210502_065520-A__000018-000661` SNR 11.6, margin 1.05, p* 1.5e-07, WER(mode) 0.23
  - ref :[reference transcript not redistributed]
  - mode: november alfa sierra wind two fi nine kots runway two five cleared for takeoff lpof one three thousand feet climbing
  - 2nd : november alfa sierra wind two fi nine kots runway two five cleared for takeoff pof one three thousand feet climbing
  - grdy: november alfa sierra wind two f nine kots runway two five cleared for takeoff lpof one three thousand feet climbing
- `LSGS_SION_Ground_Control_121_7MHz_20210503_151946-A__000012-000584` SNR 12.7, margin 1.05, p* 1.9e-07, WER(mode) 0.45
  - ref :[reference transcript not redistributed]
  - mode: eli charlie zulu wind two seven seven degrees nine knots crossing ravoasnd for the two five lina crrection
  - 2nd : eli charlie zulu wind two seven seven degrees nine knots crossing ravoaisnd for the two five lina crrection
  - grdy: eli charlie zulu wind two seven seven degrees nine knots crossing ravoasnd forthe two five lina crrection
  - b50 : eli charlie zulu wind two seven seven degrees nine knots crossing ravoasnd forthe two five lina crrection
- `LSGS_SION_Ground_Control_121_7MHz_20210502_152026-A__000025-000608` SNR 13.0, margin 1.06, p* 1.8e-11, WER(mode) 0.41
  - ref :[reference transcript not redistributed]
  - mode: uniform golf wind two four zero degrees one four nine run i two five cleared c takeoff figh o clmb approved report leaving
  - 2nd : uniform golf wind two four zero degrees one four nine run i two five cleared c takeoff fih o clmb approved report leaving
  - grdy: uniform golf wind two four zero degrees one four nine run i two five cleared c takeoff fi  clmb approved report leaving
  - b50 : uniform golf wind two four zero degrees one four nine run i two five cleared c takeoff fih o clmb approved report leaving
- `LSZH_ZURICH_ApronS_121_75MHz_20210414_100142-A__000028-000380` SNR 14.0, margin 1.02, p* 3.0e-08, WER(mode) 0.25
  - ref :[reference transcript not redistributed]
  - mode: alitalia five seven one in hello push back and patefit approved
  - 2nd : alitalia five seven one in hello push back and patafit approved
  - grdy: alitalia five seven one ain hello push back and patefit approved
- `YSSY_SYDNEY_Tower_120_5MHz_20210503_083640-A__000420-000760` SNR 4.4, margin 1.04, p* 1.7e-13, WER(mode) 0.64
  - ref :[reference transcript not redistributed]
  - mode: cimreg egh two de runway three four let e ago
  - 2nd : cimreg eigh two de runway three four let e ago
  - grdy: cimreg u egh two dee runway three four lee ago
  - b50 : cimreg u egh two de runway three four le e ago
- `YSSY_SYDNEY_Tower_120_5MHz_20210501_014446-A__000444-000799` SNR 4.7, margin 1.01, p* 1.6e-16, WER(mode) 0.92
  - ref :[reference transcript not redistributed]
  - mode: nine three fortedeedig tow gr
  - 2nd : nine three fortedeedig tow ga
  - grdy: ninthree fortyedeedi towg
  - b50 : ninethree fortedeedig towga
- `YSSY_SYDNEY_Tower_120_5MHz_20210502_235050-A__000324-000909` SNR 4.9, margin 1.11, p* 1.3e-11, WER(mode) 0.40
  - ref :[reference transcript not redistributed]
  - mode: nm seven seven three heav eay good morning continue approach shorting two seven zero degrees seven non
  - 2nd : nm seven seven three heav eay good morning continue approach shortwing two seven zero degrees seven non
  - grdy: nm seven seven three heaveay good morning continue approach shorting two seven zero degrees seven non
- `LSGS_SION_Ground_Control_121_7MHz_20210503_140302-B__000023-000548` SNR 4.9, margin 1.05, p* 7.3e-15, WER(mode) 1.00
  - ref :[reference transcript not redistributed]
  - mode: haero keo oe oa zero
  - 2nd : haerokeo oe oa zero
  - grdy: arokioeooioa zero
  - b50 : haerokioeoo ieoa zero
- `YSSY_SYDNEY_Tower_120_5MHz_20210430_044251-A__000314-000711` SNR 4.9, margin 1.06, p* 2.9e-08, WER(mode) 0.67
  - ref :[reference transcript not redistributed]
  - mode: rthree one seventy fivee o good day
  - 2nd : rthree one seventy fivee oo good day
  - grdy: three one seventy fiveeoo good day
- `YSSY_SYDNEY_Tower_120_5MHz_20210502_062227-A__000356-000785` SNR 5.1, margin 1.04, p* 8.9e-09, WER(mode) 0.45
  - ref :[reference transcript not redistributed]
  - mode: direct six tango e papa heavy  good day continue
  - 2nd : tirect six tango e papa heavy  good day continue
  - grdy: direct six tango papa heavy good day continue
- `LSGS_SION_Tower_118_3MHz_20210423_093650-D__000016-000381` SNR 5.4, margin 1.07, p* 1.2e-09, WER(mode) 0.64
  - ref :[reference transcript not redistributed]
  - mode: n tower and passing echo three hotel bravo nevova papa zulu
  - 2nd : n tower and passing echo three hotel bravo nevava papa zulu
  - grdy: n tower adpassing ech three hotel bravo nevova papa zulu
- `LSGS_SION_Tower_118_3MHz_20210502_065945-D__000012-000312` SNR 6.0, margin 1.03, p* 2.7e-05, WER(mode) 0.50
  - ref :[reference transcript not redistributed]
  - mode: we are not ready o
  - 2nd : we arenot ready o
  - grdy: we are not ready
- `YSSY_SYDNEY_Tower_120_5MHz_20210504_065016-A__000428-000883` SNR 6.2, margin 1.04, p* 2.6e-06, WER(mode) 0.60
  - ref :[reference transcript not redistributed]
  - mode: see three zero one evigood afternoon
  - 2nd : see three zero one eavigood afternoon
  - grdy: see three zero one vgood afternoon
- `YSSY_SYDNEY_Tower_120_5MHz_20210504_213748-A__000006-000611` SNR 6.3, margin 1.04, p* 5.6e-16, WER(mode) 1.00
  - ref :[reference transcript not redistributed]
  - mode: reeoeeobyeee ye
  - 2nd : reoeeeobyeee ye
  - grdy: oieoeobyeeye
  - b50 : reeoeeobyeeee
- `LSGS_SION_Tower_118_3MHz_20210503_082715-D__000606-000907` SNR 6.3, margin 1.10, p* 6.2e-10, WER(mode) 0.57
  - ref :[reference transcript not redistributed]
  - mode: neg final two five oto te
  - 2nd : neg final two five oto e
  - grdy: neg final two five oto oe
  - b50 : neg final two five oto oe
- `LKTB_BRNO_Tower_119_605MHz_20201029_102129-B__000639-001262` SNR 6.4, margin 1.01, p* 1.2e-14, WER(mode) 1.00
  - ref :[reference transcript not redistributed]
  - mode: eoo klopa a
  - 2nd : keoo klopa a
  - grdy: oklopaoa
  - b50 : eooklopaa
- `LSZB_BERN_Approach_127_3MHz_20210424_180809-D__000013-000390` SNR 6.6, margin 1.11, p* 2.6e-05, WER(mode) 0.90
  - ref :[reference transcript not redistributed]
  - mode: hotel osto yankeee
  - 2nd : hopel osto yankeee
- `LSZH_ZURICH_Tower_118_1MHz_20210414_160105-B__000665-000968` SNR 7.4, margin 1.02, p* 6.7e-05, WER(mode) 0.22
  - ref :[reference transcript not redistributed]
  - mode: untwe one zero cleared to land hotel yankee hote
  - 2nd : untwa one zero cleared to land hotel yankee hote
  - grdy: utwa one zero cleared to land hotel yankee hote
- `LSGS_SION_Tower_118_3MHz_20210503_082715-A__000005-000540` SNR 8.2, margin 1.03, p* 3.0e-13, WER(mode) 0.61
  - ref :[reference transcript not redistributed]
  - mode: charlie  two continue for dic pproach  onot final two five
  - 2nd : charliee two continue for dic pproach  onot final two five
  - grdy: charliee two continue fo dic pproach  ono final two five
- `LZIB_STEFANIK_Tower_118_3MHz_20210503_203710-B__000488-000941` SNR 8.2, margin 1.07, p* 2.1e-08, WER(mode) 1.00
  - ref :[reference transcript not redistributed]
  - mode: r foxrotre
  - 2nd : gr foxrotre
  - grdy: foxrooe
- `LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536__vhf10dB` SNR 10.2, margin 1.01, p* 1.9e-11, WER(mode) 0.40
  - ref :[reference transcript not redistributed]
  - mode: oscar kilo foxtrot ot oscar  holding oing ey two seven vy alfa charlie
  - 2nd : oscar kilo foxtrot ot oscar  holding oing y two seven vy alfa charlie
  - grdy: oscar kilo foxrot ot ocar holding oig y two seven vy alfa charlie
- `LKTB_BRNO_Tower_119_605MHz_20201028_185619-A__000000-000536__vhf5dB` SNR 5.1, margin 1.01, p* 1.3e-11, WER(mode) 0.93
  - ref :[reference transcript not redistributed]
  - mode: o i sevenomie alfa chaie
  - 2nd : o sevenomie alfa chaie
  - grdy: seve omi alfa chaie
  - b50 : o sevenmie alfa chaie
- `LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395__vhf10dB` SNR 9.4, margin 1.00, p* 4.3e-08, WER(mode) 0.38
  - ref :[reference transcript not redistributed]
  - mode: k echo lima alfa proprceedig to tango bravi four zero two
  - 2nd : k echo lima alfa prorceedig to tango bravi four zero two
- `LKTB_BRNO_Approach-Radar_127_350MHz_20201026_111634-A__000000-000395__vhf5dB` SNR 3.3, margin 1.03, p* 6.7e-08, WER(mode) 0.77
  - ref :[reference transcript not redistributed]
  - mode: echo lima alfa fa i
  - 2nd : echo lima alfa fa
  - grdy: echo lima alfa fa
  - b50 : echo lima alfa fa
- `LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444__vhf10dB` SNR 10.7, margin 1.46, p* 7.1e-03, WER(mode) 0.08
  - ref :[reference transcript not redistributed]
  - mode: csa one delta zulu descend flight level one hundred no speed bird
  - 2nd : csa one delta zulu descend flight level one hundred no speed bird e
- `LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-A__000000-000444__vhf5dB` SNR 5.5, margin 1.30, p* 2.9e-02, WER(mode) 0.50
  - ref :[reference transcript not redistributed]
  - mode: csa one delta zulue descend f light level one hundred
  - 2nd : csa one del ta zulue descend f light level one hundred
  - grdy: csa one delta zulu descend f light level one hundred
- `LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934__vhf10dB` SNR 10.1, margin 1.03, p* 1.0e-04, WER(mode) 0.27
  - ref :[reference transcript not redistributed]
  - mode: descending flight level one  re csa one delta zulu
  - 2nd : descending flight level one re csa one delta zulu
- `LKPR_RUZYNE_Radar_120_520MHz_20201028_151125-G__000444-000934__vhf5dB` SNR 5.2, margin 1.02, p* 3.9e-12, WER(mode) 0.82
  - ref :[reference transcript not redistributed]
  - mode: eng flightlevel one praha csa onetogul
  - 2nd : eng flightlevel one praha csa oneltogul
  - grdy: g flightleve one prahacacsa oneetogul
  - b50 : eg flightleve one praha csa onetogul
- `LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349__vhf10dB` SNR 11.2, margin 1.05, p* 9.6e-06, WER(mode) 0.56
  - ref :[reference transcript not redistributed]
  - mode: osca kilo sia hotel please o holding
  - 2nd : osca kilo sia hotel pleaseo holding
  - grdy: osca kilo sia hotel pleaseo holding
- `LKPR_RUZYNE_Radar_120_520MHz_20201026_145941-G__000000-000349__vhf5dB` SNR 6.0, margin 1.04, p* 2.7e-04, WER(mode) 0.78
  - ref :[reference transcript not redistributed]
  - mode: oscar kilo kioo
  - 2nd : oscar kilo kio o
  - grdy: oscar kilo ki o
- `LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332__vhf10dB` SNR 10.5, margin 1.17, p* 1.2e-04, WER(mode) 0.44
  - ref :[reference transcript not redistributed]
  - mode: ruzyne tower helo erings one tango kilo
  - 2nd : ruzyne tower hel erings one tango kilo
  - grdy: ruzyne tower elo eoings one tango kilo
- `LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000000-000332__vhf5dB` SNR 4.8, margin 1.20, p* 3.6e-06, WER(mode) 0.44
  - ref :[reference transcript not redistributed]
  - mode: ruzyne tower ri one tango kilo
  - 2nd : ruzyne toweri one tango kilo
  - grdy: ruzyne toweri one tango kilo
- `LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742__vhf10dB` SNR 10.5, margin 1.04, p* 2.9e-03, WER(mode) 0.27
  - ref :[reference transcript not redistributed]
  - mode: ri one tango kilo tower good afternoon go ahead
  - 2nd : i one tango kilo tower good afternoon go ahead
  - grdy: i one tango kilo tower good afternoon go ahead
  - b50 : i one tango kilo tower good afternoon go ahead
- `LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-A__000334-000742__vhf5dB` SNR 5.1, margin 1.13, p* 3.7e-05, WER(mode) 0.91
  - ref :[reference transcript not redistributed]
  - mode: eving one sio zero
  - 2nd : eving one sixo zero
- `LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212__vhf10dB` SNR 10.4, margin 1.03, p* 7.8e-10, WER(mode) 0.62
  - ref :[reference transcript not redistributed]
  - mode: just requeste c toget runway two four for departure
  - 2nd : just request c toget runway two four for departure
  - grdy: just requestc toget runway two four for departure
  - b50 : just request c toget runway two four for departure
- `LKPR_RUZYNE_Tower_134_560MHz_20201025_144043-B__000744-001212__vhf5dB` SNR 5.2, margin 1.26, p* 5.8e-12, WER(mode) 0.94
  - ref :[reference transcript not redistributed]
  - mode: ef wo four fre fone
  - 2nd : ef wo four fre fine
  - grdy: f wo four fre fone


## Verdict

**At what SNR does beam-50 stop finding the certified mode with the in-domain model?** Below about 15 dB on real ATCO2-test audio: 4/8 misses at 10–15 dB, 3/11 at 5–10 dB, 3/5 below 5 dB (16/16 hits at ≥ 15 dB in the atc-in-domain report and here), with beam-800 still missing 7/24 — the misses return labellings at 0.49–0.94 × p\* (beam-800: 0.85–0.95 × p\*), so beam search is off the exact argmax by less than a factor of two, and the exact decoder is never slow (≤ 45 s, ≤ 0.23 · T²W² generations). **Is the exact mode ever a better transcript than greedy/beam there?** Not materially: WER(mode) ties greedy on 18/24 clips below 15 dB, is better on 4 (by 0.08–0.11, all on transcripts with WER ≥ 0.6) and worse on 2; it ties beam-50 on 22/24; below 10 dB the exact argmax is a deletion-biased shorter string (6 words vs 12 in the reference, WER ≥ 0.9 on 6/16), the reference is in the certified top-2 on 0/24 and carries p(ref)/p\* ≤ 8.6e-2 (median ≈ 1e-40), so what is certified is the most probable of several wrong strings. **Does the one-character-edit pattern persist?** Yes: 51/56 runner-ups are exactly one symbol from the mode and the other 5 are two symbols (still one spelling variant), margins 1.01–1.12 on every clip below 15 dB — the regime where the exact decoder finally has something to add over beam-50 is precisely the regime where p\*, the margin and the mode certify nothing a transcript consumer wants.

### Evidence limits

n = 24 real clips below 15 dB (16 chosen as the hardest of 501, 8 random in 10–15 dB), 16 synthetic; SNR is a blind estimate (two estimators, agreeing to ±3 dB, calibrated on the synthetic files); ATCO2-test is cross-corpus for this checkpoint (fine-tuned on UWB-ATCC + ATCOSIM) — a LiveATC-fine-tuned checkpoint might sharpen the posteriors at 10–15 dB, though [Z22] reports 27–31 % WER on LiveATC-test even after ATC fine-tuning, so the < 10 dB picture would be unlikely to change; references keep disfluencies and the WER is un-normalised (as in the atc-in-domain report).

## Citations

- [KS08] C. Kim, R. M. Stern, "Robust signal-to-noise ratio estimation based on waveform amplitude distribution analysis", Interspeech 2008 — the WADA-SNR estimator; G-table as in the LabROSA `snreval` Matlab port / J. Meade's Python port (fetched this run).
- [ATCO2] J. Zuluaga-Gomez, K. Veselý, I. Szöke, et al., "ATCO2 corpus: A Large-Scale Dataset for Research on Automatic Speech Recognition and Natural Language Understanding of Air Traffic Control Communications", arXiv:2211.04054 (body-read this run, `hard-atc-audio/refs/atco2corpus.txt`): "recordings are often noisy (SNR below 15 dB)"; SNR filtering uses WADA-SNR after tight SAD; Table 2 lists ATCO2-test-set as SNR ≤ 15 dB, public; Table 3 gives per-airport mean/std WADA-SNR (YSSY 3.1/7.0 … LSZB 15.4/10.7 dB).
- [Z22] J. Zuluaga-Gomez et al., "How Does Pre-trained Wav2Vec 2.0 Perform on Domain Shifted ASR? An Extensive Benchmark on Air Traffic Control Communications", arXiv:2203.16822 / SLT 2022 (`hard-atc-audio/refs/z22.txt`): Table 1 SNR bands (ATCO2-Test 10–15 dB, LiveATC-Test 5–15 dB "as low quality speech data set", UWB-ATCC ≥ 20 dB); "the most challenging test sets (SNR: 5-10 dB) … ATCO2-Test and LiveATC-Test".
- Model card `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim` (as in the atc-in-domain report). Datasets: `Jzuluaga/atco2_corpus_1h` (test split) via the HF datasets-server row API; atc-in-domain/adjacent-domains samples for the ≥ 15 dB rows.
- Prior lane artefacts: `atc-in-domain.md` (setup, ≥ 15 dB results, column-swap), `certctc/README.md` (decoder, gates), `../code/certified-exact-decoder/`, `../code/adversarial-decoder-check/`.

## Files

Deliverable = this file (`hard-atc-audio.md`). `hard-atc-audio/results__r3.json` (56 rows: SNR estimates, confidence, certificate fields, greedy/beam-5/50/800 labellings + probabilities + WER, p(ref), edit distances), `../code/hard-atc-audio/tables_r3.md`, `hard-atc-audio/manifest.json`, `hard-atc-audio/selection.json`, `hard-atc-audio/atco2_candidates_snr.json` (501 candidates with WADA/VAD/combined SNR), `../code/hard-atc-audio/a4_snr.json`, `hard-atc-audio/posteriors/*.npy` (56), `hard-atc-audio/samples/atco2_all/*.wav` (501, 77 MB), `hard-atc-audio/samples/synth/*.wav` (16), `hard-atc-audio/rows/*.json` (871 row records), `hard-atc-audio/refs/{z22,atco2corpus}.{pdf,txt}`, logs `run_r3.log`, `gate_r3.log`, `select_r3.log`, `reselect.log`, `build_manifest.log`, `fetch_atco2.log`.

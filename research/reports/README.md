# Reports

Working reports from the research programme summarised in [`../README.md`](../README.md). They
are published as written (numbers, gate lines, citations and quotations intact), with internal
paths and thread labels replaced by the names below. Each report states its own date, scope and
the code that produced its numbers.

| report | one line |
|---|---|
| [`hardness-literature.md`](hardness-literature.md) | Every published "most probable string" hardness proof is a mixture of chains with a memory bit; the product-measure case (most-frequent-subsequence) is stated open in print (Fang 2024, Rem. 4.2). |
| [`hardness-attempt.md`](hardness-attempt.md) | Attempted reductions for most-frequent-subsequence: separator-forcing lemma, interface identity, repetition bound, FPT in ambiguous slots; three gadget templates refuted with machine-checked reasons; no theorem either way. |
| [`certified-exact-decoder.md`](certified-exact-decoder.md) | The exact-backward-suffix-mode decoder: admissible bound family, gates, scaling on synthetic tables, and the 70 real posterior tables certified with mode, runner-up and margin. |
| [`quantum-argmax-construction.md`](quantum-argmax-construction.md) | The minimal correct quantum CTC decoder (product Born state, coherent collapse, exact comparator, generalized minimum-finding), verified 272/272, with the equal-units cost model. |
| [`quantum-mbr-reframing.md`](quantum-mbr-reframing.md) | Quantum minimum-Bayes-risk decoding of CTC posteriors: an unconditional Õ(σ/ε) query statement that is decision-irrelevant on real audio. |
| [`quantum-literature-sweep.md`](quantum-literature-sweep.md) | 2024–26 quantum literature against the programme's standing conclusions; identifies the generalized-minimum-finding route and the Belovs lower bound. |
| [`adjacent-domains.md`](adjacent-domains.md) | Measurements with a generic CTC model on air-traffic radio, far-field meetings and dysarthric speech; triage of other CTC domains (nanopore, HTR, sign language, …). |
| [`citation-check.md`](citation-check.md) | Adversarial re-derivation of six load-bearing citations (van Apeldoorn et al. Thm 49, Belovs Thm 4, Jarret–Wan, Aaronson–Ambainis, Rall vs Guo et al., de la Higuera–Oncina, Chakrabarti et al. Thm 1.5). |
| [`adversarial-decoder-check.md`](adversarial-decoder-check.md) | Independent re-implementation of the certified-exact decoder from its description, node-for-node agreement, the flat-row worst case (W−2)^{T/2}, and the audit of the original gates. |
| [`cost-theorem.md`](cost-theorem.md) | Proven cost bound O(W²T³·e^Λ) in the greedy log-loss Λ; ρ-confidence refuted as a parameter; FPT in ambiguous frames; the margin lemma left open. |
| [`quantum-vs-classical-baseline.md`](quantum-vs-classical-baseline.md) | The quantum argmax route costed per real utterance against the certified-exact decoder in equal units: no advantage at any operating point where exact decoding is wanted. |
| [`atc-in-domain.md`](atc-in-domain.md) | The same air-traffic clips with the field's in-domain checkpoint: the low-confidence regime was a domain-shift artefact; the runner-up is a one-character edit of the mode on 24/24 decodes. |
| [`margin-lemma.md`](margin-lemma.md) | The margin theorem: top-2 margin p*/p₂ > K (distinct suffix modes per symbol, free from the backward pass; K = D+1 on real tables) ⇒ the final search expands exactly D or D+1 nodes; the cost-theorem report's "margin 1.3–3.6" evidence withdrawn; constant-ratio conjecture C0 left open. |
| [`word-class-certificate.md`](word-class-certificate.md) | Exact posterior mass P(L\|y) of a regular word class (callsign, flight level, runway, …) by a DFA-product forward recursion, gated against brute force; on 33 air-traffic slots it certifies 21 at ≥ 0.9 and reports the two safety-relevant misreads as 10⁻⁷–10⁻⁹ mass, where beam rescoring is loose by up to 0.94. |
| [`hard-atc-audio.md`](hard-atc-audio.md) | The in-domain model on 24 real ATCO2-test clips at 4–14 dB and 16 synthetic VHF degradations: beam-50 misses the certified mode below ~15 dB (14/24), but the exact mode is not a better transcript; one-character-edit runner-ups on 80/80 certified decodes. |

## Reading notes

- **Thread labels.** The reports were written as numbered threads. In prose the labels have been
  replaced by the report names above. Inside quoted gate lines and in the code under `../code/`
  the labels `T2b` and `T9` still appear: `T2b` is `certified-exact-decoder`, `T9` is
  `adversarial-decoder-check`, `T3` is `quantum-argmax-construction`, `A2` is `cost-theorem`,
  `A3` is `quantum-vs-classical-baseline`, `A4` is `atc-in-domain`, `T7` is `adjacent-domains`,
  `R1` is `margin-lemma`, `R2` is `word-class-certificate`, `R3` is `hard-atc-audio`. Gate lines
  are quoted byte-for-byte from the runs.
- **Table identifiers.** `T4/clean/P0`, `T4/5dB/P6`, … name the LibriSpeech posterior tables
  (condition / utterance); the bare names (`atc_uwb__…`, `ami_sdm__…`, `torgo_dys_…`) are the
  adjacent-domain tables. The tables themselves are not redistributed.
- **Unpublished working directories.** Paths such as `adjacent-domains/measure.py`,
  `quantum-mbr-reframing/mbr.py`, `hardness-attempt/expE.py`, `citation-check/genmin_sim.py`,
  `quantum-literature-sweep/…` and `atc-in-domain/…` refer to working directories of threads
  whose code is not included in this release: they depend on downloaded models, audio and
  papers that are not redistributed. The code for the decoder, the quantum construction, the
  adversarial check, the cost theorem, the per-utterance costing, the margin lemma, the
  word-class certificate and the hard-audio measurement is under `../code/`. For the hard-audio
  report the scripts, logs, `tables_r3.md` and `a4_snr.json` are published; paths written
  `hard-atc-audio/…` (`results__r3.json`, `manifest.json`, `selection.json`, the candidate lists,
  `rows/`, `samples/`, `posteriors/`, `refs/`) hold corpus transcripts, audio or papers and are
  not included — every per-clip statistic they carry is in the report's tables. In
  `select_r3.log` four reference-transcript snippets of clips the report does not quote are
  replaced by `[transcript not redistributed]` and one absolute output path in `run_r3.log` is
  a placeholder; no log is otherwise altered.
- **Ledger identifiers.** Tokens such as `N30`, `N58`, `E7`, `F11`, `v10`, `C1–C6`, `D2`, `C3`,
  `C7` refer to entries in an earlier internal claims ledger of the same programme. They are kept
  so that the reports' cross-references remain traceable; the ledger itself is not published.
- **"body-read" / "abstract-only"** mark, for every citation, whether the relevant section of the
  paper was read or only its abstract.

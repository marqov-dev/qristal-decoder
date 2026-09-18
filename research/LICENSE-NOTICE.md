# License notice for `research/`

## Upstream code

Everything outside `research/` is the Qristal Decoder, © Quantum Brilliance Pty Ltd, released
under the Apache License 2.0 (see `../LICENSE`). The upstream code is unchanged by the material
in this directory; the only changes to it are the three merged pull requests (#1–#3) described
in the top-level `README.md`, which validate inputs and document the qualification boundary.

## Additions in this directory

The technical note, the reports under `reports/`, the `certctc/` package and the code under
`code/` are © Marqov and are released under the same Apache License 2.0. The reversible
collapsing map used by the quantum construction in `reports/quantum-argmax-construction.md`
is Quantum Brilliance's (`src/decoder_kernel.cpp`) and is credited as such.

`certctc/_toolkit_ctc.py` and `code/certified-exact-decoder/ctc.py` are verbatim copies of the
validation toolkit written for this programme (Apache-2.0, © Marqov).

## Datasets and models

The measurements reported here used the following corpora and checkpoints. **None of the audio,
transcripts or posterior tables are redistributed**; only derived statistics (certified
probabilities, margins, node counts, timings, error rates) are reported.

- LibriSpeech (CC BY 4.0), the public dummy split, with additive white noise at 10 / 5 / 0 dB SNR.
- AMI Meeting Corpus, single-distant-microphone condition (CC BY 4.0; `edinburghcstr/ami`).
- TORGO dysarthric speech database (research use; accessed through the public `abnerh/TORGO-database` mirror).
- UWB-ATCC air-traffic-control corpus (`Jzuluaga/uwb_atcc`) and the ATCO2 1 h test set
  (ATCO2-test-set-1h, `Jzuluaga/atco2_corpus_1h`), both public research releases; the hard-audio
  report also uses band-limited, noise-added copies of eight ATCO2 clips, likewise not redistributed.
- Models: `facebook/wav2vec2-base-960h` and
  `Jzuluaga/wav2vec2-large-960h-lv60-self-en-atc-uwb-atcc-and-atcosim` (Apache-2.0 model cards).

Papers cited in the reports are cited, not redistributed.

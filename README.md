# QB SDK - Decoder

## Description
These are control scripts for the quantum decoder and its variants.
The function of the decoder is to take a probability table, indicating the probability of each symbol in an alphabet at each of a set of timesteps, and find the most likely intended output.
The probability table is provided and comes from a classical convolutional neural network as part of a compound application, where our focus has been on a speech-to-text application. The intended outputs are not the strings naively found from the probability table but require a two-step process:
1. Contract all repetitions within the string down to one symbol,
2. Remove all _null_ characters.
Strings which return the same output after this process may be deemed equivalent and form equivalence classes which we call _beams_.
### The full decoder
The full decoder sorts the input strings into their respective beams before returning the most probable.
To find the probabilities of each beam, the decoder finds the probabilities of each string in the beam and adds them. It then uses repeated Grover searches to magnify the highest probability beam as much as possible, so that it is returned upon quantum measurement.
This is a complicated algorithm with multiple parts, which we summarize as follows:
1. At each timestep the decoder transcribes the probability data to the appropriate quantum register and then clears the input register for the next timestep.
2. The probabilities are encoded as logarithms so that multiplying them can be effected by addition, which is easier. The decoder finds the logarithm of the probability of each string and uses the exponent module to find the actual probability for later summation.
3. Strings are sorted into their respective beams by the _decoder kernel_. Since a quantum algorithm cannot remove symbols from a string it relocates them to the end of the string and flags those symbols that have been moved as being either repetitions of the previous symbol, or _null_. The original positions of those symbols are flagged separately.
4. The next step is to sum the probability values of each string within each beam class. The complications of this step include determining the relative size of each beam class and adjusting the outcome accordingly.
5. The final step is an exponential search, which is implemented in a module of the SDK core. This amplifies the amplitude of those beams whose probability is greater than the previous measurement, or zero the first time. Measuring then gives a new value to compare to until the maximum possible value is found or a set number of loops have been run.
### Simplified decoder
In order to reduce the scaling of the gate depth and to have a relevant application demonstrable to clients, we have also put together a simplified version of the decoder. This does not identify the beams but simply encodes the strings with probability amplitudes representative of the input probability table. The probability of any given string being returned upon measurement matches that expected from the probability table. Similarly for the probability of the returned string belonging to a given beam. The beam to which the returned string belongs is determined classically post-measurement. This simplified approach does not attempt to return the highest probability string or beam with certainty, _i.e._ there is no amplitude amplification of the highest probability string/beam.

## Tests
CI tests are included for both decoders and for the quantum kernel. However, the user is warned that those for the full decoder and the decoder kernel can take an excessive amount of time to run, depending on the hardware being used. 

## License
[Apache 2.0](LICENSE)

## Community qualification status (2026-09-12)

The simplified Decoder has native CPU qualification coverage. The full Decoder
is still experimental: its historical test invokes the algorithm without an
active assertion about the decoded answer. A resource-bounded run of that test
reached its 60-second limit; this is inconclusive about algorithm correctness.
The source also shadows the caller's result buffer with a local buffer, so an
explicit result contract and independent answer oracle are still needed.

Full Decoder initialization now rejects missing or incorrectly typed table/iteration
inputs and empty, ragged, non-finite, negative, out-of-range or unnormalized
probability tables before row indexing or timestep division. Each row must sum
to one within an absolute tolerance of `1e-5`. This validation remains active in
Release builds. It is not complete register validation or algorithm qualification;
existing register assertions and backend ownership still need separate review.

`FullDecoderInputValidation.*` tests exercise rejected tables and accepted
normalized inputs without executing the full algorithm. The historical full
algorithm fixture should be run only with explicit time and resource limits.

### Register and backend follow-up (review branch)

The full Decoder now checks required register dimensions, distinct nonnegative
qubit IDs, a dense allocation, minimum ancilla capacity and signed score-width
limits before choosing a backend. Register widths follow the existing algorithm's
precision formulas; the signed-int score implementation limits widths to 30 bits.
Only the implemented `canonical` method is accepted. Iterations must be positive
and no greater than the table's timestep count; trial count must be positive.

Named and shared backends are owned per Decoder instance. An explicitly invalid
or null backend is rejected rather than silently replaced, and failed
reinitialization invalidates execution. Raw backend pointers remain borrowed.
Score encoding now produces the requested register width; the old `sizeof(int)`
bitset could truncate scores and index beyond the generated string.

Validation is deliberately split: 43 dependency-free C++ checks passed on macOS
with `-DNDEBUG`, AddressSanitizer and UndefinedBehaviorSanitizer. A Linux workflow
runs the same checks. These checks exercise the production register/score helper.
The expanded XACC-linked tests and the installed runtime rebuild are pending;
the earlier three native tests apply to the earlier table-only source revision.
No full Decoder correctness or caller-visible result qualification is claimed.

Standalone reproduction, requiring only a C++17 compiler:

```sh
c++ -std=c++17 -O1 -DNDEBUG -Wall -Wextra -Werror -fsanitize=address,undefined -Iinclude tests/RegisterValidationStandalone.cpp -o /tmp/decoder-register-validation
/tmp/decoder-register-validation
```

### Caller-visible search observation (review branch)

After all trials complete, `execute` writes `initial-score`, `best-score`,
`best-string`, `has-improving-candidate`, `trials-completed`, `method` and
`result-kind=quantized-search-observation` to the supplied buffer. The score/string
pair is retained only from a strict improvement over the current maximum.
Equal or lower subsequent scores cannot replace the winning string. If no
improvement occurs, the score remains the initial threshold, the string is empty
and `has-improving-candidate` is false. These fields do not certify the globally
best beam, and the integer score is not a normalized probability.

The production result accumulator adds ten checks for maximum/pair preservation,
no-improvement behavior, malformed observations and trial accounting: 53 total
standalone sanitizer checks now pass. Full source and integration-test syntax
checks also pass. Native XACC execution remains pending at this revision; the
prior table-only native evidence does not validate this new result publication.

### Comparator register order

Full Decoder threshold preparation now uses least-significant-bit-first register
order, matching `CompareGT` with `is_LSB=true`. In a six-bit register, preparing
MSB-first `000001` previously represented 32 to that comparator rather than 1.
The separate formatting helper still returns MSB-first strings. The standalone
suite checks all six-bit thresholds and comparison boundaries; this does not
replace native quantum-comparator or full Decoder qualification.

## Independent analysis and a certified-exact classical decoder (2026)

Besides the validation work above, this fork now hosts an independent analysis of the Decoder
and the research it led to, under [`research/`](research/README.md). It contains: a reading of
what the full Decoder computes, with source citations; a minimal *correct* quantum CTC decoder
built from Quantum Brilliance's own two components (the product-state amplitude encoding and the
coherent collapsing map) plus an exact comparator and generalized minimum-finding, verified end
to end; and `certctc`, a certified-exact classical decoder that solves the Decoder's target
problem — the most probable labelling of a CTC posterior, with its runner-up and margin — on real
audio in seconds, where prefix search would need 10¹⁸–10²⁶ expansions. The upstream code is
unchanged; the research directory is self-contained and Apache-2.0.

# Public CPU decoder qualification

This is a bounded qualification of **simplified-decoder**, not certification of the full quantum decoding algorithm or a performance claim. No commercial Emulator, vQPU, GPU, cloud jobs or device credentials are used.

## Behavior repaired

* Reject empty, ragged, nonfinite, negative or unnormalized probability tables, unsupported symbol widths/methods and invalid qubit registers before constructing a circuit.
* Retain selected accelerator ownership per decoder; a function-static accelerator previously reused the first named backend in subsequent initializations. Reset bit-order inference on reinitialization.
* Normalize output symbols to MSB-first binary in input time order across qpp, Aer and sparse-sim. The previous qpp/sparse default returned `1011` where Aer returned `0111` for deterministic symbols 1,3. This intentionally changes those default output strings. `is_msb` overrides the raw measurement-order inference; it is not a request for backend-dependent output labels.
* Collapse adjacent repeats before removing blank symbols. A blank separates otherwise identical symbols, so 1,1,0,1,3 becomes 1,1,3, encoded `010111` for four symbols.
* Respect the requested CMake build type, and keep plugin registration headers out of the consumer-facing class header.

## Reproduction environment

Start with the fresh public CPU/noise workspace described in marqov-dev/qristal PR #2, source commit f877262, with merged Core `55fa21f502e47dd486ac624514af0a7983db2cab`, public XACC `d1edaa7ae53edc7e335f46d33160f93d6020aaa3`, Ubuntu 22.04 / GCC 11.4 / Python 3.10.12. Decoder starts from `1f37b19af10b8290ca2e4d65e4e2bc85107452f2` plus this patch. Qualification uses Linux amd64 under local emulation with 2 CPUs, 4 GiB memory/swap and 256 PIDs. Builds and tests are offline after public acquisition.

The minimal XACC profile additionally needs `add_subdirectory(algorithms/qpe)` next to `add_subdirectory(xasm)` in its CPU branch of quantum/plugins/CMakeLists.txt. This supplies the public `C-U` controlled-gate service used by Core's RyEncoding; it is not a private QB library. Reconfigure, build and install XACC to the isolated prefix.

In the temporary Core source only, append an include of a local CMake file with:

```cmake
set(SKIP_FIND_CORE ON)
set(qristal_core_FOUND ON)
set(qristal_core_DIR /work/qristal-core)
add_subdirectory(/work/qristal-decoder /work/build-core/decoder)
```

This is a local source-tree harness, not a proposed Core product modification. Reconfigure Core with the CPU profile and `CMAKE_BUILD_TYPE=Release`, then build targets `circuits sparse_simulator decoder simplified_decoder CITests_decoder` with parallelism 2. Expose one symlink each for the Core circuits/sparse-simulator and Decoder plugin libraries in the isolated XACC plugins directory; avoid duplicate versioned plugin copies.

Run `CITests_decoder --gtest_filter=CommunityQualification.*:SimplifiedDecoderAlgorithm.*`. The four new CommunityQualification tests use GoogleTest assertions effective with `-DNDEBUG`: malformed-input rejection; deterministic 4-qubit outputs on three real CPU backends; named-backend routing using two local recording stubs; and 10-qubit repeat/blank examples on three real CPU backends. Existing upstream tests also execute, but contain C++ assert checks disabled in Release and are not independent correctness evidence.

Full quantum-decoder runtime, statistical accuracy on general distributions, installed SDK packaging, alternative architectures and performance scaling remain unverified. Both decoder libraries compile; this does not qualify both algorithms. A clean standalone install-path build remains a follow-up to this source-tree harness.

## Recorded result

The Release build completed in 317.8 seconds. All seven selected GoogleTest cases passed; four are the new release-effective qualification tests described above. The test executable was compiled with `-O1 -DNDEBUG`. The earlier cross-backend output failure is preserved alongside final logs and a checksum manifest in `evidence/2026-09-09`. No GitHub CI or clean standalone packaging result is implied.

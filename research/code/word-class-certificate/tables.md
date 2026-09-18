
### In-domain model `Jzuluaga/...-uwb-atcc-and-atcosim` (A4 posteriors, 16 clips, 33 slots)

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

### Generic `facebook/wav2vec2-base-960h` (T7 posteriors), same 8 UWB-ATCC clips, 18 slots

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

SUMMARY {
 "a4": {
  "slots": 33,
  "p_correct_ge_0_9": 21,
  "gap_gt_0_1": 9,
  "gap_gt_0_01": 26,
  "gap_median": 0.034374839731905804,
  "gap_max": 0.9439901743273993,
  "sec_max": 0.17728649999480695,
  "competing_gt_0_5": 3
 },
 "generic": {
  "slots": 18,
  "p_correct_ge_0_9": 0,
  "gap_gt_0_1": 0,
  "gap_gt_0_01": 0,
  "gap_median": 1.0867619345110521e-12,
  "gap_max": 0.0034481270549721436,
  "sec_max": 0.18761812499724329,
  "competing_gt_0_5": 0
 }
}

### Per SNR band, REAL audio only (combined WADA/VAD estimate)

| set | n | SNR median (range) | conf mean / frac<0.9 | p\* median (range) | gate p\*<1/D | margin median (range) | margin<1.2 | greedy=mode | beam-5=mode | beam-50=mode | beam-800=mode | WER mode mean (corpus) | WER greedy mean (corpus) | WER beam-50 mean | runner-up 1-char edit | ref in top-2 | C dec s median (max) | budget-exceeded |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| real >=15 dB | 16 | 28.8 (20.4–47.3) | 0.967 / 0.10 | 1.2e-01 (1.3e-04–9.4e-01) | 5/16 | 1.64 (1.03–406.6) | 6/16 | 12/16 | 14/16 | 16/16 | 16/16 | 0.156 (0.161) | 0.149 (0.156) | 0.156 | 16/16 | 6/16 | 11.3 (32) | 0 |
| real 10-15 dB | 8 | 11.5 (10.2–14.0) | 0.907 / 0.28 | 9.0e-08 (5.4e-15–3.7e-02) | 7/8 | 1.05 (1.02–1.1) | 8/8 | 1/8 | 4/8 | 4/8 | 6/8 | 0.363 (0.378) | 0.355 (0.370) | 0.355 | 8/8 | 1/8 | 10.5 (45) | 0 |
| real 5-10 dB | 11 | 6.3 (5.1–8.2) | 0.904 / 0.29 | 8.9e-09 (5.6e-16–6.7e-05) | 11/11 | 1.04 (1.01–1.1) | 11/11 | 1/11 | 3/11 | 8/11 | 9/11 | 0.681 (0.719) | 0.692 (0.734) | 0.681 | 10/11 | 0/11 | 5.9 (21) | 0 |
| real <5 dB | 5 | 4.9 (4.4–4.9) | 0.861 / 0.40 | 1.7e-13 (1.6e-16–2.9e-08) | 5/5 | 1.05 (1.01–1.1) | 5/5 | 0/5 | 2/5 | 2/5 | 2/5 | 0.724 (0.672) | 0.759 (0.705) | 0.759 | 5/5 | 0/5 | 4.6 (38) | 0 |

### Per SNR band, SYNTHETIC VHF degradation of the 8 A4 ATCO2 clips

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

### Misses

- greedy ≠ mode on `uwb-atcc_TWR-A5lZHJ_002805_003388_PIAT` (SNR 34.9): p(greedy)/p* = 0.538; WER greedy 0.26 vs mode 0.21
- beam-5 ≠ mode on `-Radar_127_350MHz_20201026_111634-A__000000-000395` (SNR 40.1): p(beam)/p* = 0.648; WER beam 0.31 vs mode 0.31
- greedy ≠ mode on `-Radar_127_350MHz_20201026_111634-A__000000-000395` (SNR 40.1): p(greedy)/p* = 0.369; WER greedy 0.23 vs mode 0.31
- beam-5 ≠ mode on `_Radar_120_520MHz_20201028_151125-G__000444-000934` (SNR 20.4): p(beam)/p* = 0.908; WER beam 0.09 vs mode 0.18
- greedy ≠ mode on `_Radar_120_520MHz_20201028_151125-G__000444-000934` (SNR 20.4): p(greedy)/p* = 0.908; WER greedy 0.09 vs mode 0.18
- greedy ≠ mode on `_Tower_134_560MHz_20201025_144043-B__000000-000332` (SNR 27.2): p(greedy)/p* = 0.696; WER greedy 0.22 vs mode 0.22
- greedy ≠ mode on `ON_Tower_118_3MHz_20210503_152021-A__000271-000690` (SNR 10.2): p(greedy)/p* = 0.766; WER greedy 0.53 vs mode 0.53
- beam-5 ≠ mode on `_Control_121_7MHz_20210504_152004-A__000409-000840` (SNR 10.4): p(beam)/p* = 0.733; WER beam 0.41 vs mode 0.47
- beam-50 ≠ mode on `_Control_121_7MHz_20210504_152004-A__000409-000840` (SNR 10.4): p(beam)/p* = 0.897; WER beam 0.41 vs mode 0.47
- greedy ≠ mode on `_Control_121_7MHz_20210504_152004-A__000409-000840` (SNR 10.4): p(greedy)/p* = 0.469; WER greedy 0.41 vs mode 0.47
- beam-5 ≠ mode on `CH_Tower_118_1MHz_20210412_155616-B__001006-001398` (SNR 11.4): p(beam)/p* = 0.597; WER beam 0.56 vs mode 0.56
- beam-50 ≠ mode on `CH_Tower_118_1MHz_20210412_155616-B__001006-001398` (SNR 11.4): p(beam)/p* = 0.606; WER beam 0.56 vs mode 0.56
- beam-800 ≠ mode on `CH_Tower_118_1MHz_20210412_155616-B__001006-001398` (SNR 11.4): p(beam)/p* = 0.851; WER beam 0.56 vs mode 0.56
- greedy ≠ mode on `CH_Tower_118_1MHz_20210412_155616-B__001006-001398` (SNR 11.4): p(greedy)/p* = 0.403; WER greedy 0.56 vs mode 0.56
- beam-800 ≠ mode on `_Control_121_7MHz_20210502_065520-A__000018-000661` (SNR 11.6): p(beam)/p* = 0.952; WER beam 0.23 vs mode 0.23
- greedy ≠ mode on `_Control_121_7MHz_20210502_065520-A__000018-000661` (SNR 11.6): p(greedy)/p* = 0.821; WER greedy 0.23 vs mode 0.23
- beam-5 ≠ mode on `_Control_121_7MHz_20210503_151946-A__000012-000584` (SNR 12.7): p(beam)/p* = 0.919; WER beam 0.45 vs mode 0.45
- beam-50 ≠ mode on `_Control_121_7MHz_20210503_151946-A__000012-000584` (SNR 12.7): p(beam)/p* = 0.919; WER beam 0.45 vs mode 0.45
- greedy ≠ mode on `_Control_121_7MHz_20210503_151946-A__000012-000584` (SNR 12.7): p(greedy)/p* = 0.919; WER greedy 0.45 vs mode 0.45
- beam-5 ≠ mode on `_Control_121_7MHz_20210502_152026-A__000025-000608` (SNR 13.0): p(beam)/p* = 0.791; WER beam 0.41 vs mode 0.41
- beam-50 ≠ mode on `_Control_121_7MHz_20210502_152026-A__000025-000608` (SNR 13.0): p(beam)/p* = 0.941; WER beam 0.41 vs mode 0.41
- greedy ≠ mode on `_Control_121_7MHz_20210502_152026-A__000025-000608` (SNR 13.0): p(greedy)/p* = 0.522; WER greedy 0.41 vs mode 0.41
- greedy ≠ mode on `_ApronS_121_75MHz_20210414_100142-A__000028-000380` (SNR 14.0): p(greedy)/p* = 0.669; WER greedy 0.25 vs mode 0.25
- beam-5 ≠ mode on `EY_Tower_120_5MHz_20210503_083640-A__000420-000760` (SNR 4.4): p(beam)/p* = 0.269; WER beam 0.73 vs mode 0.64
- beam-50 ≠ mode on `EY_Tower_120_5MHz_20210503_083640-A__000420-000760` (SNR 4.4): p(beam)/p* = 0.824; WER beam 0.73 vs mode 0.64
- beam-800 ≠ mode on `EY_Tower_120_5MHz_20210503_083640-A__000420-000760` (SNR 4.4): p(beam)/p* = 0.871; WER beam 0.64 vs mode 0.64
- greedy ≠ mode on `EY_Tower_120_5MHz_20210503_083640-A__000420-000760` (SNR 4.4): p(greedy)/p* = 0.269; WER greedy 0.73 vs mode 0.64
- beam-5 ≠ mode on `EY_Tower_120_5MHz_20210501_014446-A__000444-000799` (SNR 4.7): p(beam)/p* = 0.419; WER beam 1.00 vs mode 0.92
- beam-50 ≠ mode on `EY_Tower_120_5MHz_20210501_014446-A__000444-000799` (SNR 4.7): p(beam)/p* = 0.799; WER beam 1.00 vs mode 0.92
- beam-800 ≠ mode on `EY_Tower_120_5MHz_20210501_014446-A__000444-000799` (SNR 4.7): p(beam)/p* = 0.861; WER beam 0.92 vs mode 0.92
- greedy ≠ mode on `EY_Tower_120_5MHz_20210501_014446-A__000444-000799` (SNR 4.7): p(greedy)/p* = 0.209; WER greedy 1.00 vs mode 0.92
- greedy ≠ mode on `EY_Tower_120_5MHz_20210502_235050-A__000324-000909` (SNR 4.9): p(greedy)/p* = 0.388; WER greedy 0.40 vs mode 0.40
- beam-5 ≠ mode on `_Control_121_7MHz_20210503_140302-B__000023-000548` (SNR 4.9): p(beam)/p* = 0.599; WER beam 1.00 vs mode 1.00
- beam-50 ≠ mode on `_Control_121_7MHz_20210503_140302-B__000023-000548` (SNR 4.9): p(beam)/p* = 0.599; WER beam 1.00 vs mode 1.00
- beam-800 ≠ mode on `_Control_121_7MHz_20210503_140302-B__000023-000548` (SNR 4.9): p(beam)/p* = 0.929; WER beam 1.00 vs mode 1.00
- greedy ≠ mode on `_Control_121_7MHz_20210503_140302-B__000023-000548` (SNR 4.9): p(greedy)/p* = 0.232; WER greedy 1.00 vs mode 1.00
- greedy ≠ mode on `EY_Tower_120_5MHz_20210430_044251-A__000314-000711` (SNR 4.9): p(greedy)/p* = 0.453; WER greedy 0.67 vs mode 0.67
- greedy ≠ mode on `EY_Tower_120_5MHz_20210502_062227-A__000356-000785` (SNR 5.1): p(greedy)/p* = 0.358; WER greedy 0.36 vs mode 0.45
- beam-5 ≠ mode on `ON_Tower_118_3MHz_20210423_093650-D__000016-000381` (SNR 5.4): p(beam)/p* = 0.616; WER beam 0.73 vs mode 0.64
- greedy ≠ mode on `ON_Tower_118_3MHz_20210423_093650-D__000016-000381` (SNR 5.4): p(greedy)/p* = 0.410; WER greedy 0.73 vs mode 0.64
- beam-5 ≠ mode on `ON_Tower_118_3MHz_20210502_065945-D__000012-000312` (SNR 6.0): p(beam)/p* = 0.953; WER beam 0.62 vs mode 0.50
- greedy ≠ mode on `ON_Tower_118_3MHz_20210502_065945-D__000012-000312` (SNR 6.0): p(greedy)/p* = 0.588; WER greedy 0.50 vs mode 0.50
- greedy ≠ mode on `EY_Tower_120_5MHz_20210504_065016-A__000428-000883` (SNR 6.2): p(greedy)/p* = 0.409; WER greedy 0.60 vs mode 0.60
- beam-5 ≠ mode on `EY_Tower_120_5MHz_20210504_213748-A__000006-000611` (SNR 6.3): p(beam)/p* = 0.174; WER beam 1.00 vs mode 1.00
- beam-50 ≠ mode on `EY_Tower_120_5MHz_20210504_213748-A__000006-000611` (SNR 6.3): p(beam)/p* = 0.493; WER beam 1.00 vs mode 1.00
- beam-800 ≠ mode on `EY_Tower_120_5MHz_20210504_213748-A__000006-000611` (SNR 6.3): p(beam)/p* = 0.872; WER beam 1.00 vs mode 1.00
- greedy ≠ mode on `EY_Tower_120_5MHz_20210504_213748-A__000006-000611` (SNR 6.3): p(greedy)/p* = 0.059; WER greedy 1.00 vs mode 1.00
- beam-5 ≠ mode on `ON_Tower_118_3MHz_20210503_082715-D__000606-000907` (SNR 6.3): p(beam)/p* = 0.826; WER beam 0.57 vs mode 0.57
- beam-50 ≠ mode on `ON_Tower_118_3MHz_20210503_082715-D__000606-000907` (SNR 6.3): p(beam)/p* = 0.826; WER beam 0.57 vs mode 0.57
- greedy ≠ mode on `ON_Tower_118_3MHz_20210503_082715-D__000606-000907` (SNR 6.3): p(greedy)/p* = 0.826; WER greedy 0.57 vs mode 0.57
- beam-5 ≠ mode on `_Tower_119_605MHz_20201029_102129-B__000639-001262` (SNR 6.4): p(beam)/p* = 0.463; WER beam 1.00 vs mode 1.00
- beam-50 ≠ mode on `_Tower_119_605MHz_20201029_102129-B__000639-001262` (SNR 6.4): p(beam)/p* = 0.852; WER beam 1.00 vs mode 1.00
- beam-800 ≠ mode on `_Tower_119_605MHz_20201029_102129-B__000639-001262` (SNR 6.4): p(beam)/p* = 0.935; WER beam 1.00 vs mode 1.00
- greedy ≠ mode on `_Tower_119_605MHz_20201029_102129-B__000639-001262` (SNR 6.4): p(greedy)/p* = 0.183; WER greedy 1.00 vs mode 1.00
- beam-5 ≠ mode on `CH_Tower_118_1MHz_20210414_160105-B__000665-000968` (SNR 7.4): p(beam)/p* = 0.980; WER beam 0.22 vs mode 0.22
- greedy ≠ mode on `CH_Tower_118_1MHz_20210414_160105-B__000665-000968` (SNR 7.4): p(greedy)/p* = 0.795; WER greedy 0.22 vs mode 0.22
- beam-5 ≠ mode on `ON_Tower_118_3MHz_20210503_082715-A__000005-000540` (SNR 8.2): p(beam)/p* = 0.970; WER beam 0.67 vs mode 0.61
- greedy ≠ mode on `ON_Tower_118_3MHz_20210503_082715-A__000005-000540` (SNR 8.2): p(greedy)/p* = 0.575; WER greedy 0.72 vs mode 0.61
- beam-5 ≠ mode on `IK_Tower_118_3MHz_20210503_203710-B__000488-000941` (SNR 8.2): p(beam)/p* = 0.272; WER beam 1.00 vs mode 1.00
- greedy ≠ mode on `IK_Tower_118_3MHz_20210503_203710-B__000488-000941` (SNR 8.2): p(greedy)/p* = 0.272; WER greedy 1.00 vs mode 1.00
- beam-800 ≠ mode on `9_605MHz_20201028_185619-A__000000-000536__vhf10dB` (SNR 10.2): p(beam)/p* = 0.989; WER beam 0.40 vs mode 0.40
- greedy ≠ mode on `9_605MHz_20201028_185619-A__000000-000536__vhf10dB` (SNR 10.2): p(greedy)/p* = 0.433; WER greedy 0.53 vs mode 0.40
- beam-5 ≠ mode on `19_605MHz_20201028_185619-A__000000-000536__vhf5dB` (SNR 5.1): p(beam)/p* = 0.994; WER beam 0.93 vs mode 0.93
- beam-50 ≠ mode on `19_605MHz_20201028_185619-A__000000-000536__vhf5dB` (SNR 5.1): p(beam)/p* = 0.979; WER beam 0.93 vs mode 0.93
- greedy ≠ mode on `19_605MHz_20201028_185619-A__000000-000536__vhf5dB` (SNR 5.1): p(greedy)/p* = 0.215; WER greedy 0.93 vs mode 0.93
- beam-5 ≠ mode on `27_350MHz_20201026_111634-A__000000-000395__vhf5dB` (SNR 3.3): p(beam)/p* = 0.975; WER beam 0.77 vs mode 0.77
- beam-50 ≠ mode on `27_350MHz_20201026_111634-A__000000-000395__vhf5dB` (SNR 3.3): p(beam)/p* = 0.975; WER beam 0.77 vs mode 0.77
- greedy ≠ mode on `27_350MHz_20201026_111634-A__000000-000395__vhf5dB` (SNR 3.3): p(greedy)/p* = 0.540; WER greedy 0.77 vs mode 0.77
- greedy ≠ mode on `20_520MHz_20201028_151125-A__000000-000444__vhf5dB` (SNR 5.5): p(greedy)/p* = 0.659; WER greedy 0.42 vs mode 0.50
- beam-5 ≠ mode on `20_520MHz_20201028_151125-G__000444-000934__vhf5dB` (SNR 5.2): p(beam)/p* = 0.573; WER beam 0.91 vs mode 0.82
- beam-50 ≠ mode on `20_520MHz_20201028_151125-G__000444-000934__vhf5dB` (SNR 5.2): p(beam)/p* = 0.705; WER beam 0.82 vs mode 0.82
- beam-800 ≠ mode on `20_520MHz_20201028_151125-G__000444-000934__vhf5dB` (SNR 5.2): p(beam)/p* = 0.854; WER beam 0.82 vs mode 0.82
- greedy ≠ mode on `20_520MHz_20201028_151125-G__000444-000934__vhf5dB` (SNR 5.2): p(greedy)/p* = 0.292; WER greedy 0.91 vs mode 0.82
- beam-5 ≠ mode on `0_520MHz_20201026_145941-G__000000-000349__vhf10dB` (SNR 11.2): p(beam)/p* = 0.956; WER beam 0.67 vs mode 0.56
- greedy ≠ mode on `0_520MHz_20201026_145941-G__000000-000349__vhf10dB` (SNR 11.2): p(greedy)/p* = 0.956; WER greedy 0.67 vs mode 0.56
- beam-5 ≠ mode on `20_520MHz_20201026_145941-G__000000-000349__vhf5dB` (SNR 6.0): p(beam)/p* = 0.958; WER beam 0.78 vs mode 0.78
- greedy ≠ mode on `20_520MHz_20201026_145941-G__000000-000349__vhf5dB` (SNR 6.0): p(greedy)/p* = 0.500; WER greedy 0.78 vs mode 0.78
- beam-5 ≠ mode on `4_560MHz_20201025_144043-B__000000-000332__vhf10dB` (SNR 10.5): p(beam)/p* = 0.671; WER beam 0.44 vs mode 0.44
- greedy ≠ mode on `4_560MHz_20201025_144043-B__000000-000332__vhf10dB` (SNR 10.5): p(greedy)/p* = 0.322; WER greedy 0.44 vs mode 0.44
- greedy ≠ mode on `34_560MHz_20201025_144043-B__000000-000332__vhf5dB` (SNR 4.8): p(greedy)/p* = 0.833; WER greedy 0.56 vs mode 0.44
- beam-50 ≠ mode on `4_560MHz_20201025_144043-A__000334-000742__vhf10dB` (SNR 10.5): p(beam)/p* = 0.961; WER beam 0.27 vs mode 0.27
- greedy ≠ mode on `4_560MHz_20201025_144043-A__000334-000742__vhf10dB` (SNR 10.5): p(greedy)/p* = 0.961; WER greedy 0.27 vs mode 0.27
- beam-5 ≠ mode on `4_560MHz_20201025_144043-B__000744-001212__vhf10dB` (SNR 10.4): p(beam)/p* = 0.970; WER beam 0.62 vs mode 0.62
- beam-50 ≠ mode on `4_560MHz_20201025_144043-B__000744-001212__vhf10dB` (SNR 10.4): p(beam)/p* = 0.970; WER beam 0.62 vs mode 0.62
- greedy ≠ mode on `4_560MHz_20201025_144043-B__000744-001212__vhf10dB` (SNR 10.4): p(greedy)/p* = 0.469; WER greedy 0.62 vs mode 0.62
- beam-5 ≠ mode on `34_560MHz_20201025_144043-B__000744-001212__vhf5dB` (SNR 5.2): p(beam)/p* = 0.716; WER beam 0.94 vs mode 0.94
- greedy ≠ mode on `34_560MHz_20201025_144043-B__000744-001212__vhf5dB` (SNR 5.2): p(greedy)/p* = 0.708; WER greedy 0.94 vs mode 0.94

### Paired: A4 ATCO2 clip clean → +VHF 10 dB → +VHF 5 dB

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

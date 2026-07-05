# Benchmark Results: parallel_outcome

## 7-1 intel

| Name (time in s)                                                               | Min            | Mean           | Median         | Max            | StdDev          | Rounds |
|:------------------------------------------------------------------------------ |:-------------- |:-------------- |:-------------- |:-------------- |:--------------- |:------ |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-16-sd]` | 18.0107 (1.0)  | 18.3486 (1.0)  | 18.3486 (1.0)  | 18.6865 (1.0)  | 0.4778 (56.02)  | 2      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-8-sd]`  | 20.5970 (1.14) | 20.6030 (1.12) | 20.6030 (1.12) | 20.6090 (1.10) | 0.0085 (1.0)    | 2      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-32-sd]` | 21.3169 (1.18) | 21.3628 (1.16) | 21.3628 (1.16) | 21.4088 (1.15) | 0.0650 (7.62)   | 2      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-4-sd]`  | 22.6280 (1.26) | 23.1370 (1.26) | 23.1370 (1.26) | 23.6459 (1.27) | 0.7198 (84.38)  | 2      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-2-sd]`  | 32.4069 (1.80) | 33.0532 (1.80) | 33.0532 (1.80) | 33.6994 (1.80) | 0.9139 (107.14) | 2      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-1-sd]`  | 55.4144 (3.08) | 55.8382 (3.04) | 55.8382 (3.04) | 56.2620 (3.01) | 0.5993 (70.26)  | 2      |

## 7-1 intel

| Name (time in s)                                                               | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:------------------------------------------------------------------------------ |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-16-sd]` | 16.7668 (1.0)  | 18.5460 (1.0)  | 18.5035 (1.0)  | 19.8789 (1.0)  | 1.1472 (8.09) | 5      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-8-sd]`  | 20.7094 (1.24) | 20.8646 (1.13) | 20.8006 (1.12) | 21.0236 (1.06) | 0.1417 (1.0)  | 5      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-32-sd]` | 20.9699 (1.25) | 21.7123 (1.17) | 21.7334 (1.17) | 22.2574 (1.12) | 0.4964 (3.50) | 5      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-4-sd]`  | 22.7663 (1.36) | 23.2978 (1.26) | 23.4920 (1.27) | 23.6436 (1.19) | 0.4118 (2.91) | 5      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-2-sd]`  | 33.0266 (1.97) | 34.1418 (1.84) | 34.2635 (1.85) | 35.2197 (1.77) | 1.0582 (7.47) | 5      |
| `test_pick_flat_speed[/root/autodl-tmp/data/Example_read/example.imzML-1-sd]`  | 56.5588 (3.37) | 56.7283 (3.06) | 56.6746 (3.06) | 56.9365 (2.86) | 0.1725 (1.22) | 5      |

## 7-1 AMD

### peak pick

| Name (time in s)                                                  | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:----------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-32-sd]` | 13.6553 (1.0)  | 13.8575 (1.0)  | 13.8791 (1.0)  | 14.0380 (1.0)  | 0.1922 (1.0)  | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-16-sd]` | 14.8705 (1.09) | 15.0698 (1.09) | 15.0231 (1.08) | 15.3158 (1.09) | 0.2263 (1.18) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-8-sd]`  | 17.7839 (1.30) | 18.1323 (1.31) | 17.7950 (1.28) | 18.8180 (1.34) | 0.5939 (3.09) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-4-sd]`  | 21.2389 (1.56) | 21.9311 (1.58) | 22.2100 (1.60) | 22.3445 (1.59) | 0.6032 (3.14) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-2-sd]`  | 34.3365 (2.51) | 34.9423 (2.52) | 34.7844 (2.51) | 35.7062 (2.54) | 0.6984 (3.63) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-1-sd]`  | 57.2754 (4.19) | 57.8713 (4.18) | 57.9129 (4.17) | 58.4257 (4.16) | 0.5763 (3.00) | 3      |

| Name (time in s)                                                  | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:----------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-32-sd]` | 11.1470 (1.0)  | 11.2333 (1.0)  | 11.2591 (1.0)  | 11.2937 (1.0)  | 0.0767 (1.0)  | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-16-sd]` | 12.9302 (1.16) | 13.0622 (1.16) | 12.9643 (1.15) | 13.2919 (1.18) | 0.1997 (2.60) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-8-sd]`  | 15.4936 (1.39) | 15.7619 (1.40) | 15.6467 (1.39) | 16.1453 (1.43) | 0.3408 (4.44) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-4-sd]`  | 22.2769 (2.00) | 22.3500 (1.99) | 22.3362 (1.98) | 22.4367 (1.99) | 0.0808 (1.05) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-2-sd]`  | 31.0143 (2.78) | 31.2813 (2.78) | 31.2286 (2.77) | 31.6010 (2.80) | 0.2969 (3.87) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-1-sd]`  | 54.0666 (4.85) | 54.1918 (4.82) | 54.1937 (4.81) | 54.3150 (4.81) | 0.1242 (1.62) | 3      |

## 7-1 baseline m=5

| Name (time in s)                                                              | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:----------------------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-32-snip_numba]` | 22.8146 (1.0)  | 23.1685 (1.00) | 23.2369 (1.01) | 23.4540 (1.01) | 0.3252 (3.42) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-8-snip_numba]`  | 22.9682 (1.01) | 23.0884 (1.00) | 23.0295 (1.00) | 23.2674 (1.00) | 0.1580 (1.66) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-16-snip_numba]` | 23.7319 (1.04) | 24.1616 (1.05) | 23.9748 (1.04) | 24.7781 (1.06) | 0.5476 (5.75) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-4-snip_numba]`  | 24.4004 (1.07) | 24.5025 (1.06) | 24.5183 (1.06) | 24.5887 (1.06) | 0.0952 (1.0)  | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-2-snip_numba]`  | 26.9764 (1.18) | 27.8657 (1.21) | 28.1021 (1.22) | 28.5184 (1.23) | 0.7978 (8.38) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-1-snip_numba]`  | 31.4828 (1.38) | 31.8615 (1.38) | 31.7774 (1.38) | 32.3243 (1.39) | 0.4270 (4.49) | 3      |

## 7-1 baseline m=100

| Name (time in s)                                                              | Min             | Mean            | Median          | Max             | StdDev        | Rounds |
|:----------------------------------------------------------------------------- |:--------------- |:--------------- |:--------------- |:--------------- |:------------- |:------ |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-32-snip_numba]` | 32.1960 (1.0)   | 32.5265 (1.0)   | 32.6446 (1.0)   | 32.7388 (1.0)   | 0.2901 (1.0)  | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-16-snip_numba]` | 36.3715 (1.13)  | 36.6391 (1.13)  | 36.5610 (1.12)  | 36.9848 (1.13)  | 0.3141 (1.08) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-8-snip_numba]`  | 44.8190 (1.39)  | 45.2730 (1.39)  | 45.4509 (1.39)  | 45.5491 (1.39)  | 0.3962 (1.37) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-4-snip_numba]`  | 62.5132 (1.94)  | 63.0711 (1.94)  | 63.2541 (1.94)  | 63.4462 (1.94)  | 0.4927 (1.70) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-2-snip_numba]`  | 99.7343 (3.10)  | 100.5024 (3.09) | 100.6910 (3.08) | 101.0818 (3.09) | 0.6933 (2.39) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-1-snip_numba]`  | 168.5862 (5.24) | 170.3795 (5.24) | 170.4568 (5.22) | 172.0955 (5.26) | 1.7560 (6.05) | 3      |

## 7-1 noise reduction

| Name (time in ms)                                                         | Min                | Mean               | Median             | Max               | StdDev         | Rounds |
|:------------------------------------------------------------------------- |:------------------ |:------------------ |:------------------ |:----------------- |:-------------- |:------ |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-32-savgol_numba]` | 677.7048 (1.0)     | 726.3590 (1.0)     | 717.0860 (1.0)     | 784.2863 (1.0)    | 53.8924 (3.88) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-16-savgol_numba]` | 942.4128 (1.39)    | 963.7180 (1.33)    | 954.1029 (1.33)    | 994.6385 (1.27)   | 27.4084 (1.98) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-8-savgol_numba]`  | 1,354.3513 (2.00)  | 1,430.6561 (1.97)  | 1,445.0345 (2.02)  | 1,492.5824 (1.90) | 70.2283 (5.06) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-4-savgol_numba]`  | 2,255.8819 (3.33)  | 2,270.2337 (3.13)  | 2,271.2386 (3.17)  | 2,283.5804 (2.91) | 13.8766 (1.0)  | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-2-savgol_numba]`  | 3,960.3180 (5.84)  | 3,974.0931 (5.47)  | 3,966.8822 (5.53)  | 3,995.0792 (5.09) | 18.4684 (1.33) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-1-savgol_numba]`  | 7,385.8656 (10.90) | 7,426.2619 (10.22) | 7,440.7758 (10.38) | 7,452.1443 (9.50) | 35.4430 (2.55) | 3      |

| Name (time in ms)                                                           | Min               | Mean              | Median            | Max               | StdDev         | Rounds |
|:--------------------------------------------------------------------------- |:----------------- |:----------------- |:----------------- |:----------------- |:-------------- |:------ |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-32-gaussian_numba]` | 664.7337 (1.0)    | 679.1510 (1.0)    | 676.2905 (1.0)    | 696.4288 (1.0)    | 16.0400 (1.0)  | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-16-gaussian_numba]` | 809.6904 (1.22)   | 836.7266 (1.23)   | 843.5006 (1.25)   | 856.9889 (1.23)   | 24.3660 (1.52) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-8-gaussian_numba]`  | 1,201.9953 (1.81) | 1,227.9569 (1.81) | 1,228.0317 (1.82) | 1,253.8437 (1.80) | 25.9243 (1.62) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-4-gaussian_numba]`  | 1,872.7825 (2.82) | 1,935.3759 (2.85) | 1,905.8878 (2.82) | 2,027.4573 (2.91) | 81.4447 (5.08) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-2-gaussian_numba]`  | 3,227.2684 (4.85) | 3,251.6046 (4.79) | 3,259.1484 (4.82) | 3,268.3970 (4.69) | 21.5771 (1.35) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-1-gaussian_numba]`  | 6,105.9469 (9.19) | 6,169.8708 (9.08) | 6,184.3325 (9.14) | 6,219.3329 (8.93) | 58.0599 (3.62) | 3      |

## 7-1 peak align

| Name (time in s)                                                        | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:----------------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-32-min-ppm]` | 2.2243 (1.0)   | 2.2389 (1.0)   | 2.2389 (1.0)   | 2.2535 (1.0)   | 0.0206 (3.35) | 2      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-16-min-ppm]` | 2.5758 (1.16)  | 2.5837 (1.15)  | 2.5837 (1.15)  | 2.5916 (1.15)  | 0.0112 (1.82) | 2      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-8-min-ppm]`  | 3.5456 (1.59)  | 3.5547 (1.59)  | 3.5547 (1.59)  | 3.5639 (1.58)  | 0.0129 (2.10) | 2      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-4-min-ppm]`  | 5.3876 (2.42)  | 5.3986 (2.41)  | 5.3986 (2.41)  | 5.4097 (2.40)  | 0.0156 (2.54) | 2      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-2-min-ppm]`  | 8.9959 (4.04)  | 9.0199 (4.03)  | 9.0199 (4.03)  | 9.0438 (4.01)  | 0.0339 (5.50) | 2      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-1-min-ppm]`  | 16.1922 (7.28) | 16.1965 (7.23) | 16.1965 (7.23) | 16.2009 (7.19) | 0.0062 (1.0)  | 2      |

## 7-2 AMD

### peak pick

| Name (time in s)                                                  | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:----------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-32-sd]` | 13.9549 (1.0)  | 14.0558 (1.0)  | 14.0486 (1.0)  | 14.1639 (1.0)  | 0.1047 (3.51) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-16-sd]` | 15.5891 (1.12) | 15.6509 (1.11) | 15.6276 (1.11) | 15.7360 (1.11) | 0.0762 (2.55) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-8-sd]`  | 19.6482 (1.41) | 19.6732 (1.40) | 19.6591 (1.40) | 19.7125 (1.39) | 0.0344 (1.15) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-4-sd]`  | 28.0434 (2.01) | 28.0777 (2.00) | 28.0923 (2.00) | 28.0975 (1.98) | 0.0298 (1.0)  | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-2-sd]`  | 44.8144 (3.21) | 44.8747 (3.19) | 44.8589 (3.19) | 44.9237 (3.17) | 0.0433 (1.45) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-1-sd]`  | 78.0240 (5.59) | 78.0594 (5.55) | 78.0745 (5.56) | 78.0798 (5.51) | 0.0308 (1.03) | 3      |

| Name (time in s)                                                    | Min            | Mean           | Median         | Max            | StdDev        | Rounds |
|:------------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------------- |:------ |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-32-diff]` | 8.3418 (1.0)   | 8.4111 (1.0)   | 8.3599 (1.0)   | 8.5314 (1.0)   | 0.1046 (3.10) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-16-diff]` | 9.7876 (1.17)  | 9.9919 (1.19)  | 9.8555 (1.18)  | 10.3325 (1.21) | 0.2969 (8.80) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-8-diff]`  | 13.2206 (1.58) | 13.3100 (1.58) | 13.3139 (1.59) | 13.3955 (1.57) | 0.0875 (2.59) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-4-diff]`  | 19.8895 (2.38) | 19.9271 (2.37) | 19.9371 (2.38) | 19.9548 (2.34) | 0.0337 (1.0)  | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-2-diff]`  | 33.0943 (3.97) | 33.2982 (3.96) | 33.3464 (3.99) | 33.4538 (3.92) | 0.1845 (5.47) | 3      |
| `test_pick_flat_speed[/root/autodl-tmp/data/example.imzML-1-diff]`  | 55.5267 (6.66) | 55.5735 (6.61) | 55.5943 (6.65) | 55.5995 (6.52) | 0.0406 (1.20) | 3      |

### normalization

| Name (time in ms)                                                        | Min               | Mean              | Median            | Max               | StdDev          | Rounds |
|:------------------------------------------------------------------------ |:----------------- |:----------------- |:----------------- |:----------------- |:--------------- |:------ |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-32-rms_numba]` | 751.1614 (1.0)    | 822.7558 (1.0)    | 817.6213 (1.0)    | 899.4847 (1.06)   | 74.2948 (31.79) | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-16-rms_numba]` | 831.2842 (1.11)   | 842.1907 (1.02)   | 846.5162 (1.04)   | 848.7718 (1.0)    | 9.5125 (4.07)   | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-8-rms_numba]`  | 1,189.7021 (1.58) | 1,192.2714 (1.45) | 1,192.8418 (1.46) | 1,194.2702 (1.41) | 2.3369 (1.0)    | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-4-rms_numba]`  | 1,878.3912 (2.50) | 1,893.2579 (2.30) | 1,896.6582 (2.32) | 1,904.7242 (2.24) | 13.4918 (5.77)  | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-2-rms_numba]`  | 3,268.6466 (4.35) | 3,289.2911 (4.00) | 3,299.6110 (4.04) | 3,299.6157 (3.89) | 17.8787 (7.65)  | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-1-rms_numba]`  | 5,506.4338 (7.33) | 5,569.6333 (6.77) | 5,583.5124 (6.83) | 5,618.9536 (6.62) | 57.5296 (24.62) | 3      |

| Name (time in ms)                                                        | Min               | Mean              | Median            | Max               | StdDev           | Rounds |
|:------------------------------------------------------------------------ |:----------------- |:----------------- |:----------------- |:----------------- |:---------------- |:------ |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-32-tic_numba]` | 755.9958 (1.0)    | 778.7838 (1.0)    | 760.1272 (1.0)    | 820.2283 (1.0)    | 35.9514 (10.74)  | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-16-tic_numba]` | 828.7292 (1.10)   | 838.5779 (1.08)   | 843.3114 (1.11)   | 843.6933 (1.03)   | 8.5314 (2.55)    | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-8-tic_numba]`  | 1,093.9713 (1.45) | 1,096.9207 (1.41) | 1,095.0029 (1.44) | 1,101.7880 (1.34) | 4.2466 (1.27)    | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-4-tic_numba]`  | 1,737.3873 (2.30) | 1,739.9153 (2.23) | 1,738.6456 (2.29) | 1,743.7132 (2.13) | 3.3487 (1.0)     | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-2-tic_numba]`  | 2,983.9309 (3.95) | 2,995.6539 (3.85) | 2,983.9527 (3.93) | 3,019.0782 (3.68) | 20.2860 (6.06)   | 3      |
| `test_norm_flat_speed[/root/autodl-tmp/data/example.imzML-1-tic_numba]`  | 5,071.8546 (6.71) | 5,149.0420 (6.61) | 5,109.9658 (6.72) | 5,265.3057 (6.42) | 102.4746 (30.60) | 3      |

### noise_reduction

| Name (time in ms)                                                         | Min                 | Mean                | Median              | Max                 | StdDev          | Rounds |
|:------------------------------------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:--------------- |:------ |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-32-savgol_numba]` | 961.1594 (1.0)      | 994.6621 (1.0)      | 977.5219 (1.0)      | 1,045.3051 (1.0)    | 44.6146 (77.11) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-16-savgol_numba]` | 1,374.9941 (1.43)   | 1,377.2718 (1.38)   | 1,377.1467 (1.41)   | 1,379.6746 (1.32)   | 2.3427 (4.05)   | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-8-savgol_numba]`  | 2,234.5104 (2.32)   | 2,235.1778 (2.25)   | 2,235.4868 (2.29)   | 2,235.5363 (2.14)   | 0.5786 (1.0)    | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-4-savgol_numba]`  | 3,938.7817 (4.10)   | 3,943.3355 (3.96)   | 3,943.3521 (4.03)   | 3,947.8727 (3.78)   | 4.5455 (7.86)   | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-2-savgol_numba]`  | 7,554.8075 (7.86)   | 7,568.6217 (7.61)   | 7,573.5381 (7.75)   | 7,577.5197 (7.25)   | 12.1280 (20.96) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-1-savgol_numba]`  | 14,755.7065 (15.35) | 14,784.8699 (14.86) | 14,763.7036 (15.10) | 14,835.1997 (14.19) | 43.7699 (75.65) | 3      |

| Name (time in ms)                                                           | Min                 | Mean                | Median              | Max                 | StdDev          | Rounds |
|:--------------------------------------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:--------------- |:------ |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-32-gaussian_numba]` | 943.4048 (1.0)      | 1,009.3084 (1.0)    | 995.6187 (1.0)      | 1,088.9018 (1.0)    | 73.7082 (74.92) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-16-gaussian_numba]` | 1,274.7751 (1.35)   | 1,275.7727 (1.26)   | 1,275.8008 (1.28)   | 1,276.7422 (1.17)   | 0.9838 (1.0)    | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-8-gaussian_numba]`  | 2,120.7209 (2.25)   | 2,128.1473 (2.11)   | 2,120.9791 (2.13)   | 2,142.7419 (1.97)   | 12.6400 (12.85) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-4-gaussian_numba]`  | 3,746.2922 (3.97)   | 3,779.7305 (3.74)   | 3,790.2251 (3.81)   | 3,802.6743 (3.49)   | 29.6199 (30.11) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-2-gaussian_numba]`  | 7,183.0391 (7.61)   | 7,222.1552 (7.16)   | 7,235.8735 (7.27)   | 7,247.5529 (6.66)   | 34.3752 (34.94) | 3      |
| `test_nr_flat_speed[/root/autodl-tmp/data/example.imzML-1-gaussian_numba]`  | 14,173.9634 (15.02) | 14,218.8441 (14.09) | 14,239.2120 (14.30) | 14,243.3570 (13.08) | 38.9230 (39.56) | 3      |

### baseline m=100

| Name (time in s)                                                              | Min             | Mean            | Median          | Max             | StdDev        | Rounds |
|:----------------------------------------------------------------------------- |:--------------- |:--------------- |:--------------- |:--------------- |:------------- |:------ |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-32-snip_numba]` | 36.8536 (1.0)   | 37.3044 (1.0)   | 37.0514 (1.0)   | 38.0862 (1.0)   | 0.6620 (1.35) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-16-snip_numba]` | 39.9776 (1.08)  | 41.3944 (1.11)  | 42.0021 (1.13)  | 42.2034 (1.11)  | 1.2311 (2.50) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-8-snip_numba]`  | 48.4593 (1.31)  | 50.1083 (1.34)  | 50.3097 (1.36)  | 51.5560 (1.35)  | 1.5581 (3.17) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-4-snip_numba]`  | 72.1354 (1.96)  | 72.5023 (1.94)  | 72.3103 (1.95)  | 73.0614 (1.92)  | 0.4920 (1.0)  | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-2-snip_numba]`  | 112.7266 (3.06) | 114.1722 (3.06) | 113.9602 (3.08) | 115.8299 (3.04) | 1.5625 (3.18) | 3      |
| `test_baseline_flat_speed[/root/autodl-tmp/data/example.imzML-1-snip_numba]`  | 206.9402 (5.62) | 207.5144 (5.56) | 207.6998 (5.61) | 207.9032 (5.46) | 0.5076 (1.03) | 3      |

### peak align

| Name (time in s)                                                        | Min            | Mean           | Median         | Max            | StdDev         | Rounds |
|:----------------------------------------------------------------------- |:-------------- |:-------------- |:-------------- |:-------------- |:-------------- |:------ |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-32-min-ppm]` | 2.4952 (1.0)   | 2.6442 (1.0)   | 2.6845 (1.0)   | 2.7530 (1.0)   | 0.1336 (87.59) | 3      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-16-min-ppm]` | 3.0080 (1.21)  | 3.0097 (1.14)  | 3.0103 (1.12)  | 3.0109 (1.09)  | 0.0015 (1.0)   | 3      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-8-min-ppm]`  | 4.0465 (1.62)  | 4.0645 (1.54)  | 4.0531 (1.51)  | 4.0939 (1.49)  | 0.0257 (16.85) | 3      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-4-min-ppm]`  | 6.0987 (2.44)  | 6.1447 (2.32)  | 6.1349 (2.29)  | 6.2005 (2.25)  | 0.0516 (33.85) | 3      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-2-min-ppm]`  | 10.3872 (4.16) | 10.4032 (3.93) | 10.4077 (3.88) | 10.4148 (3.78) | 0.0143 (9.40)  | 3      |
| `test_align_flat_speed[/root/autodl-tmp/data/example.imzML-1-min-ppm]`  | 18.2099 (7.30) | 18.2698 (6.91) | 18.2615 (6.80) | 18.3381 (6.66) | 0.0645 (42.28) | 3      |

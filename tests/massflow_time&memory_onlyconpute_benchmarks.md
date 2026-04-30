# Python Time And Memory Benchmarks

Datasets:

| key | file |
| --- | --- |
| min | `/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML` |
| mid | `/Users/dre/Desktop/data/test_data_profile/file_max_profile/file_max_profile.imzML` |
| max | `/Users/dre/Desktop/data/Example_read/example.imzML` |

## Baseline Correction

Time commands:

```bash
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_flat_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | locmin | 1.1311 | 1.1344 | 1.1335 | 1.1390 | 0.0030 | 5 |
| min | batch | snip | 6.4145 | 6.4633 | 6.4648 | 6.5209 | 0.0429 | 5 |
| min | flat | locmin_numba | 130.55 | 134.93 | 135.60 | 136.69 | 2.51 | 5 |
| min | flat | snip_numba | 671.99 | 681.94 | 681.31 | 698.20 | 10.22 | 5 |
| mid | batch | locmin | 1.7306 | 1.7367 | 1.7382 | 1.7438 | 0.0053 | 5 |
| mid | batch | snip | 10.4486 | 10.4936 | 10.5055 | 10.5150 | 0.0276 | 5 |
| mid | flat | locmin_numba | 214.77 | 216.74 | 216.23 | 220.35 | 2.26 | 5 |
| mid | flat | snip_numba | 1060.14 | 1076.10 | 1076.48 | 1093.79 | 12.56 | 5 |
| max | batch | locmin | 34.9041 | 34.9885 | 35.0182 | 35.0506 | 0.0596 | 5 |
| max | batch | snip | 88.0602 | 88.0729 | 88.0701 | 88.0911 | 0.0114 | 5 |
| max | flat | locmin_numba | 112456.88 | 133295.58 | 132634.51 | 148749.60 | 14633.29 | 5 |
| max | flat | snip_numba | 134039.19 | 148105.70 | 141513.81 | 167149.96 | 14730.28 | 5 |

![image-20260428153540246](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428153540246.png)

![image-20260428153600620](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428153600620.png)

<!--注：由于example数据较大，flat测试时需要将数据先cache，导致结果不准，下面为使用pipeline流程测试的结果，稍慢于实际速度-->

| dataset | implementation | method | min  | mean | median | max  | stddev | Rounds |
| ------- | -------------- | ------ | ---- | ---- | ------ | ---- | ------ | ------ |
| min     | flat           | locmin_numba | 1.2043 | 1.2334 | 1.2072 | 1.3204 | 0.0496 | 5 |
| min     | flat           | snip_numba   | 1.6948 | 1.7166 | 1.7113 | 1.7436 | 0.0201 | 5 |
| mid     | flat           | locmin_numba | 2.5709 | 2.6470 | 2.6385 | 2.7029 | 0.0547 | 5 |
| mid     | flat           | snip_numba   | 2.6234 | 3.6850 | 3.7612 | 4.8652 | 1.0347 | 5 |
| max     | flat           | locmin_numba | 7.1289 | 7.1768 | 7.1620 | 7.2843 | 0.0620 | 5 |
| max     | flat           | snip_numba   | 26.5619 | 26.6341 | 26.6445 | 26.6748 | 0.0433 | 5 |

Memory commands:

```bash
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

| dataset | implementation | method | total memory allocated | allocations | main allocator | notes |
| --- | --- | --- | --- | --- | --- | --- |
| min | batch | locmin | 97.7 MiB | 2055 | render:imzml (36.8MiB) | |
| min | batch | snip | 74.7 MiB | 24 | render:imzml (36.8MiB) | |
| min | flat | locmin_numba | 103.3 MiB | 2162 | flat_generator (24.8MiB) | |
| min | flat | snip_numba | 92.0 MiB | 95 | flat_generator (32.6MiB) | |
| mid | batch | locmin | 96.9 MiB | 49 | render:imzml (44.3MiB) | |
| mid | batch | snip | 90.8 MiB | 23 | render:imzml (44.3MiB) | |
| mid | flat | locmin_numba | 127.9 MiB | 161 | flat_generator (49.7MiB) | |
| mid | flat | snip_numba | 119.3 MiB | 87 | flat_generator (43.0MiB) | |
| max | batch | locmin | 149.5 MiB | 64 | resolve_data (73.0MiB) | |
| max | batch | snip | 148.7 MiB | 45 | resolve_data (73.0MiB) | |
| max | flat | locmin_numba | 1022.9 MiB | 69 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | snip_numba | 1022.9 MiB | 65 | read_contiguous_block_flat (219.0MiB) | |

![image-20260428153856405](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428153856405.png)

![image-20260428153651132](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428153651132.png)

## Noise Reduction

Time commands:

```bash
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_flat_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | ma | 300.76 | 311.61 | 305.29 | 342.07 | 17.28 | 5 |
| min | batch | gaussian | 561.40 | 567.70 | 567.22 | 573.65 | 4.88 | 5 |
| min | batch | savgol | 1986.37 | 2018.74 | 2005.34 | 2081.20 | 36.58 | 5 |
| min | flat | ma_numba | 7.66 | 7.88 | 7.83 | 8.10 | 0.19 | 5 |
| min | flat | gaussian_numba | 23.68 | 24.12 | 24.13 | 24.49 | 0.30 | 5 |
| min | flat | savgol_numba | 27.31 | 27.76 | 27.50 | 28.66 | 0.55 | 5 |
| mid | batch | ma | 399.16 | 403.62 | 404.81 | 406.00 | 2.89 | 5 |
| mid | batch | gaussian | 718.66 | 722.98 | 722.47 | 728.67 | 3.68 | 5 |
| mid | batch | savgol | 2470.43 | 2481.41 | 2480.30 | 2496.83 | 9.68 | 5 |
| mid | flat | ma_numba | 11.93 | 12.07 | 12.08 | 12.20 | 0.12 | 5 |
| mid | flat | gaussian_numba | 38.94 | 40.45 | 39.92 | 43.85 | 1.99 | 5 |
| mid | flat | savgol_numba | 43.75 | 44.10 | 44.06 | 44.75 | 0.40 | 5 |
| max | batch | ma | 1660.79 | 1928.02 | 1739.78 | 2274.39 | 302.13 | 5 |
| max | batch | gaussian | 1940.55 | 2013.80 | 1948.17 | 2274.79 | 146.14 | 5 |
| max | batch | savgol | 3986.28 | 4034.30 | 4036.24 | 4085.49 | 47.16 | 5 |
| max | flat | ma_numba | 154.06 | 174.36 | 155.96 | 245.30 | 39.78 | 5 |
| max | flat | gaussian_numba | 430.76 | 441.87 | 441.63 | 452.99 | 8.67 | 5 |
| max | flat | savgol_numba | 445.43 | 468.67 | 471.03 | 482.41 | 14.09 | 5 |

![image-20260428154823544](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428154823544.png)

![image-20260428154841441](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428154841441.png)

Memory commands:

```bash
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

| dataset | implementation | method | total memory allocated | allocations | main allocator | notes |
| --- | --- | --- | --- | --- | --- | --- |
| min | batch | ma | 82.9 MiB | 78 | render:imzml (36.8MiB) | |
| min | batch | gaussian | 78.7 MiB | 30 | render:imzml (36.8MiB) | |
| min | batch | savgol | 74.7 MiB | 27 | render:imzml (36.8MiB) | |
| min | flat | ma_numba | 99.4 MiB | 2093 | render:imzml (36.6MiB) | |
| min | flat | gaussian_numba | 74.8 MiB | 57 | render:imzml (36.6MiB) | |
| min | flat | savgol_numba | 74.7 MiB | 56 | render:imzml (36.6MiB) | |
| mid | batch | ma | 96.9 MiB | 51 | render:imzml (44.3MiB) | |
| mid | batch | gaussian | 91.8 MiB | 25 | render:imzml (44.3MiB) | |
| mid | batch | savgol | 89.8 MiB | 22 | render:imzml (44.3MiB) | |
| mid | flat | ma_numba | 94.6 MiB | 86 | render:imzml (44.1MiB) | |
| mid | flat | gaussian_numba | 89.4 MiB | 47 | render:imzml (44.1MiB) | |
| mid | flat | savgol_numba | 89.4 MiB | 43 | render:imzml (44.1MiB) | |
| max | batch | ma | 220.1 MiB | 70 | convolve (146.6MiB) | |
| max | batch | gaussian | 220.0 MiB | 47 | convolve (146.6MiB) | |
| max | batch | savgol | 147.3 MiB | 48 | resolve_data (73.0MiB) | |
| max | flat | ma_numba | 439.3 MiB | 80 | smooth_signal_ma_numba (219.0MiB) | |
| max | flat | gaussian_numba | 440.4 MiB | 82 | smooth_signal_gaussian_numba (219.0MiB) | |
| max | flat | savgol_numba | 440.4 MiB | 80 | smooth_signal_savgol_numba (219.0MiB) | |

![image-20260428154924177](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428154924177.png)

![image-20260428154945744](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428154945744.png)

![image-20260428155010659](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428155010659.png)

![image-20260428155030353](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428155030353.png)

## Normalization

Time commands:

```bash
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_batch_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_flat_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | tic | 162.6904 | 164.2962 | 163.4760 | 167.5874 | 1.9588 | 5 |
| min | batch | rms | 291.2572 | 293.0027 | 292.6805 | 295.6136 | 1.8387 | 5 |
| min | flat | tic_numba | 9.7031 | 9.8635 | 9.8848 | 10.0408 | 0.1410 | 5 |
| min | flat | rms_numba | 9.5685 | 9.6915 | 9.7070 | 9.8115 | 0.1177 | 5 |
| min | flat | ref_numba | 5.4549 | 5.5878 | 5.5468 | 5.7152 | 0.1085 | 5 |
| mid | batch | tic | 210.3838 | 211.4506 | 211.3409 | 212.5107 | 0.8393 | 5 |
| mid | batch | rms | 380.6927 | 382.7615 | 382.8047 | 384.8069 | 1.4577 | 5 |
| mid | flat | tic_numba | 14.7972 | 15.0500 | 15.1602 | 15.2734 | 0.2274 | 5 |
| mid | flat | rms_numba | 14.7828 | 15.0179 | 14.9827 | 15.2770 | 0.1928 | 5 |
| mid | flat | ref_numba | 8.5352 | 8.7572 | 8.6519 | 8.9849 | 0.2068 | 5 |
| max | batch | tic | 812.4262 | 858.5671 | 823.7050 | 938.9686 | 56.0191 | 5 |
| max | batch | rms | 1580.0045 | 1635.1218 | 1593.3326 | 1756.5840 | 73.7023 | 5 |
| max | flat | tic_numba | 190.8477 | 198.8921 | 193.8262 | 214.7626 | 9.6715 | 5 |
| max | flat | rms_numba | 190.9602 | 242.8363 | 194.9674 | 403.7213 | 91.3836 | 5 |
| max | flat | ref_numba | 144.6160 | 147.2572 | 147.0023 | 150.7912 | 2.2946 | 5 |

![image-20260428160342726](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160342726.png)

![image-20260428160515100](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160515100.png)

Memory commands:

```bash
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

| dataset | implementation | method | total memory allocated | allocations | main allocator | notes |
| --- | --- | --- | --- | --- | --- | --- |
| min | batch | tic | 82.9 MiB | 72 | render:imzml (36.8MiB) | |
| min | batch | rms | 76.8 MiB | 27 | render:imzml (36.8MiB) | |
| min | flat | tic_numba | 99.6 MiB | 2092 | render:imzml (36.6MiB) | |
| min | flat | rms_numba | 74.4 MiB | 45 | render:imzml (36.6MiB) | |
| min | flat | ref_numba | 75.3 MiB | 107 | render:imzml (36.6MiB) | |
| mid | batch | tic | 96.9 MiB | 47 | render:imzml (44.3MiB) | |
| mid | batch | rms | 89.8 MiB | 20 | render:imzml (44.3MiB) | |
| mid | flat | tic_numba | 95.6 MiB | 85 | render:imzml (44.1MiB) | |
| mid | flat | rms_numba | 89.4 MiB | 44 | render:imzml (44.1MiB) | |
| mid | flat | ref_numba | 89.7 MiB | 92 | render:imzml (44.1MiB) | |
| max | batch | tic | 146.6 MiB | 66 | resolve_data (73.0MiB) | |
| max | batch | rms | 146.6 MiB | 47 | resolve_data (73.0MiB) | |
| max | flat | tic_numba | 439.4 MiB | 83 | normalizer_numba (219.0MiB) | |
| max | flat | rms_numba | 438.9 MiB | 67 | normalizer_numba (219.0MiB) | |
| max | flat | ref_numba | 439.4 MiB | 81 | normalizer_numba (219.0MiB) | |

![image-20260428160633912](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160633912.png)

![image-20260428160703512](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160703512.png)

![image-20260428160740118](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160740118.png)

## Peak Pick

Time commands:

```bash
pytest tests/test_pick_speed.py::TestPick::test_pick_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_pick_speed.py::TestPick::test_pick_flat_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | origin | 3.6505 | 3.6639 | 3.6582 | 3.6983 | 0.0195 | 5 |
| min | flat | quantile | 420.6285 | 428.8802 | 429.9599 | 434.3725 | 5.6892 | 5 |
| min | flat | diff | 92.5882 | 93.6321 | 93.6824 | 94.4190 | 0.7693 | 5 |
| min | flat | sd | 139.9152 | 140.8043 | 140.9937 | 141.3369 | 0.5633 | 5 |
| min | flat | mad | 709.8871 | 717.7916 | 712.7316 | 731.6925 | 9.2975 | 5 |
| mid | batch | origin | 4.8658 | 4.8761 | 4.8732 | 4.8852 | 0.0086 | 5 |
| mid | flat | quantile | 669.2692 | 674.3095 | 670.9308 | 686.1438 | 6.9336 | 5 |
| mid | flat | diff | 142.2649 | 144.7512 | 144.8588 | 146.1282 | 1.4951 | 5 |
| mid | flat | sd | 216.5575 | 217.8723 | 217.6926 | 220.1715 | 1.3700 | 5 |
| mid | flat | mad | 1124.0133 | 1133.4865 | 1134.2369 | 1140.8427 | 6.5671 | 5 |
| max | batch | origin | 36.6172 | 36.7218 | 36.6833 | 36.8416 | 0.1067 | 5 |
| max | flat | quantile | 25201.3968 | 28027.8260 | 27199.8571 | 33082.1962 | 2970.5881 | 5 |
| max | flat | diff | 2903.4213 | 2973.3779 | 2949.0915 | 3102.8177 | 78.9338 | 5 |
| max | flat | sd | 25036.9244 | 31781.4732 | 34174.6944 | 36326.6448 | 4867.1634 | 5 |
| max | flat | mad | 40250.9033 | 42983.5111 | 42942.0202 | 46543.7809 | 2706.1032 | 5 |

![image-20260428163857081](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428163857081.png)

![image-20260428163914688](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428163914688.png)

<!--注：由于example数据较大，flat测试时需要将数据先cache，导致结果不准，下面为使用pipeline流程测试的结果，稍慢于实际速度-->

| dataset | implementation | method | min | mean | median | median | stddev | rounds |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| min  | flat | diff | 1.1893 | 1.1949 | 1.1911 | 1.2132 | 0.0103 | 5 |
| min  | flat | sd   | 1.1929 | 1.1970 | 1.1950 | 1.2021 | 0.0043 | 5 |
| min  | flat | quantile | 1.4617 | 1.4895 | 1.4759 | 1.5284 | 0.0283 | 5 |
| min  | flat | mad  | 1.9668 | 1.9701 | 1.9688 | 1.9740 | 0.0033 | 5 |
| mid  | flat | diff | 1.4579 | 1.4595 | 1.4598 | 1.4610 | 0.0015 | 5 |
| mid  | flat | sd   | 1.4681 | 1.4768 | 1.4706 | 1.4981 | 0.0125 | 5 |
| mid  | flat | quantile | 2.0726 | 2.0830 | 2.0769 | 2.1052 | 0.0134 | 5 |
| mid  | flat | mad  | 2.9989 | 3.0152 | 3.0059 | 3.0476 | 0.0194 | 5 |
| max  | flat | diff | 6.0222 | 6.0347 | 6.0319 | 6.0464 | 0.0100 | 5 |
| max  | flat | sd   | 7.9860 | 8.0348 | 8.0479 | 8.0552 | 0.0286 | 5 |
| max  | flat | quantile | 24.7824 | 24.8683 | 24.8303 | 25.0101 | 0.0887 | 5 |
| max  | flat | mad  | 41.7309 | 41.7990 | 41.8071 | 41.9015 | 0.0695 | 5 |

Memory commands:

```bash
pytest tests/test_pick_memory.py::TestPick::test_pick_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_pick_memory.py::TestPick::test_pick_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

| dataset | implementation | method | total memory allocated | allocations | main allocator | notes |
| --- | --- | --- | --- | --- | --- | --- |
| min | batch | origin | 99.6 MiB | 2079 | render:imzml (36.7MiB) | |
| min | flat | quantile | 102.6 MiB | 2127 | render:imzml (36.4MiB) | |
| min | flat | diff | 102.6 MiB | 2127 | render:imzml (36.4MiB) | |
| min | flat | sd | 74.2 MiB | 49 | render:imzml (36.5MiB) | |
| min | flat | mad | 74.2 MiB | 49 | render:imzml (36.5MiB) | |
| mid | batch | origin | 96.3 MiB | 59 | render:imzml (44.1MiB) | |
| mid | flat | quantile | 95.1 MiB | 90 | render:imzml (43.9MiB) | |
| mid | flat | diff | 89.0 MiB | 47 | render:imzml (43.9MiB) | |
| mid | flat | sd | 89.0 MiB | 49 | render:imzml (43.9MiB) | |
| mid | flat | mad | 89.2 MiB | 47 | render:imzml (44.0MiB) | |
| max | batch | origin | 83.1 MiB | 82 | resolve_data (73.0MiB) | |
| max | flat | quantile | 677.0 MiB | 110 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | diff | 521.1 MiB | 80 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | sd | 706.7 MiB | 76 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | mad | 714.3 MiB | 70 | read_contiguous_block_flat (219.0MiB) | |

![image-20260428163956065](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428163956065.png)

![image-20260428164049851](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428164049851.png)

![image-20260428164122821](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428164122821.png)

## Peak Align

Time commands:

```bash
pytest tests/test_align_speed.py::TestAlign::test_align_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_align_speed.py::TestAlign::test_align_flat_speed --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | units | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | ppm | 524.7981 | 528.0402 | 526.8753 | 532.9519 | 3.1484 | 5 |
| min | flat | ppm | 58.0314 | 58.4158 | 58.0805 | 59.7188 | 0.7319 | 5 |
| mid | batch | ppm | 779.9096 | 782.4510 | 781.9376 | 785.3853 | 1.9999 | 5 |
| mid | flat | ppm | 96.1572 | 97.1384 | 97.2147 | 98.0786 | 0.8589 | 5 |
| max | batch | ppm | 16283.8834 | 16323.1002 | 16313.1287 | 16377.9675 | 35.6921 | 5 |
| max | flat | ppm | 2980.4472 | 2990.3812 | 2985.5680 | 3013.7259 | 13.4880 | 5 |

![image-20260428165952790](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428165952790.png)

![image-20260428165926714](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428165926714.png)

Memory commands:

```bash
pytest tests/test_align_memory.py::TestAlign::test_align_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_align_memory.py::TestAlign::test_align_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

| dataset | implementation | units | total memory allocated | allocations | main allocator | notes |
| --- | --- | --- | --- | --- | --- | --- |
| min | batch | ppm | 78.1 MiB | 116 | render:imzml (36.6MiB) | |
| min | flat | ppm | 81.2 MiB | 124 | render:imzml (36.4MiB) | |
| mid | batch | ppm | 90.1 MiB | 71 | render:imzml (44.1MiB) | |
| mid | flat | ppm | 89.1 MiB | 55 | render:imzml (43.9MiB) | |
| max | batch | ppm | 77.2 MiB | 47 | render:imzml (37.9MiB) | |
| max | flat | ppm | 76.8 MiB | 54 | render:imzml (37.8MiB) | |

![image-20260428170026335](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428170026335.png)

![image-20260428170050275](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428170050275.png)

# Python Pipeline Time And Memory Benchmarks

Datasets:

| key | file |
| --- | --- |
| min | `/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML` |
| mid | `/Users/dre/Desktop/data/test_data_profile/file_max_profile/file_max_profile.imzML` |
| max | `/Users/dre/Desktop/data/Example_read/example.imzML` |
| ultra | `/Users/dre/Desktop/data/original/original.imzML` |

## Baseline Correction

Time commands:

```bash
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_flat_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | locmin | 2.3209 | 2.4424 | 2.3463 | 2.7659 | 0.1859 | 5 |
| min | batch | snip | 7.6301 | 7.6925 | 7.7066 | 7.7392 | 0.0488 | 5 |
| min | flat | locmin_numba | 1.2321 | 1.2460 | 1.2467 | 1.2610 | 0.0104 | 5 |
| min | flat | snip_numba | 1.7102 | 1.7388 | 1.7270 | 1.7984 | 0.0346 | 5 |
| mid | batch | locmin | 3.4650 | 3.8722 | 3.8096 | 4.4442 | 0.3902 | 5 |
| mid | batch | snip | 11.9430 | 11.9815 | 11.9780 | 12.0209 | 0.0312 | 5 |
| mid | flat | locmin_numba | 1.5324 | 1.5893 | 1.5475 | 1.7758 | 0.1045 | 5 |
| mid | flat | snip_numba | 2.4686 | 2.4839 | 2.4772 | 2.5099 | 0.0159 | 5 |
| max | batch | locmin | 39.2451 | 39.2905 | 39.2965 | 39.3407 | 0.0420 | 5 |
| max | batch | snip | 92.3343 | 92.5096 | 92.5551 | 92.6555 | 0.1394 | 5 |
| max | flat | locmin_numba | 7.6331 | 7.8098 | 7.7991 | 7.9720 | 0.1286 | 5 |
| max | flat | snip_numba | 27.0182 | 27.1179 | 27.1393 | 27.2072 | 0.0783 | 5 |
| ultra | batch | locmin | 45.1039 | 47.4395 | 48.1250 | 49.5450 | 1.9203 | 5 |
| ultra | batch | snip | 144.3553 | 144.4356 | 144.4278 | 144.5233 | 0.0649 | 5 |
| ultra | flat | locmin_numba | 24.5627 | 24.7616 | 24.7276 | 25.0879 | 0.2207 | 5 |
| ultra | flat | snip_numba | 35.5328 | 35.9224 | 36.1076 | 36.1658 | 0.2941 | 5 |

![image-20260430105232800](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430105232800.png)

![image-20260430105304984](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430105304984.png)

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
| ultra | batch | locmin | 461.4 MiB | 2049 | render:imzml (202.4MiB) | |
| ultra | batch | snip | 437.6 MiB | 32 | render:imzml (202.4MiB) | |
| ultra | flat | locmin_numba | 620.6 MiB | 185 | flat_generator (238.4MiB) | |
| ultra | flat | snip_numba | 544.1 MiB | 96 | flat_generator (195.3MiB) | |

![image-20260428153856405](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428153856405.png)

![image-20260428153651132](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428153651132.png)

![image-20260430165322547](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430165322547.png)

## Noise Reduction

Time commands:

```bash
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_flat_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | ma | 1.4912 | 1.5133 | 1.5047 | 1.5647 | 0.0303 | 5 |
| min | batch | gaussian | 1.7829 | 1.7996 | 1.7893 | 1.8393 | 0.0229 | 5 |
| min | batch | savgol | 3.2425 | 3.2784 | 3.2814 | 3.3155 | 0.0345 | 5 |
| min | flat | ma_numba | 1.2340 | 1.2949 | 1.2668 | 1.4484 | 0.0886 | 5 |
| min | flat | gaussian_numba | 1.2095 | 1.2291 | 1.2309 | 1.2458 | 0.0131 | 5 |
| min | flat | savgol_numba | 1.1988 | 1.2853 | 1.2289 | 1.5569 | 0.1524 | 5 |
| mid | batch | ma | 1.8963 | 1.9138 | 1.9071 | 1.9361 | 0.0156 | 5 |
| mid | batch | gaussian | 2.2471 | 2.2524 | 2.2494 | 2.2653 | 0.0074 | 5 |
| mid | batch | savgol | 3.9966 | 4.0253 | 4.0114 | 4.0620 | 0.0315 | 5 |
| mid | flat | ma_numba | 2.4258 | 2.4720 | 2.4580 | 2.5524 | 0.0496 | 5 |
| mid | flat | gaussian_numba | 2.3309 | 2.3859 | 2.3528 | 2.5178 | 0.0756 | 5 |
| mid | flat | savgol_numba | 2.3104 | 2.7503 | 2.3939 | 3.9365 | 0.6821 | 5 |
| max | batch | ma | 6.5992 | 7.0790 | 6.9177 | 7.7555 | 0.4814 | 5 |
| max | batch | gaussian | 6.8106 | 7.1483 | 7.0285 | 7.5801 | 0.3049 | 5 |
| max | batch | savgol | 8.2987 | 8.4028 | 8.4333 | 8.4973 | 0.0816 | 5 |
| max | flat | ma_numba | 3.7409 | 4.3401 | 3.8730 | 6.1026 | 1.0028 | 5 |
| max | flat | gaussian_numba | 3.6410 | 3.8812 | 3.7404 | 4.5727 | 0.3891 | 5 |
| max | flat | savgol_numba | 3.6229 | 3.8573 | 3.7900 | 4.1448 | 0.2503 | 5 |
| ultra | batch | ma | 25.4878 | 26.2703 | 26.3349 | 26.7587 | 0.4809 | 5 |
| ultra | batch | gaussian | 25.1731 | 26.5951 | 26.4046 | 28.2017 | 1.1323 | 5 |
| ultra | batch | savgol | 34.9224 | 37.8728 | 38.2320 | 40.1095 | 1.9637 | 5 |
| ultra | flat | ma_numba | 24.2380 | 24.6143 | 24.6391 | 24.9688 | 0.2702 | 5 |
| ultra | flat | gaussian_numba | 23.6550 | 23.9425 | 23.9805 | 24.0725 | 0.1701 | 5 |
| ultra | flat | savgol_numba | 23.7565 | 24.0176 | 23.9262 | 24.3212 | 0.2316 | 5 |

![image-20260430113407875](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430113407875.png)

![image-20260430113427712](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430113427712.png)

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
| ultra | batch | ma | 445.7 MiB | 78 | render:imzml (202.4MiB) | |
| ultra | batch | gaussian | 439.6 MiB | 36 | render:imzml (202.4MiB) | |
| ultra | batch | savgol | 406.6 MiB | 27 | render:imzml (202.4MiB) | |
| ultra | flat | ma_numba | 546.7 MiB | 2124 | flat_generator (337.5MiB) | |
| ultra | flat | gaussian_numba | 540.2 MiB | 133 | flat_generator (337.5MiB) | |
| ultra | flat | savgol_numba | 540.2 MiB | 139 | flat_generator (337.5MiB) | |

![image-20260428154924177](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428154924177.png)

![image-20260428154945744](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428154945744.png)

![image-20260428155010659](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428155010659.png)

![image-20260428155030353](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428155030353.png)

![image-20260430165437818](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430165437818.png)

## Normalization

Time commands:

```bash
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_flat_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | tic | 1.3323 | 1.3394 | 1.3424 | 1.3462 | 0.0064 | 5 |
| min | batch | rms | 1.4587 | 1.4849 | 1.4859 | 1.5188 | 0.0223 | 5 |
| min | flat | tic_numba | 1.1695 | 1.1845 | 1.1835 | 1.2097 | 0.0165 | 5 |
| min | flat | rms_numba | 1.1804 | 1.1879 | 1.1886 | 1.1952 | 0.0062 | 5 |
| min | flat | ref_numba | 1.1758 | 1.1866 | 1.1793 | 1.2101 | 0.0142 | 5 |
| mid | batch | tic | 2.0035 | 2.1888 | 2.1645 | 2.4128 | 0.1501 | 5 |
| mid | batch | rms | 1.9012 | 1.9502 | 1.9227 | 2.0584 | 0.0628 | 5 |
| mid | flat | tic_numba | 2.3991 | 2.4674 | 2.4831 | 2.5251 | 0.0570 | 5 |
| mid | flat | rms_numba | 2.3703 | 3.2031 | 2.4570 | 4.3877 | 1.0660 | 5 |
| mid | flat | ref_numba | 2.1167 | 2.1819 | 2.1224 | 2.3948 | 0.1200 | 5 |
| max | batch | tic | 6.7086 | 6.9554 | 6.8376 | 7.4811 | 0.3223 | 5 |
| max | batch | rms | 6.6459 | 6.9815 | 6.9879 | 7.2331 | 0.2341 | 5 |
| max | flat | tic_numba | 3.6504 | 4.3329 | 3.9076 | 6.1772 | 1.0406 | 5 |
| max | flat | rms_numba | 3.5676 | 3.7718 | 3.7414 | 3.9653 | 0.1593 | 5 |
| max | flat | ref_numba | 3.5667 | 3.8045 | 3.8498 | 4.1635 | 0.2450 | 5 |
| ultra | batch | tic | 25.8237 | 26.4522 | 26.1531 | 27.7388 | 0.7843 | 5 |
| ultra | batch | rms | 24.1672 | 26.1432 | 26.3474 | 27.8324 | 1.5516 | 5 |
| ultra | flat | tic_numba | 24.2389 | 24.7824 | 24.7831 | 25.0943 | 0.3494 | 5 |
| ultra | flat | rms_numba | 24.0575 | 24.2586 | 24.2284 | 24.5280 | 0.2056 | 5 |
| ultra | flat | ref_numba | 22.0461 | 23.2055 | 22.1775 | 27.4939 | 2.3979 | 5 |

![image-20260430121246327](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430121246327.png)

![image-20260430121305087](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430121305087.png)

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
| ultra | batch | tic | 445.7 MiB | 79 | render:imzml (202.4MiB) | |
| ultra | batch | rms | 437.6 MiB | 29 | render:imzml (202.4MiB) | |
| ultra | flat | tic_numba | 547.9 MiB | 2136 | flat_generator (311.8MiB) | |
| ultra | flat | rms_numba | 539.9 MiB | 128 | flat_generator (337.5MiB) | |
| ultra | flat | ref_numba | 544.8 MiB | 241 | flat_generator (337.5MiB) | |

![image-20260428160633912](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160633912.png)

![image-20260428160703512](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160703512.png)

![image-20260428160740118](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428160740118.png)

![image-20260430165509763](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430165509763.png)

## Peak Pick

Time commands:

```bash
pytest tests/test_pick_memory.py::TestPick::test_pick_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_pick_memory.py::TestPick::test_pick_flat_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | method | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | origin | 4.7569 | 4.7783 | 4.7794 | 4.7931 | 0.0155 | 5 |
| min | flat | quantile | 1.4475 | 1.4538 | 1.4545 | 1.4598 | 0.0048 | 5 |
| min | flat | diff | 1.1702 | 1.1755 | 1.1748 | 1.1807 | 0.0041 | 5 |
| min | flat | sd | 1.1790 | 1.1833 | 1.1831 | 1.1870 | 0.0032 | 5 |
| min | flat | mad | 1.9487 | 1.9634 | 1.9568 | 1.9940 | 0.0179 | 5 |
| mid | batch | origin | 6.2275 | 6.4168 | 6.3466 | 6.7800 | 0.2289 | 5 |
| mid | flat | quantile | 2.0531 | 2.0588 | 2.0546 | 2.0780 | 0.0108 | 5 |
| mid | flat | diff | 1.4404 | 1.4453 | 1.4440 | 1.4530 | 0.0051 | 5 |
| mid | flat | sd | 1.4456 | 1.4492 | 1.4487 | 1.4548 | 0.0035 | 5 |
| mid | flat | mad | 2.9771 | 2.9857 | 2.9792 | 3.0056 | 0.0121 | 5 |
| max | batch | origin | 39.2271 | 39.4886 | 39.4695 | 39.7526 | 0.2174 | 5 |
| max | flat | quantile | 24.6375 | 24.6802 | 24.6965 | 24.7194 | 0.0368 | 5 |
| max | flat | diff | 6.0172 | 6.0213 | 6.0193 | 6.0277 | 0.0043 | 5 |
| max | flat | sd | 7.9312 | 7.9576 | 7.9556 | 7.9827 | 0.0198 | 5 |
| max | flat | mad | 41.5391 | 41.5663 | 41.5663 | 41.5977 | 0.0215 | 5 |
| ultra | batch | origin | 53.5041 | 53.9450 | 53.8871 | 54.3511 | 0.3649 | 5 |
| ultra | flat | quantile | 28.8600 | 28.9606 | 28.8843 | 29.1130 | 0.1251 | 5 |
| ultra | flat | diff | 11.2938 | 11.3753 | 11.3600 | 11.5407 | 0.0967 | 5 |
| ultra | flat | sd | 10.8858 | 10.9617 | 10.9736 | 11.0039 | 0.0447 | 5 |
| ultra | flat | mad | 48.1220 | 48.1335 | 48.1309 | 48.1440 | 0.0090 | 5 |

![image-20260430153019343](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430153019343.png)

![image-20260430152850633](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430152850633.png)

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
| ultra | batch | origin | 458.4 MiB | 2085 | render:imzml (201.3MiB) | |
| ultra | flat | quantile | 445.2 MiB | 88 | render:imzml (200.6MiB) | |
| ultra | flat | diff | 403.1 MiB | 44 | render:imzml (200.6MiB) | |
| ultra | flat | sd | 402.5 MiB | 47 | render:imzml (200.4MiB) | |
| ultra | flat | mad | 403.5 MiB | 48 | render:imzml (200.9MiB) | |

![image-20260428163956065](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428163956065.png)

![image-20260428164049851](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428164049851.png)

![image-20260428164122821](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428164122821.png)

![image-20260430165622399](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430165622399.png)

## Peak Align

Time commands:

```bash
pytest tests/test_align_memory.py::TestAlign::test_align_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
pytest tests/test_align_memory.py::TestAlign::test_align_flat_memory --benchmark-only --benchmark-columns=min,mean,median,max,stddev,rounds -q
```

| dataset | implementation | units | min | mean | median | max | stddev | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | batch | ppm | 1.8579 | 1.8619 | 1.8596 | 1.8698 | 0.0050 | 5 |
| min | flat | ppm | 0.9340 | 0.9440 | 0.9430 | 0.9577 | 0.0088 | 5 |
| mid | batch | ppm | 2.4610 | 2.4694 | 2.4697 | 2.4747 | 0.0055 | 5 |
| mid | flat | ppm | 1.1456 | 1.1509 | 1.1468 | 1.1692 | 0.0102 | 5 |
| max | batch | ppm | 19.1083 | 19.1729 | 19.1545 | 19.3141 | 0.0821 | 5 |
| max | flat | ppm | 4.4906 | 4.5226 | 4.5087 | 4.5796 | 0.0381 | 5 |
| ultra | batch | ppm | 15.6528 | 15.6636 | 15.6582 | 15.6863 | 0.0134 | 5 |
| ultra | flat | ppm | 5.7051 | 5.7167 | 5.7068 | 5.7384 | 0.0152 | 5 |

![image-20260430153054640](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430153054640.png)

![image-20260430152922840](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430152922840.png)

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
| ultra | batch | ppm | 428.7 MiB | 105 | render:imzml (201.3MiB) | |
| ultra | flat | ppm | 440.4 MiB | 124 | render:imzml (200.5MiB) | |

![image-20260428170026335](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428170026335.png)

![image-20260428170050275](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428170050275.png)

![image-20260430165655813](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430165655813.png)

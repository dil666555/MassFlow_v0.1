# MassFlow Pipeline (flat/numba) Time And Memory Benchmarks

> 数据来源：本文件中所有 Baseline / Noise Reduction / Normalization / Peak Pick 章节对应 [`tests/massflow_time&memory_benchmarks.md`](../tests/massflow_time&memory_benchmarks.md) 的 `flat` 行；Peak Align 章节对应 [`tests/peak_align_new_test.md`](../tests/peak_align_new_test.md) 的 `test_align_flat_memory -- time` 与 `test_align_flat_memory` 表（`pipeline_outcome.py` 中 `Peak Alignment.Default` 的第二个数值取自 `test_align_flat_memory -- time` 表的 `mean` 列，单位 ms 已换算为 s）。

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
| min | flat | locmin_numba | 1.2321 | 1.2460 | 1.2467 | 1.2610 | 0.0104 | 5 |
| min | flat | snip_numba | 1.7102 | 1.7388 | 1.7270 | 1.7984 | 0.0346 | 5 |
| mid | flat | locmin_numba | 1.5324 | 1.5893 | 1.5475 | 1.7758 | 0.1045 | 5 |
| mid | flat | snip_numba | 2.4686 | 2.4839 | 2.4772 | 2.5099 | 0.0159 | 5 |
| max | flat | locmin_numba | 7.6331 | 7.8098 | 7.7991 | 7.9720 | 0.1286 | 5 |
| max | flat | snip_numba | 27.0182 | 27.1179 | 27.1393 | 27.2072 | 0.0783 | 5 |
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
| min | flat | locmin_numba | 103.3 MiB | 2162 | flat_generator (24.8MiB) | |
| min | flat | snip_numba | 92.0 MiB | 95 | flat_generator (32.6MiB) | |
| mid | flat | locmin_numba | 127.9 MiB | 161 | flat_generator (49.7MiB) | |
| mid | flat | snip_numba | 119.3 MiB | 87 | flat_generator (43.0MiB) | |
| max | flat | locmin_numba | 1022.9 MiB | 69 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | snip_numba | 1022.9 MiB | 65 | read_contiguous_block_flat (219.0MiB) | |
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
| min | flat | ma_numba | 1.2340 | 1.2949 | 1.2668 | 1.4484 | 0.0886 | 5 |
| min | flat | gaussian_numba | 1.2095 | 1.2291 | 1.2309 | 1.2458 | 0.0131 | 5 |
| min | flat | savgol_numba | 1.1988 | 1.2853 | 1.2289 | 1.5569 | 0.1524 | 5 |
| mid | flat | ma_numba | 2.4258 | 2.4720 | 2.4580 | 2.5524 | 0.0496 | 5 |
| mid | flat | gaussian_numba | 2.3309 | 2.3859 | 2.3528 | 2.5178 | 0.0756 | 5 |
| mid | flat | savgol_numba | 2.3104 | 2.7503 | 2.3939 | 3.9365 | 0.6821 | 5 |
| max | flat | ma_numba | 3.7409 | 4.3401 | 3.8730 | 6.1026 | 1.0028 | 5 |
| max | flat | gaussian_numba | 3.6410 | 3.8812 | 3.7404 | 4.5727 | 0.3891 | 5 |
| max | flat | savgol_numba | 3.6229 | 3.8573 | 3.7900 | 4.1448 | 0.2503 | 5 |
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
| min | flat | ma_numba | 99.4 MiB | 2093 | render:imzml (36.6MiB) | |
| min | flat | gaussian_numba | 74.8 MiB | 57 | render:imzml (36.6MiB) | |
| min | flat | savgol_numba | 74.7 MiB | 56 | render:imzml (36.6MiB) | |
| mid | flat | ma_numba | 94.6 MiB | 86 | render:imzml (44.1MiB) | |
| mid | flat | gaussian_numba | 89.4 MiB | 47 | render:imzml (44.1MiB) | |
| mid | flat | savgol_numba | 89.4 MiB | 43 | render:imzml (44.1MiB) | |
| max | flat | ma_numba | 439.3 MiB | 80 | smooth_signal_ma_numba (219.0MiB) | |
| max | flat | gaussian_numba | 440.4 MiB | 82 | smooth_signal_gaussian_numba (219.0MiB) | |
| max | flat | savgol_numba | 440.4 MiB | 80 | smooth_signal_savgol_numba (219.0MiB) | |
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
| min | flat | tic_numba | 1.1695 | 1.1845 | 1.1835 | 1.2097 | 0.0165 | 5 |
| min | flat | rms_numba | 1.1804 | 1.1879 | 1.1886 | 1.1952 | 0.0062 | 5 |
| min | flat | ref_numba | 1.1758 | 1.1866 | 1.1793 | 1.2101 | 0.0142 | 5 |
| mid | flat | tic_numba | 2.3991 | 2.4674 | 2.4831 | 2.5251 | 0.0570 | 5 |
| mid | flat | rms_numba | 2.3703 | 3.2031 | 2.4570 | 4.3877 | 1.0660 | 5 |
| mid | flat | ref_numba | 2.1167 | 2.1819 | 2.1224 | 2.3948 | 0.1200 | 5 |
| max | flat | tic_numba | 3.6504 | 4.3329 | 3.9076 | 6.1772 | 1.0406 | 5 |
| max | flat | rms_numba | 3.5676 | 3.7718 | 3.7414 | 3.9653 | 0.1593 | 5 |
| max | flat | ref_numba | 3.5667 | 3.8045 | 3.8498 | 4.1635 | 0.2450 | 5 |
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
| min | flat | tic_numba | 99.6 MiB | 2092 | render:imzml (36.6MiB) | |
| min | flat | rms_numba | 74.4 MiB | 45 | render:imzml (36.6MiB) | |
| min | flat | ref_numba | 75.3 MiB | 107 | render:imzml (36.6MiB) | |
| mid | flat | tic_numba | 95.6 MiB | 85 | render:imzml (44.1MiB) | |
| mid | flat | rms_numba | 89.4 MiB | 44 | render:imzml (44.1MiB) | |
| mid | flat | ref_numba | 89.7 MiB | 92 | render:imzml (44.1MiB) | |
| max | flat | tic_numba | 439.4 MiB | 83 | normalizer_numba (219.0MiB) | |
| max | flat | rms_numba | 438.9 MiB | 67 | normalizer_numba (219.0MiB) | |
| max | flat | ref_numba | 439.4 MiB | 81 | normalizer_numba (219.0MiB) | |
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
| min | flat | quantile | 1.4475 | 1.4538 | 1.4545 | 1.4598 | 0.0048 | 5 |
| min | flat | diff | 1.1702 | 1.1755 | 1.1748 | 1.1807 | 0.0041 | 5 |
| min | flat | sd | 1.1790 | 1.1833 | 1.1831 | 1.1870 | 0.0032 | 5 |
| min | flat | mad | 1.9487 | 1.9634 | 1.9568 | 1.9940 | 0.0179 | 5 |
| mid | flat | quantile | 2.0531 | 2.0588 | 2.0546 | 2.0780 | 0.0108 | 5 |
| mid | flat | diff | 1.4404 | 1.4453 | 1.4440 | 1.4530 | 0.0051 | 5 |
| mid | flat | sd | 1.4456 | 1.4492 | 1.4487 | 1.4548 | 0.0035 | 5 |
| mid | flat | mad | 2.9771 | 2.9857 | 2.9792 | 3.0056 | 0.0121 | 5 |
| max | flat | quantile | 24.6375 | 24.6802 | 24.6965 | 24.7194 | 0.0368 | 5 |
| max | flat | diff | 6.0172 | 6.0213 | 6.0193 | 6.0277 | 0.0043 | 5 |
| max | flat | sd | 7.9312 | 7.9576 | 7.9556 | 7.9827 | 0.0198 | 5 |
| max | flat | mad | 41.5391 | 41.5663 | 41.5663 | 41.5977 | 0.0215 | 5 |
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
| min | flat | quantile | 102.6 MiB | 2127 | render:imzml (36.4MiB) | |
| min | flat | diff | 102.6 MiB | 2127 | render:imzml (36.4MiB) | |
| min | flat | sd | 74.2 MiB | 49 | render:imzml (36.5MiB) | |
| min | flat | mad | 74.2 MiB | 49 | render:imzml (36.5MiB) | |
| mid | flat | quantile | 95.1 MiB | 90 | render:imzml (43.9MiB) | |
| mid | flat | diff | 89.0 MiB | 47 | render:imzml (43.9MiB) | |
| mid | flat | sd | 89.0 MiB | 49 | render:imzml (43.9MiB) | |
| mid | flat | mad | 89.2 MiB | 47 | render:imzml (44.0MiB) | |
| max | flat | quantile | 677.0 MiB | 110 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | diff | 521.1 MiB | 80 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | sd | 706.7 MiB | 76 | read_contiguous_block_flat (219.0MiB) | |
| max | flat | mad | 714.3 MiB | 70 | read_contiguous_block_flat (219.0MiB) | |
| ultra | flat | quantile | 445.2 MiB | 88 | render:imzml (200.6MiB) | |
| ultra | flat | diff | 403.1 MiB | 44 | render:imzml (200.6MiB) | |
| ultra | flat | sd | 402.5 MiB | 47 | render:imzml (200.4MiB) | |
| ultra | flat | mad | 403.5 MiB | 48 | render:imzml (200.9MiB) | |

![image-20260428163956065](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428163956065.png)

![image-20260428164049851](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428164049851.png)

![image-20260428164122821](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260428164122821.png)

![image-20260430165622399](https://neonexus-picture.oss-ap-southeast-1.aliyuncs.com/test/image-20260430165622399.png)

## Peak Align

> 来源：[`tests/peak_align_new_test.md`](../tests/peak_align_new_test.md) 的 `test_align_flat_memory -- time` 表与 `test_align_flat_memory` 表。`tests/pipeline_outcome.py` 中 `Peak Alignment.Default` 的第二个数值取自 `test_align_flat_memory -- time` 表的 `mean` 列（单位 ms 已换算为 s）；内存第二个数值取自 `test_align_flat_memory` 表的 `min` 方法行。

Time commands:

```bash
pytest tests/test_align_memory.py::TestAlign::test_align_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_align_memory.py::TestAlign::test_align_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

### test_align_flat_memory -- time

| Name | Dataset | Method | Min (ms) | Mean (ms) | Median (ms) | Max (ms) | StdDev (ms) | Rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test_align_flat_memory[.../file_min_profile.imzML-max-ppm] | min | max | 900.8059 | 915.0203 | 919.3358 | 924.5073 | 10.7515 | 5 |
| test_align_flat_memory[.../file_min_profile.imzML-median-ppm] | min | median | 904.4146 | 918.7704 | 918.1977 | 931.6270 | 10.1740 | 5 |
| test_align_flat_memory[.../file_min_profile.imzML-min-ppm] | min | min | 905.5364 | 921.4473 | 923.3250 | 929.1857 | 9.4055 | 5 |
| test_align_flat_memory[.../file_max_profile.imzML-max-ppm] | mid | max | 1,098.8740 | 1,103.7597 | 1,104.9482 | 1,107.4322 | 3.4008 | 5 |
| test_align_flat_memory[.../file_max_profile.imzML-min-ppm] | mid | min | 1,099.9598 | 1,109.7435 | 1,110.7323 | 1,120.3860 | 7.6678 | 5 |
| test_align_flat_memory[.../file_max_profile.imzML-median-ppm] | mid | median | 1,106.3932 | 1,115.7460 | 1,115.6026 | 1,127.1443 | 7.9137 | 5 |
| test_align_flat_memory[.../example.imzML-max-ppm] | max | max | 4,471.1444 | 4,526.3553 | 4,539.2806 | 4,557.9291 | 33.5865 | 5 |
| test_align_flat_memory[.../example.imzML-min-ppm] | max | min | 4,754.5693 | 4,802.1340 | 4,815.6297 | 4,832.0750 | 31.0416 | 5 |
| test_align_flat_memory[.../example.imzML-median-ppm] | max | median | 5,399.6195 | 5,437.8508 | 5,434.8849 | 5,472.9471 | 27.9359 | 5 |
| test_align_flat_memory[.../original.imzML-max-ppm] | ultra | max | 5,910.8500 | 5,940.7904 | 5,943.0552 | 5,955.2143 | 17.9267 | 5 |
| test_align_flat_memory[.../original.imzML-min-ppm] | ultra | min | 6,228.8197 | 6,574.0955 | 6,687.1666 | 6,713.6774 | 203.1943 | 5 |
| test_align_flat_memory[.../original.imzML-median-ppm] | ultra | median | 6,412.9975 | 6,547.7563 | 6,560.7674 | 6,708.1602 | 123.9681 | 5 |

12 passed

![alt text](../tests/image_of_test/image-9.png)

### test_align_flat_memory

| Dataset | Method | Total Memory (MiB) | Total Allocations | Top Allocation |
| --- | --- | --- | --- | --- |
| ultra (original.imzML) | min | 446.0 | 132 | 200.5MiB (render:imzml:132 / _write_xml) |
| ultra (original.imzML) | median | 402.8 | 52 | 200.5MiB (render:imzml:132 / _write_xml) |
| ultra (original.imzML) | max | 401.9 | 55 | 200.1MiB (render:imzml:132 / _write_xml) |
| mid (file_max_profile.imzML) | min | 89.1 | 54 | 44.0MiB (render:imzml:132 / _write_xml) |
| mid (file_max_profile.imzML) | median | 89.1 | 50 | 43.9MiB (render:imzml:132 / _write_xml) |
| mid (file_max_profile.imzML) | max | 88.9 | 53 | 43.9MiB (render:imzml:132 / _write_xml) |
| min (file_min_profile.imzML) | min | 82.3 | 116 | 36.5MiB (render:imzml:132 / _write_xml) |
| max (example.imzML) | median | 76.8 | 50 | 37.8MiB (render:imzml:132 / _write_xml) |
| max (example.imzML) | min | 76.8 | 52 | 37.8MiB (render:imzml:132 / _write_xml) |
| max (example.imzML) | max | 76.7 | 47 | 37.7MiB (render:imzml:132 / _write_xml) |
| min (file_min_profile.imzML) | median | 74.0 | 53 | 36.4MiB (render:imzml:132 / _write_xml) |
| min (file_min_profile.imzML) | max | 74.0 | 57 | 36.4MiB (render:imzml:132 / _write_xml) |

9 passed in 306.28s (0:05:06)

![alt text](../tests/image_of_test/image-4.png)
![alt text](../tests/image_of_test/image-5.png)
![alt text](../tests/image_of_test/image-6.png)

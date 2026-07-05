# m2aia 对比基准测试结果

## 归一化（Normalization）速度对比 (MassFlow vs m2aia)

**对应测试代码文件**：[test_m2aia_normalization_benchmark.py](file:///Users/dre/Desktop/dre/massflow-essay/MassFlow_v0.1/tests/test_m2aia_normalization_benchmark.py)

### 测试内容说明

- **对比的方法**：TIC 和 RMS 归一化（Normalization）。
  - **MassFlow**：采用 Flat 预处理模式（通过 `tic_numba` 和 `rms_numba` 实现的 `FlatPreprocess.normalization_flat`）。
  - **m2aia**：通过设置 `m2aia.ImzMLReader` 的 `normalization` 参数为 `TIC` 或 `RMS`，并使用质谱迭代器遍历处理全部质谱强度。
- **测试数据集**：
  - `min`：`file_min_profile.imzML`（极小数据集）
  - `mid`：`file_mid_profile.imzML`（中等数据集）
  - `example`：`example.imzML`（较大数据集）
  - `original`：`original.imzML`（原始大型数据集）
- **性能指标**：测量多轮运行的执行时间，单位为毫秒 (ms)。

### Benchmark Run 1

| Name (time in ms)                           | Min                 | Mean                | Median              | Max                 | StdDev            | Rounds |
|:------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:----------------- |:------ |
| `test_m2aia_normalization[min-tic]`         | 873.7910 (1.0)      | 877.3409 (1.0)      | 874.9119 (1.0)      | 883.3197 (1.0)      | 5.2080 (1.30)     | 3      |
| `test_m2aia_normalization[min-rms]`         | 876.8152 (1.00)     | 880.1401 (1.00)     | 878.9980 (1.00)     | 884.6071 (1.00)     | 4.0195 (1.0)      | 3      |
| `test_massflow_normalization[min-tic]`      | 1,585.2802 (1.81)   | 1,620.6946 (1.85)   | 1,629.0747 (1.86)   | 1,647.7288 (1.87)   | 32.0566 (7.98)    | 3      |
| `test_massflow_normalization[min-rms]`      | 1,597.9855 (1.83)   | 1,617.7998 (1.84)   | 1,621.5489 (1.85)   | 1,632.0555 (1.85)   | 17.4257 (4.34)    | 3      |
| `test_massflow_normalization[mid-tic]`      | 2,329.3177 (2.67)   | 2,392.7207 (2.73)   | 2,412.7498 (2.76)   | 2,436.0945 (2.76)   | 56.1355 (13.97)   | 3      |
| `test_massflow_normalization[mid-rms]`      | 2,396.6919 (2.74)   | 2,464.9839 (2.81)   | 2,447.0583 (2.80)   | 2,551.2015 (2.89)   | 78.7991 (19.60)   | 3      |
| `test_m2aia_normalization[mid-rms]`         | 2,460.4075 (2.82)   | 2,502.1485 (2.85)   | 2,504.3733 (2.86)   | 2,541.6837 (2.88)   | 40.6834 (10.12)   | 3      |
| `test_m2aia_normalization[mid-tic]`         | 2,516.8169 (2.88)   | 2,567.3020 (2.93)   | 2,588.6914 (2.96)   | 2,595.8822 (2.94)   | 43.7206 (10.88)   | 3      |
| `test_m2aia_normalization[example-rms]`     | 5,288.4086 (6.05)   | 5,333.3339 (6.08)   | 5,320.4378 (6.08)   | 5,391.1553 (6.10)   | 52.5733 (13.08)   | 3      |
| `test_m2aia_normalization[example-tic]`     | 5,328.3847 (6.10)   | 5,426.2086 (6.18)   | 5,462.6641 (6.24)   | 5,487.5771 (6.21)   | 85.6288 (21.30)   | 3      |
| `test_massflow_normalization[example-rms]`  | 7,970.3969 (9.12)   | 8,437.5112 (9.62)   | 8,648.9864 (9.89)   | 8,693.1502 (9.84)   | 405.1350 (100.79) | 3      |
| `test_massflow_normalization[example-tic]`  | 8,591.7800 (9.83)   | 8,604.0204 (9.81)   | 8,606.9045 (9.84)   | 8,613.7767 (9.75)   | 11.0834 (2.76)    | 3      |
| `test_m2aia_normalization[original-tic]`    | 10,054.3831 (11.51) | 10,125.9974 (11.54) | 10,151.1889 (11.60) | 10,172.4202 (11.52) | 62.9218 (15.65)   | 3      |
| `test_m2aia_normalization[original-rms]`    | 10,069.9793 (11.52) | 10,169.0165 (11.59) | 10,190.1103 (11.65) | 10,246.9598 (11.60) | 90.3562 (22.48)   | 3      |
| `test_massflow_normalization[original-tic]` | 18,322.0862 (20.97) | 18,422.0327 (21.00) | 18,440.7693 (21.08) | 18,503.2427 (20.95) | 92.0202 (22.89)   | 3      |
| `test_massflow_normalization[original-rms]` | 18,390.8771 (21.05) | 18,884.8685 (21.48) | 19,018.7569 (21.74) | 19,124.9715 (21.65) | 396.7386 (98.70)  | 3      |

### Benchmark Run 2

| Name (time in ms)                           | Min                 | Mean                | Median              | Max                 | StdDev               | Rounds |
|:------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:-------------------- |:------ |
| `test_m2aia_normalization[min-tic]`         | 846.5076 (1.0)      | 855.2510 (1.0)      | 854.5820 (1.0)      | 864.6634 (1.0)      | 9.0964 (5.52)        | 3      |
| `test_m2aia_normalization[min-rms]`         | 867.9265 (1.03)     | 869.2095 (1.02)     | 868.6349 (1.02)     | 871.0672 (1.01)     | 1.6473 (1.0)         | 3      |
| `test_massflow_normalization[min-tic]`      | 1,559.1942 (1.84)   | 1,603.2642 (1.87)   | 1,593.4045 (1.86)   | 1,657.1938 (1.92)   | 49.7382 (30.19)      | 3      |
| `test_massflow_normalization[min-rms]`      | 1,581.8399 (1.87)   | 1,646.2272 (1.92)   | 1,612.5449 (1.89)   | 1,744.2967 (2.02)   | 86.3072 (52.39)      | 3      |
| `test_massflow_normalization[mid-tic]`      | 2,152.6902 (2.54)   | 2,194.0382 (2.57)   | 2,171.0867 (2.54)   | 2,258.3376 (2.61)   | 56.4395 (34.26)      | 3      |
| `test_massflow_normalization[mid-rms]`      | 2,237.3291 (2.64)   | 2,273.5920 (2.66)   | 2,291.7012 (2.68)   | 2,291.7457 (2.65)   | 31.4046 (19.06)      | 3      |
| `test_m2aia_normalization[mid-tic]`         | 2,453.9332 (2.90)   | 2,472.6435 (2.89)   | 2,479.9845 (2.90)   | 2,484.0128 (2.87)   | 16.3283 (9.91)       | 3      |
| `test_m2aia_normalization[mid-rms]`         | 2,465.5941 (2.91)   | 2,499.4553 (2.92)   | 2,490.2036 (2.91)   | 2,542.5681 (2.94)   | 39.3121 (23.86)      | 3      |
| `test_m2aia_normalization[example-rms]`     | 5,288.7068 (6.25)   | 5,318.7538 (6.22)   | 5,308.6749 (6.21)   | 5,358.8795 (6.20)   | 36.1558 (21.95)      | 3      |
| `test_m2aia_normalization[example-tic]`     | 5,298.2516 (6.26)   | 5,344.5716 (6.25)   | 5,348.1592 (6.26)   | 5,387.3040 (6.23)   | 44.6345 (27.10)      | 3      |
| `test_massflow_normalization[example-tic]`  | 7,409.3674 (8.75)   | 7,580.0366 (8.86)   | 7,543.2682 (8.83)   | 7,787.4743 (9.01)   | 191.7163 (116.38)    | 3      |
| `test_massflow_normalization[example-rms]`  | 8,030.2689 (9.49)   | 8,223.9154 (9.62)   | 8,263.2642 (9.67)   | 8,378.2130 (9.69)   | 177.2781 (107.62)    | 3      |
| `test_m2aia_normalization[original-rms]`    | 10,084.0492 (11.91) | 10,180.0670 (11.90) | 10,128.0990 (11.85) | 10,328.0530 (11.94) | 130.0383 (78.94)     | 3      |
| `test_m2aia_normalization[original-tic]`    | 10,105.6193 (11.94) | 10,215.1689 (11.94) | 10,269.3280 (12.02) | 10,270.5595 (11.88) | 94.8748 (57.59)      | 3      |
| `test_massflow_normalization[original-tic]` | 17,771.6310 (20.99) | 19,834.5397 (23.19) | 20,407.9852 (23.88) | 21,324.0030 (24.66) | 1,844.3065 (>1000.0) | 3      |
| `test_massflow_normalization[original-rms]` | 21,975.1056 (25.96) | 22,612.9004 (26.44) | 22,761.0805 (26.63) | 23,102.5150 (26.72) | 578.1272 (350.96)    | 3      |

## 读取全部质谱数据（Read All Spectra）速度对比 (MassFlow vs m2aia)

**对应测试代码文件**：[test_m2aia_read_all_spectra_benchmark.py](file:///Users/dre/Desktop/dre/massflow-essay/MassFlow_v0.1/tests/test_m2aia_read_all_spectra_benchmark.py)

### 测试内容说明

- **对比的方法**：从 imzML 文件中读取并遍历全部质谱数据（不进行任何信号预处理）。
  - **MassFlow**：使用 MassFlow 自带的 Flat imzML 读取器（`MSDataManagerImzML.flat_generator`，其中 `include_mz=True`）。
  - **m2aia**：使用 `m2aia.ImzMLReader` 的 `SpectrumIterator` 遍历，并将质谱数据转换为 numpy 数组。
- **测试数据集**：`min`（极小）、`mid`（中等）、`example`（较大）、`original`（原始型大型）。
- **性能指标**：测量多轮运行的执行时间，单位为毫秒 (ms)。

| Name (time in ms)                               | Min                 | Mean                | Median              | Max                 | StdDev           | Rounds |
|:----------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:---------------- |:------ |
| `test_m2aia_read_all_spectra[min]`              | 929.9636 (1.0)      | 948.9789 (1.0)      | 955.5510 (1.0)      | 964.8276 (1.0)      | 14.2016 (1.0)    | 5      |
| `test_massflow_flat_read_all_spectra[min]`      | 2,082.6018 (2.24)   | 2,164.2724 (2.28)   | 2,127.0524 (2.23)   | 2,346.2362 (2.43)   | 104.7066 (7.37)  | 5      |
| `test_m2aia_read_all_spectra[mid]`              | 2,605.3926 (2.80)   | 2,653.5920 (2.80)   | 2,651.2840 (2.77)   | 2,717.7264 (2.82)   | 41.0367 (2.89)   | 5      |
| `test_massflow_flat_read_all_spectra[mid]`      | 3,081.7915 (3.31)   | 3,117.6911 (3.29)   | 3,116.7269 (3.26)   | 3,154.6175 (3.27)   | 25.8775 (1.82)   | 5      |
| `test_m2aia_read_all_spectra[example]`          | 5,770.3061 (6.20)   | 5,834.5905 (6.15)   | 5,848.9670 (6.12)   | 5,863.5178 (6.08)   | 37.2902 (2.63)   | 5      |
| `test_massflow_flat_read_all_spectra[example]`  | 6,158.1928 (6.62)   | 6,208.3414 (6.54)   | 6,215.2464 (6.50)   | 6,256.3386 (6.48)   | 39.4561 (2.78)   | 5      |
| `test_m2aia_read_all_spectra[original]`         | 10,730.9734 (11.54) | 10,824.6391 (11.41) | 10,809.3958 (11.31) | 10,933.7663 (11.33) | 78.8934 (5.56)   | 5      |
| `test_massflow_flat_read_all_spectra[original]` | 22,126.5455 (23.79) | 22,652.8600 (23.87) | 22,229.7971 (23.26) | 23,855.7816 (24.73) | 744.7554 (52.44) | 5      |

## 平滑预处理（Smoothing）速度对比 (MassFlow vs m2aia)

**对应测试代码文件**：[test_m2aia_smoothing_benchmark.py](file:///Users/dre/Desktop/dre/massflow-essay/MassFlow_v0.1/tests/test_m2aia_smoothing_benchmark.py)

### 测试内容说明

- **对比的方法**：高斯平滑滤波（Gaussian Smoothing，窗口大小为 5）。
  - **MassFlow**：采用 Flat 噪声消除接口 `FlatPreprocess.noise_reduction_flat`（方法设为 `gaussian_numba`，半窗口为 2，对应全窗口 5）。
  - **m2aia**：使用 `m2aia.ImzMLReader` 的 `smoothing` 设置为 `Gaussian`，半窗口为 2。
- **测试数据集**：`min`（极小）、`mid`（中等）、`example`（较大）、`original`（原始型大型）。
- **性能指标**：测量多轮运行的执行时间，单位为毫秒 (ms)。

| Name (time in ms)                                    | Min                 | Mean                | Median              | Max                 | StdDev           | Rounds |
|:---------------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:---------------- |:------ |
| `test_m2aia_smoothing[min-gaussian_window5]`         | 816.9418 (1.0)      | 831.4268 (1.0)      | 830.0119 (1.0)      | 856.7710 (1.0)      | 16.1028 (1.0)    | 5      |
| `test_massflow_smoothing[min-gaussian_window5]`      | 1,525.2256 (1.87)   | 1,544.6787 (1.86)   | 1,536.6935 (1.85)   | 1,593.1843 (1.86)   | 27.5379 (1.71)   | 5      |
| `test_massflow_smoothing[mid-gaussian_window5]`      | 1,869.2466 (2.29)   | 2,002.2206 (2.41)   | 2,004.3237 (2.41)   | 2,145.0391 (2.50)   | 98.4522 (6.11)   | 5      |
| `test_m2aia_smoothing[mid-gaussian_window5]`         | 2,376.9486 (2.91)   | 2,463.1804 (2.96)   | 2,473.9029 (2.98)   | 2,572.7515 (3.00)   | 73.6947 (4.58)   | 5      |
| `test_massflow_smoothing[example-gaussian_window5]`  | 6,666.9068 (8.16)   | 6,846.0679 (8.23)   | 6,767.1071 (8.15)   | 7,044.6272 (8.22)   | 162.2535 (10.08) | 5      |
| `test_m2aia_smoothing[original-gaussian_window5]`    | 9,555.9891 (11.70)  | 9,670.0924 (11.63)  | 9,672.1945 (11.65)  | 9,763.5929 (11.40)  | 88.2555 (5.48)   | 5      |
| `test_m2aia_smoothing[example-gaussian_window5]`     | 11,008.3608 (13.48) | 11,036.2244 (13.27) | 11,019.7589 (13.28) | 11,098.9658 (12.95) | 36.4148 (2.26)   | 5      |
| `test_massflow_smoothing[original-gaussian_window5]` | 16,538.8448 (20.24) | 16,706.3746 (20.09) | 16,714.1423 (20.14) | 16,851.3899 (19.67) | 111.0490 (6.90)  | 5      |

## 缓存输入计算（Cached Compute）速度对比 (MassFlow vs m2aia)

**对应测试代码文件**：[test_m2aia_cached_compute_benchmark.py](file:///Users/dre/Desktop/dre/massflow-essay/MassFlow_v0.1/tests/test_m2aia_cached_compute_benchmark.py)

### 测试内容说明

- **测试目的**：评估在输入数据已预加载/缓存（排除了磁盘 I/O 读取开销）的情况下的纯核函数计算性能。
- **对比的方法**：
  - **MassFlow**：预先加载扁平（flat）批次的质谱强度，在 benchmark 测试中仅统计 Flat 预处理核函数（`FlatPreprocess.normalization_flat` 和 `FlatPreprocess.noise_reduction_flat`）的计算时间。
  - **m2aia**：因为 pyM2aia 无法直接暴露 ndarray 级别的算子，所以其实现方式为：对已加载的 Reader 修改 Normalization / Smoothing 参数并执行 lib.Update 更新，最后遍历 Spectrum 迭代器以触发 C++ 底层的高效计算。因此 m2aia 的时间代表了缓存 Reader 模式下的预处理耗时，而非纯底层算子的速度。
- **限制参数**：单次测试最大处理质谱数限制为 `MAX_SPECTRA = 2048`。
- **测试数据集**：`min`（极小）、`mid`（中等）、`example`（较大）、`original`（原始型大型）。
- **性能指标**：测量多轮运行的执行时间，单位为毫秒 (ms)。

| Name (time in ms)                                           | Min                 | Mean                | Median              | Max                 | StdDev           | Rounds |
|:----------------------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:---------------- |:------ |
| `test_massflow_cached_normalization[min-rms]`               | 9.9580 (1.0)        | 10.0436 (1.0)       | 10.0469 (1.0)       | 10.1259 (1.0)       | 0.0840 (1.0)     | 3      |
| `test_massflow_cached_normalization[min-tic]`               | 10.0297 (1.01)      | 97.2156 (9.68)      | 106.1427 (10.56)    | 175.4745 (17.33)    | 83.0829 (988.76) | 3      |
| `test_massflow_cached_smoothing[min-gaussian_window5]`      | 10.8976 (1.09)      | 27.4156 (2.73)      | 11.4096 (1.14)      | 59.9395 (5.92)      | 28.1677 (335.22) | 3      |
| `test_massflow_cached_normalization[original-tic]`          | 90.7455 (9.11)      | 97.3966 (9.70)      | 91.9653 (9.15)      | 109.4791 (10.81)    | 10.4815 (124.74) | 3      |
| `test_massflow_cached_normalization[original-rms]`          | 91.1345 (9.15)      | 91.4725 (9.11)      | 91.4985 (9.11)      | 91.7845 (9.06)      | 0.3258 (3.88)    | 3      |
| `test_massflow_cached_smoothing[original-gaussian_window5]` | 102.5274 (10.30)    | 102.6285 (10.22)    | 102.6425 (10.22)    | 102.7155 (10.14)    | 0.0948 (1.13)    | 3      |
| `test_m2aia_cached_normalization[min-rms]`                  | 122.4798 (12.30)    | 126.7770 (12.62)    | 128.4253 (12.78)    | 129.4259 (12.78)    | 3.7550 (44.69)   | 3      |
| `test_m2aia_cached_smoothing[min-gaussian_window5]`         | 123.2508 (12.38)    | 125.4743 (12.49)    | 125.0736 (12.45)    | 128.0984 (12.65)    | 2.4485 (29.14)   | 3      |
| `test_m2aia_cached_normalization[min-tic]`                  | 125.7557 (12.63)    | 130.9038 (13.03)    | 126.4504 (12.59)    | 140.5054 (13.88)    | 8.3225 (99.04)   | 3      |
| `test_massflow_cached_normalization[mid-tic]`               | 270.6526 (27.18)    | 277.1734 (27.60)    | 275.9481 (27.47)    | 284.9195 (28.14)    | 7.2119 (85.83)   | 3      |
| `test_massflow_cached_normalization[mid-rms]`               | 280.6815 (28.19)    | 281.1774 (28.00)    | 280.8110 (27.95)    | 282.0396 (27.85)    | 0.7495 (8.92)    | 3      |
| `test_massflow_cached_smoothing[mid-gaussian_window5]`      | 301.6017 (30.29)    | 304.8502 (30.35)    | 301.6568 (30.03)    | 311.2921 (30.74)    | 5.5789 (66.39)   | 3      |
| `test_massflow_cached_normalization[example-tic]`           | 351.8029 (35.33)    | 358.3686 (35.68)    | 355.1948 (35.35)    | 368.1082 (36.35)    | 8.6035 (102.39)  | 3      |
| `test_massflow_cached_normalization[example-rms]`           | 353.5463 (35.50)    | 367.5032 (36.59)    | 369.4140 (36.77)    | 379.5494 (37.48)    | 13.1064 (155.98) | 3      |
| `test_massflow_cached_smoothing[example-gaussian_window5]`  | 377.3020 (37.89)    | 397.9760 (39.62)    | 389.3217 (38.75)    | 427.3043 (42.20)    | 26.1004 (310.62) | 3      |
| `test_m2aia_cached_normalization[example-tic]`              | 614.1854 (61.68)    | 628.4366 (62.57)    | 632.1558 (62.92)    | 638.9687 (63.10)    | 12.8034 (152.37) | 3      |
| `test_m2aia_cached_normalization[example-rms]`              | 616.7119 (61.93)    | 627.7879 (62.51)    | 626.4280 (62.35)    | 640.2239 (63.23)    | 11.8149 (140.61) | 3      |
| `test_m2aia_cached_smoothing[mid-gaussian_window5]`         | 776.4744 (77.98)    | 776.6771 (77.33)    | 776.6613 (77.30)    | 776.8955 (76.72)    | 0.2110 (2.51)    | 3      |
| `test_m2aia_cached_normalization[mid-tic]`                  | 789.0040 (79.23)    | 793.1496 (78.97)    | 794.9055 (79.12)    | 795.5394 (78.56)    | 3.6042 (42.89)   | 3      |
| `test_m2aia_cached_normalization[mid-rms]`                  | 791.8502 (79.52)    | 797.6306 (79.42)    | 800.4416 (79.67)    | 800.6000 (79.06)    | 5.0066 (59.58)   | 3      |
| `test_m2aia_cached_smoothing[example-gaussian_window5]`     | 1,542.7261 (154.92) | 1,552.5098 (154.58) | 1,545.0931 (153.79) | 1,569.7104 (155.02) | 14.9430 (177.84) | 3      |
| `test_m2aia_cached_smoothing[original-gaussian_window5]`    | 1,608.0915 (161.49) | 1,613.1697 (160.62) | 1,613.7508 (160.62) | 1,617.6666 (159.76) | 4.8139 (57.29)   | 3      |
| `test_m2aia_cached_normalization[original-rms]`             | 1,611.1250 (161.79) | 1,619.1705 (161.21) | 1,621.9688 (161.44) | 1,624.4175 (160.42) | 7.0743 (84.19)   | 3      |
| `test_m2aia_cached_normalization[original-tic]`             | 1,611.1458 (161.79) | 1,624.5578 (161.75) | 1,625.7949 (161.82) | 1,636.7325 (161.64) | 12.8381 (152.79) | 3      |

## 端到端流水线（End-to-End Pipeline）速度对比 (MassFlow vs m2aia)

**对应测试代码文件**：[test_m2aia_pipeline_benchmark.py](file:///Users/dre/Desktop/dre/massflow-essay/MassFlow_v0.1/tests/test_m2aia_pipeline_benchmark.py)

### 测试内容说明

- **测试目的**：测试两套库各自完整的端到端预处理流水线速度，涵盖了读取文件、解析头部信息、完整的数据读入、核心计算以及最终结果写入/输出的全流程。
- **对比的方法**：
  - **MassFlow**：构建 `MSDataManagerImzML(path)` -> 加载头部元数据 -> 创建多线程 `Preprocessor` 实例（设置 Numba 最大线程数为 32） -> 执行 `.normalization()` 或 `.noise_reduction()` 流水线 -> 开启线程处理 `.start()` 并将最终输出序列化保存至临时目录子文件夹 -> 关闭 `processed_manager`。
  - **m2aia**：构建 `ImzMLReader` 设定归一化及平滑方式，然后使用质谱迭代器 `SpectrumIterator` 遍历并消费全部质谱数据（因为 m2aia 在迭代器循环中惰性触发并执行对应的预处理逻辑）。
- **测试数据集**：`min`（极小）、`mid`（中等）、`example`（较大）、`original`（原始型大型）。
- **性能指标**：测量多轮运行的执行时间，单位为毫秒 (ms)。

| Name (time in ms)                                             | Min                 | Mean                | Median              | Max                 | StdDev              | Rounds |
|:------------------------------------------------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:------------------- |:------ |
| `test_m2aia_pipeline_smoothing[min-gaussian_window5]`         | 825.3127 (1.0)      | 834.2489 (1.0)      | 831.3201 (1.0)      | 846.1138 (1.0)      | 10.7053 (1.92)      | 3      |
| `test_m2aia_pipeline_normalization[min-rms]`                  | 842.8697 (1.02)     | 849.8563 (1.02)     | 850.3725 (1.02)     | 856.3267 (1.01)     | 6.7433 (1.21)       | 3      |
| `test_m2aia_pipeline_normalization[min-tic]`                  | 847.5529 (1.03)     | 853.5452 (1.02)     | 854.4905 (1.03)     | 858.5921 (1.01)     | 5.5800 (1.0)        | 3      |
| `test_m2aia_pipeline_smoothing[mid-gaussian_window5]`         | 2,331.3120 (2.82)   | 2,343.1506 (2.81)   | 2,339.1675 (2.81)   | 2,358.9722 (2.79)   | 14.2537 (2.55)      | 3      |
| `test_m2aia_pipeline_normalization[mid-rms]`                  | 2,486.2402 (3.01)   | 2,532.9465 (3.04)   | 2,544.5276 (3.06)   | 2,568.0717 (3.04)   | 42.1271 (7.55)      | 3      |
| `test_m2aia_pipeline_normalization[mid-tic]`                  | 2,490.2954 (3.02)   | 2,519.5229 (3.02)   | 2,501.9767 (3.01)   | 2,566.2966 (3.03)   | 40.9261 (7.33)      | 3      |
| `test_massflow_pipeline_smoothing[min-gaussian_window5]`      | 3,654.1556 (4.43)   | 3,676.9336 (4.41)   | 3,669.2227 (4.41)   | 3,707.4226 (4.38)   | 27.4579 (4.92)      | 3      |
| `test_massflow_pipeline_normalization[min-rms]`               | 3,715.4353 (4.50)   | 3,834.4282 (4.60)   | 3,869.6172 (4.65)   | 3,918.2320 (4.63)   | 105.8788 (18.97)    | 3      |
| `test_massflow_pipeline_normalization[min-tic]`               | 3,782.3033 (4.58)   | 3,942.3981 (4.73)   | 3,979.9797 (4.79)   | 4,064.9114 (4.80)   | 145.0839 (25.99)    | 3      |
| `test_massflow_pipeline_smoothing[mid-gaussian_window5]`      | 5,003.6287 (6.06)   | 5,054.6473 (6.06)   | 5,059.8132 (6.09)   | 5,100.5000 (6.03)   | 48.6418 (8.72)      | 3      |
| `test_massflow_pipeline_normalization[mid-rms]`               | 5,124.6552 (6.21)   | 5,155.1126 (6.18)   | 5,131.1311 (6.17)   | 5,209.5514 (6.16)   | 47.2565 (8.47)      | 3      |
| `test_massflow_pipeline_normalization[mid-tic]`               | 5,137.4976 (6.22)   | 5,150.2721 (6.17)   | 5,153.1219 (6.20)   | 5,160.1969 (6.10)   | 11.6149 (2.08)      | 3      |
| `test_m2aia_pipeline_normalization[example-tic]`              | 5,232.0559 (6.34)   | 5,279.6636 (6.33)   | 5,294.1267 (6.37)   | 5,312.8083 (6.28)   | 42.2744 (7.58)      | 3      |
| `test_m2aia_pipeline_normalization[example-rms]`              | 5,296.7917 (6.42)   | 5,341.8516 (6.40)   | 5,353.0831 (6.44)   | 5,375.6800 (6.35)   | 40.6258 (7.28)      | 3      |
| `test_massflow_pipeline_smoothing[example-gaussian_window5]`  | 6,805.6035 (8.25)   | 6,821.7490 (8.18)   | 6,818.4570 (8.20)   | 6,841.1865 (8.09)   | 18.0185 (3.23)      | 3      |
| `test_massflow_pipeline_normalization[example-tic]`           | 7,014.9644 (8.50)   | 7,035.4178 (8.43)   | 7,024.4060 (8.45)   | 7,066.8831 (8.35)   | 27.6556 (4.96)      | 3      |
| `test_massflow_pipeline_normalization[example-rms]`           | 7,030.6638 (8.52)   | 7,189.9811 (8.62)   | 7,141.4322 (8.59)   | 7,397.8472 (8.74)   | 188.3445 (33.75)    | 3      |
| `test_m2aia_pipeline_smoothing[original-gaussian_window5]`    | 9,663.4987 (11.71)  | 9,709.7139 (11.64)  | 9,703.1801 (11.67)  | 9,762.4629 (11.54)  | 49.8046 (8.93)      | 3      |
| `test_m2aia_pipeline_normalization[original-tic]`             | 9,960.8127 (12.07)  | 9,981.8417 (11.97)  | 9,990.3015 (12.02)  | 9,994.4109 (11.81)  | 18.3272 (3.28)      | 3      |
| `test_m2aia_pipeline_normalization[original-rms]`             | 9,999.4309 (12.12)  | 10,025.5447 (12.02) | 10,005.2228 (12.04) | 10,071.9804 (11.90) | 40.3187 (7.23)      | 3      |
| `test_m2aia_pipeline_smoothing[example-gaussian_window5]`     | 11,057.8313 (13.40) | 11,123.8719 (13.33) | 11,114.1351 (13.37) | 11,199.6492 (13.24) | 71.4085 (12.80)     | 3      |
| `test_massflow_pipeline_smoothing[original-gaussian_window5]` | 31,185.5329 (37.79) | 31,286.3021 (37.50) | 31,216.9909 (37.55) | 31,456.3826 (37.18) | 148.1314 (26.55)    | 3      |
| `test_massflow_pipeline_normalization[original-tic]`          | 31,492.3459 (38.16) | 33,401.0713 (40.04) | 33,985.2015 (40.88) | 34,725.6665 (41.04) | 1,693.9589 (303.58) | 3      |
| `test_massflow_pipeline_normalization[original-rms]`          | 33,565.8942 (40.67) | 33,865.0776 (40.59) | 33,569.9743 (40.38) | 34,459.3642 (40.73) | 514.6714 (92.24)    | 3      |



# 使用的云机器受限，所以加速比不是特别明显

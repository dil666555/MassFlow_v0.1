# S11 — Max / Ultra Python/NumPy pipeline 重测

## Pipeline

本次测量 Table S11 的 Max、Ultra Python/NumPy batch 实现，共 18 个用例；Min/Mid 不重跑。使用现有 `*_memory.py` 中的 `dm_process` 入口，逐批读取、计算和写出，不全量预加载。

| dataset | file |
| --- | --- |
| max | `/Users/dre/Desktop/data/example/example.imzML` |
| ultra | `/Users/dre/Desktop/data/original/original.imzML` |

配置：`ROUNDS=2`、`iterations=1`、`warmup_rounds=1`，即预热 1 次、正式测量 2 次；批大小 256，读取线程 8。JSON 的 `extra_info` 记录批大小、读取线程和实际 Numba 辅助线程数。

| Stage | Method | 参数 |
| --- | --- | --- |
| Baseline Correction | LocMin | `width=5`, `smooth="none"` |
| Baseline Correction | SNIP | `m=5`, `decreasing=True`, `width=5`, `smooth="none"` |
| Normalization | TIC / RMS | `scale=1.0` |
| Peak Alignment | Default | `units="ppm"`, `binfun="min"`, `binratio=2.0` |
| Noise Reduction | MA / Gaussian / Savitzky–Golay | `window=5`；Gaussian 默认 `sd=1.25`；Savgol 默认 `polyorder=3`, `deriv=0`, `delta=1.0` |
| Peak Picking | origin | `width=2`, `relheight=0.012`, `snr=2.0`, `return_type="height"`, `use_numba=True` |

计时包含逐批读算写、输出头信息加载和关闭输出 manager 的清理；输入初始化及头信息加载在计时外。输出使用 `./temp`，每轮关闭时删除临时文件。测量使用文件系统缓存，不清空系统缓存、不强制 `fsync`。

峰对齐先在计时外用默认 Quantile 挑峰准备输入（`width=5`, `snr=2.0`）；计时内每轮重新计算参考轴（`clear_memory=True`），再读取、对齐和写出。此 batch 路径仍使用项目的 Numba 对齐辅助函数。

### Time command

在仓库根目录运行以下命令，仅测 Max、Ultra 的 batch 入口，不运行 flat，不加 `--memray` 或并行运行选项：

```bash
export MASSFLOW_S11_MAX_FILE="/Users/dre/Desktop/data/example/example.imzML"
export MASSFLOW_S11_ULTRA_FILE="/Users/dre/Desktop/data/original/original.imzML"

uv run pytest \
  tests/test_baseline_memory.py::TestBaseline::test_baseline_memory \
  tests/test_normalization_memory.py::TestNormalization::test_normalization_memory \
  tests/test_align_memory.py::TestAlign::test_align_memory \
  tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_memory \
  tests/test_pick_memory.py::TestPick::test_pick_memory \
  --benchmark-only \
  --benchmark-columns=min,mean,median,max,stddev,rounds \
  --benchmark-json="10-15-重测部分内容/S11-Max-Ultra-Python-pipeline.json" \
  -q
```

如需分开测量，在 `--benchmark-only` 前添加 `-k max` 或 `-k ultra`，并将 JSON 文件分别命名为 `S11-Max-Python-pipeline.json`、`S11-Ultra-Python-pipeline.json`；合并运行和分开运行二选一。

JSON 的 `stats` 时间单位为秒，采用 `stats.mean` 填表。实际次数看 `stats.rounds=2`，不看通用配置 `options.min_rounds`。终端若显示 ms，手动摘录时将时间及标准差除以 1000。

### result

状态：18 个用例已完成，正式测量均为 2 次。结果来源：[S11-Max-Ultra-Python-pipeline.json](S11-Max-Ultra-Python-pipeline.json)，报告时间 2026-10-16 00:06:04（Asia/Shanghai）。下表直接取 JSON 的 `stats`，单位为秒，显示 10 位小数；逐轮原始计时保存在 `stats.data`。

| dataset | method | min (s) | mean (s) | median (s) | max (s) | stddev (s) | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| max | LocMin | 34.1366238340 | 34.1628225840 | 34.1628225840 | 34.1890213340 | 0.0370506276 | 2 |
| max | SNIP (m=5) | 8.5926221250 | 8.6028236040 | 8.6028236040 | 8.6130250830 | 0.0144270700 | 2 |
| max | TIC | 4.2317035420 | 4.2497348545 | 4.2497348545 | 4.2677661670 | 0.0255001267 | 2 |
| max | RMS | 5.2897696660 | 5.3693647915 | 5.3693647915 | 5.4489599170 | 0.1125645060 | 2 |
| max | Alignment (min-ppm) | 17.5507309580 | 17.5800330620 | 17.5800330620 | 17.6093351660 | 0.0414394329 | 2 |
| max | MA | 5.1325384580 | 5.3856051245 | 5.3856051245 | 5.6386717910 | 0.3578903120 | 2 |
| max | Gaussian | 6.1264699580 | 6.1459943540 | 6.1459943540 | 6.1655187500 | 0.0276116656 | 2 |
| max | Savitzky–Golay | 6.3260910000 | 6.3965252500 | 6.3965252500 | 6.4669595000 | 0.0996090716 | 2 |
| max | origin | 39.1562080830 | 39.1803183540 | 39.1803183540 | 39.2044286250 | 0.0340970722 | 2 |
| ultra | LocMin | 35.1010983750 | 35.2621780415 | 35.2621780415 | 35.4232577080 | 0.2278010490 | 2 |
| ultra | SNIP (m=5) | 27.1215969580 | 28.7595610210 | 28.7595610210 | 30.3975250840 | 2.3164309926 | 2 |
| ultra | TIC | 27.6164910000 | 29.2588686460 | 29.2588686460 | 30.9012462920 | 2.3226727415 | 2 |
| ultra | RMS | 17.3238235000 | 24.4869020205 | 24.4869020205 | 31.6499805410 | 10.1301227920 | 2 |
| ultra | Alignment (min-ppm) | 14.9354864170 | 14.9374282920 | 14.9374282920 | 14.9393701670 | 0.0027462260 | 2 |
| ultra | MA | 16.9635690000 | 24.3440776460 | 24.3440776460 | 31.7245862920 | 10.4376154244 | 2 |
| ultra | Gaussian | 32.9963619580 | 33.0496287915 | 33.0496287915 | 33.1028956250 | 0.0753306784 | 2 |
| ultra | Savitzky–Golay | 30.8866582500 | 31.7903641665 | 31.7903641665 | 32.6940700830 | 1.2780331635 | 2 |
| ultra | origin | 52.7098990840 | 52.7608307295 | 52.7608307295 | 52.8117623750 | 0.0720282238 | 2 |

Ultra RMS 两轮为 17.3238、31.6500 s；Ultra MA 为 31.7246、16.9636 s，标准差分别约占均值的 41.4%、42.9%。保留全部测量值及均值，不据此判断接近 1× 的差异具有稳定性能优势。

### 运行环境

| 项目 | 记录 |
| --- | --- |
| CPU / 操作系统 | Apple M5，10 个逻辑 CPU；Darwin 27.0.0，arm64 |
| Python / pytest-benchmark | CPython 3.12.13 / 5.2.3 |
| 批大小 / 读取线程 / Numba 辅助线程 | 256 / 8 / 4 |
| Git 提交 | `b918f4577146d931ec1fffbda64858b86eb8e013` |
| 工作区 | `dirty=true` |
| 内存容量、NumPy/Numba 版本 | JSON 未记录 |

### 与 Numba pipeline 的耗时比值

定义 `S = T_Python/NumPy / T_Numba`，均使用各自 mean；`S > 1` 表示 Numba 更快，`S < 1` 表示 Python/NumPy 更快。Numba 来自 [`tests/pipeline_outcome.py`](../tests/pipeline_outcome.py) 的 `TIME_DATA` 第二个值，与 S6 同源；SNIP 的旧 Numba 数据也显式使用 `m=5`，见 [`new_mid_file_pipeline.md`](../tests/new_mid_file_pipeline.md)。以下比值使用未舍入的原始数值计算。

**硬件不同：Python/NumPy 在 M5，旧 Numba 在 M4 Mac mini。下表仅为跨机器耗时比值，不能作为同机实现加速比。**

| Method（Python / Numba） | Max Python (s) | Max Numba (s) | Max 比值 | Ultra Python (s) | Ultra Numba (s) | Ultra 比值 |
| --- | --- | --- | --- | --- | --- | --- |
| LocMin | 34.1628 | 7.1571 | 4.77× | 35.2622 | 18.8867 | 1.87× |
| SNIP (m=5) | 8.6028 | 4.0907 | 2.10× | 28.7596 | 17.1464 | 1.68× |
| TIC | 4.2497 | 4.3329 | 0.98× | 29.2589 | 24.7824 | 1.18× |
| RMS | 5.3694 | 3.7718 | 1.42× | 24.4869 | 24.2586 | 1.01× |
| Alignment | 17.5800 | 4.8021 | 3.66× | 14.9374 | 6.5741 | 2.27× |
| MA | 5.3856 | 4.3401 | 1.24× | 24.3441 | 24.6143 | 0.99× |
| Gaussian | 6.1460 | 3.8812 | 1.58× | 33.0496 | 23.9425 | 1.38× |
| Savitzky–Golay | 6.3965 | 3.8573 | 1.66× | 31.7904 | 24.0176 | 1.32× |
| Peak picking: origin / Quantile | 39.1803 | 24.6802 | 1.59× | 52.7608 | 28.9606 | 1.82× |
| Peak picking: origin / Diff | 39.1803 | 6.0213 | 6.51× | 52.7608 | 11.3753 | 4.64× |
| Peak picking: origin / SD | 39.1803 | 7.9576 | 4.92× | 52.7608 | 10.9617 | 4.81× |

Peak picking 的 Python 只有一个 `origin` 结果，分别与 Numba Quantile、Diff、SD 对比；它们是不同挑峰方法，此处也不能解读为相同算法的编译加速比。

### 结果回填

本次只回填本文档；`tests/python_outcome.py` 尚未更新这份 pipeline JSON。后续取 JSON 的 `stats.mean` 更新该文件对应 Max/Ultra 元组的第一个值（batch，秒）；第二个值暂保留旧 S6 的 Numba pipeline 数据，并保留硬件来源区别。`origin` 作为 Quantile、Diff、SD 的共享参考，回填到这三行的 batch 值。

SI 的 S11 Max/Ultra 必须标注为 pipeline 耗时，Min/Mid 仍为纯计算；本次结果也不能用来声称“纯计算耗时必然小于 pipeline”。

# S11 — Min / Mid SNIP 统一 m=5 重测

## Baseline Correction

本次记录 Table S11 中 Python/NumPy（batch）及 Table S10 中 Numba（flat）实现的 Min、Mid SNIP 重测耗时。两种实现均显式使用 `m=5`、`decreasing=True`。

对应脚本：[`tests/test_baseline_speed.py`](../tests/test_baseline_speed.py)。batch 入口为 `TestBaseline::test_baseline_speed`，flat 入口为 `TestBaseline::test_baseline_flat_speed`。

| dataset | file |
| --- | --- |
| min | `/Users/dre/Desktop/data/min/file_min_profile.imzML` |
| mid | `/Users/dre/Desktop/data/mid/file_mid_profile.imzML` |

### Time command

#### batch（已运行，命令留档）

以下命令只测 Min、Mid 的两个 batch SNIP 用例：

```bash
uv run pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_speed \
  --benchmark-only \
  --benchmark-columns=min,mean,median,max,stddev,rounds \
  --benchmark-json="10-15-重测部分内容/S11-SNIP-min-mid-m5.json" \
  -q
```

#### flat（已运行，命令留档）

在仓库根目录运行以下命令，仅测 Min、Mid 的两个 flat SNIP 用例，不重复运行 batch：

```bash
uv run pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_flat_speed \
  --benchmark-only \
  --benchmark-columns=min,mean,median,max,stddev,rounds \
  --benchmark-json="10-15-重测部分内容/S11-SNIP-min-mid-m5-numba.json" \
  -q
```

flat 配置为 `method="snip_numba"`、`m=5`、`decreasing=True`，预先缓存批大小为 256 的 intensity/lengths 数组，不缓存 m/z；计时范围为遍历缓存并调用 `FlatPreprocess.baseline_reduction_flat`，不包含输入预加载和结果写出。`THREADS=[None]` 使用项目默认 Numba 线程配置（由 `apply_numba_runtime` 决定），不扫描 1–32 线程。

两类测试均沿用 `ROUNDS=2`、`iterations=1`、`warmup_rounds=1`，即预热 1 次、正式测量 2 次。flat 测试将实际 Numba 线程数写入 JSON 各用例的 `extra_info.numba_threads`，填表时一并记录。

JSON 保存完整计时结果；以下汇总表统一使用秒（s）。终端表格会自动选择单位，若显示 `time in ms`，填表时将时间及标准差除以 1000。

### result

状态：batch、flat 均已运行，以下统计及逐轮数据已从两份 JSON 回填。时间单位均为秒（s）；表格显示 10 位小数，JSON 和 `tests/python_outcome.py` 保留原始 mean 精度。

结果来源：

- batch：[S11-SNIP-min-mid-m5.json](S11-SNIP-min-mid-m5.json)，报告时间为 2026-10-15 23:04:34（Asia/Shanghai）。
- flat：[S11-SNIP-min-mid-m5-numba.json](S11-SNIP-min-mid-m5-numba.json)，报告时间为 2026-10-15 23:20:16（Asia/Shanghai）。

统计值取自对应用例的 `stats`。两份报告的 `options.min_rounds=5` 是通用配置，实际执行次数以 `stats.rounds=2` 为准，与脚本的 `benchmark.pedantic(rounds=2)` 一致。

#### batch — Table S11

`test_baseline_speed`（batch，SNIP，`m=5`，单位 s）

| dataset | method | m | min (s) | mean (s) | median (s) | max (s) | stddev (s) | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | snip | 5 | 0.4986974580 | 0.4990766875 | 0.4990766875 | 0.4994559170 | 0.0005363115 | 2 |
| mid | snip | 5 | 2.1208060830 | 2.1421782500 | 2.1421782500 | 2.1635504170 | 0.0302248084 | 2 |

逐轮计时（提取自 JSON 的 `stats.data`，顺序与 JSON 一致）：

| dataset | round 1 (s) | round 2 (s) |
| --- | --- | --- |
| min | 0.4994559170 | 0.4986974580 |
| mid | 2.1635504170 | 2.1208060830 |

#### flat — Table S10

`test_baseline_flat_speed`（flat，SNIP，`m=5`，单位 s）

| dataset | method | m | Numba threads | min (s) | mean (s) | median (s) | max (s) | stddev (s) | rounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| min | snip_numba | 5 | 4 | 0.1432801250 | 0.1435812705 | 0.1435812705 | 0.1438824160 | 0.0004258840 | 2 |
| mid | snip_numba | 5 | 4 | 1.0855624170 | 1.1159906670 | 1.1159906670 | 1.1464189170 | 0.0430320438 | 2 |

逐轮计时（提取自 JSON 的 `stats.data`，顺序与 JSON 一致）：

| dataset | round 1 (s) | round 2 (s) |
| --- | --- | --- |
| min | 0.1432801250 | 0.1438824160 |
| mid | 1.1464189170 | 1.0855624170 |

### 运行环境

两份 JSON 记录的运行环境一致：

| 项目 | JSON 记录 |
| --- | --- |
| 操作系统 | Darwin 27.0.0，arm64 |
| CPU | Apple M5，10 个逻辑 CPU |
| Python | CPython 3.12.13 |
| pytest-benchmark | 5.2.3 |
| flat 实际 Numba 线程数 | 4，来自各用例 `extra_info.numba_threads` |
| GC | 计时期间禁用（`disable_gc=true`） |
| Git 提交 | `b918f4577146d931ec1fffbda64858b86eb8e013` |
| 工作区 | 两次运行均为 `dirty=true`，包含未提交修改 |
| 内存容量、NumPy/Numba 版本 | JSON 未记录 |

### 结果回填

已取 JSON 的 `stats.mean`（s）更新 `tests/python_outcome.py` 中 `Baseline Correction → snip → min/mid` 的两个元组，并补充来源注释：

```python
'min': (0.4990766875052941, 0.14358127050218172),
'mid': (2.1421782500037807, 1.1159906670000055),
```

每个元组为 `(batch, flat)`，两项均为秒，无需对 JSON 再做 ms→s 换算。SI 中 Table S11 的 SNIP Min、Mid 应采用第一个值，Table S10 的对应单元格应采用第二个值；本文档不直接修改 SI 原稿。

Max、Ultra 的 Python/NumPy pipeline 重测另行记录，本次两条命令均不涉及。

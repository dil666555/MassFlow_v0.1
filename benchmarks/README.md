# 同设备统一重测

原分支 `test/time_and_memory_of_three_version` 保留旧脚本和结果；新分支 `codex/unified-benchmark-rerun` 从头采集，不引用旧测量值。

## 测什么

每行单独测一个预处理算子，不串联整套预处理。所有任务统一 **预热 1 次、正式运行 2 次**。

| 项目 | 命令 | 实际测量 | 最终表 |
| --- | --- | --- | --- |
| 1. Python/NumPy core | `python-core` | Min/Mid：cache；Max/Ultra：Python 自身 pipeline，共 36 用例 | 36 行，Max/Ultra 标注 pipeline 替代 |
| 2. Numba-parallel pipeline 时间 | `numba-pipeline` | 四份数据，13 方法，共 52 用例 | 52 行 |
| 3. Numba-parallel core | `numba-core` | 只测 Min/Mid cache，共 26 用例 | 52 行；Max/Ultra 引用第 2 项，不重复测 |
| 4. Cardinal pipeline 时间 | `cardinal-pipeline` | 四份数据，13 方法，共 52 用例 | 52 行 |
| 5. Numba-parallel pipeline 内存 | `numba-memory` | 四份数据，13 方法，共 52 用例 | 52 行，峰值 RSS，MiB |
| 6. Cardinal pipeline 内存 | `cardinal-memory` | 四份数据，13 方法，共 52 用例 | 52 行，峰值 RSS，MiB |

Python/NumPy 共 9 个方法：LocMin、SNIP、TIC、RMS、MA、Gaussian、Savgol、origin、Align。该实现没有 Reference 或 Quantile/Diff/SD/MAD 的独立实现，不补造数据；`origin` 可作为挑峰共享参考，但不是另外四种算法的等价实现。Python/NumPy 指现有 `BatchPreprocess` 路径，其中对齐仍调用项目的 Numba 辅助函数。

## 配置与参数

所有参数唯一来源：[config.json](config.json)。改路径或参数应在 `init` 前完成。

| dataset | 默认输入 |
| --- | --- |
| min | `/Users/dre/Desktop/data/min/file_min_profile.imzML` |
| mid | `/Users/dre/Desktop/data/mid/file_mid_profile.imzML` |
| max | `/Users/dre/Desktop/data/example/example.imzML` |
| ultra | `/Users/dre/Desktop/data/original/original.imzML` |

每份 imzML 必须有同名 ibd。`init` 记录谱数、数据点数、文件大小、修改时间、ibd UUID 和输入精度；只读取 XML 与各 m/z 轴端点，不加载全量 intensity。

| 项目 | Python/NumPy | Numba-parallel | Cardinal |
| --- | --- | --- | --- |
| LocMin | `width=5`, `smooth="none"`, `span=0.1`, `upper=False` | 同左 | `smooth="none"`, `span=0.1`, `upper=FALSE`；底层 `matter::locmin` 默认窗口为 5，`estbase_loc` 不接受 width |
| SNIP | `m=5`, `decreasing=True` | 同左 | `width=5`, `decreasing=TRUE` |
| TIC / RMS | `scale=1.0` | `scale=1.0` | 显式 `scale=1.0`，不采用按数据规模变化的默认 scale |
| Reference | 无 | `scale=1.0`，共用 ref，最近邻 | `scale=1.0`，同一 ref，最近邻 |
| MA | `window=5` | `window=5` | `width=5` |
| Gaussian | `window=5`, `sd=1.25` | 同左 | `width=5`, `sd=1.25`；显式覆盖不同的默认 sd |
| Savgol | `window=5`, `polyorder=3`, `deriv=0`, `delta=1` | 同左 | `method="sgolay"`, `width=5`, `order=3`, `deriv=0`, `delta=1` |
| Quantile / Diff / SD / MAD | 无 | `width=5`, `snr=2`, `return_type="height"`, `nbins=1`, `overlap=0.5` | `width=5`, `SNR=2`, `type="height"`, `nbins=1`, `overlap=0.5` |
| origin | SciPy 挑峰，`width=2`, `relheight=0.012`, `snr=2`, `return_type="height"` | 无 | 无 |
| Align | `binfun="min"`, `binratio=2`, ppm | 同左 | 同左 |

Reference 的 ref 取四舍五入前的“本数据集各谱共同 m/z 区间中点”，每个数据集固定一个值。Numba 的 `ref_tolerance` 设为整个输入 m/z 范围宽度加 1 Da，使其采用最近邻，不额外施加旧的 0.1 Da 截断；Cardinal 同样取最近邻。

固定批大小 **256**；MassFlow 读线程 **8**；Numba 工作线程 **4**，不扫描线程数。Numba pipeline 的两个队列均为 1，保留输入顺序。Cardinal 显式使用 **`SerialParam()`（1 worker）**，避免默认 BiocParallel 配置随机器变化；这是 Numba 并行实现与 Cardinal 串行后端的比较，不能称为相同线程预算的比较。BLAS 线程固定为 1。

### 计时范围

- **cache core**：计时外完整缓存 Min/Mid；Python 缓存谱对象批次，Numba 缓存 flat 数组批次。计时只遍历缓存、执行当前算子并释放输出，不读文件、不写输出。保留算子所需的分配与 Python 调用开销，不是单个底层 kernel 的时间。
- **pipeline**：计时包括输入打开与头信息解析、逐批读取、当前算子计算、最终 imzML/ibd 写出并完成；输入/输出 manager 关闭清理、临时文件删除和结果校验在计时外。没有全量预加载，Max/Ultra 没有 cache core 测试。
- **Cardinal 输出**：原生 `process(outfile=...)` 按块写中间文件，再由 `writeImzML` 按块导出，最终精度与 MassFlow 一致（m/z float64、intensity float32）。中间 I/O 和最终导出都在计时内；不把输出全部积存在内存中。Align 直接导出其 lazy sparse 结果。
- **Align**：`prepare` 先用固定的 Numba Quantile 参数生成公共挑峰输入，所有实现读取同一份文件；准备不计时。每轮计时内重新计算参考轴并对齐。pipeline 采用按批释放缓存的参考轴计算，Min/Mid core 采用缓存；内部接口统一用相对容差，避免 ppm 重复换算。

Python 和 R 都在每轮前执行 GC，计时中保持 GC 启用。使用系统文件缓存，不清空缓存、不强制 fsync，不将这些数字称为冷盘时间。各实现采用自身的数据布局、计算精度和原生算子；参数一致不代表已经验证数值逐点等价。

### 内存范围

内存单独运行，不从受采样干扰的计时结果回填时间表。每个用例启动独立进程，预热 1 次，随后正式测量 2 次，每轮单独重置 RSS 采样峰值。

外部控制器每 **5 ms** 采样被测进程 RSS，只覆盖正式 pipeline 的读、算、写阶段；停止后才校验、清理。单位为 **MiB = bytes / 2²⁰**，报告两次 `sampled_peak_rss_mib` 的均值及标准差，另保留各轮开始前的 `baseline_rss_mib`、采样次数及实际最大间隔。RSS 包含解释器、库和已驻留缓存，**不是额外分配量**；采样可能漏掉很短的峰值。Cardinal 为单进程 SerialParam，Numba 为单进程多线程，两边测同一指标；不使用 memray 累计分配量或 R Vcell 计数充当峰值内存。

## 运行命令

在新分支的仓库根目录执行，全部在同一台机器、同一软件环境下串行运行。

### 0. 环境检查与公共输入准备

Python 依赖使用仓库锁文件（dev 依赖已包含 psutil）。R 需要本机的 Cardinal、CardinalIO、matter、BiocParallel、jsonlite；本次接口核对环境为 R 4.5.2、Cardinal 3.12.0、CardinalIO 1.8.0、matter 2.12.0、BiocParallel 1.44.0。

```bash
uv sync --frozen --extra r
uv run --frozen --extra r python benchmarks/run.py init
uv run --frozen --extra r python benchmarks/run.py prepare
```

`init` 检查依赖、路径并保存环境清单；`prepare` 才开始生成四份公共对齐输入。不要在不同设备复制同一个结果目录续跑。所有任务都会检查机器、软件版本、源码和配置是否仍与 `init` 一致。

### 1. Python/NumPy core（Max/Ultra 使用自身 pipeline）

```bash
uv run --frozen --extra r python benchmarks/run.py python-core
```

### 2. Numba-parallel pipeline 时间

```bash
uv run --frozen --extra r python benchmarks/run.py numba-pipeline
```

### 3. Numba-parallel core（仅测 Min/Mid）

```bash
uv run --frozen --extra r python benchmarks/run.py numba-core
```

### 4. Cardinal pipeline 时间

```bash
uv run --frozen --extra r python benchmarks/run.py cardinal-pipeline
```

此命令由 Python 控制器调用独立的 [cardinal_bench.R](cardinal_bench.R)，R 中直接使用 Cardinal，不经 MassFlow 的 R adapter。

### 5. Numba-parallel pipeline 内存

```bash
uv run --frozen --extra r python benchmarks/run.py numba-memory
```

### 6. Cardinal pipeline 内存

```bash
uv run --frozen --extra r python benchmarks/run.py cardinal-memory
```

### 7. 汇总六张表

```bash
uv run --frozen --extra r python benchmarks/run.py summarize
```

输出在 `benchmarks/results/current/`：`manifest.json`、各用例原始 JSON、六张同名 CSV 和 `results.md`。所有时间都是秒；Max/Ultra 的两类 core 表均显式标为 `pipeline_substitution`。Numba 替代值直接引用本轮 `numba-pipeline` JSON，不复制旧数据、不重复测量。内存表单位均为 MiB。

### 中断后继续 / 分开运行

每个完整用例完成后立即保存；加 `--resume` 会跳过已完成用例，仅重新运行未完成用例，例如：

```bash
uv run --frozen --extra r python benchmarks/run.py cardinal-pipeline --resume
uv run --frozen --extra r python benchmarks/run.py python-core --dataset min mid --resume
uv run --frozen --extra r python benchmarks/run.py python-core --dataset max ultra --resume
```

`prepare` 也支持 `--resume`。可用 `--case snip` 等缩小到某个方法，之后必须补齐所有用例才可 `summarize`。日志保存在 `results/current/logs/`；失败立即停止，不把失败记录为零或静默略过。

如果要开启另一轮实验或更换机器/参数，给上述每条命令统一添加新的 `--run-dir benchmarks/results/实验名`，从 `init` 开始。不要修改已初始化实验的配置或源码后混合续跑。

## result

尚未运行正式测试，无旧结果或预估数值。测试完成后由 `summarize` 生成完整结果表，并据此更新论文 SI；core 替代列和测量范围必须随表保留。

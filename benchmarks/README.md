# 同设备重新测试

最新补测口径见 [READ_COMPUTE.md](READ_COMPUTE.md)：Min/Mid 缓存 core 保留；Max/Ultra 改为读＋算、不写出、不再用 pipeline 替代，另重测 Ultra SNIP 的三方 pipeline。新结果写入 `results/read-compute/`。下文和 `RESULTS.md` 保留为第一轮归档，不覆盖其原始数值或旧图。

原分支 `test/time_and_memory_of_three_version` 不变。新分支保存本轮脚本；仅按本次要求复用原分支在同一台 M5 上测得的 Python Min/Mid SNIP（m=5），不回填旧 M4 结果。

## 测试范围

| 项目 | 数据与计时范围 |
| --- | --- |
| Python/NumPy core | Min/Mid cache；Max/Ultra 用 Python 自身 pipeline 替代，9 方法 × 4 数据 |
| Numba-parallel pipeline 时间 | 13 方法 × 4 数据 |
| Numba-parallel core | 只测 Min/Mid cache；Max/Ultra 直接引用本轮 Numba pipeline |
| Cardinal pipeline 时间 | 沿原 R 脚本计 `process(...)`，13 方法 × 4 数据，不额外导出 |
| Numba-parallel pipeline 内存 | 同对应 Python 测试入口，单独采样 RSS |
| Cardinal pipeline 内存 | 同原 R 处理调用，不额外导出，单独采样 RSS |

全部预热 **1 次**，正式测量 **2 次**。Python 使用 **pytest / pytest-benchmark**，沿原分支的 `benchmark.pedantic(rounds=2, iterations=1, warmup_rounds=1)`；沿用项目原有 GC 配置。Cardinal 使用原脚本的 `gc()` / `system.time()`。

## 数据与参数

路径和参数见 [config.json](config.json)，在 `init` 前修改。

| dataset | file |
| --- | --- |
| min | `/Users/dre/Desktop/data/min/file_min_profile.imzML` |
| mid | `/Users/dre/Desktop/data/mid/file_mid_profile.imzML` |
| max | `/Users/dre/Desktop/data/example/example.imzML` |
| ultra | `/Users/dre/Desktop/data/original/original.imzML` |

| 算子 | 原脚本参数 |
| --- | --- |
| LocMin | Python/Numba `width=5`；三者 `smooth="none"`, `span=0.1`, `upper=False`；Cardinal 保留原默认局部窗口 |
| SNIP | Python/Numba `m=5`；Cardinal `width=5`；均 `decreasing=True` |
| TIC / RMS | Python 保留 `scale=1.0`；Numba `scale=None`；Cardinal 不传 scale，均沿各自原脚本 |
| Reference | 第一条谱 m/z 向量的中间值；Numba `ref_tolerance=0.1`，Cardinal 保留默认最近邻选择 |
| MA / Gaussian | Python/Numba `window=5`；Cardinal `width=5`；Gaussian 均不额外覆盖原来的默认 sd |
| Savgol | 窗口 5、阶数 3、`deriv=0`, `delta=1.0`；Cardinal 方法名为 `sgolay` |
| Quantile / Diff / SD / MAD | `width=5`, SNR=2、height、`nbins=1`, `overlap=0.5` |
| Python origin | `width=2`, `relheight=0.012`, `snr=2`, height，作为单独参考方法 |
| Align | `units="ppm"`, `binfun="min"`, `binratio=2.0` |

这里保留原脚本的默认值，不再擅自改成统一的 scale/sd；这些默认值在不同实现中不一定相等。Python 没有 Reference 和 Quantile/Diff/SD/MAD 的独立实现，不为其补造结果。

MassFlow 批大小 256、读取线程 8、Numba 工作线程 4；不扫描线程数。Cardinal 不设置 BPPARAM、不注册并行后端、不强制块大小，保留原脚本默认配置；注册后端与有效处理后端的区别见下文。

后端记录更正：旧 `manifest.json` 和用例 JSON 中的 `parallel_backend/workers` 来自 `BiocParallel::bpparam()`，表示注册的默认后端，不代表 Cardinal 实际调用。当前 Cardinal 的 `getCardinalBPPARAM()` 返回 `NULL`；`process()` 将它显式传给 matter，`matter:::bplapply_int(..., BPPARAM=NULL)` 使用串行循环，因此注册的 `MulticoreParam / 8` 不能解读为实际启用了 8 个进程。脚本不改变这个处理行为。

## 计时范围

- **Python/Numba core**：fixture 中缓存 Min/Mid，计时内遍历缓存并计算，不读谱文件、不写结果。
- **Python/Numba pipeline**：输入 manager 初始化和头信息加载在 fixture 中；计时包含批量读取、计算、写出及关闭输出 manager，与原 `*_memory.py` 的入口一致。Python 调用原 `dm_process`，Numba 调用原 `Preprocessor`。
- **Cardinal**：照原分支 `tests/new_mid_file_pipeline_cardinal.md`：先 `x <- readImzML(file)`，再计 `process(reduceBaseline/smooth/normalize/peakPick/peakAlign(...))`。不传 `outfile`，不调用 `writeImzML`，不额外强制物化 lazy 结果。
- **Align 准备**：MassFlow 在计时外生成固定 Quantile 挑峰输入；Cardinal 按原脚本在计时外自行 `process(peakPick(...))`。每轮参考轴计算在计时内。Numba 的参考轴 flat cache 在 fixture 中准备，与原 flat 测试一致。

Python 路径的 **ref 全流程使用 [peak_align_numpy.py](peak_align_numpy.py)**：网格估计、NumPy 最近邻查找、分箱冲突处理、频次加权合并，不调用 Numba。Numba 路径保留原 `reference_computer`。相对容差按内部接口传递，不重复转换 ppm。此修改只替换 Python 的 ref 计算；后续谱对齐仍沿用原 `BatchPreprocess`，其底层对齐 kernel 未改。

时间表应分别注明上述范围，不能把 Cardinal 描述为包含结果导出的端到端时间。

内存仍按本轮已说明的 RSS 方式单独测量：外部控制器约每 5 ms 采样正式算子阶段的进程 RSS，报告两轮峰值的均值和标准差，单位 MiB。包括解释器、库及驻留缓存；不是 memray 累计分配量或 R Vcell 计数。Cardinal 读取/挑峰准备在采样外，MassFlow 输入 fixture 在采样外；各轮 baseline 和实际采样间隔保留在原始 JSON。

## 命令

在仓库根目录、同一台机器上串行执行。

### 第一轮归档：一次运行全部时间与内存测试

```bash
mkdir -p benchmarks/results
nohup caffeinate -i bash benchmarks/run_times.sh \
  > benchmarks/results/time-run.log 2>&1 < /dev/null &
```

依次执行以下七步，均预热 1 次、正式 2 次，先完成全部时间测试，再测内存：

1. Numba pipeline：四份数据。
2. Numba core：Min/Mid。
3. Cardinal pipeline：四份数据。
4. Python core：Min/Mid。
5. Python core：Max/Ultra，使用自身 pipeline 时间替代。
6. Numba pipeline 内存：四份数据。
7. Cardinal pipeline 内存：四份数据。

脚本自动初始化并准备对齐输入；已有同轮结果时跳过已完成用例。Python/Numba 由控制器逐用例调用 pytest，每个用例独立进程，完成后立即保存 JSON。

启动脚本设置 `R_MAX_VSIZE=32Gb`，令每个新 Rscript 进程的向量堆上限为 **32768 MiB（32 GiB）**，对应此次 Max/LocMin 的 `vector memory limit of 16.0 Gb reached` 错误。RStudio 中的 `mem.maxVSize()` 设置只对当时的 R 会话生效，不会自动传给这些独立 Rscript 进程。上限、Cardinal 有效后端及 BiocParallel 注册后端另存到 `cardinal-runtime-32gb.json`，旧结果保持原样。此修改只涉及启动脚本，未改变被计时的算子源码或参数，可以使用原结果目录续跑。

32 GiB 是允许的向量堆分配上限，不增加本机 16 GiB 物理内存；较大任务可能使用交换空间，仍可能因资源不足失败。它解决已观察到的 16 GiB 软件上限，不保证所有 Max/Ultra 用例都能完成。

脚本调用 [reuse_python_core.py](reuse_python_core.py)，读取原分支的 `10-15-重测部分内容/S11-SNIP-min-mid-m5.json`，仅复用 M5 上的 Python Min/Mid SNIP 两项，其余缺失用例照常测量，Max/Ultra 全部重测。导入前检查主机、架构、逻辑 CPU 数、Python 版本及当前 SNIP 参数；原报告另存于结果目录的 `imports/`，用例带 `reused_result=true` 和原始来源信息。不会覆盖已有完整用例，也不修改原分支。

复用的旧 SNIP 入口在预加载后仍遍历线程化 batch generator，并包含运行时设置开销；本轮新 core 入口直接遍历缓存。因此两项标记为 `cache_core_legacy`，不能说计时边界完全相同。旧 JSON 未记录库版本、输入指纹及温度状态，这些信息不补造。

每一步开始前静置 **300 秒（5 分钟）**，第一步在对齐输入准备后也静置。等待不计入用例耗时，日志记录时长；每个用例内部仍按原流程连续预热和测量，不插入等待。5 分钟是减少组间余热的经验性安排，不能证明已完全冷却，也不能排除长任务内部的降频影响。需要改间隔时，在启动命令的 `nohup` 前添加 `BENCH_COOLDOWN_SECONDS=600`（10 分钟）；本轮保持统一设置。

`nohup` 允许关闭终端后继续运行；`caffeinate -i` 在脚本运行期间阻止空闲休眠，屏幕可以熄灭。电脑接电、保持开机；笔记本不要合盖。遇到错误脚本停止，修复后执行同一命令续跑。运行期间不要修改源码、配置或输入数据。

查看进度：

```bash
tail -f benchmarks/results/time-run.log
```

按 `Ctrl+C` 只退出日志查看，不停止后台测试。全部完成时日志显示 `All seven time and memory steps completed`。用例详细输出在 `benchmarks/results/current/logs/<组名>/<数据集>-<方法>/worker.log`。

结果自动保存为 `benchmarks/results/current/<组名>/<数据集>-<方法>.json`，例如 `python-core/min-snip.json`、`numba-pipeline/max-snip.json`、`cardinal-pipeline/ultra-snip.json`；包含两次正式测量值 `stats.data`、均值 `stats.mean`、标准差、参数和测量范围。时间组单位为秒，内存组单位为 MiB，内存结果分别保存在 `numba-memory/`、`cardinal-memory/`。`manifest.json` 保存本轮环境、配置及输入信息。Numba core 的 Max/Ultra 后续汇总时直接引用本轮 pipeline JSON，不重复测量。

这条脚本使用逐用例 JSON；下方手动执行整组 pytest 时才另生成整组 `*-pytest.json`。七步全部完成后，可执行下方第 7 节的汇总命令，生成六张 CSV 和 `results.md`。

### 0. 准备

```bash
uv sync --frozen --extra r
uv run --frozen --extra r python benchmarks/run.py init
uv run --frozen --extra r python benchmarks/run.py prepare
```

R 使用本机现有 Cardinal、CardinalIO、matter、BiocParallel、jsonlite。`init` 记录环境和输入信息，`prepare` 准备 MassFlow 的对齐输入；二者不生成性能结果。

### 1. Python core（Max/Ultra 使用自身 pipeline）

```bash
uv run --frozen --extra r pytest benchmarks/python_bench.py \
  --bench-group python-core --benchmark-only \
  --benchmark-columns=min,mean,median,max,stddev,rounds \
  --benchmark-json="benchmarks/results/current/python-core-pytest.json" -q
```

### 2. Numba-parallel pipeline 时间

```bash
uv run --frozen --extra r pytest benchmarks/python_bench.py \
  --bench-group numba-pipeline --benchmark-only \
  --benchmark-columns=min,mean,median,max,stddev,rounds \
  --benchmark-json="benchmarks/results/current/numba-pipeline-pytest.json" -q
```

### 3. Numba-parallel core（只测 Min/Mid）

```bash
uv run --frozen --extra r pytest benchmarks/python_bench.py \
  --bench-group numba-core --benchmark-only \
  --benchmark-columns=min,mean,median,max,stddev,rounds \
  --benchmark-json="benchmarks/results/current/numba-core-pytest.json" -q
```

### 4–6. Cardinal 时间、Numba 内存、Cardinal 内存

```bash
uv run --frozen --extra r python benchmarks/run.py cardinal-pipeline
uv run --frozen --extra r python benchmarks/run.py numba-memory
uv run --frozen --extra r python benchmarks/run.py cardinal-memory
```

Cardinal 入口直接执行 [cardinal_bench.R](cardinal_bench.R)；Numba 内存入口启动独立 pytest 进程，便于外部 RSS 采样。内存采样时的计时不回填时间表。

### 7. 汇总

```bash
uv run --frozen --extra r python benchmarks/run.py summarize
```

生成六张 CSV 和 `benchmarks/results/current/results.md`。各用例原始 JSON 分组保存；时间统一为秒，内存为 MiB。两类 core 表的 Max/Ultra 均标为 `pipeline_substitution`，Numba 直接引用本轮 pipeline。

### 续跑 / 单独测方法

pytest 命令添加 `--bench-resume` 跳过已有完整结果；可添加 `--bench-case snip` 或 `--bench-dataset min` 缩小范围。R/内存命令使用 `--resume`。全部补齐后再汇总。

换一轮实验时，pytest 使用 `--bench-run-dir benchmarks/results/新实验名`，其余命令使用 `--run-dir benchmarks/results/新实验名`，从 init 开始；不要混用不同设备、源码或配置。

NumPy ref 的小数组正确性检查入口（不加载真实数据、不测性能）：

```bash
uv run --frozen --extra r pytest benchmarks/test_peak_align_numpy.py -q
```

## result

六组已全部完成，共 270 份用例 JSON：Python core 36、Numba pipeline 52、Numba core 26、Cardinal pipeline 52、Numba memory 52、Cardinal memory 52。日志记录最后一步于 2026-10-16 10:10:29（Asia/Shanghai）结束。Cardinal Max 触及 16 GiB 向量堆上限后，剩余 R 作业在 32 GiB 上限下续跑完成；已完成用例未重测。

完整均值、标准差、SI S6–S11 表、时间/RSS 比值、波动及来源限制见 [RESULTS.md](RESULTS.md)。六张原始数据 CSV 和同内容的 `results.md` 保存在结果目录中。

论文绘图脚本与使用说明见 [plot_for_paper/README.md](../plot_for_paper/README.md)，复现原分支 `plot_paper.py` 的 a–c 样式，直接从本轮 JSON 取数：

```bash
uv run --frozen --extra r python plot_for_paper/benchmark_results.py
uv run --frozen --extra r python plot_for_paper/plot_paper.py
```

生成带文字/无文字的 SVG、PDF、600 dpi PNG 及逐柱来源 CSV；不运行 benchmark，也不混入旧分支未重测的 pyM2aia 或线程扩展结果。

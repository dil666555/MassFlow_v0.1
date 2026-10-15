# 同设备重新测试

原分支 `test/time_and_memory_of_three_version` 不变。新分支只保存本轮脚本，旧结果不参与回填。

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

MassFlow 批大小 256、读取线程 8、Numba 工作线程 4；不扫描线程数。Cardinal 不设置 BPPARAM、不注册并行后端、不强制块大小，保留原脚本默认配置，实际后端写入环境记录。

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

尚未运行本轮基准测试。没有旧结果或预估数据。

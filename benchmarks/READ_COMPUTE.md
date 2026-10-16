# Max/Ultra 读＋算；Ultra SNIP pipeline 复测

Min/Mid 保留 `results/current/` 中已完成的缓存 core，不重测。只重测 Max/Ultra：Numba 13 方法 × 2、Python 9 方法 × 2，共 44 个读＋算用例；另测 Ultra SNIP 的 Python/Numba/Cardinal pipeline 三项，共 **47 个用例**。

## 测量范围

- Min/Mid：原缓存 core；数据预加载在计时外，无结果写出。
- Max/Ultra：输入初始化、头信息加载在 fixture 中；计时内逐批读取、计算、释放批次，不创建输出 manager，不写处理结果，不全量缓存强度，不使用 pipeline 替代值。
- Numba 读＋算：顺序遍历 flat batches，内核 4 个计算线程；需要 m/z 的 Reference、挑峰、对齐才请求 flat m/z。Python 按原 Spectrum/batch API 读取并逐批释放。两者是各自原生读取接口，不是共用一个 I/O 壳的内核对照。
- 对齐：Python/Numba 各两次流式读谱构建参考轴，再一次流式读谱执行对齐；Numba 保留原计算与合并算法，只从头信息获取日志所需光谱数，避免为计数额外读取整份数据。挑峰输入在计时外准备。
- Ultra SNIP pipeline：Numba 原 `Preprocessor`；Python 原 `dm_process`；Cardinal 原 `process(reduceBaseline(...))`，不增加导出。这三个用例与读＋算结果分组保存。

新读＋算使用顺序批次循环；原 Numba pipeline 的读、算、写可以重叠。因此无写出的新读＋算时间不保证小于旧 pipeline 的墙钟时间，两者不能相减当成精确的写出耗时。对齐的参考输入缓存范围也有上述差别。

每个用例独立进程，预热 1 次、正式 2 次。组间静置 5 分钟。批大小 256、读线程 8、Numba 4；R 上限 32 GiB。保留操作系统文件缓存，不清缓存、不强制 fsync。

## SNIP 参数核对

| 项目 | Python | Numba | Cardinal/matter |
| --- | --- | --- | --- |
| 最大 clipping 偏移 | `m=5` | `m=5` | `width=5` |
| 窗口次序 | 5→4→3→2→1 | 5→4→3→2→1 | 5→4→3→2→1 |
| 递减规则 | `decreasing=True` | `decreasing=True` | `decreasing=TRUE` |
| 基线缩放 | `baseline_scale=1.0` | `baseline_scale=1.0` | `x - baseline`，系数为 1 |
| 负值 | 截至 0 | 截至 0 | `pmax(0, ...)` |
| 额外平滑/对数变换 | 无 | 无 | 无 |

已读取与本机版本一致的 [matter 2.12.0 官方源码](https://github.com/kuwisdelu/matter/blob/RELEASE_3_22/src/signal.h#L1155)，确认 `width=5` 直接传入 `m`，并非全窗口宽度再除以 2。

[C 接口入口](https://github.com/kuwisdelu/matter/blob/RELEASE_3_22/src/matterExports.cpp#L1036) 也直接使用 `Rf_asInteger(m)`，没有额外窗口换算。

启动时 `verify_snip.py` 读取 Ultra 首条、中间、末条真实光谱，在计时外核对三方校正后强度；结果保存为 `snip-parameter-check.json`。这不是全数据逐点验证。正式结果仍保留每轮耗时、实际参数及 Cardinal 有效后端。

## 一次运行

这轮使用新目录 `benchmarks/results/read-compute`，不会覆盖旧 `results/current`。修改了 benchmark 源码后，旧轮次只读归档；不要用旧七步脚本对其续跑。

对齐复用上一轮已生成的 Quantile 挑峰输入，先验证原始数据身份、挑峰参数及文件大小/时间，再复制到新目录并记录来源实验编号；不复用任何 Max/Ultra 计时结果。

```bash
mkdir -p benchmarks/results
nohup caffeinate -i bash benchmarks/run_read_compute.sh \
  > benchmarks/results/read-compute.log 2>&1 < /dev/null &
```

顺序：Numba Ultra SNIP pipeline → Python Ultra SNIP pipeline → Cardinal Ultra SNIP pipeline → Numba Max/Ultra 读＋算 → Python Max/Ultra 读＋算。已完成的新轮用例会跳过。接电、开盖，使用同一电源模式。

```bash
tail -f benchmarks/results/read-compute.log
```

全部完成后自动生成 `benchmarks/results/read-compute/results.md`，包含保留的 Min/Mid、Max/Ultra 新读＋算数值，以及 Ultra SNIP pipeline 新旧对比。原图暂保留旧轮来源，不将两种范围混用。

## 单独续跑 / pytest 入口

只补 Ultra SNIP pipeline 时：

```bash
export R_MAX_VSIZE=32Gb
uv run --frozen --extra r python benchmarks/run.py numba-pipeline --run-dir benchmarks/results/read-compute --dataset ultra --case snip --resume
uv run --frozen --extra r python benchmarks/run.py python-pipeline --run-dir benchmarks/results/read-compute --dataset ultra --case snip --resume
uv run --frozen --extra r python benchmarks/run.py cardinal-pipeline --run-dir benchmarks/results/read-compute --dataset ultra --case snip --resume
```

手动分组执行读＋算时，先按一键脚本完成 init、参数核对及 prepare，再使用 pytest：

```bash
uv run --frozen --extra r pytest benchmarks/python_bench.py \
  --bench-group numba-core --bench-run-dir benchmarks/results/read-compute \
  --bench-dataset max --bench-dataset ultra --bench-resume --benchmark-only \
  --benchmark-json=benchmarks/results/read-compute/numba-read-compute-pytest.json -q

uv run --frozen --extra r pytest benchmarks/python_bench.py \
  --bench-group python-core --bench-run-dir benchmarks/results/read-compute \
  --bench-dataset max --bench-dataset ultra --bench-resume --benchmark-only \
  --benchmark-json=benchmarks/results/read-compute/python-read-compute-pytest.json -q
```

勿与一键脚本同时运行。每组 JSON 的 `scope=read_compute`；结果没有 pipeline 替代标记。`cache_core` 仅用于 Min/Mid。

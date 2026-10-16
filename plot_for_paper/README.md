# 本轮 benchmark 绘图

## 图形约定

本图展示同一台设备上不同实现的运行时间与驻留内存差异，优势随算子及数据规模变化。所有数值直接读取本轮 JSON 的 `stats.mean`，不混入原分支的汇总数据。

采用 Python/matplotlib，布局为 quantitative grid。复现原 `plot_paper.py` 的 a–c 三行：Arial 字体、四级蓝色、阶段分组、对数纵轴、1× 虚线、低于 1× 的红色柱边、每个阶段最高柱标注，以及 7.2 × 6.25 inch 画布。字体、字号、线宽和布局间距沿用原脚本。

- a：Python / Numba 耗时比。Min/Mid 为缓存 core，Max/Ultra 为各自 pipeline 替代；Min/Mid SNIP 为明确复用的旧缓存入口。Origin 只作为 Quantile/Diff/SD 的共享方法参考；Reference、MAD 没有对应 Python 结果，保留原图空位。
- b：Cardinal / Numba pipeline 耗时比。
- c：Cardinal / Numba pipeline 采样 RSS 峰值比。

均以两次正式测量的均值相除，无误差棒、不进行显著性检验。原图的 pyM2aia 和线程扩展部分不属于本轮测量，因此不绘制。计时边界、默认参数、延迟物化、交换空间及复用数据的限制见结果总结，不能将所有柱子解释为相同算法的纯计算加速。

导出 SVG、PDF 和 600 dpi PNG，并生成无文字版本；SVG/PDF 保持可编辑文字。另存逐柱数据 CSV、来源 JSON 路径、原始文件 SHA-256、图注及检查记录。

## 命令

在仓库根目录执行，仅整理已有结果和绘图，不运行 benchmark：

```bash
uv run --frozen --extra r python plot_for_paper/benchmark_results.py
uv run --frozen --extra r python plot_for_paper/plot_paper.py
```

总结保存为 `benchmarks/RESULTS.md`，结果目录另存同内容的 `results.md`；六张原始数据 CSV 保存到 `benchmarks/results/current/`。图和逐柱数据保存到 `plot_for_paper/figures/`。

换结果目录时，两条命令都使用 `--run-dir /path/to/results`。绘图输出目录可用 `--output-dir` 指定。

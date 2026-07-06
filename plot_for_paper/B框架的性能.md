### 原生支持的预处理算法及其并行实现

#### 正文草稿

ProjectNAME 原生支持 MSI 预处理中最常用的谱图级操作，包括 SNIP 和局部最小值基线校正，moving-average、Gaussian 与 Savitzky-Golay 降噪，TIC、RMS 与参考离子归一化，基于 SD、MAD、quantile 和差分噪声估计的峰提取，以及参考 m/z 轴构建和峰对齐；在质心化数据后，还可执行同位素峰过滤和基于出现频率或聚合强度的峰过滤。这些操作并不是以逐谱图 Python 循环实现，而是先将批量谱图转换为连续的 m/z 与 intensity 缓冲区，并用 lengths 数组记录每条谱图的边界。对于原生操作，规划器先按预处理依赖关系重排任务，再由读取、计算和写出三阶段异步流水线执行：读取阶段以批次从 imzML/.ibd 或 Zarr 后端抽取谱图，计算阶段调用经 Numba JIT 编译的并行核函数在谱图维度或 m/z 匹配任务上分配 worker，写出阶段则将结果流式落盘。对于 ion-image binary、HDF5 和 Zarr 等输出后端，框架进一步采用块式磁盘交换策略，将 pixel-major 批次转置为临时 ion-major 分块，并在 finalize 阶段按 ion block 合并到最终数据集；该设计减少了完整中间矩阵的长期驻留，使多核计算、I/O 重叠和受控内存占用同时服务于大规模 MSI 数据处理。

### B. ProjectNAME 框架的性能

#### 正文草稿

为评估 ProjectNAME 是否能够作为智能体驱动 MSI 分析的高通量计算后端，我们从绝对资源开销、核心算子加速、端到端框架比较、独立 Python 工具比较和多线程扩展性五个层面进行测试。绝对性能测试覆盖四个不同规模和存储形式的 imzML 数据集，以及基线校正、归一化、峰对齐、降噪和峰提取等常用预处理任务；相对性能测试进一步将 ProjectNAME 与传统 Python/NumPy 实现、R/Bioconductor Cardinal、pyM2aia 和单线程执行路径进行比较。结果表明，ProjectNAME 的性能优势不仅来自单个算子的数值优化，也体现在完整流水线中的运行时间、峰值内存和多核 CPU 利用效率。

ProjectNAME 在不同数据规模下保持了可控的绝对运行时间和内存占用（Table 2）。在 52 个“方法-数据集”组合中，单个预处理任务的运行时间为 0.92-48.13 s，峰值内存为 42-1023 MiB。对于 Min 数据集，所有单阶段预处理任务均可在 2 s 内完成，峰值内存通常低于 110 MiB。随着数据规模增大，运行时间和内存占用随算法访问模式而变化：Ultra 数据集上的峰对齐任务耗时 6.57 s，降噪和归一化任务耗时 23.21-24.78 s，而计算量较高的 MAD 峰提取耗时 48.13 s。内存方面，多数任务的峰值内存低于约 0.7 GiB，仅 Max 数据集上的部分基线校正任务接近 1.0 GiB。上述结果说明，ProjectNAME 可以在普通 16 GB 内存工作站上完成大规模 MSI 数据的典型预处理任务，并表明其批量执行和交换式中间存储策略能够将峰值资源需求维持在可控范围内。

ProjectNAME 的核心数值路径在纯计算层面稳定快于传统 Python/NumPy 实现（Figure 2a）。该比较排除了完整文件读写和外部框架调用的影响，集中评估单个预处理算子的计算效率。在 44 个“方法-数据集”组合中，ProjectNAME 均快于对应的 Python/NumPy 基线，中位加速比为 8.35 倍，平均加速比为 13.24 倍，最高达到 72.72 倍。加速幅度最大的结果出现在 Min 数据集上的 Savitzky-Golay 降噪任务；加速幅度最低的结果出现在 Ultra 数据集上的 Diff 峰提取任务，但仍达到 1.36 倍。该结果表明，ProjectNAME 的性能收益来自底层数组组织、JIT 编译和谱图级批量计算路径的共同优化，而不是单纯依赖外层流程封装。需要说明的是，峰提取部分的传统基线采用同一种 `scipy.signal.find_peaks` 实现，因此 Quantile、Diff 和 SD 三种 ProjectNAME 峰提取配置均与该传统基线进行比较。

在完整 MSI 预处理流水线中，ProjectNAME 相比 Cardinal 同时降低了运行时间和峰值内存（Figure 2b,c）。运行时间方面，ProjectNAME 在全部 52 个匹配任务中均快于 Cardinal，Cardinal/ProjectNAME 运行时间比的中位数为 3.06，平均值为 7.62，最高达到 40.60。最明显的运行时间优势出现在 Max 数据集上的归一化和降噪任务，其中 RMS 归一化、TIC 归一化和高斯降噪分别达到 40.60、36.51 和 36.46 倍加速。对于 Min 数据集上的简单归一化任务，加速比相对有限，最低为 1.04 倍，说明当核心计算本身已足够短时，数据访问和框架固定开销会占据更高比例。峰值内存方面，ProjectNAME 在全部 52 个匹配任务中也均低于 Cardinal，Cardinal/ProjectNAME 峰值内存比的中位数为 9.30，平均值为 14.79，最高达到 44.64。运行时间和内存结果的一致性说明，ProjectNAME 并非以更高内存消耗换取速度，而是在完整预处理流程中同时提高了吞吐并降低了峰值资源需求。

ProjectNAME 在与 pyM2aia 的独立 Python 工具比较中也保持了更低的运行时间（Figure 2d）。该测试聚焦于 pyM2aia 与 ProjectNAME 均支持的 in-memory 预处理操作，包括 TIC/RMS 归一化以及 Gaussian/Savitzky-Golay 降噪。在 16 个“方法-数据集”组合中，pyM2aia/ProjectNAME 运行时间比均高于 1，中位数为 2.88，平均值为 2.72，最高达到 4.15。与 Cardinal 比较相比，pyM2aia 测试覆盖的算法范围较窄，且不包含完整流水线峰值内存测试；因此，该结果更适合作为独立 Python 工具层面的补充证据，而不是替代 Cardinal 端到端 benchmark。即便在这一受限设置下，ProjectNAME 仍在共有预处理任务上表现出一致的运行时间优势。

多线程测试进一步说明 ProjectNAME 的主要预处理核函数能够利用现代多核 CPU 缩短实际执行时间（Figure 2e）。当线程数由 1 增加至 32 时，五个代表性任务的 wall-clock time 均下降。32 线程下，峰提取、归一化、降噪、基线校正和峰对齐相对于单线程分别获得 6.61、6.77、14.86、5.56 和 6.91 倍加速。其中，降噪任务表现出最高的并行扩展性，运行时间由 14.78 s 降至 0.99 s；基线校正任务虽然扩展性较低，但具有最大的绝对时间下降，由 207.51 s 降至 37.30 s。所有任务的扩展性均低于理想线性加速，说明内存带宽、任务粒度、线程调度和部分算法的数据依赖仍会限制多核利用效率。尽管如此，这些结果证明 ProjectNAME 的性能收益可以通过多线程执行进一步放大。

总体而言，性能评估从互补角度支持 ProjectNAME 作为高通量 MSI 预处理后端的实用性。绝对性能测试显示其可在普通工作站资源范围内完成大规模数据处理；内部计算 benchmark 证明其核心数值路径持续优于传统 Python/NumPy 实现；与 Cardinal 的完整流水线比较显示其在运行时间和峰值内存上均具有优势；pyM2aia 比较提供了独立 Python 工具层面的补充证据；多线程测试则表明该框架能够进一步利用多核 CPU 资源。结合批量谱图表示、JIT 并行核函数和交换式中间存储，ProjectNAME 的性能优势更接近一套面向 MSI 数据结构定制的执行后端，而非单个函数的局部加速。上述结论的适用边界限定于本文测试的数据集、预处理方法、软件版本和硬件环境；在不同存储布局、外部 I/O 条件或算法参数下，具体加速幅度可能发生变化。在当前评估范围内，ProjectNAME 为智能体驱动的 MSI 自动化分析提供了可复现、资源可控且可扩展的计算基础。

#### 图注建议

Figure 2. ProjectNAME 的计算性能与资源占用评估。（a）传统 Python/NumPy 实现与 ProjectNAME 核心计算路径的运行时间比；比值大于 1 表示 ProjectNAME 更快。（b）Cardinal 与 ProjectNAME 在完整 MSI 预处理流水线中的运行时间比。（c）Cardinal 与 ProjectNAME 在完整 MSI 预处理流水线中的峰值内存比。（d）pyM2aia 与 ProjectNAME 在共有 in-memory 预处理任务中的运行时间比；未覆盖的方法在对应面板中留空。（e）ProjectNAME 代表性预处理核函数在 1-32 线程下的执行时间和相对于单线程的并行加速比。柱状图颜色表示数据集；虚线表示 1 倍参考线或理想线性加速。

#### 写作边界与证据对应

- 绝对性能段对应 Word 原稿 Table 2，保留 52 个“方法-数据集”组合的运行时间和峰值内存范围。
- Figure 2a 对应 `tests/python_outcome.py` 和 `plot_for_paper/plot_paper.py` 的 internal benchmark，共 44 个组合。
- Figure 2b,c 对应 `tests/pipeline_outcome.py` 的 Cardinal runtime 和 peak-memory benchmark，各 52 个组合。
- Figure 2d 对应 `tests/compare_m2aia_outcome.py`，只支持 pyM2aia 与 ProjectNAME 共有的归一化和降噪 in-memory runtime 比较。
- Figure 2e 对应 `tests/parallel_outcome.py`，用于说明代表性核函数的多线程扩展性，不等同于完整流水线端到端并行加速。
- 算法支持范围和并行/交换式实现描述对应当前 MassFlow 源码中的 `preprocess/api.py`、`preprocess/flat_pre_fun.py`、`preprocess/pipeline/flat_executor.py`、`preprocess/numba/*`、`tools/ion_major_temp_store.py`、`data_manager/ion_image_data_manager_binary.py` 和 `msi_zarr/writer.py`。
- 该草稿默认将此前分散的 Python、Cardinal、pyM2aia 和 parallel 结果合并为一张综合性能图。若正文中沿用旧图号，需要同步调整后续图号、交叉引用和图注编号。

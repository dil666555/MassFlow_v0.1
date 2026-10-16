"""Summarize the completed JSON campaigns and supply paper-figure source data."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "benchmarks" / "results" / "current"
DATASETS = ("min", "mid", "max", "ultra")
GROUPS = ("python-core", "numba-pipeline", "numba-core", "cardinal-pipeline",
          "numba-memory", "cardinal-memory")
CASE_LAYOUT = (
    ("Baseline Correction", "locmin", "locmin", "LocMin"),
    ("Baseline Correction", "snip", "snip", "SNIP"),
    ("Normalization", "TIC", "tic", "TIC"),
    ("Normalization", "RMS", "rms", "RMS"),
    ("Normalization", "Reference", "reference", "Reference"),
    ("Peak Alignment", "Default", "align", "Default"),
    ("Noise Reduction", "MA", "ma", "MA"),
    ("Noise Reduction", "Gaussian", "gaussian", "Gaussian"),
    ("Noise Reduction", "Savitzky–Golay", "savgol", "Savitzky–Golay"),
    ("Peak Picking", "Quantile", "quantile", "Quantile"),
    ("Peak Picking", "Diff", "diff", "Diff"),
    ("Peak Picking", "SD", "sd", "SD"),
    ("Peak Picking", "MAD", "mad", "MAD"),
)
DISPLAY = {case: label for _, _, case, label in CASE_LAYOUT} | {"origin": "Origin"}


class Results:
    def __init__(self, run):
        self.run = Path(run).resolve()
        self.manifest = json.loads((self.run / "manifest.json").read_text())
        self.cases = self.manifest["config"]["cases"]
        self.records = {}
        self.paths = {}
        for group in GROUPS:
            backend = group.split("-", 1)[0]
            datasets = DATASETS[:2] if group == "numba-core" else DATASETS
            for ds in datasets:
                for case in self.cases:
                    if backend not in case:
                        continue
                    key = (group, ds, case["id"])
                    path = self.run / group / f'{ds}-{case["id"]}.json'
                    record = json.loads(path.read_text())
                    values = record["stats"]["data"]
                    if (record["campaign_id"] != self.manifest["id"]
                            or record["dataset"] != ds or record["case"] != case["id"]
                            or record["backend"] != backend
                            or record["mode"] != ("memory" if group.endswith("memory") else "time")
                            or record["stats"]["rounds"] != 2 or len(values) != 2
                            or not all(math.isfinite(v) and v > 0 for v in values)
                            or not math.isclose(statistics.mean(values), record["stats"]["mean"], rel_tol=1e-10)
                            or not math.isclose(statistics.stdev(values), record["stats"]["stddev"], rel_tol=1e-10, abs_tol=1e-10)):
                        raise ValueError(f"Invalid or inconsistent result: {path}")
                    self.records[key] = record
                    self.paths[key] = path

    def key(self, group, ds, case):
        if group == "numba-core" and ds in DATASETS[2:]:
            group = "numba-pipeline"
        return group, ds, case

    def record(self, group, ds, case):
        return self.records[self.key(group, ds, case)]

    def mean(self, group, ds, case):
        return self.record(group, ds, case)["stats"]["mean"]

    def scope(self, group, ds, case):
        if group.endswith("core") and ds in DATASETS[2:]:
            return "pipeline_substitution"
        return self.record(group, ds, case)["scope"]

    def panels(self):
        panels = {label: {stage: {} for stage, *_ in CASE_LAYOUT} for label in "abc"}
        sources = []
        for stage, method, case, _ in CASE_LAYOUT:
            for panel in "abc":
                python_case = "origin" if case in ("quantile", "diff", "sd") else case
                if panel == "a" and case in ("reference", "mad"):
                    continue
                numerator_group = {"a": "python-core", "b": "cardinal-pipeline", "c": "cardinal-memory"}[panel]
                denominator_group = {"a": "numba-core", "b": "numba-pipeline", "c": "numba-memory"}[panel]
                numerator_case = python_case if panel == "a" else case
                by_dataset = {}
                for ds in DATASETS:
                    numerator = self.record(numerator_group, ds, numerator_case)
                    denominator = self.record(denominator_group, ds, case)
                    top, bottom = numerator["stats"]["mean"], denominator["stats"]["mean"]
                    by_dataset[ds] = (top, bottom)
                    source = {"panel": panel, "stage": stage, "method": method, "dataset": ds,
                              "numerator_mean": top, "denominator_mean": bottom, "ratio": top / bottom,
                              "unit": "MiB" if panel == "c" else "s",
                              "numerator_scope": self.scope(numerator_group, ds, numerator_case),
                              "denominator_scope": self.scope(denominator_group, ds, case),
                              "reused_result": numerator.get("reused_result", False),
                              "comparison": "different_peak_picking_methods" if panel == "a" and case in ("quantile", "diff", "sd") else "native_implementations"}
                    for prefix, group, source_case in (("numerator", numerator_group, numerator_case),
                                                       ("denominator", denominator_group, case)):
                        path = self.paths[self.key(group, ds, source_case)]
                        source[f"{prefix}_json"] = str(path.relative_to(self.run))
                        source[f"{prefix}_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                    sources.append(source)
                panels[panel][stage][method] = by_dataset
        return panels, sources


def write_csv(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(results, output):
    m = results.manifest
    env = m["environment"]
    lines = ["# 同设备 benchmark 结果总结", "",
             f'实验编号：`{m["id"]}`。本次所有预期用例均有完整 JSON。', "",
             "## 完整性与环境", "",
             "六组共 **270 份用例 JSON**，均为预热 1 次、正式 2 次；其中两项 Python SNIP 为原分支 M5 实测值复用。全部记录的实验编号、数据集、方法、模式、次数、均值及样本标准差已与逐轮数据核对一致。", "",
             "| 组别 | 完整结果 |", "| --- | ---: |"]
    for group in GROUPS:
        count = sum(key[0] == group for key in results.records)
        lines.append(f"| {group} | {count} |")
    lines += ["", "| 环境 | 记录 |", "| --- | --- |",
              f'| 设备 | Apple M5 MacBook Air；{env["logical_cpus"]} 逻辑 CPU；{env["ram_bytes"] / 2**30:g} GiB 内存 |',
              f'| 系统 | {env["system"]} |',
              f'| Python | {env["python"].split()[0]} |',
              f'| Python 库 | {", ".join(f"{k} {v}" for k, v in env["packages"].items())} |',
              f'| R | {env["R"]["R"]} |',
              f'| R 库 | {", ".join(f"{k} {v}" for k, v in env["R"]["packages"].items())} |',
              "| 线程配置 | Numba 计算 4；MassFlow 读取 8；BLAS 1 |",
              "| Cardinal 实际处理 | BPPARAM=NULL，经 matter 串行循环；JSON 中 MulticoreParam/8 为注册后端 |",
              "| 内存上限变更 | Cardinal 时间 Min/Mid 在原 16 GiB 向量堆上限下完成；失败后其余 R 作业改为 32 GiB；没有更改算子参数或重新测量已完成值 |",
              "| 运行安排 | 每一步开始前静置 5 分钟；每个用例内连续预热与正式测量；无温度或 swap 历史记录 |", "",
              "## 主要观察", "",
              "下表均比较 Cardinal / Numba pipeline 的均值，不使用 Numba core。几何均值对 13 个算子等权，仅作描述，不代表整个预处理工作流的总耗时比；不做显著性检验。", "",
              "| 数据集 | 时间比值范围 | 时间比值几何均值 | MassFlow 均值更小的算子数 | RSS 比值范围 | RSS 比值几何均值 |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    panels, _ = results.panels()
    for ds in DATASETS:
        time = [results.mean("cardinal-pipeline", ds, c) / results.mean("numba-pipeline", ds, c)
                for _, _, c, _ in CASE_LAYOUT]
        memory = [results.mean("cardinal-memory", ds, c) / results.mean("numba-memory", ds, c)
                  for _, _, c, _ in CASE_LAYOUT]
        lines.append(f'| {ds.title()} | {min(time):.3f}–{max(time):.3f}× | {statistics.geometric_mean(time):.3f}× | {sum(v > 1 for v in time)}/13 | {min(memory):.3f}–{max(memory):.3f}× | {statistics.geometric_mean(memory):.3f}× |')
    lines += ["", "MassFlow 的采样 RSS 峰值均值在全部 52 个对应算子/数据集组合中均低于 Cardinal。时间上 Min 有若干算子更慢，Mid/Max 的全部算子均值更快；Ultra SNIP 与 TIC 的比值低于 1。接近 1× 的差异不能据两次测量认定稳定优势。", "",
              "## SI 原始数值表", "",
              "表中均为 **mean ± sample SD**。时间为秒（s），内存为两轮采样 RSS 峰值（MiB）。`*` 表示 Max/Ultra 的 pipeline 替代值；`†` 表示复用的旧 M5 缓存入口。所有值保留原始 JSON 精度，表格仅四舍五入。", ""]
    for number, group, title in (
        (6, "numba-pipeline", "Numba-parallel pipeline 时间（s）"),
        (7, "numba-memory", "Numba-parallel pipeline 采样峰值 RSS（MiB）"),
        (8, "cardinal-pipeline", "Cardinal process 时间（s，不含结果导出）"),
        (9, "cardinal-memory", "Cardinal process 采样峰值 RSS（MiB）"),
        (10, "numba-core", "Numba core：Min/Mid 缓存，Max/Ultra pipeline 替代（s）"),
        (11, "python-core", "Python/NumPy core：Min/Mid 缓存，Max/Ultra pipeline 替代（s）"),
    ):
        lines += [f"### Table S{number}. {title}", "",
                  "| Stage | Method | Min | Mid | Max | Ultra |",
                  "| --- | --- | ---: | ---: | ---: | ---: |"]
        layout = [row for row in CASE_LAYOUT if row[2] not in ("quantile", "diff", "sd", "mad", "reference")] + [("Peak Picking", "Origin", "origin", "Origin")] if group == "python-core" else CASE_LAYOUT
        rows = []
        for stage, _, case, label in layout:
            cells = []
            for ds in DATASETS:
                record = results.record(group, ds, case)
                stats = record["stats"]
                scope = results.scope(group, ds, case)
                mark = "*" if scope == "pipeline_substitution" else "†" if record.get("reused_result") else ""
                cells.append(f'{stats["mean"]:.4f} ± {stats["stddev"]:.4f}{mark}')
                path = results.paths[results.key(group, ds, case)]
                rows.append({"dataset": ds, "case": case, "scope": scope,
                             "unit": "MiB" if group.endswith("memory") else "s",
                             **{k: stats[k] for k in ("mean", "stddev", "min", "median", "max", "rounds")},
                             "reused_result": record.get("reused_result", False),
                             "source": str(path.relative_to(results.run))})
            lines.append("| " + " | ".join([stage, label, *cells]) + " |")
        write_csv(results.run / f"{group}.csv", rows)
        lines.append("")
    for panel, title in (("a", "Python / Numba 时间比"), ("b", "Cardinal / Numba pipeline 时间比"),
                         ("c", "Cardinal / Numba pipeline RSS 比")):
        lines += [f"## {title}", "", "比值 > 1 表示 Numba/MassFlow 的对应均值更小；比值 < 1 表示更大。", "",
                  "| Stage | Method | Min | Mid | Max | Ultra |",
                  "| --- | --- | ---: | ---: | ---: | ---: |"]
        for stage, method, _, label in CASE_LAYOUT:
            if method not in panels[panel][stage]:
                continue
            values = [f'{panels[panel][stage][method][ds][0] / panels[panel][stage][method][ds][1]:.3f}×' for ds in DATASETS]
            lines.append("| " + " | ".join([stage, label, *values]) + " |")
        if panel == "a":
            lines += ["", "Quantile/Diff/SD 共用 Python Origin 作为方法参考，是不同挑峰算法的对比；不补造 Python Reference 或 MAD。Max/Ultra 两侧均为各自 pipeline，不能描述为纯计算加速比。"]
        lines.append("")
    lines += ["## 波动与采样检查", "",
              "以下列出时间结果中样本 SD / mean ≥ 20% 的用例。该阈值仅作描述性筛查，保留两次测量，不剔除或挑选较快轮次；不能据此断言原因是温度或交换空间。", "",
              "| 组别 | 数据集 | 方法 | 第一次（s） | 第二次（s） | CV |",
              "| --- | --- | --- | ---: | ---: | ---: |"]
    for (group, ds, case), record in sorted(results.records.items()):
        stats = record["stats"]
        cv = stats["stddev"] / stats["mean"]
        if record["mode"] == "time" and cv >= .2:
            lines.append(f'| {group} | {ds} | {DISPLAY[case]} | {stats["data"][0]:.6f} | {stats["data"][1]:.6f} | {cv:.1%} |')
    lines += ["", "| RSS 采样组 | 实际最大采样间隔 | 对应用例 |",
              "| --- | ---: | --- |"]
    for group in ("numba-memory", "cardinal-memory"):
        gaps = [(sample["max_sample_gap_seconds"], ds, case)
                for (g, ds, case), record in results.records.items() if g == group
                for worker in record["workers"] for sample in worker["memory"]]
        gap, ds, case = max(gaps)
        lines.append(f"| {group} | {gap * 1000:.2f} ms | {ds}/{DISPLAY[case]} |")
    lines += ["", "名义采样间隔约 5 ms，实际调度可能更慢；报告的是采样到的进程 RSS 峰值，不保证捕获瞬时绝对峰值，也不包含已换出的页面。RSS 包含解释器、库及驻留缓存，不等于纯算子分配量或 R 向量堆大小。", "",
              "## 解释边界与来源", "",
              "- MassFlow pipeline 计批量读谱、计算、写出与关闭输出；Cardinal 在 readImzML/准备之后计 process，不导出。这是各自流程的实测比值，工作量不完全相同。",
              "- Cardinal 的 peak alignment 返回延迟对象，未强制物化全部对齐强度；与 MassFlow 写出结果的范围差异尤其需要在图注说明。",
              "- Gaussian 默认 sd：Python/Numba 1.25，Cardinal 1.0；TIC/RMS scale 和 Reference 容差规则亦未完全统一。",
              "- Python Min/Mid SNIP 复用原分支同设备记录，标记为 cache_core_legacy；旧入口含线程化缓存遍历及运行时设置开销，新入口直接遍历缓存。原报告未记录完整库版本、输入指纹和温度状态。",
              "- 32 GiB 是 R 向量堆的软件上限，本机物理内存为 16 GiB。大数据耗时可能受内存压力影响；缺少同步 swap/温度记录，不能给出确定归因。",
              "- 每个方法两次正式测量；表格和图使用完整均值，没有做离群值删除、显著性检验或数据替换。",
              "", "原始 JSON、manifest.json、cardinal-runtime-32gb.json 和每个用例 worker.log 位于 benchmarks/results/current；六张 CSV 与逐柱 source_data.csv 可回溯原数值。", ""]
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines))
    if output.resolve() != results.run / "results.md":
        (results.run / "results.md").write_text("\n".join(lines))
    print(f"Validated {len(results.records)} result JSON files; wrote {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "RESULTS.md")
    args = parser.parse_args()
    summarize(Results(args.run_dir), args.output)


if __name__ == "__main__":
    main()

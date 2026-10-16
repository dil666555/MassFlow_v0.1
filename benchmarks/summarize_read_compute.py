"""Summarize the Max/Ultra read-compute campaign and Ultra SNIP pipeline retest."""
import argparse
from pathlib import Path
import statistics

from run import HERE, read_json


def checked(path, campaign, scope):
    result = read_json(path)
    stats = result["stats"]
    if (result["campaign_id"] != campaign or result["scope"] != scope
            or stats["rounds"] != 2 or len(stats["data"]) != 2
            or stats["mean"] != statistics.mean(stats["data"])):
        raise ValueError(f"Incomplete or inconsistent result: {path}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=HERE / "results" / "read-compute")
    parser.add_argument("--base-run", type=Path, default=HERE / "results" / "current")
    args = parser.parse_args()
    run, base = args.run_dir.resolve(), args.base_run.resolve()
    manifest, old = read_json(run / "manifest.json"), read_json(base / "manifest.json")
    for key in ("host", "system", "machine", "logical_cpus", "ram_bytes", "python", "python_executable", "packages", "thread_env"):
        if manifest["environment"][key] != old["environment"][key]:
            raise ValueError(f"Base and new campaign environments differ: {key}")
    for ds, info in old["inputs"].items():
        if any(manifest["inputs"][ds][key] != value for key, value in info.items()):
            raise ValueError(f"Base and new inputs differ: {ds}")
    audit = read_json(run / "snip-parameter-check.json")
    if audit["campaign_id"] != manifest["id"]:
        raise ValueError("SNIP parameter-check campaign mismatch")
    lines = ["# Max/Ultra 读＋算补测", "",
             f'新实验：`{manifest["id"]}`；保留的 Min/Mid 来源：`{old["id"]}`。', "",
             "Min/Mid 保留旧缓存 core；Max/Ultra 逐批读谱、计算、释放批次，不写出处理结果、不全量预加载、不再用 pipeline 替代。输入 manager/头信息初始化在计时外，正式计时保留操作系统文件缓存。", "",
             "每个用例独立进程，预热 1 次、正式 2 次；Numba 4 计算线程、读取 8 线程。对齐参考轴读算在计时内，Python/Numba 均流式执行两轮参考构建读谱及一轮对齐读谱；挑峰输入准备在计时外。", "",
             "## Core 时间（mean ± sample SD，s）", "",
             "| Backend | Method | Min（缓存） | Mid（缓存） | Max（读＋算） | Ultra（读＋算） |",
             "| --- | --- | ---: | ---: | ---: | ---: |"]
    for backend in ("numba", "python"):
        for case in manifest["config"]["cases"]:
            if backend not in case:
                continue
            cells = []
            for ds in ("min", "mid", "max", "ultra"):
                path = (base if ds in ("min", "mid") else run) / f"{backend}-core" / f'{ds}-{case["id"]}.json'
                if ds in ("min", "mid"):
                    record = read_json(path)
                    if record["campaign_id"] != old["id"] or record["scope"] not in ("cache_core", "cache_core_legacy"):
                        raise ValueError(f"Wrong retained cache result: {path}")
                else:
                    record = checked(path, manifest["id"], "read_compute")
                stats = record["stats"]
                mark = "†" if record.get("reused_result") else ""
                cells.append(f'{stats["mean"]:.6f} ± {stats["stddev"]:.6f}{mark}')
            lines.append("| " + " | ".join([backend, case["id"], *cells]) + " |")
    lines += ["", "† Python Min/Mid SNIP 沿用先前明确复用的 M5 记录；保留原来源与入口开销说明。Min/Mid 和 Max/Ultra 的计时范围不同，不能把四列统称纯计算时间。", "",
              "## Ultra SNIP：三方完整 pipeline 复测", "",
              "Python/Numba 包含逐批读、算、写和关闭输出；Cardinal 按原 process 调用、不导出。三者 m/width=5、decreasing=True、baseline_scale=1、负值截零；Cardinal SNIP 不接受 smooth 参数，也未额外添加平滑或对数变换。", "",
              "| Backend | 第一次（s） | 第二次（s） | Mean（s） | SD（s） | 旧 Mean（s） |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    pipeline = {}
    for backend in ("numba", "python", "cardinal"):
        group = f"{backend}-pipeline"
        record = checked(run / group / "ultra-snip.json", manifest["id"],
                         "cardinal_process" if backend == "cardinal" else "pipeline")
        previous_group = "python-core" if backend == "python" else group
        before = read_json(base / previous_group / "ultra-snip.json")["stats"]["mean"]
        stats = record["stats"]
        pipeline[backend] = stats["mean"]
        lines.append(f'| {backend} | {stats["data"][0]:.6f} | {stats["data"][1]:.6f} | {stats["mean"]:.6f} | {stats["stddev"]:.6f} | {before:.6f} |')
    lines += ["", f'新 pipeline 比值 Python/Numba = **{pipeline["python"] / pipeline["numba"]:.3f}×**；Cardinal/Numba = **{pipeline["cardinal"] / pipeline["numba"]:.3f}×**。均为两个均值相除，没有剔除任意一轮。', "",
              "## Ultra SNIP：读＋算与完整 pipeline", "",
              "| Backend | 读＋算 mean（s） | 完整 pipeline mean（s） |",
              "| --- | ---: | ---: |"]
    for backend in ("numba", "python"):
        core = checked(run / f"{backend}-core" / "ultra-snip.json", manifest["id"], "read_compute")
        lines.append(f'| {backend} | {core["stats"]["mean"]:.6f} | {pipeline[backend]:.6f} |')
    lines += ["", "两个均值来自独立测试，不能直接相减当成精确写出耗时；Python 与 Numba 的读谱路径不同，Numba 读＋算使用顺序批次循环，完整 pipeline 使用原三阶段异步实现。", "",
              "## 参数核对", "",
              "核对结果见 snip-parameter-check.json：三条真实 Ultra 光谱在计时外分别通过 Python、Numba 与 Cardinal 实际 SNIP 回调，比较校正后强度；Cardinal 输出转换成输入存储精度后核对。该检查不代表每条光谱的全量数值验证。", "",
              "matter 2.12.0 官方源码确认 width 直接作为最大偏移 m，递减次序为 5、4、3、2、1：", "",
              "- [SNIP clipping loop](https://github.com/kuwisdelu/matter/blob/RELEASE_3_22/src/signal.h#L1155)",
              "- [Version 2.12.0](https://github.com/kuwisdelu/matter/blob/RELEASE_3_22/DESCRIPTION)", "",
              "Cardinal 有效处理 BPPARAM=NULL（串行）；注册后端信息单独记录。R 向量堆上限 32 GiB。其余算子的参数沿旧配置，不将 TIC/RMS scale、Gaussian sd 等既有差异描述成完全统一。原 current 目录 JSON 与旧图均未覆盖。", ""]
    output = run / "results.md"
    output.write_text("\n".join(lines))
    print("Wrote", output, flush=True)


if __name__ == "__main__":
    main()

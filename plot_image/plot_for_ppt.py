import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from tests.pipeline_outcome import TIME_DATA, MEMORY_DATA

# ── Style parameters ────────────────────────────────────────────────────────
CARDINAL_COLOR  = "#F7BDBC"
MASSFLOW_COLOR  = "#B6E3F8"
FONT_FAMILY     = ".AppleSystemUIFont"
FONT_SIZE       = 12
TITLE_SIZE      = 13
SUPTITLE_SIZE   = 15
LEGEND_SIZE     = 11
BAR_LABEL_SIZE  = 6
BAR_WIDTH       = 0.22
GROUP_STEP      = 0.58
FIGSIZE         = (3.0, 5)
DPI             = 300
OUTPUT_BASE     = "./images"
# 轴区域位置（两版共用，保证 no_label 是有标签版轴区域的等比放大）
AXES_RECT       = [0.22, 0.10, 0.72, 0.68]  # [left, bottom, width, height]

# ── PPT 版专用参数 ────────────────────────────────────────────────────────────
PPT_FONT_FAMILY     = ".AppleSystemUIFont"     # macOS 黑体；Windows 可改为 "SimHei"
PPT_FONT_SIZE       = 14
PPT_BAR_LABEL_SIZE  = 12           # 粉色柱标注字体
PPT_BAR_WIDTH       = 0.30         # PPT 版柱子宽度
PPT_GROUP_STEP      = 0.70         # PPT 版组间距
PPT_AXES_RECT       = [0.15, 0.12, 0.80, 0.75]
PPT_BASELINE_COLOR  = "#000305"    # 1x 灰色虚线颜色

# ── Scales ──────────────────────────────────────────────────────────────────
SCALES         = ['min', 'mid', 'max', 'ultra']
SCALE_DISPLAY  = ['Min', 'Mid', 'Max', 'Ultra']

# ── Stage definitions: stage_key → (output_subdir, methods, time_log, mem_log) ──
STAGES = {
    'Peak Alignment':      ('peak_alignment', ['PPM'],                              False, False),
    'Peak Picking':        ('peak_picking',   ['Quantile', 'Diff', 'SD', 'MAD'],   False, False),
    'Baseline Correction': ('baseline',       ['locmin', 'snip'],                   True,  False),
    'Noise Reduction':     ('noise_reduction',['MA', 'Gaussian', 'Savitzky–Golay'],True,  False),
    'Normalization':       ('normalization',  ['TIC', 'RMS', 'Reference'],          True,  False),
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def _ratio(c, m):
    return float('inf') if m == 0 else c / m


def _format_label(h):
    if abs(h - 1.0) < 1e-5:
        return '1.0x'
    label = f'{h:.2f}x' if 0.95 <= h < 1.05 else f'{h:.1f}x'
    return '1.0x' if label == '1.00x' else label


def _add_bar_labels(ax, bars, label_off, use_log_scale, fontsize=None):
    fs = fontsize if fontsize is not None else BAR_LABEL_SIZE
    for bar in bars:
        h = bar.get_height()
        y = h * label_off if use_log_scale else h + label_off
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                _format_label(h), ha='center', va='bottom', fontsize=fs)


# ── 论文版（有标签 / 无标签）────────────────────────────────────────────────
def plot_one(stage_key, method, data_label, data, output_dir, use_log_scale=False, no_label=False):
    """论文插图：有标签版 / 无标签版（轴区域严格对齐）。"""
    plt.rcParams['font.family'] = FONT_FAMILY
    plt.rcParams['font.size']   = FONT_SIZE

    method_data = data[stage_key][method]
    ratios = [_ratio(method_data[s][0], method_data[s][1]) for s in SCALES]
    global_max = max(ratios) if ratios else 2

    x = np.arange(len(SCALES)) * GROUP_STEP
    fig, ax = plt.subplots(figsize=FIGSIZE)

    if use_log_scale:
        ax.set_yscale('log')
        ax.set_ylim(0.5, global_max * 3.0)
        ax.yaxis.set_minor_locator(ticker.NullLocator())
    else:
        ax.set_ylim(0, global_max * 1.15)

    bars_m = ax.bar(x - BAR_WIDTH / 2, [1.0] * len(SCALES), BAR_WIDTH,
                    color=MASSFLOW_COLOR, label='MassFlow', edgecolor='white', linewidth=0.6)
    bars_c = ax.bar(x + BAR_WIDTH / 2, ratios, BAR_WIDTH,
                    color=CARDINAL_COLOR, label='Cardinal', edgecolor='white', linewidth=0.6)

    ax.set_xticks(x)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_position(AXES_RECT)

    if no_label:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    else:
        label_off = 1.08 if use_log_scale else global_max * 0.02
        _add_bar_labels(ax, bars_m, label_off, use_log_scale)
        _add_bar_labels(ax, bars_c, label_off, use_log_scale)
        ax.set_xticklabels(SCALE_DISPLAY)
        ax.set_title(method, fontweight='bold', fontsize=TITLE_SIZE)
        ax.set_ylabel(f'{data_label} — Relative Ratio')
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.88),
                   ncol=2, frameon=False, fontsize=LEGEND_SIZE)
        fig.suptitle(f'{data_label} — {stage_key}', fontweight='bold', fontsize=SUPTITLE_SIZE, y=0.98)

    os.makedirs(output_dir, exist_ok=True)
    safe_method = method.replace('–', '-').replace(' ', '_')
    suffix = '_no_label' if no_label else ''
    base = os.path.join(output_dir,
                        f'{stage_key.replace(" ", "_").lower()}_{safe_method}_{data_label.lower()}{suffix}')
    fig.savefig(f'{base}.png', dpi=DPI)
    fig.savefig(f'{base}.svg', format='svg')
    print(f'Saved: {base}.png / .svg')
    plt.close(fig)


# ── PPT 版 ────────────────────────────────────────────────────────────────────
def plot_one_ppt(stage_key, method, data_label, data, output_dir, use_log_scale=False):
    """PPT 插图：黑体、灰色虚线代替 1x、只标粉色柱数值。"""
    plt.rcParams['font.family'] = PPT_FONT_FAMILY
    plt.rcParams['font.size']   = PPT_FONT_SIZE

    method_data = data[stage_key][method]
    ratios = [_ratio(method_data[s][0], method_data[s][1]) for s in SCALES]
    global_max = max(ratios) if ratios else 2

    bw = PPT_BAR_WIDTH
    x = np.arange(len(SCALES)) * PPT_GROUP_STEP
    fig, ax = plt.subplots(figsize=FIGSIZE)

    if use_log_scale:
        ax.set_yscale('log')
        ax.set_ylim(0.5, global_max * 3.0)
        ax.yaxis.set_minor_locator(ticker.NullLocator())
    else:
        ax.set_ylim(0, global_max * 1.15)

    ax.bar(x - bw / 2, [1.0] * len(SCALES), bw,
           color=MASSFLOW_COLOR, edgecolor='white', linewidth=0.6, zorder=2)
    bars_c = ax.bar(x + bw / 2, ratios, bw,
                    color=CARDINAL_COLOR, edgecolor='white', linewidth=0.6, zorder=4)

    # 灰色虚线：从纵轴起、与横轴等宽，zorder 在蓝柱(2)上、粉柱(4)下
    ax.axhline(y=1.0, color=PPT_BASELINE_COLOR, linestyle='--', linewidth=1.2, zorder=3)

    # 纵轴只标整数（log 尺度只显 10 的次幂；线性尺度只显整数）
    if use_log_scale:
        ax.yaxis.set_major_locator(ticker.LogLocator(base=10.0, subs=[1.0]))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f'{int(v)}'))
    else:
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # 只标粉色柱（Cardinal）的倍数，跳过约等于 1 的
    label_off = 1.08 if use_log_scale else global_max * 0.02
    for bar in bars_c:
        h = bar.get_height()
        if abs(h - 1.0) < 1e-5:
            continue
        y = h * label_off if use_log_scale else h + label_off
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                _format_label(h), ha='center', va='bottom',
                fontsize=PPT_BAR_LABEL_SIZE, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(SCALE_DISPLAY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(x[0] - bw * 1.5, x[-1] + bw * 1.5)   # 横轴两侧留适当边距
    ax.set_position(PPT_AXES_RECT)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')

    os.makedirs(output_dir, exist_ok=True)
    safe_method = method.replace('–', '-').replace(' ', '_')
    base = os.path.join(output_dir,
                        f'{stage_key.replace(" ", "_").lower()}_{safe_method}_{data_label.lower()}_ppt')
    fig.savefig(f'{base}.png', dpi=DPI)
    fig.savefig(f'{base}.svg', format='svg')
    print(f'Saved: {base}.png / .svg')
    plt.close(fig)


# ── Entry point ──────────────────────────────────────────────────────────────
def plot_all():
    for stage_key, (subdir, methods, time_log, mem_log) in STAGES.items():
        output_dir = os.path.join(OUTPUT_BASE, subdir)
        for method in methods:
            for data_label, data, use_log in [
                ('Time',   TIME_DATA,   time_log),
                ('Memory', MEMORY_DATA, mem_log),
            ]:
                # plot_one(stage_key, method, data_label, data, output_dir, use_log_scale=use_log)
                # plot_one(stage_key, method, data_label, data, output_dir, use_log_scale=use_log, no_label=True)
                plot_one_ppt(stage_key, method, data_label, data, output_dir, use_log_scale=use_log)


if __name__ == '__main__':
    plot_all()

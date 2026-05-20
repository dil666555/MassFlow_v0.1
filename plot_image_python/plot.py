import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from tests.python_outcome import TIME_DATA as PYTHON_TIME_DATA

# ── Style parameters ────────────────────────────────────────────────────────
CARDINAL_COLOR  = "#F7BDBC"
MASSFLOW_COLOR  = "#B6E3F8"
FONT_FAMILY     = "Arial"
FONT_SIZE       = 12
TITLE_SIZE      = 13
SUPTITLE_SIZE   = 15
LEGEND_SIZE     = 11
BAR_LABEL_SIZE  = 8
BAR_WIDTH       = 0.20
GROUP_STEP      = 0.55
FIGSIZE         = (2.3, 5)
DPI             = 300
OUTPUT_BASE     = "./images_python-1"
# 轴区域位置（两版共用，保证 no_label 是有标签版轴区域的等比放大）
AXES_RECT       = [0.22, 0.10, 0.72, 0.68]  # [left, bottom, width, height]

# ── Scales ──────────────────────────────────────────────────────────────────
SCALES         = ['min', 'mid', 'max']
SCALE_DISPLAY  = ['Min', 'Mid', 'Max']

# ── Stage definitions: stage_key → (output_subdir, methods, use_log_scale) ──
STAGES = {
    'Peak Alignment':      ('peak_align',      ['PPM'],                             False),
    'Peak Picking':        ('peak_pick',       ['Quantile', 'Diff', 'SD', 'MAD'],  True),
    'Baseline Correction': ('baseline',        ['locmin', 'snip'],                  True),
    'Noise Reduction':     ('noise_reduction', ['MA', 'Gaussian', 'Savitzky–Golay'], True),
    'Normalization':       ('normalization',   ['TIC', 'RMS'],                      True),
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def _ratio(c, m):
    return float('inf') if m == 0 else c / m


def _format_label(h):
    if abs(h - 1.0) < 1e-5:
        return '1.0x'
    label = f'{h:.2f}x' if 0.95 <= h < 1.05 else f'{h:.1f}x'
    return '1.0x' if label == '1.00x' else label


def _add_bar_labels(ax, bars, label_off, use_log_scale):
    for bar in bars:
        h = bar.get_height()
        y = h * label_off if use_log_scale else h + label_off
        ax.text(bar.get_x() + bar.get_width() / 2, y,
                _format_label(h), ha='center', va='bottom', fontsize=BAR_LABEL_SIZE)


# ── Core plot function (one method → one figure) ─────────────────────────────
def plot_one(stage_key, method, output_dir, use_log_scale=False, no_label=False):
    """Plot a single grouped bar chart for one method."""
    plt.rcParams['font.family'] = FONT_FAMILY
    plt.rcParams['font.size']   = FONT_SIZE

    data = PYTHON_TIME_DATA[stage_key][method]
    ratios = [_ratio(data[s][0], data[s][1]) for s in SCALES]
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
                    color=MASSFLOW_COLOR, label='Flat', edgecolor='white', linewidth=0.6)
    bars_c = ax.bar(x + BAR_WIDTH / 2, ratios, BAR_WIDTH,
                    color=CARDINAL_COLOR, label='Batch', edgecolor='white', linewidth=0.6)

    ax.set_xticks(x)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 固定轴区域位置，两版完全一致
    ax.set_position(AXES_RECT) # type: ignore[no-untyped-call]

    if no_label:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    else:
        label_off = 1.08 if use_log_scale else global_max * 0.02
        _add_bar_labels(ax, bars_m, label_off, use_log_scale)
        _add_bar_labels(ax, bars_c, label_off, use_log_scale)
        ax.set_xticklabels(SCALE_DISPLAY)
        ax.set_title(method, fontweight='bold', fontsize=TITLE_SIZE)
        ax.set_ylabel('Time — Relative Ratio')
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.88),
                   ncol=2, frameon=False, fontsize=LEGEND_SIZE)
        fig.suptitle(f'Time — {stage_key}', fontweight='bold', fontsize=SUPTITLE_SIZE, y=0.98)

    os.makedirs(output_dir, exist_ok=True)
    safe_method = method.replace('–', '-').replace(' ', '_')
    suffix = '_no_label' if no_label else ''
    base = os.path.join(output_dir, f'{stage_key.replace(" ", "_").lower()}_{safe_method}_time{suffix}')

    fig.savefig(f'{base}.png', dpi=DPI)
    fig.savefig(f'{base}.svg', format='svg')
    print(f'Saved: {base}.png / .svg')
    plt.close(fig)


# ── Entry point ──────────────────────────────────────────────────────────────
def plot_all():
    for stage_key, (subdir, methods, use_log) in STAGES.items():
        output_dir = os.path.join(OUTPUT_BASE, subdir)
        for method in methods:
            plot_one(stage_key, method, output_dir, use_log_scale=use_log)
            plot_one(stage_key, method, output_dir, use_log_scale=use_log, no_label=True)


if __name__ == '__main__':
    plot_all()

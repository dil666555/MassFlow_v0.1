import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
from tests.pipeline_outcome import TIME_DATA, MEMORY_DATA

OUTPUT_DIR = './images/peak_alignment'

CARDINAL_COLOR = "#F7BDBC"
MASSFLOW_COLOR = "#B6E3F8"

METHODS = ['PPM']


def _ratio(c, m):
    if m == 0:
        return float('inf')
    return c / m


def plot_peak_alignment(data, data_label, save_name, output_dir=OUTPUT_DIR):
    """Plot grouped bar chart for Peak Alignment stage (1 method)."""
    scales = ['min', 'mid', 'max', 'ultra']
    scale_display = ['Min', 'Mid', 'Max', 'Ultra']
    n = len(METHODS)
    x = np.arange(len(scales))
    width = 0.35

    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 12

    all_ratios = []
    for method in METHODS:
        for scale in scales:
            c_val, m_val = data[method][scale]
            all_ratios.append(_ratio(c_val, m_val))
    global_max = max(all_ratios) if all_ratios else 2

    fig, axes = plt.subplots(1, n, figsize=(6, 5), sharey=True, squeeze=False)

    for idx, method in enumerate(METHODS):
        ax = axes.flat[idx]
        method_data = data[method]

        cardinal_ratios = [_ratio(method_data[s][0], method_data[s][1]) for s in scales]
        massflow_ratios = [1.0] * len(scales)

        bars_m = ax.bar(x - width / 2, massflow_ratios, width,
                        color=MASSFLOW_COLOR, label='MassFlow',
                        edgecolor='white', linewidth=0.6)
        bars_c = ax.bar(x + width / 2, cardinal_ratios, width,
                        color=CARDINAL_COLOR, label='Cardinal',
                        edgecolor='white', linewidth=0.6)

        offset = global_max * 0.02
        for bar in bars_m:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                    f'{h:.1f}x', ha='center', va='bottom', fontsize=9)
        for bar in bars_c:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                    f'{h:.1f}x', ha='center', va='bottom', fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels(scale_display)
        ax.set_title(method, fontweight='bold', fontsize=13)
        ax.set_ylabel(f'{data_label} — Relative Ratio')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    axes.flat[0].set_ylim(0, global_max * 1.15)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.88),
               ncol=2, frameon=False, fontsize=11)

    fig.suptitle(f'{data_label} — Peak Alignment (PPM)', fontweight='bold', fontsize=15, y=0.98)
    plt.tight_layout(rect=(0, 0, 1, 0.82))

    os.makedirs(output_dir, exist_ok=True)

    png_path = os.path.join(output_dir, f'{save_name}.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f'Figure saved to {png_path}')

    svg_path = os.path.join(output_dir, f'{save_name}.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight')
    print(f'Figure saved to {svg_path}')

    plt.close(fig)


def plot_all_peak_alignment(output_dir=OUTPUT_DIR):
    plot_peak_alignment(TIME_DATA['Peak Alignment'], 'Time', 'peak_alignment_time', output_dir)
    plot_peak_alignment(MEMORY_DATA['Peak Alignment'], 'Memory', 'peak_alignment_memory', output_dir)


if __name__ == '__main__':
    plot_all_peak_alignment()

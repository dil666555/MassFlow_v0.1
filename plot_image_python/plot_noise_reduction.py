import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from tests.python_outcome import TIME_DATA, MEMORY_DATA

OUTPUT_DIR = './images_python/noise_reduction'

CARDINAL_COLOR = "#F7BDBC"
MASSFLOW_COLOR = "#B6E3F8"

METHODS = ['MA', 'Gaussian', 'Savitzky–Golay']


def _ratio(c, m):
    if m == 0:
        return float('inf')
    return c / m


def format_ratio_label(h):
    if abs(h - 1.0) < 1e-5:
        return '1.0x'

    elif 0.95 <= h < 1.05:
        label = f'{h:.2f}x'
        if label == '1.00x':
            return '1.0x'
        return label

    else:
        return f'{h:.1f}x'


def plot_noise_reduction(data, data_label, save_name, output_dir=OUTPUT_DIR, use_log_scale=False):
    """Plot grouped bar chart for Noise Reduction stage (3 methods)."""
    scales = ['min', 'mid', 'max']
    scale_display = ['Min', 'Mid', 'Max']
    n = len(METHODS)
    x = np.arange(len(scales))
    width = 0.35

    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 12

    all_ratios = []
    for method in METHODS:
        for scale in scales:
            c_val, m_val = data[method][scale]
            all_ratios.append(_ratio(c_val, m_val))
    global_max = max(all_ratios) if all_ratios else 2

    fig, axes = plt.subplots(1, n, figsize=(15, 5), sharey=True, squeeze=False)

    if use_log_scale:
        axes.flat[0].set_yscale('log')
        axes.flat[0].set_ylim(0.5, global_max * 3.0)
        axes.flat[0].yaxis.set_minor_locator(ticker.NullLocator())
    else:
        axes.flat[0].set_ylim(0, global_max * 1.15)

    for idx, method in enumerate(METHODS):
        ax = axes.flat[idx]
        method_data = data[method]

        cardinal_ratios = [_ratio(method_data[s][0], method_data[s][1]) for s in scales]
        massflow_ratios = [1.0] * len(scales)

        bars_m = ax.bar(x - width / 2, massflow_ratios, width,
                        color=MASSFLOW_COLOR, label='Flat',
                        edgecolor='white', linewidth=0.6)
        bars_c = ax.bar(x + width / 2, cardinal_ratios, width,
                        color=CARDINAL_COLOR, label='Batch',
                        edgecolor='white', linewidth=0.6)

        label_off = 1.08 if use_log_scale else global_max * 0.02
        for bar in bars_m:
            h = bar.get_height()
            y = h * label_off if use_log_scale else h + label_off
            ax.text(bar.get_x() + bar.get_width() / 2, y,
                    format_ratio_label(h), ha='center', va='bottom', fontsize=9)
        for bar in bars_c:
            h = bar.get_height()
            y = h * label_off if use_log_scale else h + label_off
            ax.text(bar.get_x() + bar.get_width() / 2, y,
                    format_ratio_label(h), ha='center', va='bottom', fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels(scale_display)
        ax.set_title(method, fontweight='bold', fontsize=13)

        if idx == 0:
            ax.set_ylabel(f'{data_label} — Relative Ratio')

        if use_log_scale:
            ax.yaxis.set_minor_locator(ticker.NullLocator())

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.88),
               ncol=2, frameon=False, fontsize=11)

    fig.suptitle(f'{data_label} — Noise Reduction', fontweight='bold', fontsize=15, y=0.98)
    plt.tight_layout(rect=(0, 0, 1, 0.82))

    os.makedirs(output_dir, exist_ok=True)

    png_path = os.path.join(output_dir, f'{save_name}.png')
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f'Figure saved to {png_path}')

    svg_path = os.path.join(output_dir, f'{save_name}.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight')
    print(f'Figure saved to {svg_path}')

    plt.close(fig)


def plot_all_noise_reduction(output_dir=OUTPUT_DIR):
    plot_noise_reduction(TIME_DATA['Noise Reduction'], 'Time', 'noise_reduction_time', output_dir, use_log_scale=True)
    plot_noise_reduction(MEMORY_DATA['Noise Reduction'], 'Memory', 'noise_reduction_memory', output_dir)


if __name__ == '__main__':
    plot_all_noise_reduction()

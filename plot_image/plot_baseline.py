import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker  # 新增：用于控制刻度

OUTPUT_DIR = './images/baseline'

def cal_time_or_mem_ratio(val_1, val_2):
    """Calculate the ratio of Cardinal to MassFlow values."""
    if val_2 == 0:
        return float('inf')  # Avoid division by zero; return infinity.
    return val_1 / val_2

def _card_b_to_mib(v):
    """Cardinal peakRAM reports bytes in a column labelled MiB; convert."""
    return v / (1024 * 1024)

def format_ratio_label(h):
    if abs(h - 1.0) < 1e-5:
        return '1.0x'  # 绝对基准

    elif 0.95 <= h < 1.05:
        label = f'{h:.2f}x'
        # 如果算出来正好是 1.00x，就强行显示为 1.0x 保持美观
        if label == '1.00x':
            return '1.0x'
        return label

    else:
        return f'{h:.1f}x'  # 其他数据正常保留一位小数

BASELINE_TIME_DATA = {
    'locmin': {
        'min':   (2.887, 1.2460),
        'mid':   (3.970, 1.5893),
        'max':   (173.571, 7.8098),
        'ultra': (78.830, 24.7616),
    },
    'snip': {
        'min':   (1.696, 1.7388),
        'mid':   (2.493, 2.4839),
        'max':   (106.933, 27.1179),
        'ultra': (48.831, 35.9224),
    },
}

BASELINE_MEM_DATA = {
    'locmin': {
        'min':   (_card_b_to_mib(82548434),   103.3),
        'mid':   (_card_b_to_mib(130062630),  127.9),
        'max':   (_card_b_to_mib(2567841898), 1022.9),
        'ultra': (_card_b_to_mib(2008841587), 620.6),
    },
    'snip': {
        'min':   (_card_b_to_mib(115940482),  92.0),
        'mid':   (_card_b_to_mib(125356535),  119.3),
        'max':   (_card_b_to_mib(2567837149), 1022.9),
        'ultra': (_card_b_to_mib(1893013771), 544.1),
    },
}

CARDINAL_COLOR = "#F7BDBC"
MASSFLOW_COLOR = "#B6E3F8"

def plot_baseline(data, data_label, save_name, output_dir=OUTPUT_DIR, use_log_scale=False):
    """Plot a grouped bar chart comparing MassFlow vs Cardinal for two methods."""
    methods = ['locmin', 'snip']
    scales = ['min', 'mid', 'max', 'ultra']
    scale_display = ['Min', 'Mid', 'Max', 'Ultra']
    x = np.arange(len(scales))
    width = 0.35

    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['font.size'] = 12

    all_cardinal_ratios = []
    for method in methods:
        for scale in scales:
            c_val, m_val = data[method][scale]
            all_cardinal_ratios.append(cal_time_or_mem_ratio(c_val, m_val))
    global_max_ratio = max(all_cardinal_ratios) if all_cardinal_ratios else 2

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharey=True)

    if use_log_scale:
        axes[0].set_yscale('log')
        axes[0].set_ylim(0.5, global_max_ratio * 3.0)  # log模式下底部设为0.5更合理，顶部留出足够空间
        # 清除烦人的对数轴短横线(minor ticks)
        axes[0].yaxis.set_minor_locator(ticker.NullLocator())
    else:
        axes[0].set_ylim(0, global_max_ratio * 1.15)

    for col, method in enumerate(methods):
        ax = axes[col]
        method_data = data[method]

        cardinal_ratios = []
        for scale in scales:
            c_val, m_val = method_data[scale]
            cardinal_ratios.append(cal_time_or_mem_ratio(c_val, m_val))
        massflow_ratios = [1.0] * len(scales)

        # MassFlow 在左
        bars_m = ax.bar(x - width / 2, massflow_ratios, width,
                        color=MASSFLOW_COLOR, label='MassFlow',
                        edgecolor='white', linewidth=0.6)

        # Cardinal 在右
        bars_c = ax.bar(x + width / 2, cardinal_ratios, width,
                        color=CARDINAL_COLOR, label='Cardinal',
                        edgecolor='white', linewidth=0.6)

        label_off = 1.08 if use_log_scale else global_max_ratio * 0.02

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

        if col == 0:
            ax.set_ylabel(f'{data_label} — Relative Ratio')

        # 如果开启了对数轴，确保每个子图的次级刻度都被关闭
        if use_log_scale:
            ax.yaxis.set_minor_locator(ticker.NullLocator())

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.88), ncol=2, frameon=False, fontsize=11)

    fig.suptitle(f'{data_label} Baseline Comparison', fontweight='bold', fontsize=15, y=0.98)

    plt.tight_layout(rect=(0, 0, 1, 0.82))

    os.makedirs(output_dir, exist_ok=True)

    save_path = os.path.join(output_dir, f'{save_name}.png')
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f'Figure saved to {save_path}')

    svg_path = os.path.join(output_dir, f'{save_name}.svg')
    fig.savefig(svg_path, format='svg', bbox_inches='tight')
    print(f'Figure saved to {svg_path}')

    plt.close(fig)

def plot_all_baselines(output_dir=OUTPUT_DIR):
    plot_baseline(BASELINE_TIME_DATA, 'Time', 'baseline_time', output_dir, use_log_scale=True)
    plot_baseline(BASELINE_MEM_DATA, 'Memory', 'baseline_memory', output_dir, use_log_scale=False)

if __name__ == '__main__':
    plot_all_baselines()

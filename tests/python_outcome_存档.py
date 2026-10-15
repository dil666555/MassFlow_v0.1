# ============================================================================
# 数据来源说明
# 本文件是 MassFlow 两种实现的纯计算耗时对比 (无 IO):
#   每个元组 = (batch 值, flat 值)
#     · batch (元组第一个值) = Python/NumPy 实现 (test_*_speed, method="origin")
#     · flat  (元组第二个值) = Parallel/Pipeline 实现 (test_*_flat_speed, numba)
# 总览文档: outcome_of_test/massflow-only-compute.md 第 1-9 行 (明确上述对应关系)
#
# 规模取源 (min/max 用原测, mid/ultra 用重测):
#   min/max -> oc-orig ;  mid -> oc-mid ;  ultra -> oc-ultra
# 文件缩写:
#   oc-orig  = outcome_of_test/massflow-only-compute.md   (min/max 原测, 同时是总览)
#   oc-mid   = tests/only_compute_new_mid.md              (mid 重测)
#   oc-ultra = tests/only_compute_new_original.md         (ultra/original 重测)
#
# 取值列: 除特别注明外, 均取各表 mean 列
# 行尾注释:  # B: <源>:<行> | F: <源>:<行>   (B=batch 第一值, F=flat 第二值)
#   带 "(÷1000, ms→s)" 表示该值由源表 mean(单位 ms) 除以 1000 换算得到; 不带则直接取源表 mean
#
# 特殊情况:
#   · Baseline 与 Peak Pick 的 max flat 值因 example 数据首次 flat 测试 cache 异常,
#     取用 oc-orig 内的 "pipeline 流程修正表" (而非首测表), 详见 oc-orig:259
#   · Peak Align 取 "min" 方法行 (binfun="min", 即 min-ppm)
#   · Peak Pick 的 batch 实现只有一种 (method="origin"), 故 Quantile/Diff/SD 三个方法
#     共用同一组 batch 值 (来源行相同)
#
# 单位注意 (源表单位不一, python_outcome.py 未完全统一, 解读时需留意):
#   · Baseline / Peak Pick: 全部为 s (flat 的 min 来自 ms 首测表, 已 ÷1000; 其余原表即 s)
#   · Noise Reduction / Normalization / Peak Alignment:
#       - min/max: 保留源表 ms 原值 (如 noise MA min=311.61 为 ms, flat=7.88 为 ms)
#       - mid/ultra: 已换算为 s (即源码中 "统一成s" 注释所指)
#     ⇒ 故这三类的 min 元组数值看起来远大于 mid/ultra, 实因 min/max 为 ms 而 mid/ultra 为 s
#   · Peak Pick ultra batch=46.8220 实际取自 oc-ultra:87 的 mean 列;
#     注: oc-orig:183 注释称 "使用 min 列 (46.5643)", 与本文件实际值 (46.8220=mean) 不符
# ============================================================================

TIME_DATA = {
    'Baseline Correction': {
        'locmin': {
            'min':   (1.1344, 0.13493),    # B: oc-orig:37 | F: oc-orig:273(÷1000, ms→s)
            'mid':   (12.3736, 1.3717787),  # 统一成s; B: oc-mid:15 | F: oc-mid:24(÷1000, ms→s)
            'max':   (34.9885, 7.1768),    # B: oc-orig:41 | F: oc-orig:290(修正表, s)
            'ultra': (23.4377, 3.2848),  # 统一成s; B: oc-ultra:15 | F: oc-ultra:23(s)
        },
        'snip': {
            'min':   (6.4633, 0.68194),    # B: oc-orig:38 | F: oc-orig:274(÷1000, ms→s)
            'mid':   (30.8963, 0.8601780),  # 统一成s; B: oc-mid:16 | F: oc-mid:23(÷1000, ms→s)
            'max':   (88.0729, 26.6341),  # B: oc-orig:42 | F: oc-orig:291(修正表, s)
            'ultra': (106.7622, 2.7108),  # 统一成s; B: oc-ultra:16 | F: oc-ultra:22(s)
        },
    },
    'Noise Reduction': {
        'MA': {
            'min':   (311.61, 7.88),       # B: oc-orig:82(ms) | F: oc-orig:331(ms)   [min/max 保留 ms 原值]
            'mid':   (0.4674691, 0.0564380),  # 统一成s; B: oc-mid:41(÷1000, ms→s) | F: oc-mid:50(÷1000, ms→s)
            'max':   (1928.02, 174.36),    # B: oc-orig:88(ms) | F: oc-orig:337(ms)   [min/max 保留 ms 原值]
            'ultra': (4.3494, 0.1923563),  # 统一成s; B: oc-ultra:39(s) | F: oc-ultra:45(÷1000, ms→s)
        },
        'Gaussian': {
            'min':   (567.70, 24.12),      # B: oc-orig:83(ms) | F: oc-orig:332(ms)   [min/max 保留 ms 原值]
            'mid':   (0.5777913, 0.1647026),  # 统一成s; B: oc-mid:42(÷1000, ms→s) | F: oc-mid:51(÷1000, ms→s)
            'max':   (2013.80, 441.87),     # B: oc-orig:89(ms) | F: oc-orig:338(ms)   [min/max 保留 ms 原值]
            'ultra': (6.0477, 0.4965438),  # 统一成s; B: oc-ultra:40(s) | F: oc-ultra:46(÷1000, ms→s)
        },
        'Savitzky–Golay': {
            'min':   (2018.74, 27.76),     # B: oc-orig:84(ms) | F: oc-orig:333(ms)   [min/max 保留 ms 原值]
            'mid':   (1.4490980, 0.2012019),  # 统一成s; B: oc-mid:43(÷1000, ms→s) | F: oc-mid:52(÷1000, ms→s)
            'max':   (4034.30, 468.67),     # B: oc-orig:90(ms) | F: oc-orig:339(ms)   [min/max 保留 ms 原值]
            'ultra': (13.1050, 0.6860692),  # 统一成s; B: oc-ultra:41(s) | F: oc-ultra:47(÷1000, ms→s)
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (164.2962, 9.8635),   # B: oc-orig:134(ms) | F: oc-orig:389(ms)   [min/max 保留 ms 原值]
            'mid':   (0.2364373, 0.0728811),  # 统一成s; B: oc-mid:69(÷1000, ms→s) | F: oc-mid:78(÷1000, ms→s)
            'max':   (858.5671, 198.8921),  # B: oc-orig:138(ms) | F: oc-orig:393(ms)   [min/max 保留 ms 原值]
            'ultra': (3.0824, 0.8758963),  # 统一成s; B: oc-ultra:63(s) | F: oc-ultra:69(÷1000, ms→s)
        },
        'RMS': {
            'min':   (293.0027, 9.6915),   # B: oc-orig:135(ms) | F: oc-orig:390(ms)   [min/max 保留 ms 原值]
            'mid':   (0.5019894, 0.0745676),  # 统一成s; B: oc-mid:70(÷1000, ms→s) | F: oc-mid:79(÷1000, ms→s)
            'max':   (1635.1218, 242.8363),  # B: oc-orig:139(ms) | F: oc-orig:394(ms)   [min/max 保留 ms 原值]
            'ultra': (4.4271, 0.2223605),  # 统一成s; B: oc-ultra:64(s) | F: oc-ultra:68(÷1000, ms→s)
        },
    },
    'Peak Picking': {
        # batch 实现只有 "origin" 一种, 故 Quantile/Diff/SD 的 batch(第一)值共用同一来源行
        'Quantile': {
            'min':   (3.6639, 0.4288802),   # B: oc-orig:179(s) | F: oc-orig:440(÷1000, ms→s)
            'mid':   (15.1977, 4.4862),  # 统一成s; B: oc-mid:96(s) | F: oc-mid:105(s)
            'max':   (36.7218, 24.8683),   # B: oc-orig:181(s) | F: oc-orig:469(修正表, s)
            'ultra': (46.8220, 26.5196),  # 统一成s; B: oc-ultra:87(mean, s) | F: oc-ultra:92(s)
        },
        'Diff': {
            'min':   (3.6639, 0.0936321),   # B: oc-orig:179(s) | F: oc-orig:441(÷1000, ms→s)
            'mid':   (15.1977, 1.1553),  # 统一成s; B: oc-mid:96(s) | F: oc-mid:103(s)
            'max':   (36.7218, 6.0347),    # B: oc-orig:181(s) | F: oc-orig:467(修正表, s)
            'ultra': (46.8220, 34.3804),  # 统一成s; B: oc-ultra:87(mean, s) | F: oc-ultra:93(s)
        },
        'SD': {
            'min':   (3.6639, 0.1408043),   # B: oc-orig:179(s) | F: oc-orig:442(÷1000, ms→s)
            'mid':   (15.1977, 1.5082),  # 统一成s; B: oc-mid:96(s) | F: oc-mid:104(s)
            'max':   (36.7218, 8.0348),    # B: oc-orig:181(s) | F: oc-orig:468(修正表, s)
            'ultra': (46.8220, 19.0254),  # 统一成s; B: oc-ultra:87(mean, s) | F: oc-ultra:91(s)
        },
    },
    'Peak Alignment': {
        'Default': {
            'min':   (600.1969, 67.0235),   # B: oc-orig:222(ms) | F: oc-orig:526(ms)   [min/max 保留 ms 原值]
            'mid':   (3.1284, 0.6179468),  # 统一成s; B: oc-mid:123(s) | F: oc-mid:130(÷1000, ms→s)
            'max':   (15520.2496, 3245.4160),  # B: oc-orig:228(ms) | F: oc-orig:530(ms)   [min/max 保留 ms 原值]
            'ultra': (7.1831, 1.8301),  # 统一成s; B: oc-ultra:112(s) | F: oc-ultra:113(s)
        },
    },
}

# ============================================================================
# 数据来源说明
# 本文件是 MassFlow 两种实现的耗时对比，含纯计算与 pipeline 替代值:
#   每个元组 = (batch 值, flat 值)
#     · batch (元组第一个值) = Python/NumPy 实现 (test_*_speed, method="origin")
#     · flat  (元组第二个值) = Numba 实现；min/mid 为纯计算，max/ultra 为 pipeline
# 总览文档: outcome_of_test/massflow-only-compute.md 第 1-9 行 (明确上述对应关系)
#
# 规模取源:
#   batch: min/max -> oc-orig ; mid -> oc-mid ; ultra -> oc-ultra
#   flat: min -> oc-orig ; mid -> oc-mid ; max/ultra -> pipeline
#   例外: SNIP min/mid 的 batch/flat 均取本次 m=5 重测 JSON 的 stats.mean (s)
# 文件缩写:
#   oc-orig  = outcome_of_test/massflow-only-compute.md   (min/max 原测, 同时是总览)
#   oc-mid   = tests/only_compute_new_mid.md              (mid 重测)
#   oc-ultra = tests/only_compute_new_original.md         (ultra/original 重测)
#   pipeline = tests/pipeline_outcome.py 的 TIME_DATA 同阶段、方法、规模的第二个值 (s)
#              第一个值是 Cardinal 耗时，不用于本文件的 batch 值
#   snip-batch = 10-15-重测部分内容/S11-SNIP-min-mid-m5.json
#   snip-flat  = 10-15-重测部分内容/S11-SNIP-min-mid-m5-numba.json (Numba 4 线程)
#   重测说明及统计表: 10-15-重测部分内容/S11-SNIP-统一m=5.md
#
# 取值列: 除特别注明外, 均取各表 mean 列
# 行尾注释:  # B: <源>:<行> | F: <源>:<行>   (B=batch 第一值, F=flat 第二值)
#   带 "(÷1000, ms→s)" 表示该值由源表 mean(单位 ms) 除以 1000 换算得到; 不带则直接取源表 mean
#
# 特殊情况:
#   · max/ultra 的全部 flat 值统一采用 pipeline，与 SI Table S6 同源；包含读写开销
#   · SNIP min/mid 已回填 m=5 重测；其余 batch 仍为原纯计算测量值
#     max/ultra batch pipeline 重测尚未回填
#   · Peak Align 取 "min" 方法行 (binfun="min", 即 min-ppm)
#   · Peak Pick 的 batch 实现只有一种 (method="origin"), 故 Quantile/Diff/SD 三个方法
#     共用同一组 batch 值 (来源行相同)
#
# 单位注意 (源表单位不一, python_outcome.py 未完全统一, 解读时需留意):
#   · Baseline / Peak Pick: 全部为 s (flat 的 min 来自 ms 首测表, 已 ÷1000; 其余原表即 s)
#   · Noise Reduction / Normalization / Peak Alignment:
#       - min: 保留源表 ms 原值 (如 noise MA min=311.61 为 ms, flat=7.88 为 ms)
#       - mid/max/ultra: 均为 s；max batch 仅作 ms→s 换算，以匹配 pipeline flat 的单位
#     ⇒ 故这三类的 min 元组数值看起来远大于其他规模，不能直接跨规模比较绝对数值
#   · Peak Pick ultra batch=46.8220 实际取自 oc-ultra:87 的 mean 列;
#     注: oc-orig:183 注释称 "使用 min 列 (46.5643)", 与本文件实际值 (46.8220=mean) 不符
# ============================================================================

TIME_DATA = {
    'Baseline Correction': {
        'locmin': {
            'min':   (1.1344, 0.13493),    # B: oc-orig:37 | F: oc-orig:273(÷1000, ms→s)
            'mid':   (12.3736, 1.3717787),  # 统一成s; B: oc-mid:15 | F: oc-mid:24(÷1000, ms→s)
            'max':   (34.9885, 7.1571),    # B: oc-orig:41 | F: pipeline (s)
            'ultra': (23.4377, 18.8867),  # B: oc-ultra:15 | F: pipeline (s)
        },
        'snip': {
            'min':   (0.4990766875052941, 0.14358127050218172),  # B: snip-batch:min stats.mean | F: snip-flat:min stats.mean (s, m=5)
            'mid':   (2.1421782500037807, 1.1159906670000055),  # B: snip-batch:mid stats.mean | F: snip-flat:mid stats.mean (s, m=5)
            'max':   (88.0729, 4.0907),  # B: oc-orig:42 | F: pipeline (s)
            'ultra': (106.7622, 17.1464),  # B: oc-ultra:16 | F: pipeline (s)
        },
    },
    'Noise Reduction': {
        'MA': {
            'min':   (311.61, 7.88),       # B: oc-orig:82(ms) | F: oc-orig:331(ms)   [min 保留 ms 原值]
            'mid':   (0.4674691, 0.0564380),  # 统一成s; B: oc-mid:41(÷1000, ms→s) | F: oc-mid:50(÷1000, ms→s)
            'max':   (1.92802, 4.3401),    # B: oc-orig:88(÷1000, ms→s) | F: pipeline (s)
            'ultra': (4.3494, 24.6143),  # B: oc-ultra:39(s) | F: pipeline (s)
        },
        'Gaussian': {
            'min':   (567.70, 24.12),      # B: oc-orig:83(ms) | F: oc-orig:332(ms)   [min 保留 ms 原值]
            'mid':   (0.5777913, 0.1647026),  # 统一成s; B: oc-mid:42(÷1000, ms→s) | F: oc-mid:51(÷1000, ms→s)
            'max':   (2.01380, 3.8812),     # B: oc-orig:89(÷1000, ms→s) | F: pipeline (s)
            'ultra': (6.0477, 23.9425),  # B: oc-ultra:40(s) | F: pipeline (s)
        },
        'Savitzky–Golay': {
            'min':   (2018.74, 27.76),     # B: oc-orig:84(ms) | F: oc-orig:333(ms)   [min 保留 ms 原值]
            'mid':   (1.4490980, 0.2012019),  # 统一成s; B: oc-mid:43(÷1000, ms→s) | F: oc-mid:52(÷1000, ms→s)
            'max':   (4.03430, 3.8573),     # B: oc-orig:90(÷1000, ms→s) | F: pipeline (s)
            'ultra': (13.1050, 24.0176),  # B: oc-ultra:41(s) | F: pipeline (s)
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (164.2962, 9.8635),   # B: oc-orig:134(ms) | F: oc-orig:389(ms)   [min 保留 ms 原值]
            'mid':   (0.2364373, 0.0728811),  # 统一成s; B: oc-mid:69(÷1000, ms→s) | F: oc-mid:78(÷1000, ms→s)
            'max':   (0.8585671, 4.3329),  # B: oc-orig:138(÷1000, ms→s) | F: pipeline (s)
            'ultra': (3.0824, 24.7824),  # B: oc-ultra:63(s) | F: pipeline (s)
        },
        'RMS': {
            'min':   (293.0027, 9.6915),   # B: oc-orig:135(ms) | F: oc-orig:390(ms)   [min 保留 ms 原值]
            'mid':   (0.5019894, 0.0745676),  # 统一成s; B: oc-mid:70(÷1000, ms→s) | F: oc-mid:79(÷1000, ms→s)
            'max':   (1.6351218, 3.7718),  # B: oc-orig:139(÷1000, ms→s) | F: pipeline (s)
            'ultra': (4.4271, 24.2586),  # B: oc-ultra:64(s) | F: pipeline (s)
        },
    },
    'Peak Picking': {
        # batch 实现只有 "origin" 一种, 故 Quantile/Diff/SD 的 batch(第一)值共用同一来源行
        'Quantile': {
            'min':   (3.6639, 0.4288802),   # B: oc-orig:179(s) | F: oc-orig:440(÷1000, ms→s)
            'mid':   (15.1977, 4.4862),  # 统一成s; B: oc-mid:96(s) | F: oc-mid:105(s)
            'max':   (36.7218, 24.6802),   # B: oc-orig:181(s) | F: pipeline (s)
            'ultra': (46.8220, 28.9606),  # B: oc-ultra:87(mean, s) | F: pipeline (s)
        },
        'Diff': {
            'min':   (3.6639, 0.0936321),   # B: oc-orig:179(s) | F: oc-orig:441(÷1000, ms→s)
            'mid':   (15.1977, 1.1553),  # 统一成s; B: oc-mid:96(s) | F: oc-mid:103(s)
            'max':   (36.7218, 6.0213),    # B: oc-orig:181(s) | F: pipeline (s)
            'ultra': (46.8220, 11.3753),  # B: oc-ultra:87(mean, s) | F: pipeline (s)
        },
        'SD': {
            'min':   (3.6639, 0.1408043),   # B: oc-orig:179(s) | F: oc-orig:442(÷1000, ms→s)
            'mid':   (15.1977, 1.5082),  # 统一成s; B: oc-mid:96(s) | F: oc-mid:104(s)
            'max':   (36.7218, 7.9576),    # B: oc-orig:181(s) | F: pipeline (s)
            'ultra': (46.8220, 10.9617),  # B: oc-ultra:87(mean, s) | F: pipeline (s)
        },
    },
    'Peak Alignment': {
        'Default': {
            'min':   (600.1969, 67.0235),   # B: oc-orig:222(ms) | F: oc-orig:526(ms)   [min 保留 ms 原值]
            'mid':   (3.1284, 0.6179468),  # 统一成s; B: oc-mid:123(s) | F: oc-mid:130(÷1000, ms→s)
            'max':   (15.5202496, 4.8021340),  # B: oc-orig:228(÷1000, ms→s) | F: pipeline (s)
            'ultra': (7.1831, 6.5740955),  # B: oc-ultra:112(s) | F: pipeline (s)
        },
    },
}

# ============================================================================
# 数据来源说明
# 每个元组 = (Cardinal 值, MassFlow 值):
#   · Cardinal 时间 —— bench_time 表 mean 列 (单位 s)
#   · Cardinal 内存 —— baseline/noise/normal/pick 取 peakRAM 表 Peak_RAM_Used_MiB 列
#     (实为 Vcell 计数, 经下方 _card_b_to_mib 换算为 MiB); Peak Align 取
#     Peak_RAM_Normalized_MiB 列 (已归一化, 直接使用, 不换算)
#   · MassFlow 时间 —— pytest-benchmark mean 列 (单位 s; Peak Align 原测表为 ms, 已 ÷1000)
#   · MassFlow 内存 —— memray "total memory allocated" 列 (MiB)
# 规模取源: mid 规模用"重测"文件, min/max/ultra 用"原测"文件
#   (baseline 的 MassFlow 时间为例外: 4 个规模均取自重测文件 mf-mid)
# 文件缩写:
#   card-orig = outcome_of_test/cardinal-pipeline.md          (Cardinal 原测, min/max/ultra)
#   card-mid  = tests/new_mid_file_pipeline_cardinal.md        (Cardinal 重测, 仅 mid)
#   mf-orig   = outcome_of_test/massflow-pipeline.md           (MassFlow 原测, min/max/ultra)
#   mf-mid    = tests/new_mid_file_pipeline.md                 (MassFlow 重测, baseline 全集 + 各类别 mid)
#   Peak Align 另有原始源 tests/peak_align_new_test-只用了min.md, 与 cardinal-pipeline.md 的 Peak Align 表互为镜像
# 行尾注释:  # C: <源>:<行> | MF: <源>:<行>  (C=元组第一个值 Cardinal, MF=第二个值 MassFlow)
# ============================================================================

TIME_DATA = {
    'Baseline Correction': {
        'locmin': {
            'min':   (2.887, 1.2457),    # C: card-orig:93 | MF: mf-mid:16
            'mid':   (24.513, 3.0543),   # C: card-mid:81 | MF: mf-mid:18
            'max':   (173.571, 7.1571),  # C: card-orig:95 | MF: mf-mid:21
            'ultra': (78.830, 18.8867),  # C: card-orig:96 | MF: mf-mid:22
        },
        'snip': {
            'min':   (1.696, 1.2773),    # C: card-orig:97 | MF: mf-mid:17
            'mid':   (9.407, 3.4709),    # C: card-mid:82 | MF: mf-mid:19
            'max':   (106.933, 4.0907),  # C: card-orig:99 | MF: mf-mid:20
            'ultra': (48.831, 17.1464),  # C: card-orig:100 | MF: mf-mid:23
        },
    },
    'Noise Reduction': {
        'MA': {
            'min':   (1.640, 1.2949),    # C: card-orig:171 | MF: mf-orig:73
            'mid':   (10.3505, 3.5652),  # C: card-mid:147 | MF: mf-mid:53
            'max':   (142.227, 4.3401),  # C: card-orig:173 | MF: mf-orig:79
            'ultra': (66.829, 24.6143),  # C: card-orig:174 | MF: mf-orig:82
        },
        'Gaussian': {
            'min':   (1.719, 1.2291),    # C: card-orig:175 | MF: mf-orig:74
            'mid':   (11.5960, 3.4915),  # C: card-mid:148 | MF: mf-mid:54
            'max':   (141.495, 3.8812),  # C: card-orig:177 | MF: mf-orig:80
            'ultra': (75.651, 23.9425),  # C: card-orig:178 | MF: mf-orig:83
        },
        'Savitzky–Golay': {
            'min':   (1.963, 1.2853),    # C: card-orig:179 | MF: mf-orig:75
            'mid':   (11.8505, 3.4703),  # C: card-mid:149 | MF: mf-mid:55
            'max':   (117.427, 3.8573),  # C: card-orig:181 | MF: mf-orig:81
            'ultra': (73.261, 24.0176),  # C: card-orig:182 | MF: mf-orig:84
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (1.338, 1.1845),    # C: card-orig:271 | MF: mf-orig:133
            'mid':   (7.920, 2.6237),    # C: card-mid:228 | MF: mf-mid:87
            'max':   (158.212, 4.3329),  # C: card-orig:273 | MF: mf-orig:139
            'ultra': (47.316, 24.7824),  # C: card-orig:274 | MF: mf-orig:142
        },
        'RMS': {
            'min':   (1.233, 1.1879),    # C: card-orig:275 | MF: mf-orig:134
            'mid':   (8.852, 2.6145),    # C: card-mid:229 | MF: mf-mid:86
            'max':   (153.117, 3.7718),  # C: card-orig:277 | MF: mf-orig:140
            'ultra': (56.278, 24.2586),  # C: card-orig:278 | MF: mf-orig:143
        },
        'Reference': {
            'min':   (1.293, 1.1866),    # C: card-orig:279 | MF: mf-orig:135
            'mid':   (8.398, 2.1222),    # C: card-mid:230 | MF: mf-mid:85
            'max':   (119.599, 3.8045),  # C: card-orig:281 | MF: mf-orig:141
            'ultra': (39.300, 23.2055),  # C: card-orig:282 | MF: mf-orig:144
        },
    },
    'Peak Picking': {
        'Quantile': {
            'min':   (5.352, 1.4538),    # C: card-orig:371 | MF: mf-orig:191
            'mid':   (22.0870, 9.9685),  # C: card-mid:308 | MF: mf-mid:119
            'max':   (57.080, 24.6802),  # C: card-orig:373 | MF: mf-orig:199
            'ultra': (87.883, 28.9606),  # C: card-orig:374 | MF: mf-orig:203
        },
        'Diff': {
            'min':   (3.185, 1.1755),    # C: card-orig:375 | MF: mf-orig:192
            'mid':   (13.3945, 2.5713),  # C: card-mid:309 | MF: mf-mid:117
            'max':   (32.793, 6.0213),    # C: card-orig:377 | MF: mf-orig:200
            'ultra': (59.712, 11.3753),  # C: card-orig:378 | MF: mf-orig:204
        },
        'SD': {
            'min':   (3.965, 1.1833),    # C: card-orig:379 | MF: mf-orig:193
            'mid':   (17.2255, 3.2416),  # C: card-mid:310 | MF: mf-mid:118
            'max':   (54.422, 7.9576),   # C: card-orig:381 | MF: mf-orig:201
            'ultra': (78.692, 10.9617),  # C: card-orig:382 | MF: mf-orig:205
        },
        'MAD': {
            'min':   (5.274, 1.9634),    # C: card-orig:383 | MF: mf-orig:194
            'mid':   (26.7245, 16.5783), # C: card-mid:311 | MF: mf-mid:120
            'max':   (78.969, 41.5663),  # C: card-orig:385 | MF: mf-orig:202
            'ultra': (105.347, 48.1335), # C: card-orig:386 | MF: mf-orig:206
        },
    },
    'Peak Alignment': {
        'Default': {
            'min':   (2.827, 0.9214473),  # C: card-orig:586 | MF: mf-orig:263
            'mid':   (3.718667, 1.1204),  # C: card-mid:491 | MF: mf-mid:151
            'max':   (10.376333, 4.8021340),  # C: card-orig:588 | MF: mf-orig:268
            'ultra': (28.203, 6.5740955), # C: card-orig:589 | MF: mf-orig:271
        },
    },
}

def _card_b_to_mib(v):
    """Cardinal peakRAM reports Vcell counts in a column labelled MiB; convert."""
    return v * 8 / (1024 * 1024)


MEMORY_DATA = {
    'Baseline Correction': {
        'locmin': {
            'min':   (_card_b_to_mib(82548434),   103.3),   # C: card-orig:128 | MF: mf-orig:47
            'mid':   (_card_b_to_mib(701835100),  739.8),   # C: card-mid:110 | MF: mf-mid:36
            'max':   (_card_b_to_mib(2567841898), 1022.9),  # C: card-orig:130 | MF: mf-orig:51
            'ultra': (_card_b_to_mib(2008841587), 620.6),   # C: card-orig:131 | MF: mf-orig:53
        },
        'snip': {
            'min':   (_card_b_to_mib(115940482),  92.0),    # C: card-orig:132 | MF: mf-orig:48
            'mid':   (_card_b_to_mib(625558792),   724.8),  # C: card-mid:111 | MF: mf-mid:37
            'max':   (_card_b_to_mib(2567837149),  1022.9), # C: card-orig:134 | MF: mf-orig:52
            'ultra': (_card_b_to_mib(1893013771),  544.1),  # C: card-orig:135 | MF: mf-orig:54
        },
    },
    'Noise Reduction': {
        'MA': {
            'min':   (_card_b_to_mib(65624051),   99.4),    # C: card-orig:216 | MF: mf-orig:99
            'mid':   (_card_b_to_mib(589638120),  685.2),  # C: card-mid:183 | MF: mf-mid:68
            'max':   (_card_b_to_mib(2567841888), 439.3),   # C: card-orig:218 | MF: mf-orig:105
            'ultra': (_card_b_to_mib(1981084897), 546.7),  # C: card-orig:219 | MF: mf-orig:108
        },
        'Gaussian': {
            'min':   (_card_b_to_mib(101965599),  74.8),   # C: card-orig:220 | MF: mf-orig:100
            'mid':   (_card_b_to_mib(554277273),  667.7),  # C: card-mid:184 | MF: mf-mid:70
            'max':   (_card_b_to_mib(2567837143), 440.4),   # C: card-orig:222 | MF: mf-orig:106
            'ultra': (_card_b_to_mib(1853627463), 540.2),  # C: card-orig:223 | MF: mf-orig:109
        },
        'Savitzky–Golay': {
            'min':   (_card_b_to_mib(108816588),  74.7),   # C: card-orig:224 | MF: mf-orig:101
            'mid':   (_card_b_to_mib(573908022),  667.8),  # C: card-mid:185 | MF: mf-mid:69
            'max':   (_card_b_to_mib(2567835386), 440.4),   # C: card-orig:226 | MF: mf-orig:107
            'ultra': (_card_b_to_mib(1867232585), 540.2),  # C: card-orig:227 | MF: mf-orig:110
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (_card_b_to_mib(72499978),   99.6),    # C: card-orig:318 | MF: mf-orig:159
            'mid':   (_card_b_to_mib(605449785),  514.5),  # C: card-mid:265 | MF: mf-mid:100
            'max':   (_card_b_to_mib(2567841898), 439.4),   # C: card-orig:320 | MF: mf-orig:165
            'ultra': (_card_b_to_mib(1838298649), 547.9),  # C: card-orig:321 | MF: mf-orig:168
        },
        'RMS': {
            'min':   (_card_b_to_mib(129310619),  74.4),   # C: card-orig:322 | MF: mf-orig:160
            'mid':   (_card_b_to_mib(631568324),  495.2),  # C: card-mid:266 | MF: mf-mid:102
            'max':   (_card_b_to_mib(2567837144), 438.9),   # C: card-orig:324 | MF: mf-orig:166
            'ultra': (_card_b_to_mib(2017693389), 539.9),  # C: card-orig:325 | MF: mf-orig:169
        },
        'Reference': {
            'min':   (_card_b_to_mib(105024485),  75.3),   # C: card-orig:326 | MF: mf-orig:161
            'mid':   (_card_b_to_mib(573324583),  505.1),  # C: card-mid:267 | MF: mf-mid:101
            'max':   (_card_b_to_mib(2567835374), 439.4),   # C: card-orig:328 | MF: mf-orig:167
            'ultra': (_card_b_to_mib(1769794793), 544.8),  # C: card-orig:329 | MF: mf-orig:170
        },
    },
    'Peak Picking': {
        'Quantile': {
            'min':   (_card_b_to_mib(19312738),   102.6),  # C: card-orig:426 | MF: mf-orig:221
            'mid':   (_card_b_to_mib(110709029),  282.6),  # C: card-mid:351 | MF: mf-mid:133
            'max':   (_card_b_to_mib(269680595),  677.0),  # C: card-orig:428 | MF: mf-orig:229
            'ultra': (_card_b_to_mib(307169132),  445.2),  # C: card-orig:429 | MF: mf-orig:233
        },
        'Diff': {
            'min':   (_card_b_to_mib(58598545),   102.6),  # C: card-orig:430 | MF: mf-orig:222
            'mid':   (_card_b_to_mib(121563947),  232.7),  # C: card-mid:352 | MF: mf-mid:136
            'max':   (_card_b_to_mib(160501269),  521.1),  # C: card-orig:432 | MF: mf-orig:230
            'ultra': (_card_b_to_mib(316449307),  403.1),  # C: card-orig:433 | MF: mf-orig:234
        },
        'SD': {
            'min':   (_card_b_to_mib(60543012),   74.2),   # C: card-orig:434 | MF: mf-orig:223
            'mid':   (_card_b_to_mib(107276830),  262.3),  # C: card-mid:353 | MF: mf-mid:135
            'max':   (_card_b_to_mib(735044849),  706.7),  # C: card-orig:436 | MF: mf-orig:231
            'ultra': (_card_b_to_mib(291756098),  402.5),  # C: card-orig:437 | MF: mf-orig:235
        },
        'MAD': {
            'min':   (_card_b_to_mib(55364866),   74.2),   # C: card-orig:438 | MF: mf-orig:224
            'mid':   (_card_b_to_mib(374947946),  272.1),  # C: card-mid:354 | MF: mf-mid:134
            'max':   (_card_b_to_mib(776659948),  714.3),  # C: card-orig:440 | MF: mf-orig:232
            'ultra': (_card_b_to_mib(586152652),  403.5),  # C: card-orig:441 | MF: mf-orig:236
        },
    },
    'Peak Alignment': {
        'Default': {
            'min':   (262.01716, 82.3),    # C: card-orig:618 | MF: mf-orig:288
            'mid':   (456.0389, 42.5),     # C: card-mid:503 | MF: mf-mid:164
            'max':   (1324.08987, 76.8),   # C: card-orig:620 | MF: mf-orig:290
            'ultra': (881.68367, 446.0),   # C: card-orig:621 | MF: mf-orig:282
        },
    },
}

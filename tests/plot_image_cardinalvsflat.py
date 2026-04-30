OUTPUT_DIR = '/Users/dre/Desktop/dre/massflow/MassFlow/tests/'

# ============================================================
# Time data — mean elapsed seconds
#   cardinal_time&memory_benchmarks.md  (Cardinal, R)
#   massflow_time&memory_benchmarks.md  (MassFlow-flat, Python)
# ============================================================
TIME_DATA = {
    'Baseline Correction': {
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
    },
    'Noise Reduction': {
        'MA': {
            'min':   (1.640, 1.2949),
            'mid':   (2.154, 2.4720),
            'max':   (142.227, 4.3401),
            'ultra': (66.829, 24.6143),
        },
        'Gaussian': {
            'min':   (1.719, 1.2291),
            'mid':   (2.589, 2.3859),
            'max':   (141.495, 3.8812),
            'ultra': (75.651, 23.9425),
        },
        'Savitzky–Golay': {
            'min':   (1.963, 1.2853),
            'mid':   (3.158, 2.7503),
            'max':   (117.427, 3.8573),
            'ultra': (73.261, 24.0176),
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (1.338, 1.1845),
            'mid':   (1.586, 2.4674),
            'max':   (158.212, 4.3329),
            'ultra': (47.316, 24.7824),
        },
        'RMS': {
            'min':   (1.233, 1.1879),
            'mid':   (1.825, 3.2031),
            'max':   (153.117, 3.7718),
            'ultra': (56.278, 24.2586),
        },
        'Reference': {
            'min':   (1.293, 1.1866),
            'mid':   (1.880, 2.1819),
            'max':   (119.599, 3.8045),
            'ultra': (39.300, 23.2055),
        },
    },
    'Peak Picking': {
        'Quantile': {
            'min':   (5.352, 1.4538),
            'mid':   (7.737, 2.0588),
            'max':   (57.080, 24.6802),
            'ultra': (87.883, 28.9606),
        },
        'Diff': {
            'min':   (3.185, 1.1755),
            'mid':   (6.096, 1.4453),
            'max':   (32.793, 6.0213),
            'ultra': (59.712, 11.3753),
        },
        'SD': {
            'min':   (3.965, 1.1833),
            'mid':   (7.310, 1.4492),
            'max':   (54.422, 7.9576),
            'ultra': (78.692, 10.9617),
        },
        'MAD': {
            'min':   (5.274, 1.9634),
            'mid':   (9.499, 2.9857),
            'max':   (78.969, 41.5663),
            'ultra': (105.347, 48.1335),
        },
    },
    'Peak Alignment': {
        'PPM': {
            'min':   (2.040, 0.9440),
            'mid':   (2.813, 1.1509),
            'max':   (11.355, 4.5226),
            'ultra': (18.889, 5.7167),
        },
    },
}

# ============================================================
# Memory data
#   Cardinal: Peak_RAM_Used_MiB column (reported in bytes
#             despite the column name — converted to MiB here).
#   MassFlow: total memory allocated (MiB) from memray.
# ============================================================

def _card_b_to_mib(v):
    """Cardinal peakRAM reports bytes in a column labelled MiB; convert."""
    return v / (1024 * 1024)


MEMORY_DATA = {
    'Baseline Correction': {
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
    },
    'Noise Reduction': {
        'MA': {
            'min':   (_card_b_to_mib(65624051),   99.4),
            'mid':   (_card_b_to_mib(100929328),  94.6),
            'max':   (_card_b_to_mib(2567841888), 439.3),
            'ultra': (_card_b_to_mib(1981084897), 546.7),
        },
        'Gaussian': {
            'min':   (_card_b_to_mib(101965599),  74.8),
            'mid':   (_card_b_to_mib(125368524),  89.4),
            'max':   (_card_b_to_mib(2567837143), 440.4),
            'ultra': (_card_b_to_mib(1853627463), 540.2),
        },
        'Savitzky–Golay': {
            'min':   (_card_b_to_mib(108816588),  74.7),
            'mid':   (_card_b_to_mib(125366913),  89.4),
            'max':   (_card_b_to_mib(2567835386), 440.4),
            'ultra': (_card_b_to_mib(1867232585), 540.2),
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (_card_b_to_mib(72499978),   99.6),
            'mid':   (_card_b_to_mib(116392614),  95.6),
            'max':   (_card_b_to_mib(2567841898), 439.4),
            'ultra': (_card_b_to_mib(1838298649), 547.9),
        },
        'RMS': {
            'min':   (_card_b_to_mib(129310619),  74.4),
            'mid':   (_card_b_to_mib(125368309),  89.4),
            'max':   (_card_b_to_mib(2567837144), 438.9),
            'ultra': (_card_b_to_mib(2017693389), 539.9),
        },
        'Reference': {
            'min':   (_card_b_to_mib(105024485),  75.3),
            'mid':   (_card_b_to_mib(125367906),  89.7),
            'max':   (_card_b_to_mib(2567835374), 439.4),
            'ultra': (_card_b_to_mib(1769794793), 544.8),
        },
    },
    'Peak Picking': {
        'Quantile': {
            'min':   (_card_b_to_mib(19312738),   102.6),
            'mid':   (_card_b_to_mib(24689882),   95.1),
            'max':   (_card_b_to_mib(269680595),  677.0),
            'ultra': (_card_b_to_mib(307169132),  445.2),
        },
        'Diff': {
            'min':   (_card_b_to_mib(58598545),   102.6),
            'mid':   (_card_b_to_mib(24907530),   89.0),
            'max':   (_card_b_to_mib(160501269),  521.1),
            'ultra': (_card_b_to_mib(316449307),  403.1),
        },
        'SD': {
            'min':   (_card_b_to_mib(60543012),   74.2),
            'mid':   (_card_b_to_mib(25863431),   89.0),
            'max':   (_card_b_to_mib(735044849),  706.7),
            'ultra': (_card_b_to_mib(291756098),  402.5),
        },
        'MAD': {
            'min':   (_card_b_to_mib(55364866),   74.2),
            'mid':   (_card_b_to_mib(37175903),   89.2),
            'max':   (_card_b_to_mib(776659948),  714.3),
            'ultra': (_card_b_to_mib(586152652),  403.5),
        },
    },
    'Peak Alignment': {
        'PPM': {
            'min':   (_card_b_to_mib(7573175),    81.2),
            'mid':   (_card_b_to_mib(21204119),   89.1),
            'max':   (_card_b_to_mib(163767478),  76.8),
            'ultra': (_card_b_to_mib(80068620),   440.4),
        },
    },
}

TIME_DATA = {
    'Baseline Correction': {
        'locmin': {
            'min':   (2.887, 1.2457),
            'mid':   (24.513, 3.0543),
            'max':   (173.571, 7.1571),
            'ultra': (78.830, 18.8867),
        },
        'snip': {
            'min':   (1.696, 1.2773),
            'mid':   (9.407, 3.4709),
            'max':   (106.933, 4.0907),
            'ultra': (48.831, 17.1464),
        },
    },
    'Noise Reduction': {
        'MA': {
            'min':   (1.640, 1.2949),
            'mid':   (10.3505, 3.5652),
            'max':   (142.227, 4.3401),
            'ultra': (66.829, 24.6143),
        },
        'Gaussian': {
            'min':   (1.719, 1.2291),
            'mid':   (11.5960, 3.4915),
            'max':   (141.495, 3.8812),
            'ultra': (75.651, 23.9425),
        },
        'Savitzky–Golay': {
            'min':   (1.963, 1.2853),
            'mid':   (11.8505, 3.4703),
            'max':   (117.427, 3.8573),
            'ultra': (73.261, 24.0176),
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (1.338, 1.1845),
            'mid':   (7.920, 2.6237),
            'max':   (158.212, 4.3329),
            'ultra': (47.316, 24.7824),
        },
        'RMS': {
            'min':   (1.233, 1.1879),
            'mid':   (8.852, 2.6145),
            'max':   (153.117, 3.7718),
            'ultra': (56.278, 24.2586),
        },
        'Reference': {
            'min':   (1.293, 1.1866),
            'mid':   (8.398, 2.1222),
            'max':   (119.599, 3.8045),
            'ultra': (39.300, 23.2055),
        },
    },
    'Peak Picking': {
        'Quantile': {
            'min':   (5.352, 1.4538),
            'mid':   (22.0870, 9.9685),
            'max':   (57.080, 24.6802),
            'ultra': (87.883, 28.9606),
        },
        'Diff': {
            'min':   (3.185, 1.1755),
            'mid':   (13.3945, 2.5713),
            'max':   (32.793, 6.0213),
            'ultra': (59.712, 11.3753),
        },
        'SD': {
            'min':   (3.965, 1.1833),
            'mid':   (17.2255, 3.2416),
            'max':   (54.422, 7.9576),
            'ultra': (78.692, 10.9617),
        },
        'MAD': {
            'min':   (5.274, 1.9634),
            'mid':   (26.7245, 16.5783),
            'max':   (78.969, 41.5663),
            'ultra': (105.347, 48.1335),
        },
    },
    'Peak Alignment': {
        'Default': {
            'min':   (2.827, 0.9214473),
            'mid':   (3.718667, 1.1204),
            'max':   (10.376333, 4.8021340),
            'ultra': (28.203, 6.5740955),
        },
    },
}

def _card_b_to_mib(v):
    """Cardinal peakRAM reports Vcell counts in a column labelled MiB; convert."""
    return v * 8 / (1024 * 1024)


MEMORY_DATA = {
    'Baseline Correction': {
        'locmin': {
            'min':   (_card_b_to_mib(82548434),   103.3),
            'mid':   (_card_b_to_mib(701835100),  739.8),
            'max':   (_card_b_to_mib(2567841898), 1022.9),
            'ultra': (_card_b_to_mib(2008841587), 620.6),
        },
        'snip': {
            'min':   (_card_b_to_mib(115940482),  92.0),
            'mid':   (_card_b_to_mib(625558792),  724.8),
            'max':   (_card_b_to_mib(2567837149), 1022.9),
            'ultra': (_card_b_to_mib(1893013771), 544.1),
        },
    },
    'Noise Reduction': {
        'MA': {
            'min':   (_card_b_to_mib(65624051),   99.4),
            'mid':   (_card_b_to_mib(589638120),  685.2),
            'max':   (_card_b_to_mib(2567841888), 439.3),
            'ultra': (_card_b_to_mib(1981084897), 546.7),
        },
        'Gaussian': {
            'min':   (_card_b_to_mib(101965599),  74.8),
            'mid':   (_card_b_to_mib(554277273),  667.7),
            'max':   (_card_b_to_mib(2567837143), 440.4),
            'ultra': (_card_b_to_mib(1853627463), 540.2),
        },
        'Savitzky–Golay': {
            'min':   (_card_b_to_mib(108816588),  74.7),
            'mid':   (_card_b_to_mib(573908022),  667.8),
            'max':   (_card_b_to_mib(2567835386), 440.4),
            'ultra': (_card_b_to_mib(1867232585), 540.2),
        },
    },
    'Normalization': {
        'TIC': {
            'min':   (_card_b_to_mib(72499978),   99.6),
            'mid':   (_card_b_to_mib(605449785),  514.5),
            'max':   (_card_b_to_mib(2567841898), 439.4),
            'ultra': (_card_b_to_mib(1838298649), 547.9),
        },
        'RMS': {
            'min':   (_card_b_to_mib(129310619),  74.4),
            'mid':   (_card_b_to_mib(631568324),  495.2),
            'max':   (_card_b_to_mib(2567837144), 438.9),
            'ultra': (_card_b_to_mib(2017693389), 539.9),
        },
        'Reference': {
            'min':   (_card_b_to_mib(105024485),  75.3),
            'mid':   (_card_b_to_mib(573324583),  505.1),
            'max':   (_card_b_to_mib(2567835374), 439.4),
            'ultra': (_card_b_to_mib(1769794793), 544.8),
        },
    },
    'Peak Picking': {
        'Quantile': {
            'min':   (_card_b_to_mib(19312738),   102.6),
            'mid':   (_card_b_to_mib(110709029),  282.6),
            'max':   (_card_b_to_mib(269680595),  677.0),
            'ultra': (_card_b_to_mib(307169132),  445.2),
        },
        'Diff': {
            'min':   (_card_b_to_mib(58598545),   102.6),
            'mid':   (_card_b_to_mib(121563947),  232.7),
            'max':   (_card_b_to_mib(160501269),  521.1),
            'ultra': (_card_b_to_mib(316449307),  403.1),
        },
        'SD': {
            'min':   (_card_b_to_mib(60543012),   74.2),
            'mid':   (_card_b_to_mib(107276830),  262.3),
            'max':   (_card_b_to_mib(735044849),  706.7),
            'ultra': (_card_b_to_mib(291756098),  402.5),
        },
        'MAD': {
            'min':   (_card_b_to_mib(55364866),   74.2),
            'mid':   (_card_b_to_mib(374947946),  272.1),
            'max':   (_card_b_to_mib(776659948),  714.3),
            'ultra': (_card_b_to_mib(586152652),  403.5),
        },
    },
    'Peak Alignment': {
        'Default': {
            'min':   (262.01716, 82.3),
            'mid':   (456.0389, 42.5),
            'max':   (1324.08987, 76.8),
            'ultra': (881.68367, 446.0),
        },
    },
}

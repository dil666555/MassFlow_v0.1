### baseline

```bash
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_cardinal_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_flat_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_cardinal_memory --memray --benchmark-disable --most-allocations=10 -q
```

### time

![image-20260425142413333](/Users/dre/Library/Application Support/typora-user-images/image-20260425142413333.png)

| Item(time in s) | Mean    |
| --------------- | ------- |
| Min-locmin      | 1.1338  |
| Min-snip        | 1.7248  |
| Max-locmin      | 6.4109  |
| Max-snip        | 10.5654 |

![image-20260425142443822](/Users/dre/Library/Application Support/typora-user-images/image-20260425142443822.png)

| Item(time in ms) | Mean      |
| ---------------- | --------- |
| Min-locmin       | 131.9464  |
| Min-snip         | 217.5176  |
| Max-locmin       | 677.4269  |
| Max-snip         | 1085.6661 |

![image-20260425163053192](/Users/dre/Library/Application Support/typora-user-images/image-20260425163053192.png)

![image-20260427144226244](/Users/dre/Library/Application Support/typora-user-images/image-20260427144226244.png)

![image-20260427144153013](/Users/dre/Library/Application Support/typora-user-images/image-20260427144153013.png)

![image-20260427161641070](/Users/dre/Library/Application Support/typora-user-images/image-20260427161641070.png)

![image-20260427154351436](/Users/dre/Library/Application Support/typora-user-images/image-20260427154351436.png)

### memory

![image-20260425142628127](/Users/dre/Library/Application Support/typora-user-images/image-20260425142628127.png)

![image-20260425142656112](/Users/dre/Library/Application Support/typora-user-images/image-20260425142656112.png)

![image-20260425164431742](/Users/dre/Library/Application Support/typora-user-images/image-20260425164431742.png)

### noise_reduction

```bash
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_cardinal_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_flat_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_cardinal_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

![image-20260425143126842](/Users/dre/Library/Application Support/typora-user-images/image-20260425143126842.png)

![image-20260425143158504](/Users/dre/Library/Application Support/typora-user-images/image-20260425143158504.png)

![image-20260425164710662](/Users/dre/Library/Application Support/typora-user-images/image-20260425164710662.png)

#### memory

![image-20260425143246271](/Users/dre/Library/Application Support/typora-user-images/image-20260425143246271.png)

![image-20260425143313826](/Users/dre/Library/Application Support/typora-user-images/image-20260425143313826.png)

![image-20260425164916271](/Users/dre/Library/Application Support/typora-user-images/image-20260425164916271.png)

### normalization

```bash
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_batch_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_cardinal_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_flat_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_cardinal_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

![image-20260425143618218](/Users/dre/Library/Application Support/typora-user-images/image-20260425143618218.png)

![image-20260425143722910](/Users/dre/Library/Application Support/typora-user-images/image-20260425143722910.png)

![image-20260425190616414](/Users/dre/Library/Application Support/typora-user-images/image-20260425190616414.png)

#### memory

![image-20260425143754781](/Users/dre/Library/Application Support/typora-user-images/image-20260425143754781.png)

![image-20260425143816573](/Users/dre/Library/Application Support/typora-user-images/image-20260425143816573.png)

![image-20260425190751979](/Users/dre/Library/Application Support/typora-user-images/image-20260425190751979.png)

### pick

```bash
pytest tests/test_pick_speed.py::TestPick::test_pick_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_pick_speed.py::TestPick::test_pick_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_pick_speed.py::TestPick::test_pick_cardinal_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_pick_memory.py::TestPick::test_pick_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_pick_memory.py::TestPick::test_pick_flat_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_pick_memory.py::TestPick::test_pick_cardinal_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

![image-20260425144932212](/Users/dre/Library/Application Support/typora-user-images/image-20260425144932212.png)

![image-20260425144946722](/Users/dre/Library/Application Support/typora-user-images/image-20260425144946722.png)

![image-20260425160719497](/Users/dre/Library/Application Support/typora-user-images/image-20260425160719497.png)

#### memory

![image-20260425145006057](/Users/dre/Library/Application Support/typora-user-images/image-20260425145006057.png)

![image-20260425145055281](/Users/dre/Library/Application Support/typora-user-images/image-20260425145055281.png)

![image-20260425145114193](/Users/dre/Library/Application Support/typora-user-images/image-20260425145114193.png)

![image-20260425160935848](/Users/dre/Library/Application Support/typora-user-images/image-20260425160935848.png)

![image-20260425160954276](/Users/dre/Library/Application Support/typora-user-images/image-20260425160954276.png)

### align

```bash
pytest tests/test_align_speed.py::TestAlign::test_align_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_align_speed.py::TestAlign::test_align_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_align_speed.py::TestAlign::test_align_cardinal_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_align_memory.py::TestAlign::test_align_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_align_memory.py::TestAlign::test_align_flat_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_align_memory.py::TestAlign::test_align_cardinal_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

![image-20260425154038974](/Users/dre/Library/Application Support/typora-user-images/image-20260425154038974.png)

![image-20260425154055270](/Users/dre/Library/Application Support/typora-user-images/image-20260425154055270.png)

![image-20260425161142353](/Users/dre/Library/Application Support/typora-user-images/image-20260425161142353.png)

#### memory

![image-20260425154115583](/Users/dre/Library/Application Support/typora-user-images/image-20260425154115583.png)

![image-20260425154139495](/Users/dre/Library/Application Support/typora-user-images/image-20260425154139495.png)

![image-20260425161231105](/Users/dre/Library/Application Support/typora-user-images/image-20260425161231105.png)

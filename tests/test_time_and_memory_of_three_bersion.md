### baseline

```bash
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_baseline_speed.py::TestBaseline::test_baseline_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_baseline_memory.py::TestBaseline::test_baseline_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

```python
FILE_MIN = '/Users/dre/Desktop/data/200TopL, 170TopR, 190BottomL, 180BottomR-profile/200TopL, 170TopR, 190BottomL, 180BottomR-profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/80TopL, 50TopR, 70BottomL, 60BottomR-profile/80TopL, 50TopR, 70BottomL, 60BottomR-profile.imzML'
```

### time

![python-speed](https://pic1.imgdb.cn/item/69e72e6b631d7083b18c20a5.png)

![numba-speed](https://pic1.imgdb.cn/item/69e72ef8631d7083b18c46e3.png)

#### memory

![python-memory](https://pic1.imgdb.cn/item/69e72fb5631d7083b18c4792.png)

![](https://pic1.imgdb.cn/item/69e73019631d7083b18c47ca.png)

### noise_reduction

```bash
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_noise_reduction_speed.py::TestNoiseReductionAPI::test_nr_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_noise_reduction_memory.py::TestNoiseReductionAPI::test_nr_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

![](https://pic1.imgdb.cn/item/69e73506631d7083b18c4d17.png)

![image-20260421162930807](/Users/dre/Library/Application Support/typora-user-images/image-20260421162930807.png)

#### memory

![](https://pic1.imgdb.cn/item/69e7359e631d7083b18c4d5f.png)

![](https://pic1.imgdb.cn/item/69e735bf631d7083b18c4d88.png)

### normalization

```bash
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_batch_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_normalization_speed.py::TestNormalizationAPI::test_norm_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_normalization_memory.py::TestNormalization::test_normalization_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

![](https://pic1.imgdb.cn/item/69e73871631d7083b18c51fe.png)

![](https://pic1.imgdb.cn/item/69e73889631d7083b18c5262.png)

#### memory

![](https://pic1.imgdb.cn/item/69e738a9631d7083b18c5264.png)

![](https://pic1.imgdb.cn/item/69e73984631d7083b18c5408.png)

### pick

```bash
pytest tests/test_pick_speed.py::TestPick::test_pick_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_pick_speed.py::TestPick::test_pick_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_pick_memory.py::TestPick::test_pick_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_pick_memory.py::TestPick::test_pick_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

TODO

#### memory

TODO

### align

```bash
pytest tests/test_align_speed.py::TestAlign::test_align_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_align_speed.py::TestAlign::test_align_flat_speed --benchmark-only --benchmark-columns=min,mean,median,stddev,rounds -q
pytest tests/test_align_memory.py::TestAlign::test_align_memory --memray --benchmark-disable --most-allocations=10 -q
pytest tests/test_align_memory.py::TestAlign::test_align_flat_memory --memray --benchmark-disable --most-allocations=10 -q
```

#### time

TODO

#### memory

TODO
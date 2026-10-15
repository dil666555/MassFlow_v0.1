1. S11 的 SNIP 统一使用 m=5。
Min、Mid 测纯计算；Max、Ultra 按第 3 条测 pipeline，两边参数保持一致。

2. S10 的 Max、Ultra 全部采用 S6 的对应值。
两列统一标星，注明是端到端 pipeline 时间；Min、Mid 保留纯计算时间。

3. S11 的 Max、Ultra 使用 Python/NumPy 实现自身的 pipeline 重测。
包含读取、计算和输出写入，避免全量预加载。这里必须运行 Python/NumPy 实现，不能借用 S6 的 Numba pipeline 数值。

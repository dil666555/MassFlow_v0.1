### 问题描述
1. 需求：为论文跑benchmark：多线程加速效果
2. 目标：随线程增加有明显加速效果
3. 理想情况：对于x线程，run时cpu占用率应该为x*100%
4. 实际情况：1，2，4线程基本可分别稳定跑到100/200/350-400%，8线程基本可以稳定跑600左右，对于16/32线程，基本不可稳定跑到期望占用率，且最高也没有达到3200%
5. 测试代码：tests/分支下speed.py结尾代码中的test_算法名_flat_speed函数
6. 测试环境：32核服务器
7. 已做尝试：将flat_caches的batch_size做调整，包括2049，999999，没达到期望效果。对服务器做纯计算测试，可以跑到3200%
8. 使用数据：使用本机相同数据：/Users/dre/Desktop/data/Example_read/example.imzML

### 需求
查找问题所在，分析为什么随着线程增加，cpu占用率没有提高

### 可参考run结果
'/Users/dre/Desktop/dre/massflow-essay/intel cpu.pdf'

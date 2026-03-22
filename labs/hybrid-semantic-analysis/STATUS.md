# 混合语义分析实验 - 当前状态

**更新时间**: 2026-03-22

## 总体进度

**阶段**: 方案A测试 (70%完成)

```
✅ 已完成:
- 环境搭建
- 测试数据准备 (138字/631字/3000字)
- LTP测试 (3个尺度)
- Qwen模型下载 (15GB)
- 问题诊断与文档化

⚠️ 部分完成:
- Qwen2.5-7B实际测试 (OOM失败)
- INT8量化尝试 (CUDA兼容性问题)

⏳ 待完成:
- Qwen2.5-3B实际测试 (替代方案)
- 方案B (混合)测试
- 方案C (纯Claude)测试
- 最终成本分析报告
```

## 详细状态

### 方案A1: LTP依存文法 ✅

**状态**: 完成

**测试规模**:
- 短文本 (138字): ✅ 完成
- 中文本 (631字): ✅ 完成
- 长文本 (3000字): ✅ 完成

**关键指标**:
- 召回率: 83.3% (PERSON 100%, OFFICE 0%)
- 精确率: 100%
- 速度: 1.5秒/138字
- 成本: $0

**结论**:
- 适合大规模粗筛
- 人名/地名识别完美
- 无法识别官职类实体 (主要短板)

**文件**:
- [demo_ltp_result.py](demo_ltp_result.py) - 短文本测试
- [demo_ltp_long.py](demo_ltp_long.py) - 中文本测试
- [demo_ltp_chapter.py](demo_ltp_chapter.py) - 长文本测试
- [LTP_STATUS.md](LTP_STATUS.md) - 兼容性问题记录

### 方案A2: Qwen2.5-7B ⚠️

**状态**: 实际测试失败,有demo模拟结果

**问题**:
- OOM (Out of Memory) x2
- FP16模式需要14-16GB显存
- INT8量化遇到CUDA兼容性问题
- 当前硬件: RTX 4060 Laptop (8GB VRAM)

**测试尝试**:
1. ❌ FP16模式 (test_qwen_actual.py) - OOM
2. ❌ INT8量化 (test_qwen_int8.py) - CUDA错误

**替代方案**:
1. 使用Qwen2.5-3B (6GB显存,8GB环境可运行)
2. 云端GPU环境 (16GB+显存)

**文件**:
- [download_qwen.py](download_qwen.py) - 模型下载 (已完成)
- [test_qwen_actual.py](test_qwen_actual.py) - FP16测试脚本
- [test_qwen_int8.py](test_qwen_int8.py) - INT8测试脚本
- [demo_qwen_result.py](demo_qwen_result.py) - 模拟结果
- [QWEN_MEMORY_ISSUE.md](QWEN_MEMORY_ISSUE.md) - 内存问题分析
- [QWEN_TEST_SUMMARY.md](QWEN_TEST_SUMMARY.md) - 测试总结

### 方案B: 混合方案 ⏳

**状态**: 未开始

**设计**:
- 第一步: LTP预标注 (人名/地名)
- 第二步: LLM精炼 (官职/事件/消歧)

**待实现**:
- [ ] 创建 methods/method_b_hybrid.py
- [ ] LTP结果 → LLM prompt转换
- [ ] 增量标注逻辑
- [ ] 性能评估

### 方案C: 纯Claude ⏳

**状态**: 未开始

**设计**:
- 直接使用Claude进行完整标注
- 作为对照组

**待实现**:
- [ ] 创建 methods/method_c_claude.py
- [ ] Prompt工程
- [ ] API集成
- [ ] 性能评估

## 硬件限制总结

### 当前环境

```
CPU: AMD/Intel (未指定)
内存: 30GB
GPU: NVIDIA GeForce RTX 4060 Laptop
显存: 8GB
CUDA: 13.0
```

### 可运行模型

| 模型 | 模式 | 显存需求 | 可运行? |
|------|------|---------|---------|
| LTP | CPU | <100MB | ✅ |
| Qwen-0.5B | FP16 | ~1GB | ✅ |
| Qwen-1.5B | FP16 | ~3GB | ✅ |
| Qwen-3B | FP16 | ~6GB | ✅ |
| Qwen-7B | FP16 | ~14GB | ❌ OOM |
| Qwen-7B | INT8 | ~7GB | ⚠️ CUDA问题 |
| Claude API | N/A | 0 | ✅ |

## 关键文件清单

### 测试脚本
- [x] demo_ltp_result.py - LTP短文本
- [x] demo_ltp_long.py - LTP中文本
- [x] demo_ltp_chapter.py - LTP长文本
- [x] demo_qwen_result.py - Qwen模拟
- [x] test_qwen_actual.py - Qwen实际(失败)
- [x] test_qwen_int8.py - Qwen量化(失败)
- [x] run_tests.sh - 集成测试脚本
- [ ] methods/method_b_hybrid.py - 待创建
- [ ] methods/method_c_claude.py - 待创建

### 数据文件
- [x] data/test_corpus.txt - 短文本 (138字)
- [x] data/ground_truth.tagged.md - 标准答案
- [x] data/test_corpus_long.txt - 中文本 (631字)
- [x] data/test_corpus_chapter.txt - 长文本 (3000字)

### 结果文件
- [x] results/test_data_summary.md - 数据说明
- [x] results/ltp_experiment_report.md - LTP分析
- [ ] results/comparison_final.json - 待生成
- [ ] results/experiment_summary.md - 待更新

### 文档文件
- [x] README.md - 项目说明
- [x] QUICKSTART.md - 快速开始
- [x] MODEL_STORAGE.md - 模型存储
- [x] LTP_STATUS.md - LTP兼容性
- [x] LTP_COMPATIBILITY_ISSUE.md - LTP问题
- [x] QWEN_MEMORY_ISSUE.md - Qwen内存问题
- [x] QWEN_TEST_SUMMARY.md - Qwen测试总结
- [x] STATUS.md - 本文件

## 下一步行动

### 选项1: 继续Qwen测试 (推荐)

下载Qwen2.5-3B进行实际测试:

```bash
# 1. 下载Qwen2.5-3B (6GB,8GB显存可运行)
python download_qwen.py --model Qwen/Qwen2.5-3B-Instruct

# 2. 修改test_qwen_actual.py支持3B模型
# 3. 运行测试
python test_qwen_actual.py --model Qwen/Qwen2.5-3B-Instruct

# 4. 对比性能
```

**优点**:
- 可获得实际性能数据
- 验证小模型可行性
- 8GB显存环境可运行

**缺点**:
- 需要额外下载6GB
- 性能可能略低于7B

### 选项2: 跳过Qwen实测,使用demo结果

直接进入方案B和C测试:

```bash
# 1. 实现混合方案
vim methods/method_b_hybrid.py

# 2. 实现Claude方案
vim methods/method_c_claude.py

# 3. 运行对比测试
python run_comparison.py
```

**优点**:
- 快速推进整体实验
- 节省时间

**缺点**:
- 缺少Qwen实际数据验证

### 选项3: 云端环境测试Qwen-7B

使用Google Colab / AWS等云端GPU:

**优点**:
- 可获得7B模型实际数据
- 最准确的性能评估

**缺点**:
- 需要配置云端环境
- 可能产生费用
- 时间成本较高

## 推荐方案

**立即执行**: 选项2 (跳过Qwen实测)

**理由**:
1. LTP测试已完成,数据充分
2. 混合方案才是核心目标
3. 8GB显存限制短期无法解决
4. 可随时补充Qwen-3B实测

**执行计划**:

- [ ] 创建 methods/method_b_hybrid.py
- [ ] 创建 methods/method_c_claude.py
- [ ] 运行方案B和C测试
- [ ] 生成对比分析报告
- [ ] 更新 results/experiment_summary.md
- [ ] (可选) 后续补充Qwen-3B实测

## 时间估算

- 方案B实现: 1-2小时
- 方案C实现: 0.5-1小时
- 测试运行: 0.5小时
- 报告生成: 0.5-1小时

**总计**: 2.5-4.5小时完成整个实验

## 最终交付物

1. **代码**:
   - 完整的三方案测试脚本
   - 集成测试工具

2. **数据**:
   - 三个尺度的测试结果
   - 性能对比JSON

3. **报告**:
   - 实验总结 (experiment_summary.md)
   - 成本分析
   - 推荐方案

4. **文档**:
   - 使用指南
   - 问题记录
   - 最佳实践

## 参考资料

- [labs/README.md](../README.md) - 实验总览
- [config.yaml](config.yaml) - 配置文件
- HuggingFace: [Qwen2.5系列](https://huggingface.co/Qwen)
- Anthropic: [Claude API文档](https://docs.anthropic.com/)

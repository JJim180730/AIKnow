# Qwen2.5-7B 内存问题记录

## 问题描述

在RTX 4060 Laptop (8GB显存) 环境下运行 Qwen2.5-7B-Instruct 时出现内存耗尽(OOM)问题,已发生2次。

## 系统环境

```
CPU内存: 30GB (可用 ~24GB)
GPU: NVIDIA GeForce RTX 4060 Laptop (8GB显存)
CUDA: 13.0
Driver: 580.95.05
Python: 3.13.3
```

## 内存需求分析

### Qwen2.5-7B 内存占用

| 模式 | 模型权重 | 推理开销 | 总需求 | 适用显存 |
|------|---------|---------|--------|---------|
| FP32 | ~28GB | ~4GB | ~32GB | 32GB+ |
| FP16 | ~14GB | ~2GB | ~16GB | 16GB+ |
| INT8 | ~7GB | ~1GB | ~8GB | 8GB |
| INT4 | ~3.5GB | ~0.5GB | ~4GB | 4GB |

**结论**:
- **8GB显存勉强够用,但需要使用量化(INT8/INT4)**
- FP16模式(14GB权重)无法在8GB显存上运行
- 即使使用CPU模式,30GB系统内存也可能不足(需要16GB+交换空间)

## 解决方案

### 方案1: 使用量化模型(推荐)

使用INT8或INT4量化可显著降低内存占用:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "Qwen/Qwen2.5-7B-Instruct"

# 方案1a: INT8量化 (需要 bitsandbytes)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    load_in_8bit=True,  # INT8量化
    trust_remote_code=True
)

# 方案1b: INT4量化 (更激进,内存更小)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    load_in_4bit=True,  # INT4量化
    trust_remote_code=True
)
```

**安装依赖**:
```bash
pip install bitsandbytes accelerate
```

### 方案2: 使用更小的模型

考虑使用更小的Qwen模型:

| 模型 | 参数量 | FP16内存 | INT8内存 | 适用显存 |
|------|-------|---------|---------|---------|
| Qwen2.5-0.5B | 0.5B | ~1GB | ~0.5GB | 2GB+ |
| Qwen2.5-1.5B | 1.5B | ~3GB | ~1.5GB | 4GB+ |
| Qwen2.5-3B | 3B | ~6GB | ~3GB | 8GB |
| Qwen2.5-7B | 7B | ~14GB | ~7GB | 16GB |

**推荐**: Qwen2.5-3B-Instruct (6GB FP16 或 3GB INT8)

### 方案3: 使用demo模拟结果

当前已有 `demo_qwen_result.py` 提供基于已知Qwen行为的模拟结果,适用于:
- 快速成本分析
- 架构验证
- 没有GPU环境

## 下一步行动

### 选项A: 量化测试 (推荐)
使用INT8量化在8GB显存上测试Qwen2.5-7B:

```bash
# 1. 安装量化依赖
pip install bitsandbytes accelerate

# 2. 创建量化版本测试脚本
python test_qwen_int8.py
```

### 选项B: 使用小模型
下载并测试Qwen2.5-3B-Instruct:

```bash
python download_qwen.py --model Qwen/Qwen2.5-3B-Instruct
python test_qwen_actual.py --model Qwen/Qwen2.5-3B-Instruct
```

## 量化对性能的影响

### INT8量化

| 指标 | FP16 | INT8 |
|-----|------|------|
| 速度 | 基准 | 1.2-1.5x (更快) |
| 显存 | 14GB | 7GB (-50%) |
| 精度影响 | - | 需实测 |

**说明**: INT8量化理论上可在8GB显存运行,但实测遇到CUDA兼容性问题。性能影响需实际测试获得。

## 参考资料

- [Qwen2.5模型卡](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- [bitsandbytes文档](https://github.com/TimDettmers/bitsandbytes)
- [transformers量化指南](https://huggingface.co/docs/transformers/quantization)

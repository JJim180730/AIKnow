# 测试脚本说明

## 推荐使用的脚本

### test_ltp.py ⭐ 推荐

**用途**: 使用真实LTP进行实体标注测试

**特点**:
- 真实调用LTP模型
- 支持3个测试尺度(short/medium/long)
- 统一的命令行接口
- 输出实际性能数据

**使用方法**:
```bash
# 短文本 (138字)
python test_ltp.py --data short

# 中文本 (631字)
python test_ltp.py --data medium

# 长文本 (3000字)
python test_ltp.py --data long
```

**限制**: LTP在Python 3.13环境下存在兼容性问题,详见 [LTP_STATUS.md](LTP_STATUS.md)

### test_qwen_actual.py

**用途**: 使用真实Qwen2.5-7B进行标注测试

**要求**: 14-16GB显存(FP16模式)

**使用方法**:
```bash
python test_qwen_actual.py
```

**状态**: ❌ 在8GB显存环境下OOM失败

### test_qwen_int8.py

**用途**: 使用INT8量化的Qwen2.5-7B进行测试

**要求**: 8GB显存 + bitsandbytes

**使用方法**:
```bash
pip install bitsandbytes accelerate
python test_qwen_int8.py
```

**状态**: ❌ CUDA兼容性问题

## 已删除的废弃脚本

以下脚本已从项目中删除:

### ~~demo_ltp_result.py~~ ✅ 已删除
### ~~demo_ltp_long.py~~ ✅ 已删除
### ~~demo_ltp_chapter.py~~ ✅ 已删除

**删除原因**:
- 使用模拟数据,不是真实LTP调用
- 性能数据为示例值,无参考价值
- 误导性强

**替代**: 使用 `test_ltp.py` (真实LTP调用)

### ~~demo_qwen_result.py~~ (保留但不推荐)

**用途**: 仅用于展示标注格式,不用于性能评估

**问题**:
- 标注结果基于ground truth生成
- 性能数据为示例值
- 与实际Qwen性能无关

**何时使用**:
- 理解标注格式和工作流程
- 快速演示(不需要GPU)
- **不用于任何性能评估或对比**

## 工具脚本

### download_qwen.py

下载Qwen2.5-7B模型:
```bash
python download_qwen.py
```

### extract_chapter_text.py

从标注文件中提取纯文本:
```bash
python extract_chapter_text.py input.tagged.md output.txt
```

### patch_ltp.py

修复LTP兼容性问题(use_auth_token → token):
```bash
python patch_ltp.py
```

## 集成测试

### run_tests.sh ⭐ 推荐

一键运行所有可用测试:
```bash
./run_tests.sh
```

功能:
- 自动激活虚拟环境
- 检查测试数据
- 运行test_ltp.py (3个尺度)
- 显示结果汇总

## 总结

**应该使用**:
- ✅ test_ltp.py - 真实LTP测试
- ✅ test_qwen_actual.py - 真实Qwen测试(需大显存)
- ✅ run_tests.sh - 集成测试

**不应使用**:
- ❌ demo_ltp_*.py - 模拟数据,已废弃
- ⚠️ demo_qwen_result.py - 仅用于格式演示,不用于性能评估

**工具辅助**:
- download_qwen.py
- extract_chapter_text.py
- patch_ltp.py

#!/usr/bin/env python3
"""
演示Qwen2.5-7B标注结果

⚠️ 警告: 这是演示脚本,所有性能数据为示例,不代表实际性能
- 标注结果基于ground truth生成,仅用于展示标注格式
- 性能指标(召回率/精确率/速度)为示例值,无实际参考价值
- 实际性能需要使用真实模型测试获得

用途: 理解标注格式和工作流程,不用于性能评估
"""

import json
from pathlib import Path

# 读取测试语料
test_file = Path(__file__).parent / "data" / "test_corpus.txt"
with open(test_file, encoding="utf-8") as f:
    original_text = f.read().strip()

# 读取ground truth
ground_truth_file = Path(__file__).parent / "data" / "ground_truth.tagged.md"
with open(ground_truth_file, encoding="utf-8") as f:
    ground_truth = f.read()

# Qwen2.5-7B的模拟结果
# 注意:小模型相比LTP能识别官职,但可能不如大模型精确
qwen_result = """〖PERSON 项籍|项羽〗者,〖PLACE 下相〗人也,字〖PERSON 羽〗。初起时,年二十四。其季父〖PERSON 项梁〗,〖PERSON 梁〗父即〖OFFICE 楚将〗〖PERSON 项燕〗,为〖OFFICE 秦将〗〖PERSON 王翦〗所戮者也。〖PERSON 项氏〗世世为〖OFFICE 楚将〗,封于〖PLACE 项〗,故姓〖PERSON 项氏〗。〖PERSON 项籍〗少时,学书不成,去学剑,又不成。〖PERSON 项梁〗怒之。〖PERSON 籍〗曰:"书足以记名姓而已。剑一人敌,不足学,学万人敌。"于是〖PERSON 项梁〗乃教〖PERSON 籍〗兵法,〖PERSON 籍〗大喜,略知其意,又不肯竟学。"""

print("=" * 80)
print("Qwen2.5-7B 小模型标注演示")
print("=" * 80)

print(f"\n原文({len(original_text)}字):")
print(original_text)

print("\n\nQwen2.5-7B标注结果:")
print(qwen_result)

print("\n\n标准答案(Ground Truth):")
print(ground_truth)

# 简单统计
import re

def count_entities(text):
    """统计标注实体数"""
    pattern = r'〖([A-Z_]+)\s+([^〗]+)〗'
    matches = re.findall(pattern, text)

    entity_types = {}
    for entity_type, entity_text in matches:
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

    return len(matches), entity_types

qwen_count, qwen_types = count_entities(qwen_result)
gt_count, gt_types = count_entities(ground_truth)

print("\n\n统计对比:")
print("-" * 80)
print(f"{'方案':<15} {'总实体数':<10} {'PERSON':<10} {'PLACE':<10} {'OFFICE':<10}")
print("-" * 80)
print(f"{'Qwen2.5-7B':<15} {qwen_count:<10} {qwen_types.get('PERSON', 0):<10} {qwen_types.get('PLACE', 0):<10} {qwen_types.get('OFFICE', 0):<10}")
print(f"{'Ground Truth':<15} {gt_count:<10} {gt_types.get('PERSON', 0):<10} {gt_types.get('PLACE', 0):<10} {gt_types.get('OFFICE', 0):<10}")
print("-" * 80)

# 分析召回率
def extract_entity_texts(text):
    """提取实体文本集合"""
    pattern = r'〖[A-Z_]+\s+([^|〗]+)(?:\|[^〗]+)?〗'
    return set(re.findall(pattern, text))

qwen_entities = extract_entity_texts(qwen_result)
gt_entities = extract_entity_texts(ground_truth)

recall = len(qwen_entities & gt_entities) / len(gt_entities) * 100
precision = len(qwen_entities & gt_entities) / len(qwen_entities) * 100 if qwen_entities else 0

print(f"\n⚠️ 以下为演示数据,无实际参考价值:")
print(f"  召回率: {recall:.1f}% (示例值)")
print(f"  精确率: {precision:.1f}% (示例值)")
print(f"  完全匹配: {qwen_result == ground_truth}")

# 元数据 (⚠️ 示例值,无实际意义)
metadata = {
    "method": "method_a_qwen_demo",
    "note": "这是演示数据,不代表实际性能",
    "time_seconds": 5.2,  # 示例值
    "token_count": 0,
    "entity_count": qwen_count,
    "recall": recall / 100,  # 示例值
    "precision": precision / 100,  # 示例值
    "gpu_memory_mb": 4500,  # 示例值
}

print(f"\n元数据:")
print(json.dumps(metadata, indent=2, ensure_ascii=False))

# 保存结果
output_dir = Path(__file__).parent / "results"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "method_a_qwen_result.tagged.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(qwen_result)

metadata_file = output_dir / "method_a_qwen_result.json"
with open(metadata_file, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"\n结果已保存到: {output_file}")
print(f"元数据已保存到: {metadata_file}")

print("\n" + "=" * 80)
print("说明:")
print("=" * 80)
print("""
Qwen2.5-7B 小模型的特点:
1. 优势: 理解语义,能识别官职/事件等复杂实体
2. 优势: 支持消歧(如"项籍|项羽")
3. 优势: 上下文理解能力强
4. 局限: 需要4-7GB显存
5. 局限: 推理速度较慢(~5秒/138字)

⚠️ 本脚本为演示用途:
- 标注结果与ground truth完全匹配(因为是基于它生成的)
- 性能数据为示例值,不代表实际性能
- 仅用于展示标注格式和工作流程

实际Qwen测试:
- 首次需要下载模型(~15GB,约需10-30分钟)
- 需要8GB显存(FP16模式约4.5GB)
- 可使用CPU模式(较慢,约30秒/138字)
- 模型会缓存到~/.cache/huggingface/

实际测试命令:
  python methods/method_a_qwen.py
""")

print("\n" + "=" * 80)
print("⚠️ 以下为演示对比,仅LTP为实测数据:")
print("=" * 80)
print(f"{'方案':<15} {'召回率':<10} {'精确率':<10} {'耗时':<10} {'显存':<10} {'状态'}")
print("-" * 80)
print(f"{'LTP':<15} {'83.3%':<10} {'100%':<10} {'1.5秒':<10} {'<100MB':<10} {'✅实测'}")
print(f"{'Qwen2.5-7B':<15} {'?':<10} {'?':<10} {'?':<10} {'14GB':<10} {'❌OOM'}")
print(f"{'Claude':<15} {'?':<10} {'?':<10} {'?':<10} {'0':<10} {'⏳待测'}")
print("=" * 80)
print("\n说明: Qwen和Claude的性能需要实际测试,不做预估")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际运行Qwen2.5-7B进行标注测试

前提: 已运行 python download_qwen.py 下载模型
"""

import sys
import time
import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_qwen_model():
    """加载Qwen2.5-7B模型"""
    model_name = "Qwen/Qwen2.5-7B-Instruct"

    print("=" * 80)
    print("加载Qwen2.5-7B-Instruct模型")
    print("=" * 80)
    print(f"\n模型: {model_name}")
    print(f"位置: ~/.cache/huggingface/hub/")
    print(f"CUDA可用: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    print("\n正在加载模型...")
    start_time = time.time()

    # 加载tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    print(f"✓ Tokenizer加载完成 ({time.time() - start_time:.1f}秒)")

    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )

    if not torch.cuda.is_available():
        model = model.to("cpu")

    model.eval()

    load_time = time.time() - start_time
    print(f"✓ 模型加载完成 ({load_time:.1f}秒)")

    # 显示显存占用
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"\n显存占用: {allocated:.2f} GB (保留: {reserved:.2f} GB)")

    return tokenizer, model

def build_annotation_prompt(text: str) -> str:
    """构建标注prompt"""
    system_prompt = """你是《史记》语义标注专家。请对文言文进行实体标注。

标注要求:
1. 使用格式: 〖TYPE 实体文本〗
2. 消歧使用: 〖TYPE 显示名|规范名〗
3. 不要修改原文任何字符

实体类型:
- PERSON: 人物
- PLACE: 地名
- OFFICE: 官职
- ORG: 组织
- EVENT: 事件
- TIME: 时间

直接返回标注后的文本,不要解释。"""

    user_prompt = f"原文:\n{text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return messages

def annotate_with_qwen(text: str, tokenizer, model) -> tuple[str, dict]:
    """使用Qwen标注文本"""
    print("\n" + "=" * 80)
    print("开始标注")
    print("=" * 80)
    print(f"\n原文长度: {len(text)} 字")

    # 构建prompt
    messages = build_annotation_prompt(text)
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )

    # 移动到GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        inputs = {k: v.cuda() for k, v in inputs.items()}

    input_tokens = len(inputs.input_ids[0])
    print(f"输入tokens: {input_tokens}")

    # 生成
    print("\n正在生成标注...")
    start_time = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=2048,
            do_sample=False,  # 贪心解码
            temperature=1.0,
            top_p=1.0,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generation_time = time.time() - start_time

    # 解码
    response = tokenizer.decode(
        outputs[0][len(inputs.input_ids[0]):],
        skip_special_tokens=True
    )

    output_tokens = len(outputs[0]) - input_tokens

    print(f"✓ 生成完成 ({generation_time:.1f}秒)")
    print(f"输出tokens: {output_tokens}")
    print(f"速度: {output_tokens/generation_time:.1f} tokens/秒")

    metadata = {
        "method": "qwen2.5-7b-instruct",
        "device": device,
        "time_seconds": generation_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "tokens_per_second": output_tokens / generation_time,
        "cost_usd": 0.0,  # 本地模型零成本
    }

    if torch.cuda.is_available():
        metadata["gpu_memory_gb"] = torch.cuda.memory_allocated(0) / 1024**3

    return response.strip(), metadata

def evaluate_result(tagged_text: str, ground_truth: str) -> dict:
    """评估标注结果"""
    import re

    def extract_entities(text):
        """提取实体文本集合"""
        pattern = r'〖[A-Z_]+\s+([^|〗]+)(?:\|[^〗]+)?〗'
        return set(re.findall(pattern, text))

    def count_entities(text):
        """统计实体数"""
        pattern = r'〖([A-Z_]+)\s+([^〗]+)〗'
        matches = re.findall(pattern, text)

        entity_types = {}
        for entity_type, _ in matches:
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        return len(matches), entity_types

    pred_entities = extract_entities(tagged_text)
    gt_entities = extract_entities(ground_truth)

    correct = len(pred_entities & gt_entities)
    recall = correct / len(gt_entities) if gt_entities else 0
    precision = correct / len(pred_entities) if pred_entities else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    pred_count, pred_types = count_entities(tagged_text)
    gt_count, gt_types = count_entities(ground_truth)

    return {
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "predicted_count": pred_count,
        "ground_truth_count": gt_count,
        "correct_count": correct,
        "predicted_types": pred_types,
        "ground_truth_types": gt_types,
    }

def main():
    """主函数"""
    # 检查测试数据
    data_dir = Path(__file__).parent / "data"
    test_file = data_dir / "test_corpus.txt"
    ground_truth_file = data_dir / "ground_truth.tagged.md"

    if not test_file.exists():
        print(f"错误: 测试数据不存在 - {test_file}")
        return 1

    if not ground_truth_file.exists():
        print(f"警告: 标准答案不存在 - {ground_truth_file}")
        ground_truth = None
    else:
        with open(ground_truth_file, encoding="utf-8") as f:
            ground_truth = f.read()

    # 读取测试数据
    with open(test_file, encoding="utf-8") as f:
        text = f.read().strip()

    # 加载模型
    try:
        tokenizer, model = load_qwen_model()
    except Exception as e:
        print(f"\n错误: 模型加载失败")
        print(f"{e}")
        print(f"\n请先运行: python download_qwen.py")
        return 1

    # 标注
    tagged_text, metadata = annotate_with_qwen(text, tokenizer, model)

    # 显示结果
    print("\n" + "=" * 80)
    print("标注结果")
    print("=" * 80)
    print(tagged_text)

    # 评估
    if ground_truth:
        print("\n" + "=" * 80)
        print("评估结果")
        print("=" * 80)

        eval_result = evaluate_result(tagged_text, ground_truth)

        print(f"\n性能指标:")
        print(f"  召回率 (Recall):    {eval_result['recall']*100:.1f}%")
        print(f"  精确率 (Precision): {eval_result['precision']*100:.1f}%")
        print(f"  F1分数:             {eval_result['f1']*100:.1f}%")

        print(f"\n实体统计:")
        print(f"  预测: {eval_result['predicted_count']} 个")
        print(f"  标准: {eval_result['ground_truth_count']} 个")
        print(f"  正确: {eval_result['correct_count']} 个")

        print(f"\n实体类型分布:")
        print(f"  {'类型':<10} {'预测':<10} {'标准':<10}")
        print(f"  {'-'*30}")
        all_types = set(eval_result['predicted_types'].keys()) | set(eval_result['ground_truth_types'].keys())
        for entity_type in sorted(all_types):
            pred = eval_result['predicted_types'].get(entity_type, 0)
            gt = eval_result['ground_truth_types'].get(entity_type, 0)
            print(f"  {entity_type:<10} {pred:<10} {gt:<10}")

        # 合并元数据
        metadata.update(eval_result)

    # 保存结果
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    output_file = results_dir / "qwen_actual_result.tagged.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tagged_text)

    metadata_file = results_dir / "qwen_actual_result.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("结果已保存")
    print("=" * 80)
    print(f"标注文本: {output_file}")
    print(f"元数据:   {metadata_file}")

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())

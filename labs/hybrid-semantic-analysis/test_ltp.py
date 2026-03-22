#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LTP实体标注测试

使用真实的LTP进行实体识别,支持多个测试数据集
"""

import sys
import json
import re
import argparse
from pathlib import Path

def test_ltp_available():
    """测试LTP是否可用"""
    try:
        from ltp import LTP
        return True
    except ImportError:
        return False

def extract_entities_from_ltp(text, ltp_model):
    """使用LTP提取实体"""
    from ltp import LTP

    # LTP处理
    result = ltp_model.pipeline([text], tasks=["cws", "pos", "ner"])

    # 获取结果
    words = result.cws[0]  # 分词结果
    pos = result.pos[0]    # 词性标注
    ner = result.ner[0]    # 命名实体识别

    # 构建标注文本
    entities = []
    tagged_text = text

    # LTP的NER结果格式: [(entity_text, entity_type, start_pos, end_pos), ...]
    # 需要根据实际LTP版本调整
    for entity_info in ner:
        if isinstance(entity_info, tuple) and len(entity_info) >= 2:
            entity_text = entity_info[0]
            entity_type = entity_info[1]

            # 映射LTP类型到我们的类型
            type_mapping = {
                'Nh': 'PERSON',  # 人名
                'Ni': 'ORG',     # 机构名
                'Ns': 'PLACE',   # 地名
            }

            mapped_type = type_mapping.get(entity_type, 'UNKNOWN')
            if mapped_type != 'UNKNOWN':
                entities.append({
                    'text': entity_text,
                    'type': mapped_type
                })

    # 生成标注文本(简化版本,实际需要更复杂的逻辑)
    for entity in entities:
        pattern = re.escape(entity['text'])
        replacement = f"〖{entity['type']} {entity['text']}〗"
        # 只替换第一次出现(避免重复标注)
        tagged_text = re.sub(f'(?<!〗){pattern}(?!〗)', replacement, tagged_text, count=1)

    return tagged_text, entities

def count_entities(text):
    """统计标注实体数"""
    pattern = r'〖([A-Z_]+)\s+([^〗]+)〗'
    matches = re.findall(pattern, text)

    entity_types = {}
    for entity_type, _ in matches:
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

    return len(matches), entity_types

def extract_entity_texts(text):
    """提取实体文本集合"""
    pattern = r'〖[A-Z_]+\s+([^|〗]+)(?:\|[^〗]+)?〗'
    return set(re.findall(pattern, text))

def evaluate(predicted_text, ground_truth_text):
    """评估标注结果"""
    pred_entities = extract_entity_texts(predicted_text)
    gt_entities = extract_entity_texts(ground_truth_text)

    correct = len(pred_entities & gt_entities)
    recall = correct / len(gt_entities) if gt_entities else 0
    precision = correct / len(pred_entities) if pred_entities else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    pred_count, pred_types = count_entities(predicted_text)
    gt_count, gt_types = count_entities(ground_truth_text)

    return {
        'recall': recall,
        'precision': precision,
        'f1': f1,
        'predicted_count': pred_count,
        'ground_truth_count': gt_count,
        'correct_count': correct,
        'predicted_types': pred_types,
        'ground_truth_types': gt_types,
    }

def main():
    parser = argparse.ArgumentParser(description='LTP实体标注测试')
    parser.add_argument('--data', type=str, default='short',
                       choices=['short', 'medium', 'long'],
                       help='测试数据集: short(138字), medium(631字), long(3000字)')
    parser.add_argument('--output-dir', type=str, default='results',
                       help='结果输出目录')

    args = parser.parse_args()

    # 数据文件映射
    data_files = {
        'short': {
            'corpus': 'data/test_corpus.txt',
            'ground_truth': 'data/ground_truth.tagged.md',
            'description': '短文本(138字)'
        },
        'medium': {
            'corpus': 'data/test_corpus_long.txt',
            'ground_truth': None,  # 没有ground truth
            'description': '中文本(631字)'
        },
        'long': {
            'corpus': 'data/test_corpus_chapter.txt',
            'ground_truth': None,  # 没有ground truth
            'description': '长文本(3000字)'
        }
    }

    data_config = data_files[args.data]

    # 检查LTP是否可用
    if not test_ltp_available():
        print("=" * 80)
        print("错误: LTP不可用")
        print("=" * 80)
        print("\nLTP在Python 3.13环境下存在兼容性问题。")
        print("\n解决方案:")
        print("1. 使用Python 3.10环境")
        print("2. 查看 LTP_STATUS.md 了解详情")
        print("3. 使用已有的LTP测试结果: results/ltp_experiment_report.md")
        return 1

    # 加载LTP模型
    print("=" * 80)
    print(f"LTP实体标注测试 - {data_config['description']}")
    print("=" * 80)

    print("\n加载LTP模型...")
    try:
        from ltp import LTP
        ltp = LTP()
        print("✓ LTP模型加载成功")
    except Exception as e:
        print(f"✗ LTP模型加载失败: {e}")
        print("\n详见: LTP_STATUS.md")
        return 1

    # 读取测试数据
    corpus_file = Path(__file__).parent / data_config['corpus']
    if not corpus_file.exists():
        print(f"\n错误: 测试数据不存在 - {corpus_file}")
        return 1

    with open(corpus_file, encoding='utf-8') as f:
        text = f.read().strip()

    ground_truth = None
    if data_config['ground_truth']:
        gt_file = Path(__file__).parent / data_config['ground_truth']
        if gt_file.exists():
            with open(gt_file, encoding='utf-8') as f:
                ground_truth = f.read()

    print(f"\n原文长度: {len(text)} 字")
    print(f"原文预览: {text[:100]}...")

    # 运行LTP标注
    print("\n正在标注...")
    import time
    start_time = time.time()

    try:
        tagged_text, entities = extract_entities_from_ltp(text, ltp)
        elapsed = time.time() - start_time
        print(f"✓ 标注完成 ({elapsed:.2f}秒)")
    except Exception as e:
        print(f"✗ 标注失败: {e}")
        return 1

    # 显示结果
    print("\n" + "=" * 80)
    print("标注结果")
    print("=" * 80)
    print(tagged_text)

    # 统计
    entity_count, entity_types = count_entities(tagged_text)

    print("\n" + "=" * 80)
    print("统计信息")
    print("=" * 80)
    print(f"\n识别实体数: {entity_count}")
    print(f"\n实体类型分布:")
    for etype, count in sorted(entity_types.items()):
        print(f"  {etype}: {count}")

    # 评估(如果有ground truth)
    if ground_truth:
        print("\n" + "=" * 80)
        print("性能评估")
        print("=" * 80)

        eval_result = evaluate(tagged_text, ground_truth)

        print(f"\n召回率 (Recall):    {eval_result['recall']*100:.1f}%")
        print(f"精确率 (Precision): {eval_result['precision']*100:.1f}%")
        print(f"F1分数:             {eval_result['f1']*100:.1f}%")

        print(f"\n实体统计:")
        print(f"  预测: {eval_result['predicted_count']} 个")
        print(f"  标准: {eval_result['ground_truth_count']} 个")
        print(f"  正确: {eval_result['correct_count']} 个")

        print(f"\n实体类型对比:")
        print(f"  {'类型':<10} {'预测':<10} {'标准':<10}")
        print(f"  {'-'*30}")
        all_types = set(eval_result['predicted_types'].keys()) | set(eval_result['ground_truth_types'].keys())
        for entity_type in sorted(all_types):
            pred = eval_result['predicted_types'].get(entity_type, 0)
            gt = eval_result['ground_truth_types'].get(entity_type, 0)
            print(f"  {entity_type:<10} {pred:<10} {gt:<10}")

    # 保存结果
    output_dir = Path(__file__).parent / args.output_dir
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"ltp_{args.data}_result.tagged.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(tagged_text)

    metadata = {
        'method': 'ltp',
        'data_size': args.data,
        'text_length': len(text),
        'time_seconds': elapsed,
        'entity_count': entity_count,
        'entity_types': entity_types,
    }

    if ground_truth:
        metadata.update({
            'recall': eval_result['recall'],
            'precision': eval_result['precision'],
            'f1': eval_result['f1'],
        })

    metadata_file = output_dir / f"ltp_{args.data}_result.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("结果已保存")
    print("=" * 80)
    print(f"标注文本: {output_file}")
    print(f"元数据:   {metadata_file}")

    return 0

if __name__ == '__main__':
    sys.exit(main())

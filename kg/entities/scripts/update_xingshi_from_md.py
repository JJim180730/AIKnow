#!/usr/bin/env python3
"""
从 person_xingshi.md 增量更新 person_xingshi.json

策略：保留旧 JSON 中的所有数据，用 MD 中的详细记录更新/覆盖对应人物。
MD 中只有 616 人的详细表格（R1 + 重要人物补充），其余人物保留旧数据。

Usage:
    python kg/entities/scripts/update_xingshi_from_md.py

Input:  kg/entities/data/person_xingshi.md (616人详细)
        kg/entities/data/person_xingshi.json (2053人，旧版)
Output: kg/entities/data/person_xingshi.json (更新后)
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def parse_evidence(evidence_str):
    """解析证据字符串为列表"""
    if not evidence_str or evidence_str.strip() == "":
        return []
    parts = re.split(r'[;|]', evidence_str)
    return [p.strip() for p in parts if p.strip()]


def parse_chapter_refs(evidence_list):
    """从证据中提取章节编号"""
    chapters = set()
    for ev in evidence_list:
        match = re.match(r'(\d{3}):', ev)
        if match:
            chapters.add(match.group(1))
    return sorted(list(chapters))


def parse_markdown_table(md_file):
    """解析 Markdown 文件中的所有表格"""
    persons = {}

    content = md_file.read_text(encoding='utf-8')
    lines = content.split('\n')

    current_round = None
    in_table = False
    headers = []

    for i, line in enumerate(lines):
        # 检测章节标题
        if line.startswith('##'):
            current_round = line.strip('# ').strip()
            in_table = False
            continue

        # 检测表格头
        if '|' in line and not in_table:
            if i + 1 < len(lines) and '---' in lines[i + 1]:
                headers = [h.strip() for h in line.split('|')[1:-1]]
                in_table = True
                continue

        # 解析表格行
        if in_table and '|' in line and '---' not in line:
            cells = [c.strip() for c in line.split('|')[1:-1]]

            if len(cells) < len(headers) or not cells[0]:
                continue

            row_data = dict(zip(headers, cells))
            person_name = row_data.get('人名', '').strip()

            if not person_name:
                continue

            # 提取字段
            xing = row_data.get('姓', '').strip() or None
            shi = row_data.get('氏', '').strip() or None
            ming = row_data.get('名', '').strip() or None
            zi = row_data.get('字', '').strip() or None
            confidence = row_data.get('置信度', '').strip().lower()
            evidence_str = row_data.get('证据', '').strip()

            # 解析证据
            evidence = parse_evidence(evidence_str)
            source_chapter = parse_chapter_refs(evidence)

            # 推断规则
            if "Round 1" in current_round or "直接记载" in current_round:
                rule = "R1"
            elif "重要人物" in current_round or "补充" in current_round:
                rule = "R_supplement"
            else:
                rule = "R_unknown"

            # 判断时期
            period = row_data.get('时代', 'pre-qin').strip()

            # 构建条目
            person_entry = {
                "xing": xing,
                "shi": shi,
                "ming": ming,
                "zi": zi,
                "period": period,
                "confidence": confidence if confidence in ['exact', 'high', 'medium', 'low'] else 'medium',
                "evidence": evidence,
                "rule": rule,
                "source_chapter": source_chapter
            }

            persons[person_name] = person_entry

    return persons


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent.parent
    md_file = project_root / "kg" / "entities" / "data" / "person_xingshi.md"
    json_file = project_root / "kg" / "entities" / "data" / "person_xingshi.json"

    if not md_file.exists():
        print(f"❌ 源文件不存在: {md_file}")
        return

    print("=" * 60)
    print("增量更新 person_xingshi.json")
    print("策略：保留旧数据 + MD详细记录覆盖")
    print("=" * 60)
    print()

    # 1. 读取现有 JSON
    existing_persons = {}
    old_stats = {}

    if json_file.exists():
        print(f"📖 读取现有 JSON: {json_file.name}")
        with open(json_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            existing_persons = old_data.get('persons', {})
            old_stats = old_data.get('_stats', {})
        print(f"   现有数据: {len(existing_persons)} 人")
        print(f"   版本: {old_data.get('_version', 'unknown')}")
        print()

    # 2. 解析 Markdown
    print(f"📖 读取 Markdown: {md_file.name}")
    md_persons = parse_markdown_table(md_file)
    print(f"   MD 详细记录: {len(md_persons)} 人")
    print()

    # 3. 合并数据：MD 覆盖 JSON
    print("🔄 合并数据...")
    updated_count = 0
    new_count = 0

    for name, md_entry in md_persons.items():
        if name in existing_persons:
            updated_count += 1
        else:
            new_count += 1
        existing_persons[name] = md_entry

    print(f"   更新: {updated_count} 人")
    print(f"   新增: {new_count} 人")
    print(f"   总计: {len(existing_persons)} 人")
    print()

    # 4. 统计信息
    rule_dist = defaultdict(int)
    conf_dist = defaultdict(int)

    for p in existing_persons.values():
        rule_dist[p.get('rule', 'unknown')] += 1
        conf_dist[p.get('confidence', 'unknown')] += 1

    print("规则分布:")
    for rule in sorted(rule_dist.keys()):
        print(f"  {rule}: {rule_dist[rule]}")
    print()

    print("置信度分布:")
    for conf in ['exact', 'high', 'medium', 'low', 'unknown']:
        if conf in conf_dist:
            print(f"  {conf}: {conf_dist[conf]}")
    print()

    # 5. 构建输出 JSON
    output = {
        "_doc": "史记人物姓氏推理表。先秦人物区分姓（血缘）与氏（分家）。秦后人物仅记姓。",
        "_version": "v2.1",
        "_update_note": "基于 MD 详细记录更新，保留旧数据",
        "_stats": {
            **dict(rule_dist),
            "total": len(existing_persons)
        },
        "persons": existing_persons
    }

    # 6. 写入 JSON
    print(f"💾 写入: {json_file.name}")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    file_size = json_file.stat().st_size
    print(f"   文件大小: {file_size:,} 字节 ({file_size / 1024:.1f} KB)")
    print()

    # 7. 验证
    print("✓ 验证数据...")
    with open(json_file, 'r', encoding='utf-8') as f:
        verify = json.load(f)

    print(f"  JSON格式正确")
    print(f"  包含 {len(verify['persons'])} 人")

    print("=" * 60)
    print("✓ 更新完成！")
    print("=" * 60)
    print()
    print(f"输出文件: {json_file.relative_to(project_root)}")
    print()
    print("下一步:")
    print("  1. 检查生成的 JSON 文件")
    print("  2. 运行: python scripts/publish_xingshi_data.py")
    print("  3. 提交更新: git add kg/entities/data/person_xingshi.json")


if __name__ == "__main__":
    main()

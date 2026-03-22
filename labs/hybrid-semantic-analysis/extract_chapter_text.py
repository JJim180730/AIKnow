#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从标注的章节文件中提取纯文本
移除所有标注符号,保留实体文本
"""

import re
import sys
from pathlib import Path

def remove_entity_tags(text: str) -> str:
    """移除实体标注符号,保留实体文本"""

    # 处理消歧语法: 〖TYPE 显示名|规范名〗 → 显示名
    # 例如: 〖@项籍|项羽〗 → 项籍
    text = re.sub(r'〖[^〖〗\s]+\s+([^|〖〗]+)\|[^〖〗]+〗', r'\1', text)

    # 处理普通标注: 〖TYPE 文本〗 → 文本
    # 例如: 〖@项梁〗 → 项梁
    text = re.sub(r'〖[^〖〗\s]+\s+([^〖〗]+)〗', r'\1', text)

    return text

def extract_clean_text(tagged_file: str, max_chars: int = 3000) -> str:
    """从标注文件中提取纯文本"""

    with open(tagged_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 移除实体标注符号
    text = remove_entity_tags(content)

    # 2. 移除markdown标题 (# ## ###)
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)

    # 3. 移除段落编号 [1.1] [2.1] 等
    text = re.sub(r'\[\d+\.?\d*\]\s*', '', text)

    # 4. 移除引用符号 >
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # 5. 合并文本行
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:  # 跳过空行
            lines.append(line)

    text = ''.join(lines)

    # 6. 截取指定长度
    text = text[:max_chars]

    return text

if __name__ == "__main__":
    tagged_file = Path(__file__).parent.parent.parent / "chapter_md" / "007_项羽本纪.tagged.md"
    output_file = Path(__file__).parent / "data" / "test_corpus_chapter.txt"

    print("提取纯文本...")
    print(f"输入: {tagged_file}")

    text = extract_clean_text(str(tagged_file), max_chars=3000)

    print(f"提取字数: {len(text)} 字")
    print()
    print("前300字预览:")
    print(text[:300])
    print("...")
    print()

    # 保存
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✓ 已保存到: {output_file}")

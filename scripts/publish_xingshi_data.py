#!/usr/bin/env python3
"""
发布姓氏数据脚本

将 kg/entities/data/ 中的姓氏相关JSON文件复制到 docs/special/data/xingshi/
供网页前端使用。

Usage:
    python scripts/publish_xingshi_data.py
"""

import shutil
from pathlib import Path


def publish_xingshi_data():
    """发布姓氏数据到docs目录"""

    # 定义路径
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "kg" / "entities" / "data"
    target_dir = project_root / "docs" / "special" / "data" / "xingshi"

    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)

    # 要复制的文件列表
    files_to_copy = [
        "person_xingshi.json",      # 人物姓氏JSON数据
        "person_xingshi.md",        # 人物姓氏推理详情
        "xing_index.json",          # 先秦大姓索引
        "pre_qin_xingshi.md"        # 先秦姓氏说明文档
    ]

    print("=" * 60)
    print("开始发布姓氏数据...")
    print("=" * 60)

    copied_count = 0
    total_size = 0

    for filename in files_to_copy:
        source_file = source_dir / filename
        target_file = target_dir / filename

        if not source_file.exists():
            print(f"⚠️  源文件不存在: {source_file}")
            continue

        # 复制文件
        shutil.copy2(source_file, target_file)
        file_size = target_file.stat().st_size
        total_size += file_size

        print(f"✓ 复制: {filename}")
        print(f"  大小: {file_size:,} 字节 ({file_size / 1024:.1f} KB)")
        print(f"  目标: {target_file.relative_to(project_root)}")

        copied_count += 1

    print("=" * 60)
    print(f"✓ 发布完成！")
    print(f"  复制文件数: {copied_count}/{len(files_to_copy)}")
    print(f"  总大小: {total_size:,} 字节 ({total_size / 1024:.1f} KB)")
    print(f"  目标目录: {target_dir.relative_to(project_root)}")
    print("=" * 60)


if __name__ == "__main__":
    publish_xingshi_data()

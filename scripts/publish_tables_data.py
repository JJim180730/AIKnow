#!/usr/bin/env python3
"""
十表数据发布脚本
将 data/tables/data/ 中的JSON文件复制到 docs/special/data/tables/ 供Web访问
"""

import os
import shutil
from pathlib import Path

def publish_tables_data():
    """发布十表JSON数据到docs目录"""

    # 定义路径
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "data" / "tables" / "data"
    target_dir = project_root / "docs" / "special" / "data" / "tables"

    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")

    # 检查源目录
    if not source_dir.exists():
        print(f"❌ 错误：源目录不存在 {source_dir}")
        return False

    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建目标目录: {target_dir}")

    # 复制JSON文件
    json_files = list(source_dir.glob("*.json"))

    if not json_files:
        print(f"❌ 错误：源目录中没有找到JSON文件")
        return False

    print(f"\n找到 {len(json_files)} 个JSON文件:")

    copied_count = 0
    for json_file in sorted(json_files):
        target_file = target_dir / json_file.name
        try:
            shutil.copy2(json_file, target_file)
            file_size = json_file.stat().st_size
            print(f"  ✅ {json_file.name} ({file_size:,} bytes)")
            copied_count += 1
        except Exception as e:
            print(f"  ❌ {json_file.name} - 错误: {e}")

    print(f"\n总结:")
    print(f"  成功复制: {copied_count}/{len(json_files)} 个文件")
    print(f"  目标位置: {target_dir}")

    # 生成访问URL示例
    print(f"\n访问示例:")
    for json_file in sorted(json_files)[:3]:  # 只显示前3个
        relative_path = f"data/tables/{json_file.name}"
        print(f"  {relative_path}")

    return copied_count == len(json_files)

if __name__ == "__main__":
    success = publish_tables_data()
    exit(0 if success else 1)

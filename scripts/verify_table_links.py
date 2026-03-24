#!/usr/bin/env python3
"""
验证 tables.html 中的所有链接是否有效
"""

import os
import re
from pathlib import Path

def verify_links():
    """验证tables.html中的所有链接"""

    project_root = Path(__file__).parent.parent
    tables_html = project_root / "docs" / "special" / "tables.html"

    print(f"检查文件: {tables_html}\n")

    if not tables_html.exists():
        print(f"❌ 文件不存在: {tables_html}")
        return False

    # 读取HTML内容
    with open(tables_html, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取所有链接
    # 匹配 href="..." 的内容
    links = re.findall(r'href="([^"]+)"', content)

    # 过滤出相对路径链接（排除#和http）
    relative_links = [link for link in links if not link.startswith(('#', 'http'))]

    print(f"找到 {len(relative_links)} 个相对路径链接\n")

    # 验证每个链接
    base_dir = tables_html.parent
    success_count = 0
    fail_count = 0

    json_links = []
    chapter_links = []
    other_links = []

    for link in relative_links:
        if 'json' in link:
            json_links.append(link)
        elif 'chapters' in link:
            chapter_links.append(link)
        else:
            other_links.append(link)

    # 验证JSON链接
    print("=" * 60)
    print("JSON数据链接验证")
    print("=" * 60)
    for link in json_links:
        target = base_dir / link
        if target.exists():
            print(f"✅ {link}")
            success_count += 1
        else:
            print(f"❌ {link} (文件不存在)")
            print(f"   预期路径: {target}")
            fail_count += 1

    # 验证章节链接
    print("\n" + "=" * 60)
    print("章节原文链接验证")
    print("=" * 60)
    for link in chapter_links:
        target = base_dir / link
        if target.exists():
            file_size = target.stat().st_size
            print(f"✅ {link} ({file_size:,} bytes)")
            success_count += 1
        else:
            print(f"❌ {link} (文件不存在)")
            print(f"   预期路径: {target}")
            fail_count += 1

    # 验证其他链接
    if other_links:
        print("\n" + "=" * 60)
        print("其他链接验证")
        print("=" * 60)
        for link in other_links:
            target = base_dir / link
            if target.exists():
                print(f"✅ {link}")
                success_count += 1
            else:
                print(f"❌ {link} (文件不存在)")
                print(f"   预期路径: {target}")
                fail_count += 1

    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    print(f"总链接数: {success_count + fail_count}")
    print(f"✅ 有效链接: {success_count}")
    print(f"❌ 失效链接: {fail_count}")

    if fail_count == 0:
        print("\n🎉 所有链接验证通过！")
        return True
    else:
        print(f"\n⚠️  发现 {fail_count} 个失效链接，需要修复")
        return False

if __name__ == "__main__":
    success = verify_links()
    exit(0 if success else 1)

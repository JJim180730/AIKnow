#!/usr/bin/env python3
"""
临时修补LTP以兼容新版huggingface_hub

问题: LTP使用旧API `use_auth_token`, 而新版huggingface_hub使用 `token`
解决: 自动替换LTP源码中的参数名
"""

import site
from pathlib import Path

def patch_ltp():
    """修补LTP的interface.py文件"""

    print("=" * 60)
    print("LTP兼容性修补工具")
    print("=" * 60)
    print()

    # 找到LTP的安装位置
    ltp_interface = None
    for site_pkg in site.getsitepackages():
        candidate = Path(site_pkg) / "ltp" / "interface.py"
        if candidate.exists():
            ltp_interface = candidate
            break

    if not ltp_interface:
        print("❌ 未找到LTP安装")
        print()
        print("请先安装LTP:")
        print("  pip install ltp")
        return False

    print(f"找到LTP: {ltp_interface}")
    print()

    # 读取文件
    try:
        with open(ltp_interface, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

    # 检查是否需要修补
    if 'use_auth_token=' not in content:
        print("✓ LTP已经是最新版本,无需修补")
        return True

    print("发现需要修补的代码:")
    # 显示需要修改的行
    for i, line in enumerate(content.split('\n'), 1):
        if 'use_auth_token=' in line:
            print(f"  第{i}行: {line.strip()}")
    print()

    # 替换
    print("正在修补...")
    new_content = content.replace('use_auth_token=', 'token=')

    # 备份原文件
    backup_file = ltp_interface.with_suffix('.py.bak')
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已备份原文件: {backup_file}")
    except Exception as e:
        print(f"⚠ 备份失败: {e}")

    # 写回修补后的内容
    try:
        with open(ltp_interface, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✓ 修补完成!")
    except Exception as e:
        print(f"❌ 写入失败: {e}")
        return False

    print()
    print("=" * 60)
    print("修补成功! 现在可以使用LTP了")
    print("=" * 60)
    print()
    print("测试LTP:")
    print("  python -c \"from ltp import LTP; ltp = LTP(device='cpu'); print('✓ LTP工作正常')\"")
    print()
    print("运行实际标注:")
    print("  python methods/method_a_local.py")
    print()

    return True

if __name__ == "__main__":
    import sys
    success = patch_ltp()
    sys.exit(0 if success else 1)

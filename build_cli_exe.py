"""
编译 cli_convert.py 为独立的 exe 文件
"""

import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_exe():
    """使用 PyInstaller 编译 cli_convert.py"""
    
    script_dir = Path(__file__).parent
    cli_script = script_dir / "cli_convert.py"
    dist_dir = script_dir / "dist"
    
    print("=" * 60)
    print("FoldPDF CLI - EXE 编译工具")
    print("=" * 60)
    print(f"源文件: {cli_script}")
    print(f"输出目录: {dist_dir}")
    print()
    
    # PyInstaller 参数
    args = [
        str(cli_script),
        "--onefile",                    # 生成单一 exe 文件
        "--windowed",                   # 无控制台窗口（仅显示 PyQt 窗口）
        "--name=CliFoldPDF",               # exe 名称
        f"--distpath={dist_dir}",       # 输出目录
        f"--workpath={script_dir / 'build'}",
        f"--specpath={script_dir}",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PIL",
        "--hidden-import=img2pdf",
        "--hidden-import=natsort",
    ]
    
    print("正在编译，请稍候...")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        exe_path = dist_dir / "FoldPDF.exe"
        
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # 转换为 MB
            print()
            print("=" * 60)
            print("✓ 编译成功！")
            print("=" * 60)
            print(f"输出文件: {exe_path}")
            print(f"文件大小: {file_size:.2f} MB")
            print()
            print("下一步:")
            print("  1. 双击 install_context_menu.bat 安装右键菜单")
            print("  2. 在任意文件夹右键选择 'FoldPDF' 来使用")
            print()
            return True
        else:
            print("❌ 编译失败：找不到输出文件")
            return False
    
    except Exception as e:
        print(f"❌ 编译失败: {e}")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)

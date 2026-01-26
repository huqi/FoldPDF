"""
FoldPDF 右键菜单注册脚本 (Windows)
注册右键菜单，在任意文件夹右键选择 "FoldPDF"

使用方法：
  python register_context_menu.py install    # 安装右键菜单
  python register_context_menu.py uninstall  # 卸载右键菜单
  
需要管理员权限执行
"""

import sys
import os
import winreg
import ctypes
from pathlib import Path

def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except:
        return False

def get_script_dir():
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))

def find_executable():
    """查找 FoldPDF.exe，如果不存在则尝试查找 cli_convert.py"""
    script_dir = get_script_dir()
    
    # 优先查找 exe 文件
    exe_path = os.path.join(script_dir, "dist", "FoldPDF.exe")
    if os.path.exists(exe_path):
        return exe_path, True  # (path, is_exe)
    
    # 如果没有 exe，尝试查找 Python 脚本
    cli_script = os.path.join(script_dir, "cli_convert.py")
    if os.path.exists(cli_script):
        return cli_script, False
    
    return None, None

def install_context_menu():
    """安装右键菜单"""
    if not is_admin():
        print("❌ 需要管理员权限！请以管理员身份运行此脚本")
        return False
    
    try:
        script_dir = get_script_dir()
        exe_path, is_exe = find_executable()
        
        if not exe_path:
            print("❌ 安装失败: 找不到 FoldPDF.exe 或 cli_convert.py")
            print("\n解决方案:")
            print("  1. 首先运行: python build_cli_exe.py (编译 exe)")
            print("  2. 然后运行: python register_context_menu.py install")
            return False
        
        # 注册路径
        registry_path = r"Software\Classes\Folder\shell\FoldPDF"
        
        # 打开或创建注册表项
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
        
        # 设置菜单项显示文本
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "FoldPDF - 批量生成PDF")
        
        # 尝试设置图标
        icon_path = os.path.join(script_dir, "app_icon.ico")
        if os.path.exists(icon_path):
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
        
        # 设置命令
        command_key = winreg.CreateKey(key, "command")
        
        if is_exe:
            # 如果是 exe，直接调用
            command = f'"{exe_path}" "%1"'
            executable_type = "EXE"
        else:
            # 如果是 Python 脚本，需要用 Python 解释器
            python_path = sys.executable
            command = f'"{python_path}" "{exe_path}" "%1"'
            executable_type = "Python 脚本"
        
        winreg.SetValueEx(command_key, None, 0, winreg.REG_SZ, command)
        
        winreg.CloseKey(command_key)
        winreg.CloseKey(key)
        
        print("✓ 右键菜单安装成功！")
        print(f"  类型: {executable_type}")
        print(f"  路径: {exe_path}")
        print("\n现在你可以在任意文件夹右键选择 'FoldPDF' 来快速转换")
        return True
    
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False

def uninstall_context_menu():
    """卸载右键菜单"""
    if not is_admin():
        print("❌ 需要管理员权限！请以管理员身份运行此脚本")
        return False
    
    try:
        registry_path = r"Software\Classes\Folder\shell\FoldPDF"
        
        # 递归删除注册表项
        def delete_registry_tree(parent_key, sub_key):
            try:
                key = winreg.OpenKey(parent_key, sub_key, 0, winreg.KEY_ALL_ACCESS)
                while True:
                    try:
                        name = winreg.EnumKey(key, 0)
                        delete_registry_tree(key, name)
                    except WindowsError:
                        break
                winreg.CloseKey(key)
                winreg.DeleteKey(parent_key, sub_key)
            except WindowsError as e:
                pass
        
        delete_registry_tree(winreg.HKEY_CURRENT_USER, registry_path)
        print("✓ 右键菜单卸载成功！")
        return True
    
    except Exception as e:
        print(f"❌ 卸载失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python register_context_menu.py install    # 安装右键菜单")
        print("  python register_context_menu.py uninstall  # 卸载右键菜单")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "install":
        success = install_context_menu()
        sys.exit(0 if success else 1)
    elif command == "uninstall":
        success = uninstall_context_menu()
        sys.exit(0 if success else 1)
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()

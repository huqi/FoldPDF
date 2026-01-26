@echo off
REM FoldPDF 右键菜单卸载脚本
REM 双击运行此脚本可卸载右键菜单

:: 核心修复：强制使用 UTF-8 编码，解决 VS Code 终端乱码
chcp 65001 >nul

echo FoldPDF 右键菜单卸载器
echo =======================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 需要管理员权限，请以管理员身份运行此脚本
    pause
    exit /b 1
)

REM 获取当前目录
cd /d "%~dp0"

REM 运行卸载脚本
echo 正在卸载右键菜单...
.venv\Scripts\python register_context_menu.py uninstall

if %errorlevel% equ 0 (
    echo.
    echo ✓ 卸载成功！
) else (
    echo.
    echo ❌ 卸载失败，请查看上面的错误信息
)

pause

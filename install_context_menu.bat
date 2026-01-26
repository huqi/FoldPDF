@echo off
REM FoldPDF 右键菜单快速安装脚本
REM 自动编译 exe 并安装右键菜单

:: 核心修复：强制使用 UTF-8 编码，解决 VS Code 终端乱码
chcp 65001 >nul

echo FoldPDF 右键菜单安装器
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

REM 检查 exe 文件是否存在
if not exist "dist\FoldPDF.exe" (
    echo 未找到 FoldPDF.exe，正在编译...
    echo.
    .venv\Scripts\python build_cli_exe.py
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ exe 编译失败，安装中止
        pause
        exit /b 1
    )
    echo.
)

REM 运行安装脚本
echo 正在安装右键菜单...
.venv\Scripts\python register_context_menu.py install

if %errorlevel% equ 0 (
    echo.
    echo ✓ 安装成功！现在你可以在任意文件夹右键选择 'FoldPDF' 来快速转换图片
) else (
    echo.
    echo ❌ 安装失败，请查看上面的错误信息
)

pause

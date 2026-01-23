@echo off
:: 核心修复：强制使用 UTF-8 编码，解决 VS Code 终端乱码
chcp 65001 >nul

title FoldPDF 打包工具
echo ==========================================
echo       FoldPDF 一键打包脚本 (基于 uv)
echo ==========================================
echo.

:: 1. 确保安装了 pyinstaller
echo [1/4] 检查打包环境...
call uv add pyinstaller

:: 2. 清理旧的构建文件
echo [2/4] 清理旧缓存...
if exist dist del /s /q dist
if exist build del /s /q build
if exist FoldPDF.spec del /q FoldPDF.spec

:: 3. 执行打包命令
:: --noconsole: 不显示黑色命令行窗口
:: --onefile: 所有的东西打包成一个 exe
:: --optimize: 2 启用字节码优化，减少文件大小
:: --name: 程序名字
:: --clean: 打包前清理临时文件
:: --hidden-import: 隐藏导入必要的模块
echo [3/4] 开始打包，请稍候 (这可能需要 2-3 分钟)...
call uv run pyinstaller ^
    --noconsole ^
    --onefile ^
    --optimize=2 ^
    --icon="app_icon.png" ^
    --clean ^
    --name "FoldPDF" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtPrintSupport ^
    --hidden-import=PIL.Image ^
    --hidden-import=PIL.JpegImagePlugin ^
    --hidden-import=img2pdf ^
    --hidden-import=natsort ^
    --exclude-module=numpy ^
    --exclude-module=scipy ^
    --exclude-module=pandas ^
    --exclude-module=matplotlib ^
    main.py

:: 4. 检查结果
echo.
if exist "dist\FoldPDF.exe" (
    echo [4/4] 打包成功！
    echo ------------------------------------------
    echo 生成文件位于: dist\FoldPDF.exe
    echo ------------------------------------------
    explorer dist
) else (
    echo [错误] 打包失败，请检查命令行输出信息。
)

pause
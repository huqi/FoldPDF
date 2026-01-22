@echo off
chcp 65001 >nul
title FoldPDF 快速重建

echo 清理旧文件...
if exist dist rmdir /s /q dist >nul 2>&1
if exist build rmdir /s /q build >nul 2>&1
if exist FoldPDF.spec del /q FoldPDF.spec >nul 2>&1

echo 开始打包...
call uv run pyinstaller ^
    --noconsole ^
    --onefile ^
    --icon="app_icon.ico" ^
    --clean ^
    --name "FoldPDF" ^
    --collect-all PyQt6 ^
    --collect-all PIL ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PIL.Image ^
    --hidden-import=img2pdf ^
    --hidden-import=natsort ^
    main.py

if exist "dist\FoldPDF.exe" (
    echo.
    echo 打包成功！
    explorer dist
) else (
    echo 打包失败！
)

pause

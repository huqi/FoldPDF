# FoldPDF EXE 部署指南

## 概览

本指南说明如何将 `cli_convert.py` 编译为独立的 `FoldPDF.exe` 可执行文件，并将其注册到 Windows 右键菜单。

## 优势

✓ **独立运行** - 无需 Python 环境，直接双击或右键调用  
✓ **快速启动** - 编译后的 exe 启动速度极快  
✓ **便携式** - 不依赖系统 Python 路径  
✓ **易于分发** - 可以单独分发 exe 文件  

## 编译流程

### 步骤 1：编译 EXE 文件

打开 PowerShell（**不需要管理员权限**）并运行：

```powershell
cd d:\Dropbox\DevProjects\Python\FoldPDF
.venv\Scripts\python build_cli_exe.py
```

**编译过程**：
- 首次编译会下载和处理依赖库
- 编译时间通常为 1-5 分钟（取决于网络和系统速度）
- 生成的 exe 文件大约 100-150 MB（包含所有必要的库）

**成功标志**：
```
============================================================
✓ 编译成功！
============================================================
输出文件: d:\Dropbox\DevProjects\Python\FoldPDF\dist\FoldPDF.exe
文件大小: 120.45 MB

下一步:
  1. 双击 install_context_menu.bat 安装右键菜单
  2. 在任意文件夹右键选择 'FoldPDF' 来使用
```

### 步骤 2：安装右键菜单

编译完成后，**以管理员身份**双击运行：
```
install_context_menu.bat
```

或者手动运行：
```powershell
.venv\Scripts\python register_context_menu.py install
```

**成功标志**：
```
✓ 右键菜单安装成功！
  类型: EXE
  路径: d:\Dropbox\DevProjects\Python\FoldPDF\dist\FoldPDF.exe

现在你可以在任意文件夹右键选择 'FoldPDF' 来快速转换
```

## 使用方法

### 通过右键菜单使用

1. 打开文件管理器
2. 导航到包含图片的文件夹
3. 右键菜单选择 **"FoldPDF - 批量生成PDF"**
4. 进度对话框弹出，显示实时进度
5. 等待完成或点击"取消"中断

### 通过命令行使用

```powershell
# 使用 exe 文件
dist\FoldPDF.exe "D:\Your\Folder\Path"

# 使用 Python 脚本（如果未编译 exe）
.venv\Scripts\python cli_convert.py "D:\Your\Folder\Path"
```

## 文件结构

编译完成后的目录结构：

```
FoldPDF/
├── dist/
│   └── FoldPDF.exe              ← 生成的 exe 文件
├── build/                        ← PyInstaller 临时文件
├── cli_convert.py               ← CLI 源代码
├── register_context_menu.py     ← 右键菜单注册脚本
├── install_context_menu.bat     ← 快速安装脚本
├── uninstall_context_menu.bat   ← 快速卸载脚本
├── build_cli_exe.py             ← exe 编译脚本
└── ...
```

## 卸载流程

### 卸载右键菜单

**以管理员身份**双击运行：
```
uninstall_context_menu.bat
```

或者手动运行：
```powershell
.venv\Scripts\python register_context_menu.py uninstall
```

### 删除 EXE 文件（可选）

如果想完全清理编译产物：

```powershell
# 删除 exe 文件
Remove-Item dist -Recurse -Force

# 删除 PyInstaller 临时文件
Remove-Item build -Recurse -Force
Remove-Item FoldPDF.spec -Force
```

## 高级配置

### 修改 EXE 编译参数

编辑 `build_cli_exe.py` 中的 `args` 列表来自定义编译选项：

```python
args = [
    str(cli_script),
    "--onefile",                    # 单文件
    "--windowed",                   # 无控制台（改为 "--console" 显示控制台）
    "--name=FoldPDF",               # exe 名称
    # ... 其他参数
]
```

常用参数：
- `--onefile` - 生成单一 exe
- `--windowed` - 无控制台窗口
- `--console` - 显示控制台窗口
- `--icon=path/to/icon.ico` - 设置 exe 图标

### 修改右键菜单显示文本

编辑 `register_context_menu.py` 中的：

```python
winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "FoldPDF - 批量生成PDF")
```

### 添加 EXE 图标

将 ico 文件放在项目目录，在 `build_cli_exe.py` 中添加：

```python
"--icon=" + str(script_dir / "app_icon.ico"),
```

## 故障排除

### 问题 1：编译时出现错误

**症状**：`UnicodeDecodeError`, `ModuleNotFoundError` 等

**解决方案**：
```powershell
# 清理缓存
Remove-Item dist, build -Recurse -Force 2>$null

# 重新编译
.venv\Scripts\python build_cli_exe.py
```

### 问题 2：EXE 文件很大（> 200 MB）

这是正常的，PyInstaller 会打包所有依赖库。可以通过参数优化大小：

编辑 `build_cli_exe.py`，添加 UPX 压缩（需要单独安装 UPX）。

### 问题 3：右键菜单没有显示

**检查清单**：
- [ ] 以管理员身份运行了 `install_context_menu.bat`
- [ ] `dist\FoldPDF.exe` 文件存在
- [ ] 注册表路径正确：`HKEY_CURRENT_USER\Software\Classes\Folder\shell\FoldPDF`

可以使用注册表编辑器（`regedit.exe`）验证。

### 问题 4：EXE 启动无反应

**检查**：
1. 确保 exe 文件有执行权限
2. 查看是否有杀毒软件阻止
3. 检查 `foldpdf.log` 日志文件

## 性能指标

- **EXE 文件大小**：~120-150 MB
- **启动时间**：< 2 秒（包括 PyQt 初始化）
- **内存占用**：100-200 MB（运行中）
- **单个 PDF 转换速度**：1-10 张/秒（取决于图片大小）

## 快速参考

```bash
# 完整流程（一键执行）
.venv\Scripts\python build_cli_exe.py     # 编译 exe
install_context_menu.bat                   # 安装右键菜单

# 测试 exe
dist\FoldPDF.exe "D:\test\folder"

# 卸载
uninstall_context_menu.bat
```

## 常见问题解答

**Q: EXE 文件可以单独分发吗？**  
A: 可以。编译后的 `dist\FoldPDF.exe` 是自包含的，可以复制到任何 Windows 系统使用。但如果要使用右键菜单，需要在目标系统上运行 `register_context_menu.py` 来注册。

**Q: 更新代码后需要重新编译吗？**  
A: 是的。修改 Python 代码后，需要重新运行 `build_cli_exe.py` 重新编译。

**Q: 能否跳过编译直接使用 Python 脚本？**  
A: 可以。如果删除了 `dist\FoldPDF.exe`，`register_context_menu.py` 会自动回退到使用 `cli_convert.py` 脚本。

**Q: 如何添加命令行参数（如修改纸张尺寸）？**  
A: 目前 CLI 使用固定配置。需要修改 `cli_convert.py` 中的 `page_size_name` 等参数或扩展命令行参数支持。

---

现在就开始吧！运行 `build_cli_exe.py` 编译你的第一个 FoldPDF.exe 文件！

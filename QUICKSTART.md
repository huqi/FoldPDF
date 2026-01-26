# FoldPDF 右键菜单功能 - 快速开始

## 一分钟快速安装

### 步骤 1：打开项目目录
```
d:\Dropbox\DevProjects\Python\FoldPDF
```

### 步骤 2：安装右键菜单（选一种方式）

#### 方式 A：双击批处理文件（推荐，最简单）
- 双击 **`install_context_menu.bat`** 文件
- 系统会要求管理员权限，点击"是"
- 看到"✓ 安装成功！"表示完成

#### 方式 B：使用 PowerShell（需要管理员权限）
```powershell
# 在 PowerShell 中以管理员身份运行
cd d:\Dropbox\DevProjects\Python\FoldPDF
python register_context_menu.py install
```

## 使用方法

### 1. 在文件管理器中使用
- 打开任意文件夹
- 右键菜单中选择 **"FoldPDF - 批量生成PDF"**
- 等待进度对话框显示
- 查看实时进度并可随时取消

### 2. 命令行使用
```powershell
# 使用 CLI 脚本
.venv\Scripts\python cli_convert.py "C:\Your\Folder\Path"
```

## 工作流程

```
右键点击文件夹
        ↓
选择 "FoldPDF - 批量生成PDF"
        ↓
CLI 快速启动（轻量级）
        ↓
扫描该目录及所有子目录
        ↓
进度对话框显示处理进度
        ↓
按需点击"取消"中断或等待完成
        ↓
各含图片的文件夹中生成 {文件夹名}.pdf
```

## 功能特点

✓ **极快启动速度** - 只加载必需的模块  
✓ **实时进度显示** - 显示已处理目录数  
✓ **随时可取消** - 点击取消按钮立即中断  
✓ **递归处理** - 自动处理所有子目录  
✓ **智能压缩** - 自动缩放和压缩图片  

## 卸载

如需移除右键菜单：
- 双击 **`uninstall_context_menu.bat`**，或
- 运行 `python register_context_menu.py uninstall`

## 常见问题

### Q: 右键菜单没有显示？
A: 
1. 确保以管理员身份运行了安装脚本
2. 可能需要重启文件管理器或系统
3. 检查 PowerShell 输出中是否有错误消息

### Q: 点击菜单后没反应？
A: 
1. 检查目录是否真的包含图片文件
2. 查看 `foldpdf.log` 了解详细错误
3. 尝试命令行方式测试：`.venv\Scripts\python cli_convert.py "你的文件夹路径"`

### Q: 如何修改配置（纸张尺寸、图片质量等）？
A: 编辑 `config.py` 文件中的全局参数或修改 `cli_convert.py` 中第 99-102 行的默认值

## 文件说明

- **`cli_convert.py`** - 轻量级 CLI 入口脚本
- **`register_context_menu.py`** - 右键菜单注册脚本
- **`install_context_menu.bat`** - 快速安装脚本
- **`uninstall_context_menu.bat`** - 快速卸载脚本
- **`CONTEXT_MENU_README.md`** - 详细文档

## 性能指标

- **启动时间**：< 1 秒（不包括扫描和转换）
- **内存占用**：轻量级，仅在处理图片时占用内存
- **转换速度**：取决于图片数量和尺寸，通常 1-10 张/秒

## 下一步

现在就试试吧！打开文件管理器，在任意包含图片的文件夹右键选择 "FoldPDF"！

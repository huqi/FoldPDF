# FoldPDF 右键菜单功能说明

## 功能介绍

该功能允许你在 Windows 文件管理器中，对任意文件夹右键选择 **FoldPDF**，快速将该目录及所有子目录中的图片转换为 PDF 文件。

## 安装步骤

### 1. 注册右键菜单

打开命令提示符或 PowerShell，**以管理员身份**运行：

```powershell
# 进入项目目录
cd d:\Dropbox\DevProjects\Python\FoldPDF

# 以管理员身份运行（PowerShell中）
python register_context_menu.py install
```

### 2. 验证安装

在文件管理器中任选一个文件夹，右键菜单中应该能看到 **"FoldPDF - 批量生成PDF"** 选项。

## 使用方法

### 方式一：通过右键菜单（推荐）

1. 在文件管理器中选中一个包含图片的文件夹
2. 右键选择 **"FoldPDF - 批量生成PDF"**
3. 等待进度对话框显示，可以实时查看处理进度
4. 点击 **"取消"** 按钮可以中断转换
5. 转换完成后，PDF 文件会生成在各个含图片的子目录内

### 方式二：通过命令行

```powershell
# 基本用法
python cli_convert.py "D:\path\to\folder"

# 示例
python cli_convert.py "D:\Documents\MyPhotos"
```

## 输出说明

- 每个包含图片的文件夹内会生成一个 PDF 文件，命名为 `文件夹名.pdf`
- 原始图片文件不会被删除或修改
- PDF 中的图片会根据配置进行压缩和优化

## 配置选项

CLI 模式目前使用以下默认配置：
- 纸张尺寸：A4
- 自动旋转：启用
- 图片质量：80（由 config.py 中的 IMAGE_QUALITY 决定）

如需修改，可以编辑 `config.py` 文件或修改 `cli_convert.py` 中的参数。

## 卸载右键菜单

如需移除右键菜单，**以管理员身份**运行：

```powershell
python register_context_menu.py uninstall
```

## 性能特点

- **快速启动**：仅在开始转换时导入重型模块（PIL、img2pdf 等）
- **内存优化**：及时释放已处理的图片数据
- **进度反馈**：实时显示已处理的目录数和总进度
- **可随时取消**：点击取消按钮可立即中断转换

## 故障排除

### 问题：运行 register_context_menu.py 时报错

**解决方案**：需要以管理员身份运行。在 PowerShell 中右键选择"以管理员身份运行"，或使用 UAC 提示。

### 问题：右键菜单没有显示

**解决方案**：
1. 确保脚本已经以管理员身份运行
2. 注册表修改可能需要重启才能生效
3. 可以手动检查注册表 `HKEY_CURRENT_USER\Software\Classes\Folder\shell\FoldPDF`

### 问题：点击右键菜单后没有响应

**解决方案**：
1. 检查目录中是否真的包含图片文件
2. 查看 `foldpdf.log` 日志文件了解详细错误信息
3. 尝试通过命令行直接运行 CLI 脚本测试

## 日志文件

程序会在项目目录生成 `foldpdf.log` 日志文件，记录所有转换过程。出现问题时可以查阅此文件。

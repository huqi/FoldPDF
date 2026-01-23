import sys
import os
import io
import platform
import subprocess
from PyQt6.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QStandardPaths
from ui_main import FoldPDFWindow
from config import (
    MAX_IMAGE_SIZE, IMAGE_QUALITY, IMAGE_OPTIMIZE,
    VALID_IMAGE_EXTENSIONS, PAGE_SIZES
)
from logger import logger

# 延迟导入重型模块 - 在使用时才导入，加快启动速度
def _import_img2pdf():
    global img2pdf
    if 'img2pdf' not in globals():
        import img2pdf
    return img2pdf

def _import_natsort():
    global natsorted
    if 'natsorted' not in globals():
        from natsort import natsorted
    return natsorted

def _import_pil():
    global Image
    if 'Image' not in globals():
        from PIL import Image
    return Image


# --- 核心转换后台线程 ---
class BatchConvertThread(QThread):
    # 定义信号：(当前文件夹名, 当前步骤进度0-100, 总体进度百分比, 已完成任务数)
    progress_update = pyqtSignal(str, int, int, int)
    finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)  # 新增：日志信号

    def __init__(self, task_list, page_size_name, auto_rotate):
        super().__init__()
        self.task_list = task_list
        self.page_size_name = page_size_name
        self.auto_rotate = auto_rotate
        self._is_running = True

    def stop(self):
        """停止转换线程"""
        self._is_running = False
        logger.info("转换线程已停止")

    def run(self):
        try:
            # 在循环前导入一次重型模块，避免循环中重复调用
            Image = _import_pil()
            img2pdf = _import_img2pdf()
            
            page_sizes = PAGE_SIZES
            base_w, base_h = page_sizes[self.page_size_name]
            total_tasks = len(self.task_list)
            logger.info(f"开始转换 {total_tasks} 个任务，纸张尺寸: {self.page_size_name}")
            
            for index, (folder_path, images) in enumerate(self.task_list):
                if not self._is_running:
                    logger.info("转换已被用户取消")
                    break
                    
                folder_name = os.path.basename(folder_path)
                logger.debug(f"处理文件夹: {folder_name} ({index + 1}/{total_tasks})")
                self.progress_update.emit(folder_name, 0, int((index / total_tasks) * 100), index)
                self.log_message.emit(f"处理中: {folder_name}")

                processed_images = []
                for img_path in images:
                    if not self._is_running:
                        break
                        
                    try:
                        with Image.open(img_path) as img:
                            # --- 核心优化：智能缩放与压缩 ---
                            # 1. 转换模式
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            
                            # 2. 智能缩放：如果图片分辨率极高，限制其长边为 2560px (2K级别)
                            if max(img.size) > MAX_IMAGE_SIZE:
                                img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
                                logger.debug(f"已缩放: {os.path.basename(img_path)} -> {img.size}")
                            
                            # 3. 内存压缩
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='JPEG', quality=IMAGE_QUALITY, optimize=IMAGE_OPTIMIZE)
                            processed_images.append(img_byte_arr.getvalue())
                    except Exception as e:
                        logger.warning(f"处理图片失败 {img_path}: {e}")
                        continue

                if not processed_images:
                    logger.warning(f"文件夹 {folder_name} 没有有效的图片")
                    self.log_message.emit(f"⚠️  {folder_name}: 无有效图片")
                    processed_images.clear()
                    self.progress_update.emit(folder_name, 100, int(((index + 1) / total_tasks) * 100))
                    continue

                # 适配你之前 get_resize 逻辑的布局函数
                def my_layout(image_width_pt, image_height_pt, *args):
                    tw, th = base_w, base_h
                    if self.auto_rotate and image_width_pt > image_height_pt:
                        tw, th = base_h, base_w # 自动切横向
                    
                    wi, hi = tw / image_width_pt, th / image_height_pt
                    factor = min(wi, hi, 1) # 维持你以前的逻辑：不放大，只缩小
                    return (tw, th, image_width_pt * factor, image_height_pt * factor)

                output_pdf_path = os.path.join(folder_path, f"{folder_name}.pdf")
                
                try:
                    with open(output_pdf_path, "wb") as f:
                        f.write(img2pdf.convert(processed_images, layout_fun=my_layout))
                    logger.info(f"成功生成: {output_pdf_path}")
                    self.log_message.emit(f"✓ {folder_name}")
                except Exception as e:
                    logger.error(f"PDF 生成失败 {folder_name}: {e}")
                    self.log_message.emit(f"✗ {folder_name}: {str(e)}")
                    raise
                
                # --- 核心优化：及时释放内存 ---
                processed_images.clear() 
                self.progress_update.emit(folder_name, 100, int(((index + 1) / total_tasks) * 100), index + 1)

            if self._is_running:
                logger.info("所有转换任务已完成")
                self.finished.emit(True, f"处理完成！PDF 已生成在各子目录内。")
            else:
                self.finished.emit(False, "转换已被中断")
        except Exception as e:
            logger.error(f"转换失败: {str(e)}")
            self.finished.emit(False, f"转换失败: {str(e)}")

# --- 主程序逻辑 ---
class FoldPDFApp(FoldPDFWindow):
    def __init__(self):
        super().__init__()
        self.all_tasks = []  # 存储格式: [(文件夹绝对路径, [图片路径列表]), ...]
        self.root_folder = None  # 保存拖拽进去的根目录
        self.worker = None
        logger.info("应用启动")
        
        # 连接 UI 信号与逻辑函数
        self.folderDropped.connect(self.handle_drop)
        self.clickedSelect.connect(self.open_dialog)
        self.btn_convert.clicked.connect(self.start_batch_conversion)
        self.btn_cancel.clicked.connect(self.cancel_conversion)

    def open_dialog(self):
        """点击触发：默认打开桌面"""
        desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        path = QFileDialog.getExistingDirectory(self, "选择包含图片的根目录", desktop)
        if path:
            logger.debug(f"用户选择目录: {path}")
            self.handle_drop(path)

    def handle_drop(self, path):
        """处理路径导入（拖拽或选择）"""
        if not os.path.isdir(path):
            return
        
        self.root_folder = path  # 保存根目录
        self.file_tree.clear()
        self.all_tasks = []
        self.total_progress_bar.setValue(0)
        
        # 创建根节点
        root_item = QTreeWidgetItem(self.file_tree)
        root_item.setText(0, os.path.basename(path))
        root_item.setExpanded(True)

        # 递归扫描并构建树
        self.scan_directory(path, root_item)
        
        if self.all_tasks:
            self.task_stats_label.setText(f"待处理：共 {len(self.all_tasks)} 个含图目录")
            self.btn_convert.setEnabled(True)
            self.status_label.setText("准备就绪")
        else:
            self.status_label.setText("未在目录下发现任何图片文件")
            self.btn_convert.setEnabled(False)

    def scan_directory(self, current_path, parent_item):
        """递归扫描核心算法：实现自然排序"""
        valid_exts = VALID_IMAGE_EXTENSIONS
        try:
            # 使用 natsorted 替代原生 sorted，确保 1.jpg < 2.jpg < 10.jpg
            natsorted_fn = _import_natsort()
            items = natsorted_fn(os.listdir(current_path))
        except OSError as e:
            logger.warning(f"无法访问目录 {current_path}: {e}")
            return

        current_folder_images = []
        
        for name in items:
            full_path = os.path.join(current_path, name)
            if os.path.isdir(full_path):
                # 发现子目录，创建节点并递归
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, name)
                self.scan_directory(full_path, child_item)
            elif name.lower().endswith(valid_exts):
                # 发现图片文件
                current_folder_images.append(full_path)
                file_item = QTreeWidgetItem(parent_item)
                file_item.setText(0, name)
                file_item.setForeground(0, Qt.GlobalColor.gray) # 灰色显示文件名

        # 如果这个文件夹内有图，就加入待转换任务列表
        if current_folder_images:
            self.all_tasks.append((current_path, current_folder_images))
            logger.debug(f"添加任务: {current_path} ({len(current_folder_images)} 张图片)")

    def start_batch_conversion(self):
        """启动转换线程"""
        self.btn_convert.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.status_label.setText("正在初始化转换任务...")
        logger.info("启动转换任务")
        
        self.worker = BatchConvertThread(
            self.all_tasks, 
            self.size_combo.currentText(),
            self.check_auto_rotate.isChecked()
        )
        self.worker.progress_update.connect(self.update_ui_progress)
        self.worker.log_message.connect(self.add_log_message)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def cancel_conversion(self):
        """取消转换"""
        if self.worker:
            logger.info("用户取消了转换")
            self.worker.stop()
            self.btn_cancel.setEnabled(False)
            self.status_label.setText("正在停止转换...")

    def add_log_message(self, message):
        """添加日志消息到 UI"""
        self.log_output.appendPlainText(message)

    def update_ui_progress(self, folder_name, current_val, total_val, processed):
        self.status_label.setText(f"当前处理: {folder_name}")
        self.current_progress_bar.setValue(current_val)
        self.total_progress_bar.setValue(total_val)
        
        # 直接显示已处理的任务数
        self.task_stats_label.setText(f"进度：{processed} / {len(self.all_tasks)} 目录")

    def on_finished(self, success, message):
        self.btn_convert.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.status_label.setText(message)
        
        if success:
            logger.info("转换成功完成")
            self.total_progress_bar.setValue(100)
            self.current_progress_bar.setValue(100)
            
            # 自动打开根目录
            if self.root_folder:
                self.open_output_folder(self.root_folder)
        else:
            logger.warning(f"转换失败: {message}")

    def open_output_folder(self, folder_path):
        """打开输出文件夹"""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", folder_path])
            logger.info(f"已打开文件夹: {folder_path}")
        except Exception as e:
            logger.error(f"无法打开文件夹: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FoldPDFApp()
    window.show()
    sys.exit(app.exec())
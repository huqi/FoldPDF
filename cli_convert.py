"""
FoldPDF CLI 模式 - 轻量级命令行入口
用于右键菜单快速启动
"""

import sys
import os
import io
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QProgressBar, QPushButton
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from config import (
    MAX_IMAGE_SIZE, IMAGE_QUALITY, IMAGE_OPTIMIZE,
    VALID_IMAGE_EXTENSIONS, PAGE_SIZES
)


class ProgressDialog(QDialog):
    """简洁高效的进度对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FoldPDF - 批量压缩中")
        self.setGeometry(100, 100, 500, 120)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 信息标签（显示进度和文件夹）
        self.info_label = QLabel("(0/0) -- 准备中...")
        main_layout.addWidget(self.info_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)
        
        # 按钮布局（居中）
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumWidth(80)
        self.cancel_btn.setMinimumHeight(30)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        self.worker = None
        
        # 窗口居中
        self.center_window()
    
    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


class BatchConvertThread(QThread):
    """后台转换线程"""
    progress_update = pyqtSignal(str, int, int, int)  # (folder_name, current_progress, processed_count, total_count)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, root_folder, page_size_name="A4", auto_rotate=True, image_quality=None):
        super().__init__()
        self.root_folder = root_folder
        self.page_size_name = page_size_name
        self.auto_rotate = auto_rotate
        self.image_quality = image_quality if image_quality is not None else IMAGE_QUALITY
        self._is_running = True
        self.task_list = []
        self.total_tasks = 0
        
    def stop(self):
        """停止转换"""
        self._is_running = False
    
    def scan_directory(self, current_path):
        """递归扫描目录，收集所有含图片的文件夹"""
        valid_exts = VALID_IMAGE_EXTENSIONS
        current_folder_images = []
        
        try:
            items = os.listdir(current_path)
        except OSError as e:
            return
        
        for name in items:
            full_path = os.path.join(current_path, name)
            if os.path.isdir(full_path):
                # 递归扫描子目录
                self.scan_directory(full_path)
            elif name.lower().endswith(valid_exts):
                current_folder_images.append(full_path)
        
        # 如果这个文件夹内有图，就加入任务列表
        if current_folder_images:
            self.task_list.append((current_path, current_folder_images))
    
    def run(self):
        try:
            # 延迟导入重型模块
            from PIL import Image
            import img2pdf
            from natsort import natsorted
            
            # 扫描目录
            self.scan_directory(self.root_folder)
            self.total_tasks = len(self.task_list)
            
            if self.total_tasks == 0:
                self.finished.emit(False, "未找到任何含图片的目录")
                return
            
            
            page_sizes = PAGE_SIZES
            base_w, base_h = page_sizes[self.page_size_name]
            
            for index, (folder_path, images) in enumerate(self.task_list):
                if not self._is_running:
                    logger.info("转换已被用户取消")
                    self.finished.emit(False, "已取消")
                    break
                
                folder_name = os.path.basename(folder_path)
                
                # 发送更新信号
                self.progress_update.emit(folder_name, 0, index, self.total_tasks)
                
                processed_images = []
                for img_path in images:
                    if not self._is_running:
                        break
                    
                    try:
                        with Image.open(img_path) as img:
                            # 转换模式
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            
                            # 智能缩放
                            if max(img.size) > MAX_IMAGE_SIZE:
                                img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
                            
                            # 内存压缩
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='JPEG', quality=self.image_quality, optimize=IMAGE_OPTIMIZE)
                            processed_images.append(img_byte_arr.getvalue())
                    except Exception as e:
                        continue
                
                if not processed_images:
                    processed_images.clear()
                    self.progress_update.emit(folder_name, 100, index + 1, self.total_tasks)
                    continue
                
                # 布局函数
                def my_layout(image_width_pt, image_height_pt, *args):
                    tw, th = base_w, base_h
                    if self.auto_rotate and image_width_pt > image_height_pt:
                        tw, th = base_h, base_w
                    
                    wi, hi = tw / image_width_pt, th / image_height_pt
                    factor = min(wi, hi, 1)
                    return (tw, th, image_width_pt * factor, image_height_pt * factor)
                
                output_pdf_path = os.path.join(folder_path, f"{folder_name}.pdf")
                
                try:
                    with open(output_pdf_path, "wb") as f:
                        f.write(img2pdf.convert(processed_images, layout_fun=my_layout))
                except Exception as e:
                    raise
                
                processed_images.clear()
                self.progress_update.emit(folder_name, 100, index + 1, self.total_tasks)
            
            if self._is_running:
                self.finished.emit(True, f"处理完成！已生成 {self.total_tasks} 个 PDF")
        
        except Exception as e:
            self.finished.emit(False, f"转换失败: {str(e)}")


class CLIConverter:
    """CLI 模式转换器"""
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.dialog = ProgressDialog()
        self.worker = None
        
    def start(self):
        """启动转换"""
        self.worker = BatchConvertThread(
            self.folder_path,
            page_size_name="A4",
            auto_rotate=True,
            image_quality=IMAGE_QUALITY
        )
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.dialog.cancel_btn.clicked.connect(self.cancel_conversion)
        
        self.dialog.show()
        self.worker.start()
        
        return self.app.exec()
    
    def update_progress(self, folder_name, progress, processed, total):
        """更新进度"""
        # 截断过长的文件夹名称
        display_name = folder_name
        if len(display_name) > 40:
            display_name = "..." + display_name[-37:]
        
        # 显示为 "(已处理/总数) -- 文件夹名" 的格式
        info_text = f"({processed}/{total}) -- {display_name}"
        self.dialog.info_label.setText(info_text)
        
        # 更新进度条（总体进度比）
        if total > 0:
            overall_progress = int((processed / total) * 100)
        else:
            overall_progress = 0
        self.dialog.progress_bar.setValue(overall_progress)
    
    def cancel_conversion(self):
        """取消转换"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        self.dialog.close()
    
    def on_finished(self, success, message):
        """转换完成"""
        self.dialog.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    
    folder_path = sys.argv[1]
    if not os.path.isdir(folder_path):
        sys.exit(1)
    
    converter = CLIConverter(folder_path)
    sys.exit(converter.start())

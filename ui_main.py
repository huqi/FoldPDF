from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QProgressBar, QPushButton, 
                             QFrame, QCheckBox, QTreeWidget, QHeaderView, QPlainTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_ICON

class FoldPDFWindow(QMainWindow):
    # 定义自定义信号（必须在类级别定义）
    folderDropped = pyqtSignal(str)
    clickedSelect = pyqtSignal()  

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(WINDOW_ICON))
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT + 150)  # 增加高度以容纳日志
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 1. 拖拽/点击感应区
        self.drop_frame = QFrame()
        self.drop_frame.setObjectName("DropFrame")
        self.drop_frame.setAcceptDrops(True)
        self.drop_frame.setStyleSheet("""
            #DropFrame {
                border: 2px dashed #3498db;
                border-radius: 12px;
                background-color: #f8fafd;
            }
            #DropFrame:hover {
                background-color: #ebf5fb;
            }
        """)
        
        drop_layout = QVBoxLayout(self.drop_frame)
        self.drop_label = QLabel("将文件夹拖到这里\n或点击此处选择")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet("color: #3498db; font-size: 14px; font-weight: bold;")
        drop_layout.addWidget(self.drop_label)
        main_layout.addWidget(self.drop_frame, stretch=1)

        # 2. 树形文件列表
        main_layout.addWidget(QLabel("目录结构:"))
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("名称")
        self.file_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.file_tree.setStyleSheet("QTreeWidget { border: 1px solid #dcdde1; border-radius: 5px; }")
        main_layout.addWidget(self.file_tree, stretch=3)

        # 3. 设置区
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("尺寸:"))
        self.size_combo = QComboBox()
        self.size_combo.addItems(["A4", "A3", "B5"])
        settings_layout.addWidget(self.size_combo)
        
        settings_layout.addSpacing(15)
        self.check_auto_rotate = QCheckBox("允许自动横向")
        self.check_auto_rotate.setChecked(True)
        settings_layout.addWidget(self.check_auto_rotate)
        settings_layout.addStretch()
        main_layout.addLayout(settings_layout)

        # 4. 进度反馈区
        self.task_stats_label = QLabel("状态: 等待导入")
        self.task_stats_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(self.task_stats_label)

        self.total_progress_bar = QProgressBar()
        self.total_progress_bar.setFixedHeight(12)
        self.total_progress_bar.setStyleSheet("""
            QProgressBar { background: #ecf0f1; border-radius: 6px; text-align: center; font-size: 9px; }
            QProgressBar::chunk { background: #3498db; border-radius: 6px; }
        """)
        main_layout.addWidget(self.total_progress_bar)

        self.current_progress_bar = QProgressBar()
        self.current_progress_bar.setFixedHeight(4)
        self.current_progress_bar.setTextVisible(False)
        main_layout.addWidget(self.current_progress_bar)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        main_layout.addWidget(self.status_label)

        # 5. 按钮
        button_layout = QHBoxLayout()
        
        self.btn_convert = QPushButton("开始生成 FoldPDF")
        self.btn_convert.setMinimumHeight(45)
        self.btn_convert.setEnabled(False)
        self.btn_convert.setStyleSheet("""
            QPushButton { background: #3498db; color: white; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #2980b9; }
            QPushButton:disabled { background: #bdc3c7; }
        """)
        button_layout.addWidget(self.btn_convert)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.setMaximumWidth(100)
        self.btn_cancel.setStyleSheet("""
            QPushButton { background: #e74c3c; color: white; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #c0392b; }
            QPushButton:disabled { background: #bdc3c7; }
        """)
        button_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(button_layout)
        
        # 6. 日志输出面板
        main_layout.addWidget(QLabel("处理日志:"))
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(120)
        self.log_output.setStyleSheet("QPlainTextEdit { border: 1px solid #dcdde1; border-radius: 5px; background-color: #f5f5f5; }")
        main_layout.addWidget(self.log_output)

    # 事件处理
    def mousePressEvent(self, event):
        if self.drop_frame.geometry().contains(event.pos()):
            self.clickedSelect.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.folderDropped.emit(urls[0].toLocalFile())
"""
FoldPDF 配置文件
包含所有全局配置参数
"""

import os
from pathlib import Path

# ===== 图片处理配置 =====
# 最大图片分辨率（长边），超过此值会缩小。推荐 2560 (2K) 或 1920 (1080p)
MAX_IMAGE_SIZE = 2560

# JPEG 压缩质量 (1-100)，推荐 75-85 平衡质量和文件大小
IMAGE_QUALITY = 80

# 是否启用图片优化压缩
IMAGE_OPTIMIZE = True

# ===== 支持的图片格式 =====
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

# ===== 纸张尺寸配置（单位：毫米）=====
MM_TO_PT = lambda mm: mm * 72 / 25.4

PAGE_SIZES = {
    "A4": (MM_TO_PT(210), MM_TO_PT(297)),
    "A3": (MM_TO_PT(420), MM_TO_PT(297)),
    "B5": (MM_TO_PT(176), MM_TO_PT(250)),
}

# ===== UI 配置 =====
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 650
WINDOW_TITLE = "FoldPDF - 文件夹转PDF工具"
WINDOW_ICON = "app_icon.ico"

# ===== 日志配置 =====
LOG_ENABLED = True
LOG_FILE = "foldpdf.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# ===== 线程配置 =====
THREAD_TIMEOUT = 300  # 单个任务超时（秒）

# ===== 文件输出配置 =====
PDF_SUFFIX = ".pdf"  # PDF 文件后缀
OVERWRITE_PDF = True  # 是否覆盖已存在的 PDF

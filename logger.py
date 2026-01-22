"""
FoldPDF 日志模块
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_ENABLED, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT


def setup_logger(name: str = "FoldPDF") -> logging.Logger:
    """初始化日志记录器"""
    logger = logging.getLogger(name)
    
    if logger.handlers:  # 避免重复添加处理器
        return logger
    
    if not LOG_ENABLED:
        logger.disabled = True
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # 日志格式
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带文件轮转）
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"无法创建日志文件: {e}")
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# 全局日志记录器
logger = setup_logger()

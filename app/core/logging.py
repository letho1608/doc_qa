"""
Logging configuration for RAG System
"""
import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "rag_system.log", level: int = logging.INFO):
    """
    Cấu hình logging cho ứng dụng
    
    Args:
        log_file: Tên file log
        level: Logging level
    """
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    return root_logger


# Initialize logging
logger = setup_logging()

"""
log_service

Centralized logging service — generic, dùng cho mọi dự án.

Usage:
    from log_service import setup_logging, get_logger

    # main.py — gọi một lần
    setup_logging(project_name="crawler")

    # bất kỳ module nào
    logger = get_logger(__name__)
"""

from .logger import get_logger, get_class_logger, setup_logging

__all__ = ["get_logger", "get_class_logger", "setup_logging"]
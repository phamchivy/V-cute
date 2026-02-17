"""
log_service/logger.py

Core logging module — generic, dùng được cho mọi dự án.
Không biết gì về schema config hay tên module của dự án cụ thể.
"""

import logging
import logging.config
import os
import yaml
from pathlib import Path
from typing import Optional
from config import get_project_root, load_config

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_PROJECT_NAME = "app"

def _resolve_log_dir() -> Path:
    """
    Xác định thư mục lưu log dựa trên APP_ENV.

    - test / không set → log_service/log_files/
    - production       → đọc từ LOG_DIR env var (bắt buộc phải set)

    Raises:
        EnvironmentError: Nếu APP_ENV=production nhưng LOG_DIR chưa set
    """
    env = os.getenv("APP_ENV", "test").lower()

    if env == "production":
        log_dir = os.getenv("LOG_DIR")
        if not log_dir:
            raise EnvironmentError(
                "APP_ENV=production requires LOG_DIR env var to be set.\n"
                "Example: export LOG_DIR=/var/log/myapp"
            )
        return Path(log_dir)

    # test hoặc mọi giá trị khác → local
    return get_project_root() / "log_service" / "log_files"


# ---------------------------------------------------------------------------
# LoggerManager — Singleton
# ---------------------------------------------------------------------------

class LoggerManager:
    """
    Singleton quản lý cấu hình logging toàn ứng dụng.
    Setup một lần duy nhất tại entry point (main.py).
    Các module khác chỉ gọi get_logger() — không cần biết setup đã chạy chưa.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not LoggerManager._initialized:
            self._project_name: Optional[str] = None
            self._log_dir: Optional[Path] = None
            LoggerManager._initialized = True

    def setup(
        self,
        project_name: str = _DEFAULT_PROJECT_NAME,
        config_path: Optional[Path] = None,
    ) -> None:
        """
        Khởi tạo hệ thống logging. Gọi một lần duy nhất tại main.py.

        Args:
            project_name: Tên dự án — dùng để đặt tên file log.
                          Ví dụ: "crawler" → log_files/crawler.log
            config_path:  Override đường dẫn logging_config.yaml nếu cần.
                          Mặc định: config/logging_config.yaml tại project root.
        """
        self._project_name = project_name
        self._log_dir = _resolve_log_dir()
        self._log_dir.mkdir(parents=True, exist_ok=True)

        config = load_config("logging_config") if config_path is None else yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))

        # Inject log file path động vào handler file_all
        log_file = self._log_dir / f"{project_name}.log"
        config["handlers"]["file_all"]["filename"] = str(log_file)

        logging.config.dictConfig(config)

        # Banner khởi động
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info(f"Logging initialized | project={project_name}")
        logger.info(f"APP_ENV : {os.getenv('APP_ENV', 'test')}")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 60)

    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)


# ---------------------------------------------------------------------------
# Singleton instance + public API
# ---------------------------------------------------------------------------

_manager = LoggerManager()


def setup_logging(
    project_name: str = _DEFAULT_PROJECT_NAME,
    config_path: Optional[Path] = None,
) -> None:
    """
    Khởi tạo logging — gọi một lần tại entry point.

    Args:
        project_name: Tên dự án để đặt tên log file.
        config_path:  Override đường dẫn logging_config.yaml nếu cần.
    """
    _manager.setup(project_name=project_name, config_path=config_path)


def get_logger(name: str) -> logging.Logger:
    """
    Lấy logger cho một module. Gọi tự do ở bất kỳ đâu,
    kể cả trước setup_logging() — Python logging tự xử lý lazy binding.

    Args:
        name: Tên module, thường là __name__

    Example:
        logger = get_logger(__name__)
        logger.info("Starting...")
    """
    return _manager.get_logger(name)


def get_class_logger(cls) -> logging.Logger:
    """
    Lấy logger gắn với tên đầy đủ của một class.

    Example:
        class MyCrawler:
            def __init__(self):
                self.logger = get_class_logger(self.__class__)
    """
    return logging.getLogger(f"{cls.__module__}.{cls.__name__}")
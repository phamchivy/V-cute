"""
config/__init__.py

Generic configuration module — dùng được cho mọi dự án.
Mỗi dự án tạo một subclass riêng, không sửa Config gốc.

Usage:
    from config import CrawlerConfig, load_config

    cfg = CrawlerConfig(load_config("crawl_config"))
    print(cfg.base_url)
"""

from pathlib import Path
import yaml
import os

# ---------------------------------------------------------------------------
# Project root — tính một lần duy nhất
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.absolute()


def get_project_root() -> Path:
    """Trả về absolute path của project root."""
    return PROJECT_ROOT


# ---------------------------------------------------------------------------
# YAML loader
# ---------------------------------------------------------------------------

def load_config(config_name: str) -> dict:
    """
    Load file YAML từ thư mục config/.

    Args:
        config_name: Tên file không có đuôi .yaml
                     Ví dụ: "crawl_config" → config/crawl_config.yaml

    Returns:
        dict parsed từ YAML

    Raises:
        FileNotFoundError: Nếu file không tồn tại
        ValueError: Nếu file YAML rỗng hoặc parse thất bại
    """
    config_path = PROJECT_ROOT / "config" / f"{config_name}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Expected location: config/{config_name}.yaml"
        )

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(f"Config file is empty or invalid YAML: {config_path}")

    return data


# ---------------------------------------------------------------------------
# Base Config — generic, không biết schema cụ thể
# ---------------------------------------------------------------------------

class Config:
    """
    Generic config wrapper — dùng được cho mọi dự án.

    Không hardcode bất kỳ key nào. Chỉ cung cấp:
    - Truy xuất nested key an toàn qua get()
    - Truy xuất raw dict qua raw()

    Không bao giờ cần sửa class này khi thêm dự án mới.
    """

    def __init__(self, cfg: dict):
        if not isinstance(cfg, dict):
            raise TypeError(f"Config expects a dict, got {type(cfg).__name__}")
        self._cfg = cfg

    def get(self, *keys, default=None):
        """
        Truy xuất nested key an toàn.

        Example:
            self.get("base", "base_url")
            # tương đương cfg["base"]["base_url"] nhưng không raise exception
        """
        val = self._cfg
        for key in keys:
            if not isinstance(val, dict):
                return default
            val = val.get(key, default)
        return val

    def require(self, *keys):
        """
        Truy xuất nested key — raise nếu không tồn tại hoặc None.
        Dùng cho các key bắt buộc phải có trong config.

        Raises:
            KeyError: Nếu key không tồn tại
        """
        val = self.get(*keys)
        if val is None:
            key_path = " → ".join(str(k) for k in keys)
            raise KeyError(f"Required config key missing: {key_path}")
        return val

    def raw(self) -> dict:
        """Trả về raw dict gốc nếu cần truy cập trực tiếp."""
        return self._cfg

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(keys={list(self._cfg.keys())})"


# ---------------------------------------------------------------------------
# CrawlerConfig — specific cho crawl_config.yaml
# ---------------------------------------------------------------------------

class CrawlerConfig(Config):
    """
    Project-specific config cho Hùng Phát crawler.

    Ánh xạ crawl_config.yaml → Python attributes.
    Hỗ trợ override qua biến môi trường (ưu tiên cao hơn yaml).

    Nếu schema yaml thay đổi → chỉ sửa class này, không đụng Config.
    """

    def __init__(self, cfg: dict):
        super().__init__(cfg)

        # --- Base request settings ---
        self.base_url: str  = self.require("base", "base_url")
        self.delay: float   = self.get("base", "delay_between_requests", default=2)
        self.timeout: int   = self.get("base", "request_timeout", default=10)
        self.max_retries: int = self.get("base", "max_retries", default=3)

        # --- Directory settings (env override → yaml fallback) ---
        _default_base = PROJECT_ROOT / self.require("crawler", "base_dir")
        self.base_dir: Path = Path(os.getenv("BASE_DIR", str(_default_base)))

        self.raw_data_dir: Path = Path(os.getenv(
            "RAW_DATA_DIR",
            str(self.base_dir / self.get("crawler", "raw_data_dir", default="raw_data"))
        ))

        self.processed_data_dir: Path = Path(os.getenv(
            "PROCESSED_DATA_DIR",
            str(self.base_dir / self.get("crawler", "processed_data_dir", default="processed_data"))
        ))

        self.images_dir: Path = Path(os.getenv(
            "IMAGES_DIR",
            str(self.base_dir / self.get("crawler", "images_dir", default="images"))
        ))

        self.metadata_dir: Path = Path(os.getenv(
            "METADATA_DIR",
            str(self.base_dir / self.get("crawler", "metadata_dir", default="metadata"))
        ))

        # --- Crawler assets ---
        self.user_agents: list       = self.get("user_agents", default=[])
        self.category_keywords: dict = self.get("category_keywords", default={})

    def __repr__(self) -> str:
        return (
            f"CrawlerConfig("
            f"base_url={self.base_url!r}, "
            f"base_dir={self.base_dir}, "
            f"delay={self.delay}s)"
        )
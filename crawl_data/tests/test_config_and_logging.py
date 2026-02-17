"""
tests/test_config_and_logging.py

Test thủ công cho 2 module: config và log_service.
Chạy từ project root:
    python tests/test_config_and_logging.py
"""

import sys
from pathlib import Path

# Đảm bảo import được từ project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_project_root, load_config, CrawlerConfig
from log_service import setup_logging, get_logger


# ---------------------------------------------------------------------------
# Test 1: PROJECT_ROOT
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("TEST 1: PROJECT_ROOT")
print("=" * 60)

root = get_project_root()
print(f"PROJECT_ROOT : {root}")
print(f"Exists       : {root.exists()}")


# ---------------------------------------------------------------------------
# Test 2: load_config raw
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("TEST 2: load_config('crawl_config') — raw dict")
print("=" * 60)

raw = load_config("crawl_config")
print(f"Keys         : {list(raw.keys())}")
print(f"base_url     : {raw['base']['base_url']}")


# ---------------------------------------------------------------------------
# Test 3: CrawlerConfig attributes
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("TEST 3: CrawlerConfig attributes")
print("=" * 60)

cfg = CrawlerConfig(raw)
print(f"base_url          : {cfg.base_url}")
print(f"delay             : {cfg.delay}")
print(f"timeout           : {cfg.timeout}")
print(f"max_retries       : {cfg.max_retries}")
print(f"base_dir          : {cfg.base_dir}")
print(f"raw_data_dir      : {cfg.raw_data_dir}")
print(f"processed_data_dir: {cfg.processed_data_dir}")
print(f"images_dir        : {cfg.images_dir}")
print(f"metadata_dir      : {cfg.metadata_dir}")
print(f"user_agents count : {len(cfg.user_agents)}")
print(f"category_keywords : {list(cfg.category_keywords.keys())}")
print(f"repr              : {cfg!r}")


# ---------------------------------------------------------------------------
# Test 4: setup_logging + get_logger
# ---------------------------------------------------------------------------

print("\n" + "=" * 60)
print("TEST 4: setup_logging + get_logger")
print("=" * 60)

setup_logging(project_name="test_run")

logger = get_logger(__name__)
logger.debug("DEBUG message — chỉ thấy trong file log")
logger.info("INFO message — thấy cả console lẫn file log")
logger.warning("WARNING message")
logger.error("ERROR message")

print("\nKiểm tra:")
print("- Console: thấy INFO / WARNING / ERROR ở trên")
print("- File   : log_service/log_files/test_run.log")
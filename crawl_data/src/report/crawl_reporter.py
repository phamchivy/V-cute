"""
src/report/crawl_reporter.py

Chỉ trách nhiệm: tổng hợp và in summary report sau khi crawl xong.
Không fetch, không lưu product data, không classify.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List

from config import CrawlerConfig
from log_service import get_logger
from src.models import Product

logger = get_logger(__name__)


class CrawlReporter:
    """Tạo summary report từ danh sách products đã crawl."""

    def __init__(self, cfg: CrawlerConfig):
        self._metadata_dir = cfg.metadata_dir

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate_summary(self, products: List[Product]) -> dict:
        """
        Tạo summary report, lưu JSON và in ra console.

        Returns:
            dict report data.
        """
        report = self._build_report(products)
        self._save(report)
        self._print(report)
        return report

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _build_report(self, products: List[Product]) -> dict:
        report = {
            "crawl_date":      datetime.now().isoformat(),
            "total_products":  len(products),
            "total_variants":  sum(len(p.variants) for p in products),
            "categories":      {},
            "materials":       {},
            "sizes":           {},
        }

        for product in products:
            # Categories
            cat = product.category
            report["categories"][cat] = report["categories"].get(cat, 0) + 1

            # Materials
            if product.material:
                mat = product.material
                report["materials"][mat] = report["materials"].get(mat, 0) + 1

            # Sizes từ variants
            for variant in product.variants:
                if variant.size:
                    report["sizes"][variant.size] = report["sizes"].get(variant.size, 0) + 1

        return report

    def _save(self, report: dict) -> None:
        path = self._metadata_dir / "crawl_summary.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Summary report saved: {path}")

    def _print(self, report: dict) -> None:
        print("\n" + "=" * 50)
        print("CRAWLING SUMMARY REPORT")
        print("=" * 50)
        print(f"Total Products : {report['total_products']}")
        print(f"Total Variants : {report['total_variants']}")
        print(f"Categories     : {report['categories']}")
        print(f"Materials      : {report['materials']}")
        print(f"Sizes          : {report['sizes']}")
        print("=" * 50)
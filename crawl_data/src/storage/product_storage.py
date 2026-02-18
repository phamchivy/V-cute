"""
src/storage/product_storage.py

Chỉ trách nhiệm: lưu product data ra file (JSON, CSV, by-category).
Không fetch, không parse, không classify.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

from config import CrawlerConfig
from log_service import get_logger
from src.models import Product

logger = get_logger(__name__)


class ProductStorage:
    """Lưu products ra các định dạng và cấu trúc thư mục khác nhau."""

    def __init__(self, cfg: CrawlerConfig):
        self._raw_data_dir       = cfg.raw_data_dir
        self._processed_data_dir = cfg.processed_data_dir
        self._setup_directories(cfg)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def save(self, products: List[Product]) -> None:
        """Lưu toàn bộ products: JSON + CSV + by-category."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_json(products, timestamp)
        self.save_csv(products, timestamp)
        self.save_by_category(products)

    def save_json(self, products: List[Product], timestamp: str) -> Path:
        """Lưu tất cả products ra một file JSON."""
        path = self._raw_data_dir / f"all_products_{timestamp}.json"
        data = [self._product_to_dict(p) for p in products]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved JSON: {path} ({len(products)} products)")
        return path

    def save_csv(self, products: List[Product], timestamp: str) -> Path:
        """Lưu products ra CSV — một row per variant."""
        path = self._processed_data_dir / f"products_summary_{timestamp}.csv"

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Name", "Category", "Subcategory", "Material",
                "Size", "Dimensions", "Weight", "Capacity", "Features", "Source URL",
            ])

            for product in products:
                if product.variants:
                    for i, v in enumerate(product.variants):
                        variant_id = f"{product.id}_V{i+1}" if len(product.variants) > 1 else product.id
                        writer.writerow([
                            variant_id,
                            f"{product.name} ({v.size})" if v.size else product.name,
                            product.category,
                            product.subcategory,
                            product.material,
                            v.size, v.dimensions, v.weight, v.capacity,
                            "|".join(product.features),
                            product.source_url,
                        ])
                else:
                    writer.writerow([
                        product.id, product.name,
                        product.category, product.subcategory, product.material,
                        "", "", "", "",
                        "|".join(product.features),
                        product.source_url,
                    ])

        logger.info(f"Saved CSV: {path}")
        return path

    def save_by_category(self, products: List[Product]) -> None:
        """Lưu products theo từng category ra file JSON riêng."""
        category_data: dict = {}

        for product in products:
            cat = product.category
            if cat not in category_data:
                category_data[cat] = []

            if product.variants:
                for i, v in enumerate(product.variants):
                    category_data[cat].append({
                        "id": f"{product.id}_V{i+1}" if len(product.variants) > 1 else product.id,
                        "name": f"{product.name} ({v.size})" if v.size else product.name,
                        "subcategory": product.subcategory,
                        "specifications": {
                            "material": product.material,
                            "size": v.size,
                            "dimensions": v.dimensions,
                            "weight": v.weight,
                            "capacity": v.capacity,
                            "features": product.features,
                        },
                        "source_url": product.source_url,
                    })
            else:
                category_data[cat].append({
                    "id": product.id,
                    "name": product.name,
                    "subcategory": product.subcategory,
                    "specifications": {
                        "material": product.material,
                        "size": "", "dimensions": "", "weight": "", "capacity": "",
                        "features": product.features,
                    },
                    "source_url": product.source_url,
                })

        by_cat_dir = self._processed_data_dir / "by_category"
        by_cat_dir.mkdir(parents=True, exist_ok=True)

        for cat, data in category_data.items():
            path = by_cat_dir / f"{cat}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved by category: {list(category_data.keys())}")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _product_to_dict(self, product: Product) -> dict:
        return {
            "product_info": {
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "subcategory": product.subcategory,
            },
            "specifications": {
                "material": product.material,
                "color_options": product.color_options,
                "features": product.features,
                "warranty": product.warranty,
            },
            "variants": [
                {
                    "size": v.size,
                    "dimensions": v.dimensions,
                    "weight": v.weight,
                    "capacity": v.capacity,
                    "price": v.price,
                }
                for v in product.variants
            ],
            "images": product.images,
            "metadata": {
                "crawled_date": product.crawled_date,
                "source_url": product.source_url,
                "description": product.description,
            },
        }

    def _setup_directories(self, cfg: CrawlerConfig) -> None:
        dirs = [
            cfg.raw_data_dir,
            cfg.processed_data_dir,
            cfg.processed_data_dir / "by_category",
            cfg.images_dir,
            cfg.metadata_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directories ready under: {cfg.base_dir}")
"""
src/models.py

Data models cho toàn bộ crawler pipeline.
Không có dependency vào bất kỳ module nào trong project.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class ProductVariant:
    """Một variant cụ thể của sản phẩm (theo size/specs)."""
    size: str = ""
    dimensions: str = ""
    weight: str = ""
    capacity: str = ""
    price: str = ""


@dataclass
class Product:
    """Thông tin đầy đủ của một sản phẩm, bao gồm nhiều variants."""
    id: str
    name: str
    brand: str                  = "Hùng Phát"
    category: str               = ""
    subcategory: str            = ""
    material: str               = ""
    color_options: List[str]    = field(default_factory=list)
    features: List[str]         = field(default_factory=list)
    variants: List[ProductVariant]          = field(default_factory=list)
    images: Dict[str, List[str]]            = field(default_factory=lambda: {
        "main": [], "gallery": [], "detail": []
    })
    source_url: str             = ""
    description: str            = ""
    warranty: str               = ""
    crawled_date: str           = field(default_factory=lambda: datetime.now().isoformat())
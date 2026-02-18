"""
src/classifier/product_classifier.py

Chỉ trách nhiệm: classify category và subcategory cho Product.
Không fetch, không lưu file, không biết về HTTP.
"""

from log_service import get_logger
from config import CrawlerConfig
from src.models import Product

logger = get_logger(__name__)


class ProductClassifier:
    """Classify product category và subcategory dựa trên nhiều signals."""

    def __init__(self, cfg: CrawlerConfig):
        self._keywords = cfg.category_keywords

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def classify(self, product: Product) -> Product:
        """
        Classify category và subcategory cho product.
        Trả về product đã được cập nhật (mutate in-place).
        """
        product.category    = self._classify_category(product)
        product.subcategory = self._classify_subcategory(product)
        return product

    # ------------------------------------------------------------------
    # Private — category
    # ------------------------------------------------------------------

    def _classify_category(self, product: Product) -> str:
        """Smart classification dùng 5 signals theo thứ tự ưu tiên."""

        # Signal 1: URL pattern
        url = product.source_url.lower()
        if "/vali-nhua" in url or ("/vali-" in url and any(w in url for w in ["nhua", "abs", "pc"])):
            return "plastic_suitcase"
        if "/vali-vai" in url or ("/vali-" in url and "vai" in url):
            return "fabric_suitcase"
        if "/balo" in url:
            return "backpack"
        if "/tui" in url:
            return "bag"

        # Signal 2: Product name
        name = product.name.lower()
        if any(w in name for w in ["vali nhựa", "hardcase", "abs", "pc"]):
            return "plastic_suitcase"
        if any(w in name for w in ["vali vải", "softcase", "fabric"]):
            return "fabric_suitcase"
        if any(w in name for w in ["balo", "backpack"]):
            return "backpack"
        if any(w in name for w in ["túi", "bag"]):
            return "bag"
        if "vali" in name:
            return "suitcase"

        # Signal 3: Description
        desc = product.description.lower()
        if any(w in desc for w in ["nhựa abs", "polycarbonate", "hard case"]):
            return "plastic_suitcase"
        if any(w in desc for w in ["vải", "polyester", "nylon", "soft case"]):
            return "fabric_suitcase"
        if any(w in desc for w in ["balo", "laptop", "học tập"]):
            return "backpack"

        # Signal 4: Features
        features_text = " ".join(product.features).lower()
        if any(w in features_text for w in ["spinner", "hard shell", "abs"]):
            return "plastic_suitcase"

        # Signal 5: Material
        material = product.material.lower()
        if any(w in material for w in ["abs", "pc", "nhựa"]):
            return "plastic_suitcase"
        if any(w in material for w in ["vải", "polyester", "nylon"]):
            return "fabric_suitcase"

        return "other"

    # ------------------------------------------------------------------
    # Private — subcategory
    # ------------------------------------------------------------------

    def _classify_subcategory(self, product: Product) -> str:
        name = product.name.lower()
        desc = product.description.lower()
        category = product.category

        if category == "plastic_suitcase":
            if "abs" in name or "abs" in desc:
                return "hardcase_abs"
            if "pc" in name or "polycarbonate" in desc:
                return "hardcase_pc"
            if "aluminum" in name or "nhôm" in name:
                return "aluminum_frame"
            return "hardcase_general"

        if category == "fabric_suitcase":
            if "nylon" in name or "nylon" in desc:
                return "softcase_nylon"
            if "polyester" in name or "polyester" in desc:
                return "softcase_polyester"
            return "softcase_general"

        if category == "backpack":
            if "laptop" in name:
                return "laptop_backpack"
            if any(w in name for w in ["kid", "trẻ em"]):
                return "kids_backpack"
            if any(w in name for w in ["sport", "thể thao"]):
                return "sport_backpack"
            return "travel_backpack"

        if category == "bag":
            if "laptop" in name:
                return "laptop_bag"
            if "du lịch" in name:
                return "travel_bag"
            return "general_bag"

        return "general"
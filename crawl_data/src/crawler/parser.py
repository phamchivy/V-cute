"""
src/crawler/parser.py

Chỉ trách nhiệm: parse HTML, extract product data.
Không fetch, không lưu file, không classify.
"""

import re
import hashlib
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from log_service import get_logger
from src.models import Product, ProductVariant

logger = get_logger(__name__)


class Parser:
    """Parse HTML page → Product object."""

    _TITLE_SELECTORS = [
        "h1.product-title", "h1", ".product-title",
        ".title", "h2", ".product-name",
    ]

    _DESC_SELECTORS = [
        ".product-description", ".product-content",
        ".content", ".description", ".detail",
        ".product-summary", ".summary",
    ]

    _IMG_SELECTORS = [
        ".product-image img", ".main-image img",
        ".gallery img", ".product-gallery img",
        "img[src*='product']", "img[src*='vali']",
    ]

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def parse_product(self, url: str, html_content: bytes) -> Product | None:
        """
        Parse HTML content → Product object.

        Args:
            url: Source URL của product page.
            html_content: Raw bytes từ response.content.

        Returns:
            Product object, hoặc None nếu không parse được title.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        title = self._extract_title(soup)
        if not title:
            logger.warning(f"No title found: {url}")
            return None

        description = self._extract_description(soup)
        specs, variants = self._extract_specifications(soup)
        images = self._extract_images(soup, url)
        product_id = self._generate_id(title, url)

        return Product(
            id=product_id,
            name=title,
            category="",       # classifier sẽ điền sau
            subcategory="",    # classifier sẽ điền sau
            material=specs.get("material", ""),
            color_options=specs.get("colors", []),
            features=specs.get("features", []),
            variants=variants,
            images=images,
            source_url=url,
            description=description,
            warranty=specs.get("warranty", ""),
        )

    # ------------------------------------------------------------------
    # Private — extract
    # ------------------------------------------------------------------

    def _extract_title(self, soup: BeautifulSoup) -> str:
        for selector in self._TITLE_SELECTORS:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        for selector in self._DESC_SELECTORS:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ""

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> dict:
        images = {"main": [], "gallery": [], "detail": []}
        for selector in self._IMG_SELECTORS:
            for img in soup.select(selector):
                src = img.get("src") or img.get("data-src")
                if src:
                    full_url = urljoin(base_url, src)
                    if full_url not in images["main"]:
                        images["main"].append(full_url)
        return images

    def _extract_specifications(self, soup: BeautifulSoup) -> tuple[dict, list[ProductVariant]]:
        """Extract specs dict và variants list từ HTML."""
        specs = {
            "material": "",
            "colors": [],
            "features": [],
            "warranty": "",
        }

        variants = self._extract_variants_from_table(soup)

        # Material từ meta keywords
        meta = soup.find("meta", {"name": "keywords"})
        if meta:
            kw = meta.get("content", "").lower()
            if "abs" in kw and "pc" in kw:
                specs["material"] = "ABS + PC"
            elif "abs" in kw:
                specs["material"] = "ABS"
            elif "pc" in kw:
                specs["material"] = "PC"
            elif "pp" in kw:
                specs["material"] = "PP"
            elif "nhựa" in kw:
                specs["material"] = "Nhựa"
            elif "vải" in kw:
                specs["material"] = "Vải"

        # Features từ product summary
        summary = soup.select_one(".product-summary")
        if summary:
            text = summary.get_text().lower()
            feature_patterns = [
                (r"bánh xe.*?360",          "360° Spinner Wheels"),
                (r"khóa số",                "TSA Lock"),
                (r"mở rộng.*?25%",          "Expandable (+25%)"),
                (r"móc treo",               "Hanging Hook"),
                (r"góc bo kim loại",        "Metal Corner Guards"),
                (r"tay kéo.*?chắc chắn",   "Sturdy Handle"),
                (r"bảo mật",               "Security Lock"),
                (r"chống trầy",            "Scratch Resistant"),
                (r"chịu lực",              "Durable"),
                (r"không gây tiếng ồn",    "Silent Wheels"),
            ]
            for pattern, feature_name in feature_patterns:
                if re.search(pattern, text):
                    specs["features"].append(feature_name)

        # Warranty
        page_text = soup.get_text().lower()
        match = re.search(r"bảo hành[:\s]*(\d+)\s*năm", page_text)
        if match:
            specs["warranty"] = f"{match.group(1)} năm"

        return specs, variants

    def _extract_variants_from_table(self, soup: BeautifulSoup) -> list[ProductVariant]:
        """Extract variants từ HTML table."""
        variants = []

        for table in soup.find_all("table"):
            table_text = table.get_text().lower()
            if not any(kw in table_text for kw in ["size", "kích thước", "trọng lượng", "dung tích"]):
                continue

            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
            size_columns = [
                i for i, h in enumerate(headers[1:], 1)
                if re.search(r"\d+\s*inch|size", h.lower())
            ] or list(range(1, len(headers)))

            # Khởi tạo variants theo số cột
            for col_idx in size_columns:
                if col_idx < len(headers):
                    variant = ProductVariant()
                    match = re.search(r'(\d+)\s*inch|(\d+)\s*"', headers[col_idx])
                    if match:
                        variant.size = f"{match.group(1) or match.group(2)} inch"
                    variants.append(variant)

            # Điền data vào từng variant
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue

                label = cells[0].get_text(strip=True).lower()

                for i, col_idx in enumerate(size_columns):
                    if col_idx >= len(cells) or i >= len(variants):
                        continue

                    value = cells[col_idx].get_text(strip=True)

                    if "kích thước" in label or "dimension" in label:
                        m = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)", value)
                        if m:
                            variants[i].dimensions = f"{m.group(1)}x{m.group(2)}x{m.group(3)}cm"

                    elif "trọng lượng" in label or "weight" in label:
                        m = re.search(r"([0-9.,]+)\s*(kg|g)", value)
                        if m:
                            variants[i].weight = f"{m.group(1)}{m.group(2)}"

                    elif "dung tích" in label or "capacity" in label:
                        m = re.search(r"([0-9.,]+)\s*l", value.lower())
                        if m:
                            variants[i].capacity = f"{m.group(1)}L"

                    elif "size" in label and not variants[i].size:
                        m = re.search(r'(\d+)\s*inch|(\d+)\s*"', value)
                        if m:
                            variants[i].size = f"{m.group(1) or m.group(2)} inch"

        return [v for v in variants if v.size or v.dimensions or v.weight or v.capacity]

    # ------------------------------------------------------------------
    # Private — utils
    # ------------------------------------------------------------------

    def _generate_id(self, title: str, url: str) -> str:
        content = f"{title}{url}".encode("utf-8")
        return f"HP_{hashlib.md5(content).hexdigest()[:8].upper()}"
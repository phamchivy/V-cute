"""
src/crawler/link_discovery.py

Chỉ trách nhiệm: tìm và lọc product URLs từ pagination pages.
Không fetch, không parse product detail.
"""

import re
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from config import CrawlerConfig
from log_service import get_logger
from src.crawler.fetcher import Fetcher

logger = get_logger(__name__)


class LinkDiscovery:
    """Tìm product links từ các pagination page."""

    # CSS selectors để tìm product links
    _PRODUCT_SELECTORS = [
        ".product-item a[href]",
        ".product a[href]",
        ".item a[href]",
        "a[href*='/vali-']",
        "a[href*='/balo-']",
        "a[href*='/tui-']",
        ".product-grid a[href]",
        ".product-list a[href]",
    ]

    # Patterns bị loại trừ
    _UNWANTED_PATTERNS = [
        "javascript:", "mailto:", "#",
        "/collections/", "/pages/", "/blogs/",
        "/cart", "/account", "/search",
    ]

    def __init__(self, cfg: CrawlerConfig, fetcher: Fetcher):
        self._base_url = cfg.base_url
        self._metadata_dir = cfg.metadata_dir
        self._fetcher = fetcher

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def discover_pagination_urls(self, max_pages: int = 10) -> list[str]:
        """
        Tạo danh sách pagination URLs.

        Args:
            max_pages: Số trang tối đa cần crawl.

        Returns:
            List các pagination URLs.
        """
        urls = [
            f"{self._base_url}/collections/all?q=&page={page}&view=grid"
            for page in range(1, max_pages + 1)
        ]

        self._save_metadata(urls, "pagination_urls.json")
        logger.info(f"Generated {len(urls)} pagination URLs")
        return urls

    def extract_product_links(self, pagination_urls: list[str]) -> list[dict]:
        """
        Extract tất cả product links từ danh sách pagination URLs.

        Returns:
            List dict: {url, source_page, title} — đã deduplicate.
        """
        seen_urls: set = set()
        all_links: list[dict] = []

        for page_url in pagination_urls:
            links = self._extract_from_page(page_url)
            for link in links:
                if link["url"] not in seen_urls:
                    seen_urls.add(link["url"])
                    all_links.append(link)

        logger.info(f"Total unique product links found: {len(all_links)}")
        self._save_metadata(all_links, "product_links.json")
        return all_links

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _extract_from_page(self, page_url: str) -> list[dict]:
        """Extract product links từ một pagination page."""
        response = self._fetcher.get(page_url)
        if not response:
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        links = []

        for selector in self._PRODUCT_SELECTORS:
            for tag in soup.select(selector):
                href = tag.get("href")
                if href and self._is_product_url(href):
                    full_url = urljoin(self._base_url, href)
                    if full_url not in [l["url"] for l in links]:
                        links.append({
                            "url": full_url,
                            "source_page": page_url,
                            "title": tag.get_text(strip=True) or tag.get("title", ""),
                        })

        logger.info(f"Found {len(links)} product links from {page_url}")
        return links

    def _is_product_url(self, url: str) -> bool:
        """Kiểm tra URL có phải product page không."""
        url_lower = url.lower()

        if any(p in url_lower for p in self._UNWANTED_PATTERNS):
            return False

        product_patterns = ["/vali-", "/balo-", "/tui-"]
        if any(p in url_lower for p in product_patterns):
            return True

        if re.search(r"/[a-zA-Z]+-[a-zA-Z0-9-]+$", url):
            return True

        return False

    def _save_metadata(self, data, filename: str) -> None:
        """Lưu metadata ra file JSON."""
        path = self._metadata_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
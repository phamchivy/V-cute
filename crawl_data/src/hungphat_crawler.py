"""
src/hungphat_crawler.py

Thin orchestrator — kết nối các package crawler, classifier, storage, report.
Không chứa business logic, không parse HTML, không lưu file trực tiếp.
"""

from typing import List, Optional

from config import CrawlerConfig
from log_service import get_logger
from src.models import Product
from src.crawler import Fetcher, Parser, LinkDiscovery
from src.classifier import ProductClassifier
from src.storage import ProductStorage
from src.report import CrawlReporter

logger = get_logger(__name__)


class HungPhatCrawler:
    """
    Orchestrator cho toàn bộ crawl pipeline.

    Thứ tự: discover links → fetch + parse → classify → save → report.
    """

    def __init__(self, cfg: CrawlerConfig):
        self._cfg        = cfg
        self._fetcher    = Fetcher(cfg)
        self._parser     = Parser()
        self._discovery  = LinkDiscovery(cfg, self._fetcher)
        self._classifier = ProductClassifier(cfg)
        self._storage    = ProductStorage(cfg)
        self._reporter   = CrawlReporter(cfg)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def discover_pagination_urls(self) -> list[str]:
        """Bước 1: Generate pagination URLs (dùng cho mode discover)."""
        return self._discovery.discover_pagination_urls()

    def run_full_crawl(self, limit: Optional[int] = None) -> List[Product]:
        """
        Chạy toàn bộ pipeline.

        Args:
            limit: Giới hạn số product links xử lý (None = tất cả).

        Returns:
            Danh sách Product đã classify và lưu.
        """
        logger.info("=" * 60)
        logger.info("Starting Hùng Phát crawl pipeline")
        logger.info("=" * 60)

        # Step 1: Discover
        pagination_urls = self._discovery.discover_pagination_urls()

        # Step 2: Extract links
        product_links = self._discovery.extract_product_links(pagination_urls)
        if limit:
            product_links = product_links[:limit]
            logger.info(f"Limit applied: processing {len(product_links)} links")

        # Step 3: Fetch + Parse
        products = self._fetch_and_parse(product_links)

        # Step 4: Classify
        products = [self._classifier.classify(p) for p in products]
        logger.info(f"Classified {len(products)} products")

        # Step 5: Save
        self._storage.save(products)

        # Step 6: Report
        self._reporter.generate_summary(products)

        logger.info(f"Pipeline complete. Total products: {len(products)}")
        return products

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _fetch_and_parse(self, product_links: list[dict]) -> List[Product]:
        """Fetch và parse từng product link."""
        products = []
        total = len(product_links)

        for i, link in enumerate(product_links, 1):
            url = link["url"]
            logger.info(f"Processing {i}/{total}: {url}")

            response = self._fetcher.get(url)
            if not response:
                continue

            product = self._parser.parse_product(url, response.content)
            if product:
                products.append(product)

        logger.info(f"Successfully parsed {len(products)}/{total} products")
        return products
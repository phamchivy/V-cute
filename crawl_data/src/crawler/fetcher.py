"""
src/crawler/fetcher.py

Chỉ trách nhiệm: thực hiện HTTP request, trả về response.
Không parse, không biết gì về cấu trúc HTML hay product.
"""

import time
import random
import requests
from log_service import get_logger
from config import CrawlerConfig

logger = get_logger(__name__)


class Fetcher:
    """HTTP fetcher với rate limiting và retry."""

    def __init__(self, cfg: CrawlerConfig):
        self._delay      = cfg.delay
        self._timeout    = cfg.timeout
        self._max_retries = cfg.max_retries
        self._crawled_urls: set = set()

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": random.choice(cfg.user_agents)
        })

    def get(self, url: str) -> requests.Response | None:
        """
        Fetch một URL với rate limiting và retry.

        Returns:
            Response object nếu thành công, None nếu thất bại.
        """
        if url in self._crawled_urls:
            logger.debug(f"Skip (already fetched): {url}")
            return None

        for attempt in range(1, self._max_retries + 1):
            try:
                time.sleep(self._delay)
                response = self._session.get(url, timeout=self._timeout)
                response.raise_for_status()

                self._crawled_urls.add(url)
                logger.info(f"Fetched: {url}")
                return response

            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt}/{self._max_retries} failed for {url}: {e}")
                if attempt == self._max_retries:
                    logger.error(f"All retries exhausted: {url}")
                    return None

    @property
    def crawled_count(self) -> int:
        return len(self._crawled_urls)
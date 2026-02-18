#!/usr/bin/env python3
"""
src/run_crawler.py

Hùng Phát JSC Product Crawler — Main execution script.
Entry point duy nhất cho toàn bộ pipeline.

Usage:
    python src/run_crawler.py --mode crawl
    python src/run_crawler.py --mode discover
    python src/run_crawler.py --mode process
    python src/run_crawler.py --mode download --limit 50
"""

import argparse
import sys
import json
import glob
import os

from config import load_config, CrawlerConfig
from log_service import setup_logging, get_logger
from src.hungphat_crawler import HungPhatCrawler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_latest_data_file(output_dir: str) -> str:
    """Tìm file crawl data mới nhất trong raw_data/."""
    pattern = f"{output_dir}/raw_data/all_products_*.json"
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(
            "No crawl data found. Run with --mode crawl first."
        )
    return max(files, key=os.path.getctime)


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------

def run_discover(cfg: CrawlerConfig, logger) -> None:
    crawler = HungPhatCrawler(cfg)
    pagination_urls = crawler.discover_pagination_urls()
    logger.info(f"Generated {len(pagination_urls)} pagination URLs")


def run_crawl(cfg: CrawlerConfig, logger, limit: int = None) -> None:
    crawler = HungPhatCrawler(cfg)
    products = crawler.run_full_crawl(limit=limit)
    logger.info(f"Crawled {len(products)} products successfully")
    logger.info(f"Data saved to: {cfg.base_dir}")


def run_process(cfg: CrawlerConfig, logger) -> None:
    from src.processing import DataProcessor
    processor = DataProcessor(str(cfg.base_dir))

    latest_file = _find_latest_data_file(str(cfg.base_dir))
    logger.info(f"Processing data from: {latest_file}")

    data = processor.load_raw_data(os.path.basename(latest_file))
    df = processor.create_dataframe(data)

    analysis = processor.analyze_data(df)
    logger.info(f"Total products : {analysis['total_products']}")
    logger.info(f"Categories     : {analysis['categories']}")
    logger.info(f"Image coverage : {analysis['image_coverage']:.1f}%")

    processor.create_visualizations(df, str(cfg.processed_data_dir))

    report = processor.generate_summary_report(df)
    report_path = cfg.metadata_dir / "analysis_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info(f"Report saved to: {report_path}")


def run_download(cfg: CrawlerConfig, logger) -> None:
    from src.image_dowloader import ImageDownloader

    latest_file = _find_latest_data_file(str(cfg.base_dir))
    logger.info(f"Loading data from: {latest_file}")

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    downloader = ImageDownloader(str(cfg.images_dir))
    success_count = downloader.download_product_images(data)
    logger.info(f"Downloaded {success_count} images to: {cfg.images_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Load config trước để dùng làm default cho CLI args
    cfg = CrawlerConfig(load_config("crawl_config"))

    parser = argparse.ArgumentParser(description="Hùng Phát JSC Product Crawler")
    parser.add_argument(
        "--mode",
        choices=["discover", "crawl", "process", "download"],
        default="crawl",
        help="Crawling mode (default: crawl)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of products to crawl",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=cfg.delay,
        help=f"Delay between requests in seconds (default: {cfg.delay})",
    )
    # parser.add_argument(
    #     "--verbose",
    #     action="store_true",
    #     help="Verbose logging (show DEBUG on console)",
    # )

    args = parser.parse_args()

    # Override config nếu CLI truyền vào
    if args.delay != cfg.delay:
        cfg.delay = args.delay

    # Setup logging — phải chạy trước mọi thứ khác
    setup_logging(project_name="crawler")
    logger = get_logger(__name__)

    # if args.verbose:
    #     import logging
    #     logging.getLogger().handlers[0].setLevel(logging.DEBUG)  # handlers[0] = console

    logger.info(f"Mode   : {args.mode}")
    logger.info(f"Config : {cfg!r}")

    try:
        if args.mode == "discover":
            run_discover(cfg, logger)

        elif args.mode == "crawl":
            run_crawl(cfg, logger, limit=args.limit)

        elif args.mode == "process":
            run_process(cfg, logger)

        elif args.mode == "download":
            run_download(cfg, logger)

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
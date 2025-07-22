# run_crawler.py - Main execution script
#!/usr/bin/env python3
"""
Hùng Phát JSC Product Crawler
Main execution script with command-line interface
"""

import argparse
import sys
import json
from datetime import datetime
import logging

def main():
    parser = argparse.ArgumentParser(description='Hùng Phát JSC Product Crawler')
    parser.add_argument('--mode', choices=['discover', 'crawl', 'process', 'download'], 
                       default='crawl', help='Crawling mode')
    parser.add_argument('--limit', type=int, default=None, 
                       help='Limit number of products to crawl')
    parser.add_argument('--category', type=str, default=None,
                       help='Crawl specific category only')
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay between requests in seconds')
    parser.add_argument('--output', type=str, default='hungphat_data',
                       help='Output directory')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    
    try:
        if args.mode == 'discover':
            # Site structure discovery only
            from hungphat_crawler import HungPhatCrawler
            crawler = HungPhatCrawler(delay=args.delay)
            categories = crawler.discover_site_structure()
            print(f"Found {len(categories)} categories")
            
        elif args.mode == 'crawl':
            # Full crawling process
            from hungphat_crawler import HungPhatCrawler
            crawler = HungPhatCrawler(delay=args.delay)
            
            # Run crawl with optional filters
            products = crawler.run_full_crawl()
            print(f"Crawled {len(products)} products successfully")
            
        elif args.mode == 'process':
            # Data processing only
            from data_processor import DataProcessor
            processor = DataProcessor(args.output)
            
            # Find latest crawl data
            import os
            import glob
            pattern = f"{args.output}/raw_data/all_products_*.json"
            files = glob.glob(pattern)
            
            if not files:
                print("No crawl data found. Run with --mode crawl first.")
                sys.exit(1)
                
            latest_file = max(files, key=os.path.getctime)
            print(f"Processing data from: {latest_file}")
            
            # Load and process data
            data = processor.load_raw_data(os.path.basename(latest_file))
            df = processor.create_dataframe(data)
            
            # Generate analysis
            analysis = processor.analyze_data(df)
            print("\nData Analysis:")
            print(f"Total products: {analysis['total_products']}")
            print(f"Categories: {analysis['categories']}")
            print(f"Image coverage: {analysis['image_coverage']:.1f}%")
            
            # Create visualizations
            processor.create_visualizations(df, f"{args.output}/processed_data")
            
            # Generate report
            report = processor.generate_summary_report(df)
            with open(f"{args.output}/metadata/analysis_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
        elif args.mode == 'download':
            # Download images only
            from image_downloader import ImageDownloader
            
            # Find latest crawl data
            import os
            import glob
            pattern = f"{args.output}/raw_data/all_products_*.json"
            files = glob.glob(pattern)
            
            if not files:
                print("No crawl data found. Run with --mode crawl first.")
                sys.exit(1)
                
            latest_file = max(files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Download images
            downloader = ImageDownloader(f"{args.output}/images")
            success_count = downloader.download_product_images(data)
            print(f"Downloaded {success_count} images")
            
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
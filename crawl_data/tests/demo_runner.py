#!/usr/bin/env python3
"""
Quick Demo Runner for Hùng Phát JSC Crawler
This script demonstrates the crawler functionality with a small sample
"""

import os
import sys
import json
import logging
from datetime import datetime

# Simple demo crawler for testing
class DemoHungPhatCrawler:
    def __init__(self):
        self.setup_logging()
        self.create_demo_directories()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def create_demo_directories(self):
        """Create basic directory structure for demo"""
        dirs = [
            'demo_data/raw_data',
            'demo_data/processed_data',
            'demo_data/images',
            'demo_data/logs'
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            
    def test_website_connection(self):
        """Test connection to Hùng Phát website"""
        import requests
        
        try:
            response = requests.get('https://hungphat-jsc.com.vn', timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ Website connection successful")
                return True
            else:
                self.logger.error(f"❌ Website returned status code: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            return False
    
    def demo_site_structure_discovery(self):
        """Demo version of site structure discovery"""
        from bs4 import BeautifulSoup
        import requests
        
        self.logger.info("🔍 Discovering site structure...")
        
        try:
            response = requests.get('https://hungphat-jsc.com.vn', timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for navigation links
            nav_links = []
            
            # Try different navigation selectors
            for selector in ['nav a', '.menu a', '.navigation a', 'header a']:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if href and text:
                        nav_links.append({
                            'text': text,
                            'href': href,
                            'full_url': requests.compat.urljoin('https://hungphat-jsc.com.vn', href)
                        })
            
            # Remove duplicates
            unique_links = []
            seen_urls = set()
            for link in nav_links:
                if link['full_url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['full_url'])
            
            self.logger.info(f"Found {len(unique_links)} navigation links")
            
            # Save results
            with open('demo_data/raw_data/navigation_links.json', 'w', encoding='utf-8') as f:
                json.dump(unique_links, f, ensure_ascii=False, indent=2)
            
            # Print some examples
            print("\n📋 Sample Navigation Links:")
            for i, link in enumerate(unique_links[:10]):
                print(f"  {i+1}. {link['text']} -> {link['full_url']}")
            
            return unique_links
            
        except Exception as e:
            self.logger.error(f"Site structure discovery failed: {e}")
            return []
    
    def demo_product_extraction(self, max_products=5):
        """Demo product extraction from a sample page"""
        from bs4 import BeautifulSoup
        import requests
        import re
        
        self.logger.info(f"🛍️ Extracting sample products (limit: {max_products})...")
        
        # Sample URLs to try (you may need to update these based on actual site structure)
        test_urls = [
            'https://hungphat-jsc.com.vn/',
            'https://hungphat-jsc.com.vn/san-pham/',
            'https://hungphat-jsc.com.vn/products/'
        ]
        
        products = []
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for product-like elements
                product_selectors = [
                    '.product', '.item', '.card', 
                    'article', '.post', '[class*="product"]'
                ]
                
                for selector in product_selectors:
                    elements = soup.select(selector)
                    
                    for element in elements[:max_products]:
                        product_data = self.extract_product_info(element, url)
                        if product_data and product_data not in products:
                            products.append(product_data)
                            
                        if len(products) >= max_products:
                            break
                    
                    if len(products) >= max_products:
                        break
                
                if len(products) >= max_products:
                    break
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract from {url}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(products)} sample products")
        
        # Save products
        if products:
            with open('demo_data/raw_data/sample_products.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            # Print sample
            print("\n🎯 Sample Products:")
            for i, product in enumerate(products):
                print(f"  {i+1}. {product.get('name', 'Unknown')} - {product.get('category', 'Unknown')}")
        
        return products
    
    def extract_product_info(self, element, base_url):
        """Extract basic product info from HTML element"""
        try:
            # Try to find product name
            name_selectors = ['h1', 'h2', 'h3', '.title', '.name', '.product-name']
            name = ""
            
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    break
            
            if not name:
                return None
            
            # Try to find product link
            link_elem = element.select_one('a')
            product_url = ""
            if link_elem:
                href = link_elem.get('href', '')
                if href:
                    import requests
                    product_url = requests.compat.urljoin(base_url, href)
            
            # Try to find images
            images = []
            img_elements = element.select('img')
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    import requests
                    full_img_url = requests.compat.urljoin(base_url, src)
                    images.append(full_img_url)
            
            # Classify product
            category = self.classify_product(name)
            
            product = {
                'id': f"DEMO_{abs(hash(name)) % 10000}",
                'name': name,
                'category': category,
                'url': product_url,
                'images': images,
                'extracted_from': base_url,
                'crawled_date': datetime.now().isoformat()
            }
            
            return product
            
        except Exception as e:
            return None
    
    def classify_product(self, name):
        """Simple product classification"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['vali nhựa', 'hardcase', 'plastic']):
            return 'plastic_suitcase'
        elif any(word in name_lower for word in ['vali vải', 'softcase']):
            return 'fabric_suitcase'
        elif any(word in name_lower for word in ['balo', 'backpack']):
            return 'backpack'
        elif 'vali' in name_lower:
            return 'suitcase'
        elif any(word in name_lower for word in ['túi', 'bag']):
            return 'bag'
        else:
            return 'other'
    
    def generate_demo_report(self):
        """Generate a demo crawling report"""
        report_data = {
            'demo_run_date': datetime.now().isoformat(),
            'website': 'hungphat-jsc.com.vn',
            'crawler_version': '1.0-demo',
            'status': 'completed'
        }
        
        # Check for data files
        nav_file = 'demo_data/raw_data/navigation_links.json'
        products_file = 'demo_data/raw_data/sample_products.json'
        
        if os.path.exists(nav_file):
            with open(nav_file, 'r', encoding='utf-8') as f:
                nav_data = json.load(f)
                report_data['navigation_links_found'] = len(nav_data)
        
        if os.path.exists(products_file):
            with open(products_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
                report_data['sample_products_extracted'] = len(products_data)
                
                # Category breakdown
                categories = {}
                for product in products_data:
                    cat = product.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                report_data['category_breakdown'] = categories
        
        # Save report
        with open('demo_data/demo_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_data
    
    def run_demo(self):
        """Run complete demo"""
        print("🚀 Starting Hùng Phát JSC Crawler Demo")
        print("=" * 50)
        
        # Test 1: Website connection
        print("\n📡 Test 1: Website Connection")
        if not self.test_website_connection():
            print("❌ Cannot connect to website. Please check your internet connection.")
            return False
        
        # Test 2: Site structure discovery
        print("\n🔍 Test 2: Site Structure Discovery")
        nav_links = self.demo_site_structure_discovery()
        
        # Test 3: Product extraction
        print("\n🛍️ Test 3: Sample Product Extraction")
        products = self.demo_product_extraction(max_products=5)
        
        # Test 4: Generate report
        print("\n📊 Test 4: Generate Demo Report")
        report = self.generate_demo_report()
        
        # Summary
        print("\n" + "=" * 50)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Navigation links found: {report.get('navigation_links_found', 0)}")
        print(f"Sample products extracted: {report.get('sample_products_extracted', 0)}")
        print(f"Categories found: {list(report.get('category_breakdown', {}).keys())}")
        print(f"Demo data saved to: demo_data/")
        print("\n💡 Next steps:")
        print("1. Review the demo_data/ folder for sample results")
        print("2. Modify the full crawler based on actual site structure")
        print("3. Run full crawling with: python hungphat_crawler.py")
        
        return True

def main():
    """Main demo execution"""
    print("Hùng Phát JSC Crawler - Demo Mode")
    print("This demo will test basic crawler functionality")
    
    # Check if required packages are installed
    try:
        import requests
        import bs4
    except ImportError:
        print("❌ Required packages not installed.")
        print("Please install with: pip install requests beautifulsoup4")
        sys.exit(1)
    
    # Run demo
    demo_crawler = DemoHungPhatCrawler()
    success = demo_crawler.run_demo()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
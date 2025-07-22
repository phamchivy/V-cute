import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from urllib.parse import urljoin, urlparse
import csv
from datetime import datetime
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hungphat_crawler.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Product:
    """Product data structure"""
    id: str
    name: str
    brand: str = "Hùng Phát"
    category: str = ""
    subcategory: str = ""
    material: str = ""
    size: str = ""
    dimensions: str = ""
    weight: str = ""
    capacity: str = ""
    color_options: List[str] = None
    features: List[str] = None
    images: Dict[str, List[str]] = None
    source_url: str = ""
    description: str = ""
    crawled_date: str = ""

    def __post_init__(self):
        if self.color_options is None:
            self.color_options = []
        if self.features is None:
            self.features = []
        if self.images is None:
            self.images = {"main": [], "gallery": [], "detail": []}
        if self.crawled_date == "":
            self.crawled_date = datetime.now().isoformat()

class HungPhatCrawler:
    def __init__(self, base_url="https://hungphat-jsc.com.vn", delay=2):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directories
        self.setup_directories()
        
        # Store crawled URLs to avoid duplicates
        self.crawled_urls = set()
        self.products = []
        
    def setup_directories(self):
        """Create directory structure for organized data storage"""
        dirs = [
            'hungphat_data/raw_data/suitcases',
            'hungphat_data/raw_data/backpacks', 
            'hungphat_data/raw_data/bags',
            'hungphat_data/raw_data/accessories',
            'hungphat_data/processed_data/by_material',
            'hungphat_data/processed_data/by_price',
            'hungphat_data/processed_data/by_size',
            'hungphat_data/processed_data/by_category',
            'hungphat_data/images/products',
            'hungphat_data/images/thumbnails',
            'hungphat_data/metadata/crawl_logs',
            'hungphat_data/metadata/site_structure'
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            
    def get_page(self, url):
        """Fetch a page with error handling and rate limiting"""
        if url in self.crawled_urls:
            logging.info(f"URL already crawled: {url}")
            return None
            
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.crawled_urls.add(url)
            logging.info(f"Successfully fetched: {url}")
            return response
            
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def discover_site_structure(self):
        """Discover and map the website structure"""
        logging.info("Starting site structure discovery...")
        
        main_page = self.get_page(self.base_url)
        if not main_page:
            return []
            
        soup = BeautifulSoup(main_page.content, 'html.parser')
        
        # Find navigation links and product categories
        category_links = []
        
        # Common selectors for Vietnamese websites
        nav_selectors = [
            'nav a', '.menu a', '.navigation a', 
            '.category a', '.product-category a',
            'ul.menu li a', '.main-menu a'
        ]
        
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and text:
                    full_url = urljoin(self.base_url, href)
                    
                    # Filter for product-related links
                    if any(keyword in text.lower() for keyword in 
                           ['vali', 'balo', 'túi', 'sản phẩm', 'product']):
                        category_links.append({
                            'url': full_url,
                            'text': text,
                            'category': self.classify_category(text)
                        })
        
        # Remove duplicates
        unique_links = []
        seen_urls = set()
        for link in category_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        # Save site structure
        with open('hungphat_data/metadata/site_structure/categories.json', 'w', encoding='utf-8') as f:
            json.dump(unique_links, f, ensure_ascii=False, indent=2)
            
        logging.info(f"Found {len(unique_links)} category links")
        return unique_links
    
    def classify_category(self, text):
        """Classify product category based on text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['vali nhựa', 'hardcase', 'plastic']):
            return 'plastic_suitcase'
        elif any(word in text_lower for word in ['vali vải', 'softcase', 'fabric']):
            return 'fabric_suitcase'  
        elif any(word in text_lower for word in ['balo', 'backpack']):
            return 'backpack'
        elif any(word in text_lower for word in ['túi', 'bag']):
            return 'bag'
        elif 'vali' in text_lower:
            return 'suitcase'
        else:
            return 'other'
    
    def extract_product_links(self, category_url, category_type):
        """Extract individual product links from category pages"""
        logging.info(f"Extracting product links from: {category_url}")
        
        page = self.get_page(category_url)
        if not page:
            return []
            
        soup = BeautifulSoup(page.content, 'html.parser')
        product_links = []
        
        # Common selectors for product links
        product_selectors = [
            '.product-item a', '.product a', '.item a',
            '.product-grid a', '.product-list a',
            'article a', '.post a[href*="san-pham"]',
            'h2 a', 'h3 a', '.title a'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                title = link.get_text(strip=True) or link.get('title', '')
                
                if href and title:
                    full_url = urljoin(self.base_url, href)
                    
                    # Filter for actual product pages
                    if any(indicator in href for indicator in 
                           ['san-pham', 'product', 'vali', 'balo']):
                        product_links.append({
                            'url': full_url,
                            'title': title,
                            'category': category_type
                        })
        
        # Handle pagination
        pagination_links = soup.select('.pagination a, .pager a, .next a')
        for page_link in pagination_links:
            href = page_link.get('href')
            if href and href not in self.crawled_urls:
                next_page_url = urljoin(category_url, href)
                product_links.extend(self.extract_product_links(next_page_url, category_type))
        
        logging.info(f"Found {len(product_links)} product links in category {category_type}")
        return product_links
    
    def extract_product_data(self, product_url, category):
        """Extract detailed product information"""
        logging.info(f"Extracting product data from: {product_url}")
        
        page = self.get_page(product_url)
        if not page:
            return None
            
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extract basic info
        title_selectors = ['h1', '.product-title', '.title', 'h2']
        title = ""
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        # Extract description
        desc_selectors = ['.product-description', '.content', '.description', '.detail']
        description = ""
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                break
        
        # Extract specifications
        specs = self.extract_specifications(soup)
        
        # Extract images
        images = self.extract_images(soup, product_url)
        
        # Generate product ID
        product_id = self.generate_product_id(title, product_url)
        
        # Create Product object
        product = Product(
            id=product_id,
            name=title,
            category=category,
            subcategory=self.classify_subcategory(title, category),
            material=specs.get('material', ''),
            size=specs.get('size', ''),
            dimensions=specs.get('dimensions', ''),
            weight=specs.get('weight', ''),
            capacity=specs.get('capacity', ''),
            color_options=specs.get('colors', []),
            features=specs.get('features', []),
            images=images,
            source_url=product_url,
            description=description
        )
        
        return product
    
    def extract_specifications(self, soup):
        """Extract technical specifications from product page"""
        specs = {
            'material': '',
            'size': '', 
            'dimensions': '',
            'weight': '',
            'capacity': '',
            'colors': [],
            'features': []
        }
        
        # Look for specification tables or lists
        spec_selectors = ['.specifications', '.specs', '.product-info', '.details']
        
        for selector in spec_selectors:
            spec_section = soup.select_one(selector)
            if spec_section:
                text = spec_section.get_text()
                
                # Extract material
                material_patterns = [
                    r'chất liệu[:\s]+(.*?)(?:\n|$)',
                    r'material[:\s]+(.*?)(?:\n|$)',
                    r'(ABS|PC|nhựa|vải|polyester|nylon)'
                ]
                for pattern in material_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        specs['material'] = match.group(1).strip()
                        break
                
                # Extract size
                size_patterns = [
                    r'(\d+)\s*inch',
                    r'size[:\s]+(.*?)(?:\n|$)',
                    r'kích thước[:\s]+(.*?)(?:\n|$)'
                ]
                for pattern in size_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        specs['size'] = match.group(1).strip()
                        break
                
                # Extract dimensions
                dim_pattern = r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*cm'
                dim_match = re.search(dim_pattern, text)
                if dim_match:
                    specs['dimensions'] = f"{dim_match.group(1)}x{dim_match.group(2)}x{dim_match.group(3)}cm"
                
                # Extract features
                feature_keywords = [
                    'TSA', 'khóa số', 'spinner', 'bánh xe', 'expandable', 
                    'mở rộng', 'lightweight', 'nhẹ', 'waterproof', 'chống nước'
                ]
                
                for keyword in feature_keywords:
                    if keyword.lower() in text.lower():
                        specs['features'].append(keyword)
        
        return specs
    
    def extract_images(self, soup, base_url):
        """Extract product images"""
        images = {"main": [], "gallery": [], "detail": []}
        
        # Main product images
        img_selectors = [
            '.product-image img', '.main-image img', 
            '.gallery img', '.product-gallery img',
            'img[src*="product"]', 'img[src*="vali"]'
        ]
        
        for selector in img_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src:
                    full_url = urljoin(base_url, src)
                    if full_url not in images['main']:
                        images['main'].append(full_url)
        
        return images
    
    def generate_product_id(self, title, url):
        """Generate unique product ID"""
        # Create hash from title and URL for uniqueness
        content = f"{title}{url}".encode('utf-8')
        return f"HP_{hashlib.md5(content).hexdigest()[:8].upper()}"
    
    def classify_subcategory(self, title, category):
        """Classify product subcategory based on title and category"""
        title_lower = title.lower()
        
        if category == 'plastic_suitcase':
            if 'abs' in title_lower:
                return 'hardcase_abs'
            elif 'pc' in title_lower:
                return 'hardcase_pc'
            elif 'aluminum' in title_lower or 'nhôm' in title_lower:
                return 'aluminum_frame'
            return 'hardcase_general'
        
        elif category == 'fabric_suitcase':
            if 'nylon' in title_lower:
                return 'softcase_nylon'
            elif 'polyester' in title_lower:
                return 'softcase_polyester'
            return 'softcase_general'
        
        elif category == 'backpack':
            if 'laptop' in title_lower:
                return 'laptop_backpack'
            elif 'kid' in title_lower or 'trẻ em' in title_lower:
                return 'kids_backpack'
            elif 'sport' in title_lower or 'thể thao' in title_lower:
                return 'sport_backpack'
            return 'travel_backpack'
        
        return 'general'
    
    def save_product_data(self, products):
        """Save product data in various formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_data = []
        for product in products:
            json_data.append({
                'product_info': {
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'category': product.category,
                    'subcategory': product.subcategory
                },
                'specifications': {
                    'material': product.material,
                    'size': product.size,
                    'dimensions': product.dimensions,
                    'weight': product.weight,
                    'capacity': product.capacity,
                    'color_options': product.color_options,
                    'features': product.features
                },
                'images': product.images,
                'metadata': {
                    'crawled_date': product.crawled_date,
                    'source_url': product.source_url,
                    'description': product.description
                }
            })
        
        json_file = f'hungphat_data/raw_data/all_products_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Save as CSV for easy analysis
        csv_file = f'hungphat_data/processed_data/products_summary_{timestamp}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Name', 'Category', 'Subcategory', 'Material', 
                'Size', 'Dimensions', 'Features', 'Source URL'
            ])
            
            for product in products:
                writer.writerow([
                    product.id, product.name, product.category, 
                    product.subcategory, product.material, product.size,
                    product.dimensions, '|'.join(product.features),
                    product.source_url
                ])
        
        logging.info(f"Saved {len(products)} products to {json_file} and {csv_file}")
        
        # Save organized by category
        self.save_by_category(products)
    
    def save_by_category(self, products):
        """Save products organized by category"""
        category_data = {}
        
        for product in products:
            category = product.category
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(product)
        
        for category, category_products in category_data.items():
            filename = f'hungphat_data/processed_data/by_category/{category}.json'
            
            json_data = []
            for product in category_products:
                json_data.append({
                    'id': product.id,
                    'name': product.name,
                    'subcategory': product.subcategory,
                    'specifications': {
                        'material': product.material,
                        'size': product.size,
                        'features': product.features
                    },
                    'source_url': product.source_url
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Saved products by category: {list(category_data.keys())}")
    
    def run_full_crawl(self):
        """Run complete crawling process"""
        logging.info("Starting Hùng Phát JSC crawling process...")
        
        # Step 1: Discover site structure
        categories = self.discover_site_structure()
        
        # Step 2: Extract product links from each category
        all_product_links = []
        for category in categories:
            product_links = self.extract_product_links(
                category['url'], 
                category['category']
            )
            all_product_links.extend(product_links)
        
        logging.info(f"Total product links found: {len(all_product_links)}")
        
        # Step 3: Extract detailed product data
        products = []
        for i, product_link in enumerate(all_product_links[:50]):  # Limit for testing
            logging.info(f"Processing product {i+1}/{min(50, len(all_product_links))}")
            
            product = self.extract_product_data(
                product_link['url'],
                product_link['category']
            )
            
            if product:
                products.append(product)
        
        # Step 4: Save all data
        self.save_product_data(products)
        
        # Step 5: Generate summary report
        self.generate_summary_report(products)
        
        logging.info(f"Crawling completed! Total products: {len(products)}")
        return products
    
    def generate_summary_report(self, products):
        """Generate crawling summary report"""
        report = {
            'crawl_date': datetime.now().isoformat(),
            'total_products': len(products),
            'categories': {},
            'materials': {},
            'sizes': {}
        }
        
        # Category breakdown
        for product in products:
            cat = product.category
            report['categories'][cat] = report['categories'].get(cat, 0) + 1
            
            mat = product.material
            if mat:
                report['materials'][mat] = report['materials'].get(mat, 0) + 1
            
            size = product.size
            if size:
                report['sizes'][size] = report['sizes'].get(size, 0) + 1
        
        # Save report
        with open('hungphat_data/metadata/crawl_summary.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("CRAWLING SUMMARY REPORT")
        print("="*50)
        print(f"Total Products Crawled: {report['total_products']}")
        print(f"Categories: {dict(report['categories'])}")
        print(f"Materials: {dict(report['materials'])}")
        print(f"Sizes: {dict(report['sizes'])}")
        print("="*50)

# Usage example
if __name__ == "__main__":
    # Initialize crawler
    crawler = HungPhatCrawler()
    
    # Run full crawl
    products = crawler.run_full_crawl()
    
    print(f"Crawling completed! Check hungphat_data/ directory for results.")
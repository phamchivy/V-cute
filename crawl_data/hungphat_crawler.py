import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from urllib.parse import urljoin
import csv
from datetime import datetime
import logging
from dataclasses import dataclass
from typing import List, Dict
import hashlib

# # Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('hungphat_crawler.log'),
#         logging.StreamHandler()
#     ]
# )

# NEW DATA STRUCTURE: Support multiple variants

@dataclass
class ProductVariant:
    """Individual product variant with specific size/specs"""
    size: str = ""
    dimensions: str = ""
    weight: str = ""
    capacity: str = ""
    price: str = ""

@dataclass  
class Product:
    """Enhanced Product data structure with multiple variants"""
    id: str
    name: str
    brand: str = "Hùng Phát"
    category: str = ""
    subcategory: str = ""
    material: str = ""
    color_options: List[str] = None
    features: List[str] = None
    variants: List[ProductVariant] = None  # ← NEW: Multiple size variants
    images: Dict[str, List[str]] = None
    source_url: str = ""
    description: str = ""
    warranty: str = ""
    crawled_date: str = ""

    def __post_init__(self):
        if self.color_options is None:
            self.color_options = []
        if self.features is None:
            self.features = []
        if self.variants is None:
            self.variants = []
        if self.images is None:
            self.images = {"main": [], "gallery": [], "detail": []}
        if self.crawled_date == "":
            self.crawled_date = datetime.now().isoformat()

class HungPhatCrawler:
    def __init__(self, base_url="https://hungphat-jsc.com.vn", delay=2, output_dir="hungphat_data"):
        self.base_url = base_url
        self.delay = delay
        self.output_dir = output_dir  # ← THÊM output_dir parameter

        # Create directories
        self.setup_directories()

        # Setup logging TRƯỚC khi làm gì khác
        self.setup_logging()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Store crawled URLs to avoid duplicates
        self.crawled_urls = set()
        self.products = []
    
    def setup_logging(self):
        """Setup logging with dynamic log file path"""
        log_file = f'{self.output_dir}/crawler.log'
        
        # Remove existing handlers to avoid duplicates
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configure logging with dynamic path
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ],
            force=True  # Force reconfiguration
        )
        
        logging.info(f"Logging initialized. Log file: {log_file}")
        logging.info(f"Log file: {log_file}")
        
    def setup_directories(self):
        """Create directory structure for organized data storage"""
        dirs = [
            f'{self.output_dir}/raw_data/suitcases',
            f'{self.output_dir}/raw_data/backpacks', 
            f'{self.output_dir}/raw_data/bags',
            f'{self.output_dir}/raw_data/accessories',
            f'{self.output_dir}/processed_data/by_material',
            f'{self.output_dir}/processed_data/by_price',
            f'{self.output_dir}/processed_data/by_size',
            f'{self.output_dir}/processed_data/by_category',
            f'{self.output_dir}/images/products',
            f'{self.output_dir}/images/thumbnails',
            f'{self.output_dir}/metadata/crawl_logs',
            f'{self.output_dir}/metadata/site_structure',
            f'{self.output_dir}/logs'  # ← THÊM logs folder
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

        logging.info(f"Created directory structure in: {self.output_dir}")
            
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
    
    # THAY ĐỔI: Thay vì tìm category links, generate pagination URLs
    def discover_pagination_urls(self):
        """Generate pagination URLs for collections/all pages"""
        logging.info("Generating pagination URLs...")
        
        pagination_urls = []
        for page in range(1, 11):  # Pages 1-10
            url = f"{self.base_url}/collections/all?q=&page={page}&view=grid"
            pagination_urls.append(url)
        
        # Save pagination URLs for reference - SỬA ĐƯỜNG DẪN
        with open(f'{self.output_dir}/metadata/pagination_urls.json', 'w', encoding='utf-8') as f:
            json.dump(pagination_urls, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Generated {len(pagination_urls)} pagination URLs")
        return pagination_urls
    
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
    
    def extract_product_links_from_page(self, page_url):
        """Extract product links from single pagination page"""
        logging.info(f"Extracting product links from: {page_url}")
        
        page = self.get_page(page_url)
        if not page:
            return []
            
        soup = BeautifulSoup(page.content, 'html.parser')
        product_links = []
        
        # Look for product links - update selectors based on actual HTML structure
        product_selectors = [
            '.product-item a[href]', 
            '.product a[href]', 
            '.item a[href]',
            'a[href*="/vali-"]',
            'a[href*="/balo-"]', 
            'a[href*="/tui-"]',
            '.product-grid a[href]',
            '.product-list a[href]'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                
                if href and self.is_product_url(href):
                    full_url = urljoin(self.base_url, href)
                    
                    # Only add if not already collected
                    if full_url not in [p['url'] for p in product_links]:
                        product_links.append({
                            'url': full_url,
                            'source_page': page_url,
                            'title': link.get_text(strip=True) or link.get('title', '')
                        })
        
        logging.info(f"Found {len(product_links)} product links from {page_url}")
        return product_links

    def is_product_url(self, url):
        """Check if URL is a product page (not category/other)"""
        # Filter out unwanted URLs
        unwanted_patterns = [
            'javascript:', 'mailto:', '#', 
            '/collections/', '/pages/', '/blogs/',
            '/cart', '/account', '/search'
        ]
        
        for pattern in unwanted_patterns:
            if pattern in url.lower():
                return False
        
        # Product URLs typically have specific patterns
        product_patterns = [
            '/vali-', '/balo-', '/tui-',
            # Add more patterns based on actual URL structure
        ]
        
        # If URL contains product indicators or has specific format
        if any(pattern in url.lower() for pattern in product_patterns):
            return True
        
        # Additional check: URLs with model numbers/codes
        if re.search(r'/[a-zA-Z]+-[a-zA-Z0-9-]+$', url):
            return True
            
        return False
    
    # THAY ĐỔI 3: Cập nhật extract_product_data()
    def extract_product_data(self, product_url):
        """Extract detailed product information with variants support"""
        logging.info(f"Extracting product data from: {product_url}")
        
        page = self.get_page(product_url)
        if not page:
            return None
            
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extract basic info
        title_selectors = [
            'h1.product-title', 'h1', '.product-title', 
            '.title', 'h2', '.product-name'
        ]
        title = ""
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        if not title:
            logging.warning(f"No title found for {product_url}")
            return None
        
        # Extract description
        desc_selectors = [
            '.product-description', '.product-content', 
            '.content', '.description', '.detail',
            '.product-summary', '.summary'
        ]
        description = ""
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                break
        
        # Extract specifications and variants
        specs, variants = self.extract_specifications(soup)
        
        # Extract images
        images = self.extract_images(soup, product_url)
        
        # Generate product ID
        product_id = self.generate_product_id(title, product_url)
        
        # Create Product object with variants
        product = Product(
            id=product_id,
            name=title,
            category="",  # Leave empty for post-processing
            subcategory="",  # Leave empty for post-processing
            material=specs.get('material', ''),
            color_options=specs.get('colors', []),
            features=specs.get('features', []),
            variants=variants,  # ← NEW: Multiple variants
            images=images,
            source_url=product_url,
            description=description,
            warranty=specs.get('warranty', '')
        )
        
        return product
    
    def extract_variants_from_table(self, soup):
        """Extract multiple product variants from table"""
        variants = []
        
        tables = soup.find_all('table')
        for table in tables:
            # Parse table as structured data
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
                
            # Try to detect if this is a specs table
            table_text = table.get_text().lower()
            if not any(keyword in table_text for keyword in ['size', 'kích thước', 'trọng lượng', 'dung tích']):
                continue
            
            # Extract headers (size variants)
            header_row = rows[0]
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Find size columns (skip first column which is usually label)
            size_columns = []
            for i, header in enumerate(headers[1:], 1):  # Skip first column
                if re.search(r'\d+\s*inch|size', header.lower()):
                    size_columns.append(i)
            
            # If no explicit size columns, assume all non-first columns are variants
            if not size_columns:
                size_columns = list(range(1, len(headers)))
            
            # Initialize variants for each size column
            for col_idx in size_columns:
                if col_idx < len(headers):
                    variant = ProductVariant()
                    # Try to extract size from header
                    header_text = headers[col_idx]
                    size_match = re.search(r'(\d+)\s*inch|(\d+)\s*"', header_text)
                    if size_match:
                        size_val = size_match.group(1) or size_match.group(2)
                        variant.size = f"{size_val} inch"
                    variants.append(variant)
            
            # Extract data for each variant
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                row_label = cells[0].get_text(strip=True).lower()
                
                # Map row data to variants
                for i, col_idx in enumerate(size_columns):
                    if col_idx < len(cells) and i < len(variants):
                        cell_value = cells[col_idx].get_text(strip=True)
                        
                        # Map based on row label
                        if 'kích thước' in row_label or 'dimension' in row_label:
                            # Parse dimensions
                            dim_match = re.search(r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)', cell_value)
                            if dim_match:
                                variants[i].dimensions = f"{dim_match.group(1)}x{dim_match.group(2)}x{dim_match.group(3)}cm"
                        
                        elif 'trọng lượng' in row_label or 'weight' in row_label:
                            # Parse weight
                            weight_match = re.search(r'([0-9.,]+)\s*(kg|g)', cell_value)
                            if weight_match:
                                variants[i].weight = f"{weight_match.group(1)}{weight_match.group(2)}"
                        
                        elif 'dung tích' in row_label or 'capacity' in row_label:
                            # Parse capacity
                            capacity_match = re.search(r'([0-9.,]+)\s*l', cell_value.lower())
                            if capacity_match:
                                variants[i].capacity = f"{capacity_match.group(1)}L"
                        
                        elif 'size' in row_label and not variants[i].size:
                            # Parse size if not extracted from header
                            size_match = re.search(r'(\d+)\s*inch|(\d+)\s*"', cell_value)
                            if size_match:
                                size_val = size_match.group(1) or size_match.group(2)
                                variants[i].size = f"{size_val} inch"
        
        # Filter out empty variants
        valid_variants = [v for v in variants if v.size or v.dimensions or v.weight or v.capacity]
        
        return valid_variants

    def extract_specifications(self, soup):
        """Enhanced specification extraction with variants support"""
        specs = {
            'material': '',
            'colors': [],
            'features': [],
            'warranty': ''
        }
        
        # Extract variants from tables
        variants = self.extract_variants_from_table(soup)
        
        # Extract common specifications (material, features, etc.)
        page_text = soup.get_text().lower()
        
        # Material extraction from meta keywords
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '').lower()
            if 'abs' in keywords and 'pc' in keywords:
                specs['material'] = 'ABS + PC'
            elif 'abs' in keywords:
                specs['material'] = 'ABS'
            elif 'pc' in keywords:
                specs['material'] = 'PC'
            elif 'pp' in keywords:
                specs['material'] = 'PP'
            elif 'nhựa' in keywords:
                specs['material'] = 'Nhựa'
            elif 'vải' in keywords:
                specs['material'] = 'Vải'
        
        # Features extraction from product summary
        product_summary = soup.select_one('.product-summary')
        if product_summary:
            summary_text = product_summary.get_text().lower()
            
            feature_patterns = [
                (r'bánh xe.*?360', '360° Spinner Wheels'),
                (r'khóa số', 'TSA Lock'),
                (r'mở rộng.*?25%', 'Expandable (+25%)'),
                (r'móc treo', 'Hanging Hook'),
                (r'góc bo kim loại', 'Metal Corner Guards'),
                (r'tay kéo.*?chắc chắn', 'Sturdy Handle'),
                (r'bảo mật', 'Security Lock'),
                (r'chống trầy', 'Scratch Resistant'),
                (r'chịu lực', 'Durable'),
                (r'không gây tiếng ồn', 'Silent Wheels')
            ]
            
            for pattern, feature_name in feature_patterns:
                if re.search(pattern, summary_text):
                    specs['features'].append(feature_name)
        
        # Warranty extraction
        warranty_match = re.search(r'bảo hành[:\s]*(\d+)\s*năm', page_text)
        if warranty_match:
            specs['warranty'] = f"{warranty_match.group(1)} năm"
        
        return specs, variants

    # ALSO ADD: Enhanced product title parsing
    def extract_additional_info_from_title(self, soup):
        """Extract additional info from product title and meta"""
        info = {}
        
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            
            # Extract model number
            model_pattern = r'(\d{4}|\w+\s*\d+)'
            model_match = re.search(model_pattern, title_text)
            if model_match:
                info['model'] = model_match.group(1)
            
            # Extract brand
            brands = ['HÙNG PHÁT', 'UZO', 'STARTUP', 'TRAVELKING', 'MARCELLO', 'PIKA']
            for brand in brands:
                if brand in title_text.upper():
                    info['brand'] = brand
                    break
        
        return info
    
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
    
    # THAY ĐỔI 4: THAY THẾ save_product_data()
    def save_product_data(self, products):
        """Save product data with multiple variants support"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON format with variants
        json_data = []
        for product in products:
            product_data = {
                'product_info': {
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand,
                    'category': product.category,
                    'subcategory': product.subcategory
                },
                'specifications': {
                    'material': product.material,
                    'color_options': product.color_options,
                    'features': product.features,
                    'warranty': product.warranty
                },
                'variants': [  # ← NEW: Multiple variants
                    {
                        'size': variant.size,
                        'dimensions': variant.dimensions,
                        'weight': variant.weight,
                        'capacity': variant.capacity,
                        'price': variant.price
                    } for variant in product.variants
                ],
                'images': product.images,
                'metadata': {
                    'crawled_date': product.crawled_date,
                    'source_url': product.source_url,
                    'description': product.description
                }
            }
            json_data.append(product_data)
        
        # Save JSON
        json_file = f'{self.output_dir}/raw_data/all_products_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # CSV format: One row per variant (normalized)
        csv_file = f'{self.output_dir}/processed_data/products_summary_{timestamp}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Name', 'Category', 'Subcategory', 'Material', 
                'Size', 'Dimensions', 'Weight', 'Capacity', 'Features', 'Source URL'
            ])
            
            for product in products:
                if product.variants:
                    # One row per variant
                    for i, variant in enumerate(product.variants):
                        variant_id = f"{product.id}_V{i+1}" if len(product.variants) > 1 else product.id
                        writer.writerow([
                            variant_id, 
                            f"{product.name} ({variant.size})" if variant.size else product.name,
                            product.category, 
                            product.subcategory, 
                            product.material, 
                            variant.size,
                            variant.dimensions, 
                            variant.weight,
                            variant.capacity,
                            '|'.join(product.features),
                            product.source_url
                        ])
                else:
                    # Fallback: single row without variants
                    writer.writerow([
                        product.id, product.name, product.category, 
                        product.subcategory, product.material, '', '', '', '',
                        '|'.join(product.features), product.source_url
                    ])
        
        logging.info(f"Saved products with variants to {json_file} and {csv_file}")
        
        # Save organized by category (keep existing method)
        self.save_by_category(products)
    
def save_by_category(self, products):
    """Save products organized by category (updated for variants)"""
    category_data = {}
    
    for product in products:
        category = product.category
        if category not in category_data:
            category_data[category] = []
        
        # Handle variants properly
        if product.variants:
            for i, variant in enumerate(product.variants):
                variant_data = {
                    'id': f"{product.id}_V{i+1}" if len(product.variants) > 1 else product.id,
                    'name': f"{product.name} ({variant.size})" if variant.size else product.name,
                    'subcategory': product.subcategory,
                    'specifications': {
                        'material': product.material,
                        'size': variant.size,  # ← From variant
                        'dimensions': variant.dimensions,  # ← From variant  
                        'weight': variant.weight,  # ← From variant
                        'capacity': variant.capacity,  # ← From variant
                        'features': product.features
                    },
                    'source_url': product.source_url
                }
                category_data[category].append(variant_data)
        else:
            # Fallback for products without variants
            variant_data = {
                'id': product.id,
                'name': product.name,
                'subcategory': product.subcategory,
                'specifications': {
                    'material': product.material,
                    'size': '',  # ← Empty
                    'dimensions': '',  # ← Empty
                    'weight': '',  # ← Empty
                    'capacity': '',  # ← Empty
                    'features': product.features
                },
                'source_url': product.source_url
            }
            category_data[category].append(variant_data)
    
    for category, category_products in category_data.items():
        filename = f'{self.output_dir}/processed_data/by_category/{category}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(category_products, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Saved products by category: {list(category_data.keys())}")

    def post_process_classification(self, products):
        """Classify products after extraction using multiple signals"""
        logging.info(f"Post-processing classification for {len(products)} products...")
        
        for product in products:
            # Combine multiple classification signals
            category = self.classify_product_smart(product)
            subcategory = self.classify_subcategory_smart(product, category)
            
            product.category = category
            product.subcategory = subcategory
        
        logging.info("Post-processing classification completed")
        return products

    def classify_product_smart(self, product):
        """Smart product classification using multiple signals"""
        # Signal 1: URL pattern
        url_lower = product.source_url.lower()
        if '/vali-nhua' in url_lower or '/vali-' in url_lower and ('nhua' in url_lower or 'abs' in url_lower or 'pc' in url_lower):
            return 'plastic_suitcase'
        elif '/vali-vai' in url_lower or '/vali-' in url_lower and 'vai' in url_lower:
            return 'fabric_suitcase'
        elif '/balo' in url_lower:
            return 'backpack'
        elif '/tui' in url_lower:
            return 'bag'
        
        # Signal 2: Product name
        name_lower = product.name.lower()
        if any(word in name_lower for word in ['vali nhựa', 'hardcase', 'abs', 'pc']):
            return 'plastic_suitcase'
        elif any(word in name_lower for word in ['vali vải', 'softcase', 'fabric']):
            return 'fabric_suitcase'
        elif any(word in name_lower for word in ['balo', 'backpack']):
            return 'backpack'
        elif any(word in name_lower for word in ['túi', 'bag']):
            return 'bag'
        elif 'vali' in name_lower:
            return 'suitcase'
        
        # Signal 3: Description content
        desc_lower = product.description.lower()
        if any(word in desc_lower for word in ['nhựa abs', 'polycarbonate', 'hard case']):
            return 'plastic_suitcase'
        elif any(word in desc_lower for word in ['vải', 'polyester', 'nylon', 'soft case']):
            return 'fabric_suitcase'
        elif any(word in desc_lower for word in ['balo', 'laptop', 'học tập']):
            return 'backpack'
        
        # Signal 4: Features
        features_text = ' '.join(product.features).lower()
        if any(word in features_text for word in ['spinner', 'hard shell', 'abs']):
            return 'plastic_suitcase'
        
        # Signal 5: Material
        if product.material:
            material_lower = product.material.lower()
            if any(word in material_lower for word in ['abs', 'pc', 'nhựa']):
                return 'plastic_suitcase'
            elif any(word in material_lower for word in ['vải', 'polyester', 'nylon']):
                return 'fabric_suitcase'
        
        # Default fallback
        return 'other'

    def classify_subcategory_smart(self, product, category):
        """Smart subcategory classification"""
        name_lower = product.name.lower()
        desc_lower = product.description.lower()
        
        if category == 'plastic_suitcase':
            if 'abs' in name_lower or 'abs' in desc_lower:
                return 'hardcase_abs'
            elif 'pc' in name_lower or 'polycarbonate' in desc_lower:
                return 'hardcase_pc'
            elif 'aluminum' in name_lower or 'nhôm' in name_lower:
                return 'aluminum_frame'
            return 'hardcase_general'
        
        elif category == 'fabric_suitcase':
            if 'nylon' in name_lower or 'nylon' in desc_lower:
                return 'softcase_nylon'
            elif 'polyester' in name_lower or 'polyester' in desc_lower:
                return 'softcase_polyester'
            return 'softcase_general'
        
        elif category == 'backpack':
            if 'laptop' in name_lower:
                return 'laptop_backpack'
            elif any(word in name_lower for word in ['kid', 'trẻ em', 'em']):
                return 'kids_backpack'
            elif any(word in name_lower for word in ['sport', 'thể thao']):
                return 'sport_backpack'
            return 'travel_backpack'
        
        elif category == 'bag':
            if 'laptop' in name_lower:
                return 'laptop_bag'
            elif 'du lịch' in name_lower:
                return 'travel_bag'
            return 'general_bag'
        
        return 'general'
    
    def run_full_crawl(self):
        """Run complete crawling process with new approach"""
        logging.info("Starting Hùng Phát JSC crawling process...")
        
        # Step 1: Generate pagination URLs (thay vì category discovery)
        logging.info("Step 1: Generating pagination URLs...")
        pagination_urls = self.discover_pagination_urls()
        
        # Step 2: Extract product links from all pages
        logging.info("Step 2: Extracting product links from all pages...")
        all_product_links = []
        
        for page_url in pagination_urls:
            product_links = self.extract_product_links_from_page(page_url)
            all_product_links.extend(product_links)
            
            # Remove duplicates
            seen_urls = set()
            unique_links = []
            for link in all_product_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            all_product_links = unique_links
        
        logging.info(f"Total unique product links found: {len(all_product_links)}")
        
        # Save product links for reference
        with open(f'{self.output_dir}/metadata/product_links.json', 'w', encoding='utf-8') as f:
            json.dump(all_product_links, f, ensure_ascii=False, indent=2)
        
        # Step 3: Extract detailed product data (without classification)
        logging.info("Step 3: Extracting product details...")
        products = []
        
        # Apply limit if set (for testing)
        #links_to_process = all_product_links[:50] if len(all_product_links) > 50 else all_product_links
        links_to_process = all_product_links
        
        for i, product_link in enumerate(links_to_process):
            logging.info(f"Processing product {i+1}/{len(links_to_process)}: {product_link['url']}")
            
            product = self.extract_product_data(product_link['url'])
            if product:
                products.append(product)
        
        logging.info(f"Successfully extracted {len(products)} products")
        
        # Step 4: Post-processing classification
        logging.info("Step 4: Post-processing classification...")
        products = self.post_process_classification(products)
        
        # Step 5: Save all data
        logging.info("Step 5: Saving data...")
        self.save_product_data(products)
        
        # Step 6: Generate summary report
        self.generate_summary_report(products)
        
        logging.info(f"Crawling completed! Total products: {len(products)}")
        return products
    
def generate_summary_report(self, products):
    """Generate crawling summary report (updated for variants)"""
    report = {
        'crawl_date': datetime.now().isoformat(),
        'total_products': len(products),
        'total_variants': sum(len(p.variants) for p in products if p.variants),
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
        
        # Size breakdown from variants
        if product.variants:
            for variant in product.variants:
                if variant.size:
                    report['sizes'][variant.size] = report['sizes'].get(variant.size, 0) + 1
    
    # Save report
    with open(f'{self.output_dir}/metadata/crawl_summary.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("CRAWLING SUMMARY REPORT")
    print("="*50)
    print(f"Total Products Crawled: {report['total_products']}")
    print(f"Total Variants: {report['total_variants']}")
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
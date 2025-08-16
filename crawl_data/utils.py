import requests
import hashlib
import re
import logging

def setup_logging(log_file="crawler.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep Vietnamese
    text = re.sub(r'[^\w\s\-.,()%]', '', text)
    
    return text

def extract_price(text):
    """Extract price from Vietnamese text"""
    # Common Vietnamese price patterns
    price_patterns = [
        r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:VNĐ|vnđ|VND|đ)',
        r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:triệu|tr)',
        r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:nghìn|k)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).replace(',', '').replace('.', '')
    return None

def create_product_id(name, url):
    """Generate unique product ID"""
    content = f"{name}_{url}".encode('utf-8')
    return f"HP_{hashlib.sha256(content).hexdigest()[:10].upper()}"

def download_image(url, filename, max_size_mb=5):
    """Download and save image with size limit"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Check file size
        if 'content-length' in response.headers:
            size_mb = int(response.headers['content-length']) / (1024 * 1024)
            if size_mb > max_size_mb:
                logging.warning(f"Image too large ({size_mb:.1f}MB): {url}")
                return False
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        logging.error(f"Failed to download image {url}: {e}")
        return False
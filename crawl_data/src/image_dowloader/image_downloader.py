import os
import requests
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor
import logging

class ImageDownloader:
    def __init__(self, base_dir="hungphat_data/images", max_workers=5):
        self.base_dir = base_dir
        self.max_workers = max_workers
        self.downloaded = set()
        
        # Create directories
        os.makedirs(f"{base_dir}/products", exist_ok=True)
        os.makedirs(f"{base_dir}/thumbnails", exist_ok=True)
        
    def download_single_image(self, url, filename, max_size_mb=10):
        """Download a single image"""
        if filename in self.downloaded:
            return True
            
        try:
            response = requests.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logging.warning(f"Not an image: {url}")
                return False
            
            # Check file size
            if 'content-length' in response.headers:
                size_mb = int(response.headers['content-length']) / (1024 * 1024)
                if size_mb > max_size_mb:
                    logging.warning(f"Image too large ({size_mb:.1f}MB): {url}")
                    return False
            
            # Download and save
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.downloaded.add(filename)
            logging.info(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to download {url}: {e}")
            return False
    
    def download_product_images(self, products_data):
        """Download all product images with threading"""
        download_tasks = []
        
        for product in products_data:
            product_id = product['product_info']['id']
            images = product['images']
            
            # Main images
            for i, img_url in enumerate(images.get('main', [])):
                if img_url:
                    ext = self.get_file_extension(img_url)
                    filename = f"{self.base_dir}/products/{product_id}_main_{i}{ext}"
                    download_tasks.append((img_url, filename))
            
            # Gallery images  
            for i, img_url in enumerate(images.get('gallery', [])):
                if img_url:
                    ext = self.get_file_extension(img_url)
                    filename = f"{self.base_dir}/products/{product_id}_gallery_{i}{ext}"
                    download_tasks.append((img_url, filename))
        
        # Download with thread pool
        logging.info(f"Starting download of {len(download_tasks)} images...")
        
        success_count = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.download_single_image, url, filename)
                for url, filename in download_tasks
            ]
            
            for future in futures:
                if future.result():
                    success_count += 1
                time.sleep(0.5)  # Rate limiting
        
        logging.info(f"Successfully downloaded {success_count}/{len(download_tasks)} images")
        return success_count
    
    def get_file_extension(self, url):
        """Extract file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path
        
        if '.' in path:
            ext = os.path.splitext(path)[1]
            if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return ext
        
        return '.jpg'  # Default extension
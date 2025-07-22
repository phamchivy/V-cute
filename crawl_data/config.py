import os

class CrawlerConfig:
    # Base settings
    BASE_URL = "https://hungphat-jsc.com.vn"
    DELAY_BETWEEN_REQUESTS = 2  # seconds
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    
    # Directory structure
    BASE_DIR = "hungphat_data"
    RAW_DATA_DIR = os.path.join(BASE_DIR, "raw_data")
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")
    IMAGES_DIR = os.path.join(BASE_DIR, "images")
    METADATA_DIR = os.path.join(BASE_DIR, "metadata")
    
    # User agent strings for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    # Category mappings
    CATEGORY_KEYWORDS = {
        'plastic_suitcase': ['vali nhựa', 'hardcase', 'plastic', 'abs', 'pc'],
        'fabric_suitcase': ['vali vải', 'softcase', 'fabric', 'polyester', 'nylon'],
        'backpack': ['balo', 'backpack', 'laptop bag'],
        'travel_bag': ['túi du lịch', 'travel bag', 'duffel'],
        'accessories': ['phụ kiện', 'accessories', 'wheels', 'handles']
    }
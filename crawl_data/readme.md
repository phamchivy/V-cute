"""
# Hùng Phát JSC Product Crawler

Crawler system for extracting product data from Hùng Phát JSC website.

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Crawling
```bash
python run_crawler.py --mode crawl
```

### Site Structure Discovery
```bash
python run_crawler.py --mode discover
```

### Data Processing
```bash
python run_crawler.py --mode process
```

### Image Download
```bash
python run_crawler.py --mode download
```

### Advanced Options
```bash
# Limit crawling to 100 products
python run_crawler.py --mode crawl --limit 100

# Crawl with custom delay
python run_crawler.py --mode crawl --delay 3

# Verbose logging
python run_crawler.py --mode crawl --verbose
```

## Output Structure

```
hungphat_data/
├── raw_data/                   # Raw JSON data
├── processed_data/             # Processed CSV/JSON
├── images/                     # Product images
└── metadata/                   # Crawl logs & reports
```

## Features

- Respectful crawling with configurable delays
- Comprehensive data extraction
- Image downloading with size limits
- Data analysis and visualization
- Duplicate detection and handling
- Vietnamese text processing
- Error handling and logging

## Data Fields

Each product includes:
- Basic info (name, category, ID)
- Specifications (material, size, dimensions)
- Features and capabilities
- Images (main, gallery, detail)
- Metadata (crawl date, source URL)

## Customization

Edit `config.py` to modify:
- Crawling delays and timeouts
- User agent rotation
- Directory structure
- Category classifications
"""
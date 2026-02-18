import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_product_page():
    url = "https://hungphat-jsc.com.vn/vali-nhua-hung-phat-2103"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("="*80)
        print("FULL HTML ANALYSIS")
        print("="*80)
        
        # 1. META TAGS ANALYSIS
        print("\n1. META TAGS:")
        description = soup.find('meta', {'name': 'description'})
        keywords = soup.find('meta', {'name': 'keywords'})
        
        if description:
            print(f"Description: {description.get('content', '')}")
        if keywords:
            print(f"Keywords: {keywords.get('content', '')}")
        
        # 2. TITLE
        title = soup.find('title')
        if title:
            print(f"\nTitle: {title.get_text().strip()}")
        
        # 3. LOOK FOR PRODUCT INFO SECTIONS
        print("\n2. POTENTIAL PRODUCT INFO SECTIONS:")
        
        # Common Bizweb selectors
        bizweb_selectors = [
            '.product-details',
            '.product-info',
            '.product-description', 
            '.product-summary',
            '.product-content',
            '.description',
            '.content',
            '.details',
            '.thong-tin',
            '.chi-tiet',
            '.mo-ta',
            '.product-tabs',
            '#product-description',
            '.product_description'
        ]
        
        found_sections = []
        for selector in bizweb_selectors:
            elements = soup.select(selector)
            if elements:
                for i, elem in enumerate(elements[:2]):  # Max 2 per selector
                    text = elem.get_text(strip=True)[:500]  # First 500 chars
                    if text:
                        found_sections.append({
                            'selector': selector,
                            'text': text,
                            'length': len(elem.get_text())
                        })
        
        for section in found_sections:
            print(f"\nSelector: {section['selector']}")
            print(f"Length: {section['length']} chars")
            print(f"Sample: {section['text'][:200]}...")
        
        # 4. LOOK FOR TABLES (specs often in tables)
        print("\n3. TABLES ANALYSIS:")
        tables = soup.find_all('table')
        for i, table in enumerate(tables[:3]):  # Max 3 tables
            text = table.get_text(strip=True)
            if text:
                print(f"\nTable {i+1}: {text[:300]}")
        
        # 5. LOOK FOR LISTS
        print("\n4. LISTS ANALYSIS:")
        lists = soup.find_all(['ul', 'ol'])
        for i, lst in enumerate(lists[:5]):  # Max 5 lists
            text = lst.get_text(strip=True)
            if len(text) > 50:  # Only substantial lists
                print(f"\nList {i+1}: {text[:200]}")
        
        # 6. STRUCTURED DATA (JSON-LD)
        print("\n5. STRUCTURED DATA:")
        scripts = soup.find_all('script', type='application/ld+json')
        for i, script in enumerate(scripts):
            try:
                data = json.loads(script.string)
                print(f"\nJSON-LD {i+1}: {json.dumps(data, indent=2)[:500]}")
            except:
                pass
        
        # 7. CUSTOM BIZWEB ANALYSIS
        print("\n6. BIZWEB SPECIFIC ELEMENTS:")
        
        # Price info
        price_selectors = ['.price', '.product-price', '.gia', '.product_price']
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                print(f"Price ({selector}): {elem.get_text(strip=True)}")
        
        # Size/specs in specific patterns
        all_text = soup.get_text().lower()
        
        # Look for size patterns
        size_matches = re.findall(r'(\d+)\s*inch|(\d+)\s*"|size\s*(\d+)', all_text)
        if size_matches:
            print(f"Size patterns found: {size_matches[:5]}")
        
        # Look for material patterns
        material_matches = re.findall(r'chất liệu[:\s]*(.*?)[.\n]|material[:\s]*(.*?)[.\n]', all_text)
        if material_matches:
            print(f"Material patterns: {material_matches[:3]}")
        
        # Look for dimension patterns
        dim_matches = re.findall(r'(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)', all_text)
        if dim_matches:
            print(f"Dimension patterns: {dim_matches[:3]}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_product_page()
# 📝 File: rag_pipeline/src/preprocessing/text_processor.py
import re
from typing import List, Dict
import pandas as pd
from unidecode import unidecode

class TextProcessor:
    """Process and normalize Vietnamese text"""
    
    @staticmethod
    def clean_vietnamese_text(text: str) -> str:
        """Clean Vietnamese text while preserving diacritics"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep Vietnamese
        text = re.sub(r'[^\w\sÀ-ỹ\-\+\(\)\/\%\°\.]', ' ', text)
        
        # Normalize spacing around punctuation
        text = re.sub(r'\s*([\.,:;!?])\s*', r'\1 ', text)
        
        return text.strip()
    
    @staticmethod
    def create_searchable_text(text: str) -> str:
        """Create searchable version with both accented and unaccented"""
        if not text:
            return ""
        
        original = TextProcessor.clean_vietnamese_text(text)
        unaccented = unidecode(original)
        
        # Combine both versions for better search
        if original != unaccented:
            return f"{original} {unaccented}"
        return original
    
    @staticmethod
    def create_product_document(row: pd.Series) -> Dict[str, str]:
        """Create a structured document from product row"""
        
        # Build main content
        content_parts = []
        
        # Product name
        if row.get('Name'):
            content_parts.append(f"Tên sản phẩm: {row['Name']}")
        
        # Category
        if row.get('Category'):
            category_text = f"Danh mục: {row['Category']}"
            if row.get('Subcategory'):
                category_text += f" - {row['Subcategory']}"
            content_parts.append(category_text)
        
        # Specifications
        specs = []
        if row.get('Material'):
            specs.append(f"Chất liệu: {row['Material']}")
        if row.get('Size'):
            specs.append(f"Kích thước: {row['Size']}")
        if row.get('Dimensions'):
            specs.append(f"Chi tiết: {row['Dimensions']}")
        if row.get('Weight'):
            specs.append(f"Trọng lượng: {row['Weight']}")
        if row.get('Capacity'):
            specs.append(f"Dung tích: {row['Capacity']}")
        
        if specs:
            content_parts.append("Thông số kỹ thuật:")
            content_parts.extend([f"- {spec}" for spec in specs])
        
        # Features
        if row.get('Features') and row['Features']:
            features = row['Features'].replace('|', ', ')
            content_parts.append(f"Tính năng: {features}")
        
        # Create document
        document = {
            'id': row['ID'],
            'content': '\n'.join(content_parts),
            'metadata': {
                'name': row.get('Name', ''),
                'category': row.get('Category', ''),
                'subcategory': row.get('Subcategory', ''),
                'material': row.get('Material', ''),
                'size': row.get('Size', ''),
                'size_numeric': row.get('Size_Numeric'),
                'weight_numeric': row.get('Weight_Numeric'),
                'features': row.get('Features_List', []),
                'url': row.get('Source URL', '')
            }
        }
        
        return document
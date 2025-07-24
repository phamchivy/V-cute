# 📝 File: rag_pipeline/src/preprocessing/data_cleaner.py
import pandas as pd
import re
from typing import List, Dict, Optional
from pathlib import Path
import json

class DataCleaner:
    """Clean and prepare product data for RAG"""
    
    def __init__(self, csv_path: Path = None):
        if csv_path is None:
            # ✅ SỬA: Auto-detect CSV path on Windows
            from config.settings import Config
            try:
                self.csv_path = Config.get_latest_csv()
            except FileNotFoundError:
                # Fallback: hardcode path
                self.csv_path = Config.PROJECT_ROOT.parent / "crawl_data" / "hungphat_data_4" / "processed_data" / "products_summary_20250723_163031.csv"
        else:
            self.csv_path = Path(csv_path)
        
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """Load CSV data"""
        print(f"📂 Loading data from: {self.csv_path}")
        self.df = pd.read_csv(self.csv_path)
        print(f"✅ Loaded {len(self.df)} records")
        return self.df
    
    def clean_data(self) -> pd.DataFrame:
        """Clean the dataframe"""
        if self.df is None:
            self.load_data()
        
        print("🧹 Cleaning data...")
        
        # Fill NaN values
        self.df = self.df.fillna('')
        
        # Clean text columns
        text_columns = ['Name', 'Material', 'Size', 'Dimensions', 'Weight', 'Features']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
        
        # Clean features (split by |)
        if 'Features' in self.df.columns:
            self.df['Features_List'] = self.df['Features'].apply(
                lambda x: [f.strip() for f in x.split('|') if f.strip()] if x else []
            )
        
        # Extract numeric values
        self.df['Size_Numeric'] = self.df['Size'].apply(self._extract_size)
        self.df['Weight_Numeric'] = self.df['Weight'].apply(self._extract_weight)
        
        print(f"✅ Data cleaned, {len(self.df)} records ready")
        return self.df
    
    def _extract_size(self, size_str: str) -> Optional[float]:
        """Extract numeric size from string"""
        if not size_str:
            return None
        match = re.search(r'(\d+(?:\.\d+)?)', size_str)
        return float(match.group(1)) if match else None
    
    def _extract_weight(self, weight_str: str) -> Optional[float]:
        """Extract numeric weight from string"""
        if not weight_str:
            return None
        match = re.search(r'(\d+(?:\.\d+)?)', weight_str)
        return float(match.group(1)) if match else None
    
    def save_cleaned_data(self, output_path: Path) -> None:
        """Save cleaned data"""
        self.df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"💾 Saved cleaned data to: {output_path}")
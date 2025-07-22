import pandas as pd
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

class DataProcessor:
    def __init__(self, data_dir="hungphat_data"):
        self.data_dir = data_dir
        
    def load_raw_data(self, filename):
        """Load raw JSON data"""
        with open(f"{self.data_dir}/raw_data/{filename}", 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_dataframe(self, json_data):
        """Convert JSON data to pandas DataFrame"""
        rows = []
        for item in json_data:
            row = {
                'id': item['product_info']['id'],
                'name': item['product_info']['name'],
                'category': item['product_info']['category'],
                'subcategory': item['product_info']['subcategory'],
                'material': item['specifications']['material'],
                'size': item['specifications']['size'],
                'dimensions': item['specifications']['dimensions'],
                'weight': item['specifications']['weight'],
                'features_count': len(item['specifications']['features']),
                'features': '|'.join(item['specifications']['features']),
                'has_images': len(item['images']['main']) > 0,
                'image_count': len(item['images']['main']),
                'source_url': item['metadata']['source_url'],
                'crawled_date': item['metadata']['crawled_date']
            }
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def analyze_data(self, df):
        """Generate data analysis report"""
        analysis = {
            'total_products': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'subcategories': df['subcategory'].value_counts().to_dict(),
            'materials': df['material'].value_counts().to_dict(),
            'sizes': df['size'].value_counts().to_dict(),
            'avg_features_per_product': df['features_count'].mean(),
            'products_with_images': df['has_images'].sum(),
            'image_coverage': df['has_images'].mean() * 100
        }
        
        return analysis
    
    def create_visualizations(self, df, output_dir):
        """Create data visualization charts"""
        plt.style.use('default')
        
        # Category distribution
        plt.figure(figsize=(10, 6))
        df['category'].value_counts().plot(kind='bar')
        plt.title('Phân bố sản phẩm theo danh mục')
        plt.xlabel('Danh mục')
        plt.ylabel('Số lượng sản phẩm')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/category_distribution.png')
        plt.close()
        
        # Material distribution
        plt.figure(figsize=(10, 6))
        material_counts = df['material'].value_counts().head(10)
        material_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Phân bố theo chất liệu')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/material_distribution.png')
        plt.close()
        
        # Features analysis
        plt.figure(figsize=(10, 6))
        df['features_count'].hist(bins=20)
        plt.title('Phân bố số lượng tính năng sản phẩm')
        plt.xlabel('Số lượng tính năng')
        plt.ylabel('Số lượng sản phẩm')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/features_distribution.png')
        plt.close()
    
    def export_filtered_data(self, df, filters, output_file):
        """Export filtered data based on criteria"""
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        filtered_df.to_csv(output_file, index=False, encoding='utf-8')
        return len(filtered_df)
    
    def generate_summary_report(self, df):
        """Generate comprehensive summary report"""
        report = {
            'crawl_summary': {
                'total_products': len(df),
                'crawl_date': datetime.now().isoformat(),
                'unique_categories': df['category'].nunique(),
                'unique_materials': df['material'].nunique()
            },
            'category_breakdown': df['category'].value_counts().to_dict(),
            'quality_metrics': {
                'products_with_descriptions': df['name'].notna().sum(),
                'products_with_images': df['has_images'].sum(),
                'avg_features_per_product': round(df['features_count'].mean(), 2),
                'image_coverage_percent': round(df['has_images'].mean() * 100, 1)
            },
            'data_completeness': {
                'material_filled': df['material'].notna().sum(),
                'size_filled': df['size'].notna().sum(),
                'dimensions_filled': df['dimensions'].notna().sum(),
                'weight_filled': df['weight'].notna().sum()
            }
        }
        
        return report
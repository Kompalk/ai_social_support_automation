"""Process tabular data from Excel files."""
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TabularProcessor:
    """Process Excel files and extract structured data."""
    
    def process_excel(self, file_path: str) -> Dict[str, Any]:
        """Process Excel file and extract assets/liabilities data."""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Identify assets and liabilities columns
            assets = []
            liabilities = []
            
            # Look for common column names
            for _, row in df.iterrows():
                item_name = str(row.get('Item', row.get('Description', '')))
                value = float(row.get('Value', row.get('Amount', 0)))
                category = str(row.get('Category', row.get('Type', ''))).lower()
                
                item_data = {
                    "name": item_name,
                    "value": value,
                    "category": category
                }
                
                if 'asset' in category or 'asset' in item_name.lower():
                    assets.append(item_data)
                elif 'liability' in category or 'liability' in item_name.lower() or 'debt' in category:
                    liabilities.append(item_data)
            
            total_assets = sum(item['value'] for item in assets)
            total_liabilities = sum(item['value'] for item in liabilities)
            net_worth = total_assets - total_liabilities
            
            return {
                "assets": assets,
                "liabilities": liabilities,
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "net_worth": net_worth,
                "raw_data": df.to_dict('records')
            }
        
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return {
                "assets": [],
                "liabilities": [],
                "total_assets": 0,
                "total_liabilities": 0,
                "net_worth": 0,
                "error": str(e)
            }


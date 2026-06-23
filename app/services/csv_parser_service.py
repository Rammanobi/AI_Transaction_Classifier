import pandas as pd
from typing import List, Dict, Any, Tuple, Optional

class CSVParserService:
    @staticmethod
    def parse(file_path: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Parses a CSV file and returns a list of dictionaries.
        Returns (rows, error_message)
        """
        try:
            # Read CSV, replacing empty strings with None for easier dictionary handling
            df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
            df = df.replace("", None)
            # Standardize column names (lowercase, strip whitespace)
            df.columns = [c.strip().lower() for c in df.columns]
            
            # Ensure required columns are present (even if empty) to avoid KeyError later
            required_columns = ["txn_id", "date", "merchant", "amount", "currency", "status", "account_id", "category", "notes"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
                    
            rows = df.to_dict('records')
            
            # Robustly convert any Pandas/Numpy NaNs to Python None
            for row in rows:
                for k, v in row.items():
                    if pd.isna(v):
                        row[k] = None
            
            # Add 1-based row_number (accounting for header)
            for i, row in enumerate(rows):
                row['row_number'] = i + 2
                
            return rows, None
        except Exception as e:
            return [], f"Failed to parse CSV: {str(e)}"

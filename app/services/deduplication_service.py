import hashlib
import json
from typing import Dict, Any, Tuple

class DeduplicationService:
    @staticmethod
    def generate_hash(row: Dict[str, Any]) -> str:
        """
        Generates a hash from the raw inputs of a row to identify exact duplicates.
        Fields: txn_id, date, merchant, amount, currency, status, category, account_id
        """
        hash_fields = [
            str(row.get("txn_id", "")),
            str(row.get("date_clean", "")),
            str(row.get("merchant_clean", "")),
            str(row.get("amount_clean", "")),
            str(row.get("currency_clean", "")),
            str(row.get("status_clean", "")),
            str(row.get("category_final", "")),
            str(row.get("account_id", ""))
        ]
        
        hash_string = "|".join(hash_fields)
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

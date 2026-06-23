from typing import Dict, Any, Optional
from decimal import Decimal, InvalidOperation
import dateutil.parser

class CleaningService:
    @staticmethod
    def clean_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans a validated row.
        Adds *_clean fields and returns the updated row dictionary.
        Also initializes category_final to None if category is missing/empty.
        """
        def get_str(key: str) -> Optional[str]:
            val = row.get(key)
            if val is None:
                return None
            s = str(val).strip()
            return s if s else None

        cleaned = dict(row)
        
        # 1. Date normalization
        date_raw = get_str("date")
        cleaned["date_raw"] = date_raw
        try:
            if date_raw:
                parsed_date = dateutil.parser.parse(date_raw, dayfirst=True)
                cleaned["date_clean"] = parsed_date.strftime("%Y-%m-%d")
            else:
                cleaned["date_clean"] = None
        except (ValueError, TypeError, dateutil.parser.ParserError):
            cleaned["date_clean"] = None

        # 2. Amount cleanup
        amount_raw = get_str("amount")
        cleaned["amount_raw"] = amount_raw
        if amount_raw:
            amount_clean_str = amount_raw.replace("$", "").replace(",", "")
            try:
                cleaned["amount_clean"] = Decimal(amount_clean_str)
            except InvalidOperation:
                cleaned["amount_clean"] = None
        else:
            cleaned["amount_clean"] = None

        # 3. Currency normalization
        currency_raw = get_str("currency")
        cleaned["currency_raw"] = currency_raw
        cleaned["currency_clean"] = currency_raw.upper() if currency_raw else None

        # 4. Status normalization
        status_raw = get_str("status")
        cleaned["status_raw"] = status_raw
        cleaned["status_clean"] = status_raw.upper() if status_raw else None

        # 5. Merchant normalization
        merchant_raw = get_str("merchant")
        cleaned["merchant_raw"] = merchant_raw
        cleaned["merchant_clean"] = merchant_raw.title() if merchant_raw else None

        # 6. Category handling
        category_raw = get_str("category")
        cleaned["category_raw"] = category_raw
        cleaned["category_final"] = category_raw

        # Pass through other fields
        cleaned["txn_id"] = get_str("txn_id")
        cleaned["account_id"] = get_str("account_id")
        cleaned["notes_raw"] = get_str("notes")

        return cleaned

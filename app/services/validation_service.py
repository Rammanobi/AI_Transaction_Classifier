from typing import Dict, Any, Tuple

class ValidationService:
    REQUIRED_COLUMNS = ["txn_id", "date", "merchant", "amount", "currency", "status", "account_id"]

    @staticmethod
    def validate_row(row: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Validates a single row.
        Returns (is_valid, error_type, error_message)
        """
        missing_fields = []
        for col in ValidationService.REQUIRED_COLUMNS:
            val = row.get(col)
            # None or empty string or only whitespace
            if val is None or str(val).strip() == "":
                missing_fields.append(col)
                
        if missing_fields:
            return False, "missing_required_field", f"Missing required fields: {', '.join(missing_fields)}"
            
        return True, "", ""

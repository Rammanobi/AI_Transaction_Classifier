from decimal import Decimal
from app.services.cleaning_service import CleaningService

def test_clean_valid_date():
    row = {"date": "01-06-2025"}
    cleaned = CleaningService.clean_row(row)
    assert cleaned["date_clean"] == "2025-06-01"

def test_clean_invalid_date():
    row = {"date": "32-99-2025"}
    cleaned = CleaningService.clean_row(row)
    assert cleaned["date_clean"] is None

def test_clean_amount():
    row = {"amount": "$1,234.56"}
    cleaned = CleaningService.clean_row(row)
    assert cleaned["amount_clean"] == Decimal("1234.56")

def test_clean_merchant_casing():
    row = {"merchant": "swiggy"}
    cleaned = CleaningService.clean_row(row)
    assert cleaned["merchant_clean"] == "Swiggy"

from app.services.validation_service import ValidationService

def test_valid_row():
    row = {
        "txn_id": "1", "date": "01-01-2025", "merchant": "Test", 
        "amount": "100", "currency": "USD", "status": "SUCCESS", "account_id": "A1"
    }
    is_valid, err_type, err_msg = ValidationService.validate_row(row)
    assert is_valid is True

def test_missing_column():
    row = {
        "txn_id": "1", "date": "01-01-2025", "merchant": "Test", 
        "amount": "100", "currency": "USD", "account_id": "A1"
    }
    is_valid, err_type, err_msg = ValidationService.validate_row(row)
    assert is_valid is False
    assert err_type == "missing_required_field"
    assert "status" in err_msg

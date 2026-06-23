from decimal import Decimal
from app.services.anomaly_detection_service import AnomalyDetectionService

def test_account_median_rule():
    rows = [
        {"account_id": "A1", "amount_clean": Decimal("100")},
        {"account_id": "A1", "amount_clean": Decimal("100")},
        {"account_id": "A1", "amount_clean": Decimal("100")},
        {"account_id": "A1", "amount_clean": Decimal("500")}, # > 3x median (100)
    ]
    result = AnomalyDetectionService.detect_anomalies(rows)
    assert result[0]["is_anomaly"] is False
    assert result[3]["is_anomaly"] is True
    assert "amount exceeds 3x account median" in result[3]["anomaly_reason"]

def test_domestic_usd_rule():
    rows = [
        {"account_id": "A1", "merchant_clean": "Swiggy", "currency_clean": "USD", "amount_clean": Decimal("10")}
    ]
    result = AnomalyDetectionService.detect_anomalies(rows)
    assert result[0]["is_anomaly"] is True
    assert "domestic merchant used with USD" in result[0]["anomaly_reason"]

def test_empty_account_safety():
    rows = [
        {"account_id": "A2", "amount_clean": None}
    ]
    result = AnomalyDetectionService.detect_anomalies(rows)
    assert result[0]["is_anomaly"] is False

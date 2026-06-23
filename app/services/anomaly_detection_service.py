from typing import List, Dict, Any
from decimal import Decimal

class AnomalyDetectionService:
    DOMESTIC_MERCHANTS = {"Swiggy", "Ola", "Irctc", "Zomato", "Flipkart", "Amazon", "Myntra", "Paytm", "Jio Recharge"}

    @staticmethod
    def detect_anomalies(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of cleaned rows and flags anomalies.
        Returns the updated list of rows.
        """
        # Calculate medians per account
        account_amounts: Dict[str, List[Decimal]] = {}
        for row in rows:
            acc = row.get("account_id")
            amt = row.get("amount_clean")
            if acc and amt is not None:
                if acc not in account_amounts:
                    account_amounts[acc] = []
                account_amounts[acc].append(amt)

        account_medians: Dict[str, Decimal] = {}
        for acc, amounts in account_amounts.items():
            amounts.sort()
            n = len(amounts)
            if n == 0:
                account_medians[acc] = None
                continue
            if n % 2 == 1:
                median = amounts[n // 2]
            else:
                median = (amounts[n // 2 - 1] + amounts[n // 2]) / Decimal('2.0')
            account_medians[acc] = median

        for row in rows:
            row["is_anomaly"] = False
            row["anomaly_reason"] = None
            reasons = []

            # Rule 1: Account Median Rule (3x median)
            acc = row.get("account_id")
            amt = row.get("amount_clean")
            if acc and amt is not None and acc in account_medians:
                median = account_medians[acc]
                if median is not None and median > 0 and amt > (3 * median):
                    reasons.append("amount exceeds 3x account median")

            # Rule 2: Domestic Merchant USD Rule
            merchant = row.get("merchant_clean")
            currency = row.get("currency_clean")
            if merchant and currency == "USD":
                # merchant_clean is title-cased
                if merchant in AnomalyDetectionService.DOMESTIC_MERCHANTS:
                    reasons.append("domestic merchant used with USD")

            if reasons:
                row["is_anomaly"] = True
                row["anomaly_reason"] = " | ".join(reasons)

        return rows

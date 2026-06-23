import json
from typing import List, Dict, Any

class PromptBuilder:
    VALID_CATEGORIES = [
        "Food", "Shopping", "Travel", "Transport", 
        "Utilities", "Cash Withdrawal", "Entertainment", "Other"
    ]

    @staticmethod
    def build_classification_prompt(transactions: List[Dict[str, Any]]) -> str:
        prompt = (
            "You are a financial categorization AI. "
            "Categorize the following transactions into exactly one of these categories: "
            f"{', '.join(PromptBuilder.VALID_CATEGORIES)}.\n\n"
            "Return ONLY a valid JSON array of objects. Each object must have exactly two keys: 'txn_id' and 'category'.\n"
            "Do not include markdown blocks like ```json ... ```, just output the raw JSON array.\n\n"
            "Transactions:\n"
        )
        # We only send what's necessary to save tokens
        clean_txns = []
        for tx in transactions:
            clean_txns.append({
                "txn_id": tx.get("txn_id"),
                "merchant": tx.get("merchant_clean"),
                "amount": str(tx.get("amount_clean")),
                "currency": tx.get("currency_clean")
            })
        prompt += json.dumps(clean_txns, indent=2)
        return prompt

    @staticmethod
    def build_summary_prompt(data: Dict[str, Any]) -> str:
        prompt = (
            "You are a financial risk analyst AI. "
            "Analyze the following financial summary for a batch of transactions.\n\n"
            "Provide a short 2-3 sentence 'narrative' summarizing the spend behavior, "
            "and assign a 'risk_level' which must be exactly one of: 'low', 'medium', or 'high'.\n\n"
            "Return ONLY a valid JSON object with keys 'narrative' and 'risk_level'. "
            "Do not include markdown blocks like ```json ... ```.\n\n"
            "Data:\n"
            f"{json.dumps(data, indent=2)}"
        )
        return prompt

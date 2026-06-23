import asyncio
import pandas as pd
from decimal import Decimal
import json

from app.services.validation_service import ValidationService
from app.services.cleaning_service import CleaningService
from app.services.deduplication_service import DeduplicationService
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.llm.openai_client import OpenAIClient
from app.services.llm.prompt_builder import PromptBuilder

# 1. Parse CSV (bypassing CSVParserService due to NameError bug)
file_path = "transactions.csv"
df = pd.read_csv(file_path, dtype=str)

print("=== SECTION 1: CSV STRUCTURE ===")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))
print("Columns:", df.columns.tolist())

# Check missing columns
required_columns = ["txn_id", "date", "merchant", "amount", "currency", "status", "account_id"]
missing = [c for c in required_columns if c not in df.columns]
print("Missing columns:", missing)
print("Empty rows:", df.isnull().all(axis=1).sum())
print("Duplicate rows exact:", df.duplicated().sum())

# Emulate parser
df_parsed = df.where(pd.notnull(df), None)
df_parsed.columns = [c.strip().lower() for c in df_parsed.columns]
parsed_rows = df_parsed.to_dict('records')
for i, r in enumerate(parsed_rows): r['row_number'] = i + 2

# 2. Validation
valid_rows = []
invalid_rows = []
error_breakdown = {}

for row in parsed_rows:
    is_valid, err_type, err_msg = ValidationService.validate_row(row)
    if is_valid:
        valid_rows.append(row)
    else:
        invalid_rows.append({"row": row, "err_type": err_type, "err_msg": err_msg})
        error_breakdown[err_type] = error_breakdown.get(err_type, 0) + 1

print("\n=== SECTION 2: VALIDATION ===")
print("Valid rows:", len(valid_rows))
print("Invalid rows:", len(invalid_rows))
print("Error breakdown:", json.dumps(error_breakdown, indent=2))
if invalid_rows:
    print("Sample invalid row:", invalid_rows[0])

# 3. Cleaning
clean_rows = []
clean_failed_rows = []

for row in valid_rows:
    cleaned = CleaningService.clean_row(row)
    if cleaned.get("date_clean") is None or cleaned.get("amount_clean") is None:
        clean_failed_rows.append(cleaned)
    else:
        clean_rows.append(cleaned)

print("\n=== SECTION 3: CLEANING ===")
print("Clean successful:", len(clean_rows))
print("Clean failed (e.g. bad date):", len(clean_failed_rows))
print("Sample cleaned row transformations:")
for i in range(min(3, len(clean_rows))):
    r = valid_rows[i]
    c = clean_rows[i]
    print(f"Date: {r['date']} -> {c['date_clean']}")
    print(f"Amount: {r['amount']} -> {c['amount_clean']}")
    print(f"Merchant: {r['merchant']} -> {c['merchant_clean']}")

# 4. Deduplication
unique_rows = []
duplicates = []
seen_hashes = set()
for row in clean_rows:
    h = DeduplicationService.generate_hash(row)
    if h in seen_hashes:
        duplicates.append(row)
    else:
        seen_hashes.add(h)
        unique_rows.append(row)

print("\n=== SECTION 4: DEDUPLICATION ===")
print("Unique rows:", len(unique_rows))
print("Duplicates caught:", len(duplicates))
if duplicates:
    print("Sample duplicate:", duplicates[0].get("txn_id"))

# 5. Anomaly Detection
anomalies_detected = AnomalyDetectionService.detect_anomalies(unique_rows)
anomalies_only = [x for x in anomalies_detected if x.get("is_anomaly")]

print("\n=== SECTION 5: ANOMALY DETECTION ===")
print("Total anomalies:", len(anomalies_only))
for a in anomalies_only:
    print(f"Row {a['txn_id']} -> {a.get('anomaly_reason')} (Amount: {a.get('amount_clean')} {a.get('currency_clean')}, Context: {a.get('merchant_clean')})")

# 7. LLM Classification (Mock or check batch logic)
missing_category = [r for r in anomalies_detected if not r.get("category_final")]
print("\n=== SECTION 7: CLASSIFICATION ===")
print("Rows missing category:", len(missing_category))
batch_size = 20
num_batches = (len(missing_category) + batch_size - 1) // batch_size
print("Batch size:", batch_size)
print("Number of batches needed:", num_batches)
print("Valid Categories List in PromptBuilder:", PromptBuilder.VALID_CATEGORIES)

# 8. Summary Generation logic
total_inr = sum([tx['amount_clean'] for tx in anomalies_detected if tx.get('currency_clean') == 'INR' and tx.get('amount_clean')])
total_usd = sum([tx['amount_clean'] for tx in anomalies_detected if tx.get('currency_clean') == 'USD' and tx.get('amount_clean')])
print("\n=== SECTION 8: SUMMARY GENERATION ===")
print("total_spend_inr:", total_inr)
print("total_spend_usd:", total_usd)

merchant_counts = {}
for tx in anomalies_detected:
    mc = tx.get("merchant_clean")
    if mc:
        merchant_counts[mc] = merchant_counts.get(mc, 0) + 1
print("top_merchants:", dict(sorted(merchant_counts.items(), key=lambda x: x[1], reverse=True)[:3]))
print("anomaly_count:", len(anomalies_only))

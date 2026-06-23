# Phase 2
Excellent. Since Phase 1 is locked, Phase 2 becomes the **core business logic phase**. This is where the assignment actually starts becoming the transaction processing system.

One important principle:

**Phase 1 built the house foundation.**

**Phase 2 builds the entire transaction processing engine.**

Do NOT start LLM classification or summary generation yet. Those belong to Phase 3.

---

# PHASE 2 – CSV INGESTION, VALIDATION, CLEANING, ANOMALY DETECTION & DATA PERSISTENCE

You are continuing from the already completed Phase 1 foundation.

Assume:

* FastAPI exists
* PostgreSQL exists
* Redis exists
* Celery exists
* Docker exists
* Models exist
* Migrations exist
* Job endpoints exist

DO NOT rebuild Phase 1.

Only implement Phase 2 functionality.

---

# PHASE 2 OBJECTIVE

Build the complete transaction processing engine.

When a CSV is uploaded:

1. Create Job
2. Queue Job
3. Worker picks Job
4. Parse CSV
5. Validate rows
6. Split rows into:

   * valid transactions
   * invalid rows
7. Clean valid rows
8. Detect anomalies
9. Save everything
10. Update Job progress

NO LLM YET.

NO SUMMARY GENERATION YET.

Those belong to Phase 3.

---

# FINAL DATA FLOW (LOCKED)

User Uploads CSV

↓

POST /jobs/upload

↓

Store uploaded CSV

↓

Create Job(status=pending)

↓

Queue Job ID

↓

Worker consumes Job

↓

Read CSV

↓

Validate Rows

↓

Valid Rows
→ Transaction Pipeline

Invalid Rows
→ RowError Table

↓

Clean Transactions

↓

Detect Anomalies

↓

Persist Results

↓

Update Job Status

↓

completed

---

# FILE STORAGE STRATEGY

Implement local storage.

Folder:

uploads/

Pattern:

uploads/{job_id}/transactions.csv

Store:

* original file
* preserve original filename

Job table should store:

file_path

Add migration if needed.

---

# CSV PARSING REQUIREMENTS

Use:

pandas

Requirements:

* support UTF-8
* support quoted values
* support commas inside quoted fields

Do not manually parse CSV.

Use pandas robust parsing.

---

# EXPECTED CSV COLUMNS

txn_id

date

merchant

amount

currency

status

category

account_id

notes

---

# FILE VALIDATION

Implement file-level validation.

Before queueing:

Check:

1. file exists
2. extension = .csv
3. not empty
4. required columns exist

Required:

txn_id
date
merchant
amount
currency
status
account_id

If validation fails:

Return:

HTTP 400

Do NOT create Job.

Do NOT enqueue.

---

# ROW VALIDATION STRATEGY

Important.

The system must support partial success.

A single bad row must NEVER fail entire Job.

---

# VALIDATION PIPELINE

For every row:

Check:

* txn_id exists
* date exists
* merchant exists
* amount exists
* currency exists
* status exists
* account_id exists

---

If row fails:

Insert into:

row_errors

Continue processing.

Never crash job.

---

# ROW ERROR STRUCTURE

Store:

job_id

row_number

raw_row_data

error_stage

error_type

error_message

Examples:

missing_required_field

invalid_date

invalid_amount

duplicate_row

malformed_row

---

# CLEANING ENGINE

Create dedicated service:

CleaningService

Do NOT mix inside worker.

Worker should orchestrate.

CleaningService performs cleaning.

---

# CLEANING RULES (LOCKED)

Rule 1

Normalize dates.

Input:

01-06-2025

Output:

2025-06-01

---

Input:

2025/06/01

Output:

2025-06-01

---

Store:

date_raw
date_clean

---

Rule 2

Amount cleanup.

Input:

$500

Output:

500

Store:

amount_raw
amount_clean

---

Rule 3

Currency normalization.

Input:

inr

Output:

INR

Input:

usd

Output:

USD

---

Rule 4

Status normalization.

Input:

success

Output:

SUCCESS

Input:

pending

Output:

PENDING

Input:

failed

Output:

FAILED

---

Rule 5

Category handling.

DO NOT permanently set:

Uncategorised

yet.

Instead:

category_raw = original value

If missing:

category_final = NULL

Because Phase 3 LLM will classify it.

Only after LLM failure do we fallback.

---

Rule 6

Merchant normalization.

Trim spaces.

Normalize casing.

Store:

merchant_raw
merchant_clean

---

# DUPLICATE DETECTION

Assignment says:

remove exact duplicates.

Implement exact-row dedupe.

Strategy:

Generate hash from:

txn_id
date
merchant
amount
currency
status
category
account_id

If hash already seen:

Insert duplicate row into:

row_errors

error_type = duplicate_row

Do not insert into transactions.

---

# ANOMALY DETECTION ENGINE

Create:

AnomalyDetectionService

Worker should call service.

Service returns:

is_anomaly

anomaly_reason

---

# ANOMALY RULE 1

Account Median Rule

For each account_id:

Calculate median amount.

Threshold:

3 × median

Example:

100
200
300
400
500

Median:

300

Threshold:

900

If amount > 900:

Flag anomaly.

---

Store:

is_anomaly = true

anomaly_reason =
"amount exceeds 3x account median"

---

# ANOMALY RULE 2

Domestic Merchant USD Rule

Domestic merchants:

Swiggy
Ola
IRCTC

If:

currency = USD

and

merchant in domestic list

Flag anomaly.

Reason:

"domestic merchant used with USD"

---

# DATABASE PERSISTENCE

Only VALID rows go into transactions.

Invalid rows NEVER go into transactions.

Invalid rows ONLY go into row_errors.

---

# TRANSACTION INSERT FLOW

Validated

↓

Cleaned

↓

Anomaly Checked

↓

Insert Transaction

---

# JOB STATUS MANAGEMENT

Job lifecycle:

pending

↓

processing

↓

completed

or

failed

---

# PROCESSING STAGE FIELD

Update during execution.

Stages:

uploaded

parsing

validating

cleaning

anomaly_detection

persisting

completed

This is internal progress tracking.

---

# WORKER FAILURE HANDLING

Worker crashes?

Do not corrupt database.

Requirements:

Use database transactions.

Commit per stage.

Never keep entire job in one transaction.

---

# PARTIAL SUCCESS HANDLING

Example:

90 rows uploaded.

82 valid.

8 invalid.

Result:

transactions = 82

row_errors = 8

job = completed

NOT failed.

---

# IDPOTENCY REQUIREMENT

If worker accidentally retries same job:

Do not duplicate rows.

Implement:

job_id + row_number

or

row_hash uniqueness.

Prevent duplicate inserts.

---

# STATUS ENDPOINT ENHANCEMENT

GET /jobs/{id}/status

Should now return:

job_id

status

processing_stage

row_count_raw

row_count_valid

row_count_invalid

---

# RESULTS ENDPOINT ENHANCEMENT

GET /jobs/{id}/results

Return:

cleaned_transactions

row_errors

anomalies

NO summary yet.

Summary comes in Phase 3.

---

# LOGGING REQUIREMENTS

Log:

Job Started

Parsing Started

Validation Started

Cleaning Started

Anomaly Detection Started

Persistence Started

Job Completed

Job Failed

Include job_id everywhere.

---

# TEST CASES REQUIRED

Test 1

Perfect CSV

Expected:

All rows valid

No row_errors

---

Test 2

Missing required fields

Expected:

Rows moved to row_errors

Job still completed

---

Test 3

Duplicate rows

Expected:

Duplicates moved to row_errors

---

Test 4

Mixed date formats

Expected:

Normalized

---

Test 5

USD + Swiggy

Expected:

Anomaly flagged

---

Test 6

Large outlier amount

Expected:

Anomaly flagged

---

# PHASE 2 DELIVERABLES

At end of Phase 2:

✓ Upload CSV

✓ Queue Job

✓ Worker Processes Job

✓ CSV Parsed

✓ Validation Working

✓ RowError Tracking Working

✓ Cleaning Working

✓ Duplicate Removal Working

✓ Anomaly Detection Working

✓ Transactions Persisted

✓ Job Status Updated

✓ Results Endpoint Working

STOP.

Do NOT implement:

LLM Classification

LLM Retry Logic

Narrative Summary

Risk Levels

JobSummary Population

Those belong entirely to Phase 3.

After Phase 2 is complete and tested, the system will already process CSVs end-to-end and store valid/invalid rows correctly. Phase 3 will then add the AI layer (batch LLM classification, retries, narrative summary, risk level generation, and JobSummary creation) on top of this deterministic pipeline.

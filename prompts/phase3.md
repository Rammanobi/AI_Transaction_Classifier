# Phase 3
Perfect. At the end of **Phase 2**, your system is already capable of:

* Uploading CSV
* Creating Jobs
* Queueing Jobs
* Processing CSVs
* Validating rows
* Cleaning data
* Detecting anomalies
* Storing valid transactions
* Storing invalid rows
* Returning results

But it is still **not AI-powered yet**.

The assignment title is:

> AI-Powered Transaction Processing Pipeline

That means Phase 3 is where we add the intelligence layer.

---

# PHASE 3 – LLM CLASSIFICATION, SUMMARY GENERATION, RETRY LOGIC & AI LAYER

Continue from completed Phase 2.

Assume:

✓ FastAPI complete

✓ PostgreSQL complete

✓ Redis complete

✓ Celery complete

✓ CSV processing complete

✓ Validation complete

✓ Cleaning complete

✓ Anomaly detection complete

✓ Transactions persistence complete

✓ RowError persistence complete

DO NOT rebuild previous phases.

Only implement AI functionality.

---

# PHASE 3 OBJECTIVE

Transform the deterministic transaction pipeline into an AI-powered transaction processing system.

Implement:

1. Missing category classification
2. Batch LLM processing
3. Retry logic
4. Narrative summary generation
5. Risk level generation
6. JobSummary persistence
7. AI failure handling

This phase must satisfy all LLM-related requirements from the assignment.

---

# FINAL AI ARCHITECTURE

Current Pipeline:

CSV

↓

Validation

↓

Cleaning

↓

Anomaly Detection

↓

Transactions Stored

Phase 3 adds:

↓

LLM Category Classification

↓

Summary Aggregation

↓

LLM Narrative Summary

↓

JobSummary Storage

↓

Job Completed

---

# CRITICAL DESIGN RULE

LLM MUST NOT PERFORM:

* cleaning
* validation
* anomaly detection
* duplicate detection

Those are deterministic operations.

LLM should only perform:

1. Category Classification
2. Narrative Summary Generation

Nothing else.

---

# CREATE LLM SERVICE LAYER

Create:

services/llm/

Structure:

classification_service.py

summary_service.py

prompt_builder.py

retry_handler.py

llm_client.py

Do not place LLM calls inside worker code.

Worker orchestrates only.

---

# SUPPORTED LLM PROVIDERS

Design abstraction layer.

Must support:

Gemini

OpenAI

Future local models

Worker should never know which provider is used.

Use:

LLMClient interface

Example:

class LLMClient:
classify()
summarize()

Implement provider adapters.

---

# CATEGORY CLASSIFICATION REQUIREMENT

Assignment categories:

Food

Shopping

Travel

Transport

Utilities

Cash Withdrawal

Entertainment

Other

No additional categories allowed.

---

# WHICH ROWS GO TO LLM?

ONLY:

category_final IS NULL

Do not send rows that already have category.

Example:

Row A

category = Food

Skip.

---

Row B

category = NULL

Send to LLM.

---

# BATCHING STRATEGY (LOCKED)

NEVER:

1 API call per row

BAD:

90 rows

↓

90 LLM calls

---

Use batching.

Example:

Batch size:

20

Rows:

1-20

↓

LLM Call

Rows:

21-40

↓

LLM Call

etc.

---

Create configurable:

CLASSIFICATION_BATCH_SIZE

Default:

20

---

# CLASSIFICATION PROMPT

Prompt must:

* force JSON output
* prohibit markdown
* prohibit explanations
* return category only

Input:

merchant

notes

currency

status

optional amount

Output:

[
{
"row_number": 12,
"category": "Food"
}
]

Strict JSON.

---

# RESPONSE VALIDATION

Never trust LLM output.

Validate response.

Rules:

category must be one of:

Food
Shopping
Travel
Transport
Utilities
Cash Withdrawal
Entertainment
Other

If invalid:

fallback = Other

Log issue.

Continue.

---

# CLASSIFICATION PERSISTENCE

Store:

llm_category

category_final

llm_raw_response

llm_failed

Update transactions table.

---

# RETRY LOGIC (LOCKED)

Assignment requires:

3 retries

Exponential backoff

Continue on failure

---

Implementation:

Attempt 1

↓

Fail

↓

Wait 1 sec

↓

Attempt 2

↓

Fail

↓

Wait 2 sec

↓

Attempt 3

↓

Fail

↓

Wait 4 sec

↓

Mark batch failed

Continue Job

---

# IF BATCH FAILS

DO NOT FAIL JOB.

Set:

llm_failed = true

category_final = Other

Continue processing.

This is a hard requirement.

---

# SUMMARY GENERATION STAGE

After all transactions processed:

Generate aggregates using Python.

NOT LLM.

---

# AGGREGATES TO COMPUTE

total_spend_inr

total_spend_usd

top_3_merchants

anomaly_count

category_breakdown

valid_row_count

invalid_row_count

---

# WHY PYTHON?

Deterministic.

Fast.

Reliable.

Do not waste LLM tokens.

---

# LLM SUMMARY GENERATION

Send ONLY aggregate data.

Do NOT send all transactions.

Input:

{
"total_spend_inr": 250000,
"total_spend_usd": 500,
"top_merchants": [
"Swiggy",
"Amazon",
"Ola"
],
"anomaly_count": 4
}

---

# REQUIRED OUTPUT

{
"narrative": "...",
"risk_level": "medium"
}

---

# RISK LEVEL RULES

Allow:

low

medium

high

No other values.

---

# SUMMARY PROMPT REQUIREMENTS

Narrative:

2-3 sentences

Concise

Professional

Financial-analysis style

No markdown

No bullet points

No explanations

JSON only

---

# RESPONSE VALIDATION

Validate:

risk_level

must be:

low
medium
high

If invalid:

fallback:

medium

---

# JOB SUMMARY TABLE

Populate:

job_summaries

Fields:

job_id

total_spend_inr

total_spend_usd

top_merchants

anomaly_count

narrative

risk_level

created_at

---

# RESULTS ENDPOINT UPGRADE

GET /jobs/{job_id}/results

Must now return:

job

summary

transactions

row_errors

anomalies

category_breakdown

---

# STATUS ENDPOINT UPGRADE

Completed jobs should include:

summary preview

Example:

{
"job_id": "...",
"status": "completed",
"summary": {
"anomaly_count": 4,
"risk_level": "medium"
}
}

Keep lightweight.

Do NOT return transactions.

---

# AI OBSERVABILITY

Log:

Classification Started

Classification Batch #1

Classification Batch #2

Summary Generation Started

Summary Generation Completed

LLM Retry Attempt

LLM Failure

Job Summary Saved

---

# AI FAILURE HANDLING

Case:

Gemini Down

OpenAI Down

Network Failure

Timeout

Rate Limit

Must not crash job.

Mark:

llm_failed = true

Fallback category:

Other

Fallback risk:

medium

Continue.

---

# TEST CASES

Test 1

Missing categories

Expected:

classified successfully

---

Test 2

Invalid category returned

Expected:

fallback Other

---

Test 3

LLM timeout

Expected:

retry

---

Test 4

LLM fails all retries

Expected:

llm_failed=true

Job completed

---

Test 5

Summary generation success

Expected:

job_summary created

---

Test 6

Summary generation failure

Expected:

fallback narrative

fallback risk level

Job completed

---

# FALLBACK SUMMARY

If summary LLM fails:

Narrative:

"Summary generation unavailable due to LLM processing failure."

Risk:

medium

Store anyway.

Never leave JobSummary empty.

---

# PHASE 3 DELIVERABLES

✓ LLM abstraction layer

✓ Batch classification

✓ Category assignment

✓ Retry logic

✓ Exponential backoff

✓ Summary generation

✓ Risk level generation

✓ JobSummary persistence

✓ LLM failure handling

✓ Results endpoint upgraded

✓ Status endpoint upgraded

STOP.

Do NOT implement:

Production scaling

Metrics

Monitoring

Security hardening

Docker optimization

Load testing

CI/CD

Cloud deployment

Those belong to Phase 4.

This completes the entire functional assignment. After Phase 3, the project fully satisfies the problem statement requirements.

**Phase 4** will be the engineering excellence phase:

* Docker production readiness
* Health checks
* Structured logging
* Monitoring
* Testing strategy
* CI/CD
* Repository cleanup
* README
* Architecture diagrams
* Interview/demo preparation
* "What breaks at 100× scale?" discussion
* Technical review video preparation

That phase is what often separates a submission that *works* from one that looks like it was built by a backend engineer.

Not fully. In Phase 3, I described the classification and summary requirements, but I did **not lock the final production prompt templates**. Those should be explicitly defined because prompt quality directly affects the assignment.

These are the two prompts I would lock.

# Prompt 1: Category Classification

This is used only for rows where:

```text
category_final IS NULL
```

### System Prompt

```text
You are a financial transaction classification engine.

Your task is to classify transactions into exactly one of the following categories:

Food
Shopping
Travel
Transport
Utilities
Cash Withdrawal
Entertainment
Other

Rules:

1. Return valid JSON only.
2. Do not return markdown.
3. Do not explain reasoning.
4. Do not create new categories.
5. Every transaction must receive exactly one category.
6. If uncertain, return "Other".

Output format:

[
  {
    "row_number": 1,
    "category": "Food"
  }
]
```

### User Prompt Template

```json
{
  "transactions": [
    {
      "row_number": 12,
      "merchant": "Swiggy",
      "notes": "food order",
      "currency": "INR"
    },
    {
      "row_number": 13,
      "merchant": "Ola",
      "notes": "cab ride",
      "currency": "INR"
    }
  ]
}
```

### Expected Response

```json
[
  {
    "row_number": 12,
    "category": "Food"
  },
  {
    "row_number": 13,
    "category": "Transport"
  }
]
```

---

# Prompt 2: Narrative Summary

Important:

Do NOT send all transactions.

Send only aggregates generated by Python.

### System Prompt

```text
You are a financial analyst.

Generate a concise financial spending summary.

Requirements:

1. Return JSON only.
2. Narrative must be 2-3 sentences.
3. Narrative should summarize spending behavior.
4. Risk level must be one of:

low
medium
high

5. No markdown.
6. No explanations.
7. No extra fields.

Output format:

{
  "narrative": "...",
  "risk_level": "medium"
}
```

### User Prompt Template

```json
{
  "total_spend_inr": 250000,
  "total_spend_usd": 500,
  "top_merchants": [
    "Swiggy",
    "Amazon",
    "Ola"
  ],
  "anomaly_count": 4,
  "category_breakdown": {
    "Food": 120000,
    "Shopping": 70000,
    "Transport": 30000
  }
}
```

### Expected Response

```json
{
  "narrative": "Most spending is concentrated in food and shopping categories. Four unusual transactions were detected, indicating moderate transaction risk.",
  "risk_level": "medium"
}
```

---

# One More Thing I Would Add

Create a dedicated module:

```text
services/llm/
│
├── prompts/
│   ├── classification_prompt.py
│   └── summary_prompt.py
│
├── classification_service.py
├── summary_service.py
├── retry_handler.py
├── llm_client.py
```

Then:

```python
classification_prompt.build_prompt(batch)

summary_prompt.build_prompt(summary_data)
```

Never hardcode prompts inside workers.

---

# One Improvement I Would Make

For classification, send:

```json
{
  "row_number": 12,
  "merchant": "Swiggy",
  "notes": "food order",
  "currency": "INR",
  "amount": 250
}
```

instead of only merchant.

The extra context improves classification accuracy significantly while still keeping token usage low.

So yes, before Phase 4 I would officially lock these two prompt templates as part of the architecture because they are the only two LLM tasks in the entire system:

1. **Category Classification Prompt** ✅
2. **Narrative Summary Prompt** ✅

Everything else remains deterministic Python logic.

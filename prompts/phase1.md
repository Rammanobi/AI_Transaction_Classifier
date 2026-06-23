# Phase 1
Perfect. At this stage, don't jump into coding. Your Anti-Gravity agent should build the project in **4 phases**.

The biggest mistake is asking Anti-Gravity:

```text
Build the entire project.
```

Instead, make it finish:

```text
Phase 1 → Foundation & Project Skeleton
Phase 2 → Database, Queue & Core Processing
Phase 3 → LLM Integration & Results Generation
Phase 4 → Docker, Testing, Documentation & Production Hardening
```

Right now I will give **PHASE 1 ONLY**.

This phase must be completed, reviewed, tested, and committed before moving to Phase 2.

---

# PHASE 1 – FOUNDATION, ARCHITECTURE LOCKING & PROJECT SKELETON

You are a Senior Backend Architect and DevOps Engineer.

Build Phase 1 of an AI-Powered Transaction Processing Pipeline.

Do NOT implement anomaly detection, LLM processing, summary generation, or business logic yet.

The goal of Phase 1 is to create a production-ready project foundation that all later phases will build upon.

---

# PROJECT OBJECTIVE

We are building a backend system that:

1. Accepts a dirty financial transaction CSV.
2. Creates a background processing job.
3. Processes the CSV asynchronously.
4. Cleans and validates transaction data.
5. Detects anomalies.
6. Uses an LLM for category classification.
7. Generates a narrative summary.
8. Stores everything in PostgreSQL.
9. Exposes polling APIs.

However, in Phase 1 we are only creating the architecture foundation.

No business processing should exist yet.

---

# FINAL ARCHITECTURE DECISIONS (LOCKED)

The following architectural decisions are already finalized and MUST NOT be changed.

## Infrastructure

Services:

* FastAPI
* PostgreSQL
* Redis
* Celery Worker
* Docker Compose

All services must eventually run using:

docker compose up

No manual setup allowed.

---

# DATABASE DESIGN (LOCKED)

We are using a hybrid approach.

Three primary tables:

## jobs

Tracks entire file processing lifecycle.

Responsibilities:

* Track uploaded files
* Track processing status
* Track counts
* Track timestamps
* Track failures

Fields:

id
filename
file_hash
status
row_count_raw
row_count_valid
row_count_invalid
created_at
started_at
completed_at
error_message
processing_stage

---

## transactions

Stores ONLY valid rows.

Invalid rows must never be stored here.

Fields:

id
job_id
row_number

txn_id

date_raw
date_clean

merchant_raw
merchant_clean

amount_raw
amount_clean

currency_raw
currency_clean

status_raw
status_clean

category_raw
category_final

account_id

notes_raw

is_anomaly
anomaly_reason

llm_category
llm_raw_response
llm_failed

created_at

---

## row_errors

Stores rejected rows.

Responsibilities:

* validation failures
* parsing failures
* malformed data
* duplicate rejection records

Fields:

id
job_id
row_number
raw_row_data
error_stage
error_type
error_message
created_at

---

## job_summaries

Stores final report.

Fields:

id
job_id

total_spend_inr
total_spend_usd

top_merchants

anomaly_count

narrative

risk_level

created_at

---

# JOB STATUS VALUES (LOCKED)

Only:

pending
processing
completed
failed

Do not create additional job statuses.

---

# API DESIGN (LOCKED)

Endpoint 1

POST /jobs/upload

Purpose:

Upload CSV.

Create Job.

Queue Job.

Return job_id immediately.

Response:

{
"job_id": "...",
"status": "pending"
}

---

Endpoint 2

GET /jobs/{job_id}/status

Lightweight endpoint.

Purpose:

Frequent polling.

Return:

* job status
* row counts
* processing stage

Must remain lightweight.

No transactions.

No anomalies.

No full report.

---

Endpoint 3

GET /jobs/{job_id}/results

Heavy endpoint.

Purpose:

Return final report.

Includes:

* cleaned transactions
* row errors
* anomalies
* category breakdown
* summary

---

Endpoint 4

GET /jobs

Returns:

* job list
* filename
* status
* timestamps
* counts

Supports:

?status=

---

# PARTIAL SUCCESS STRATEGY (LOCKED)

The system must support partial success.

Examples:

Scenario A

90 rows uploaded.

82 valid.

8 invalid.

Result:

82 rows -> transactions

8 rows -> row_errors

Job -> completed

NOT failed.

---

Scenario B

LLM classification fails.

Retry 3 times.

Still fails.

Mark:

llm_failed = true

Continue processing.

Job remains completed.

---

Scenario C

Worker crashes midway.

System must support restartability.

Architecture should allow reprocessing without corrupting data.

---

# PHASE 1 GOALS

Implement ONLY:

1. Project structure
2. Configuration system
3. Database setup
4. SQLAlchemy models
5. Alembic migrations
6. FastAPI application
7. Dependency injection
8. Health endpoints
9. Placeholder job endpoints
10. Celery skeleton
11. Redis integration skeleton
12. Docker skeleton

NO BUSINESS LOGIC YET.

---

# REQUIRED FOLDER STRUCTURE

app/

api/
v1/

jobs.py

core/

config.py
database.py

models/

job.py
transaction.py
row_error.py
job_summary.py

schemas/

job.py
transaction.py
row_error.py

services/

jobs/

repositories/

jobs/

workers/

tasks.py

utils/

main.py

---

# DATABASE REQUIREMENTS

Use:

* PostgreSQL
* SQLAlchemy 2.x
* Alembic

Create models.

Create migrations.

Create startup database initialization.

---

# CONFIGURATION REQUIREMENTS

Create centralized settings.

Environment variables:

POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT

REDIS_HOST
REDIS_PORT

CELERY_BROKER_URL

OPENAI_API_KEY

Use pydantic-settings.

No hardcoded values.

---

# FASTAPI REQUIREMENTS

Create:

GET /health

Response:

{
"status":"healthy"
}

Create placeholder endpoints:

POST /jobs/upload

GET /jobs/{job_id}/status

GET /jobs/{job_id}/results

GET /jobs

These should return mock responses for now.

No processing yet.

---

# CELERY REQUIREMENTS

Create worker skeleton.

Create sample task.

Verify:

API can enqueue task.

Worker can consume task.

No CSV processing yet.

---

# REDIS REQUIREMENTS

Configure broker.

Create queue.

Verify connectivity.

---

# DOCKER REQUIREMENTS

Create:

api container
worker container
postgres container
redis container

Create docker-compose.yml

All services must start.

Health checks preferred.

---

# DELIVERABLES OF PHASE 1

At the end of Phase 1 I expect:

1. Project structure complete
2. Database models complete
3. Migrations working
4. FastAPI running
5. Redis connected
6. Celery connected
7. Docker Compose running
8. Health endpoint working
9. Placeholder endpoints working
10. Repository ready for Phase 2

Do NOT begin cleaning logic.

Do NOT begin anomaly detection.

Do NOT begin LLM integration.

Do NOT begin summary generation.

Stop after foundation setup is complete.

This is the exact Phase 1 prompt I would give Anti-Gravity. Once Phase 1 is finished and reviewed, then we move to **Phase 2: CSV ingestion, validation pipeline, Job lifecycle management, Transaction/RowError persistence, and deterministic cleaning/anomaly engine**. That phase is where the real business logic starts.

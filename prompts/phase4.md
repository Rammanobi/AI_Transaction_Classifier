# Phase 4
Perfect. Now we reach **Phase 4**.

At the end of Phase 3, the assignment is already functionally complete.

Most candidates stop there.

But the assignment also asks:

* Docker Compose deployment
* Architecture explanation
* Scale discussion
* Technical review video
* Production thinking

This is where Phase 4 comes in.

Phase 4 is not about adding features.

Phase 4 is about making the project look like it was built by a Backend + DevOps Engineer instead of someone who only completed the requirements.

---

# PHASE 4 – PRODUCTION HARDENING, DEVOPS, TESTING, OBSERVABILITY, DOCUMENTATION & INTERVIEW PREPARATION

Continue from completed Phase 3.

Assume:

✓ CSV Processing Complete

✓ Validation Complete

✓ Cleaning Complete

✓ Anomaly Detection Complete

✓ LLM Classification Complete

✓ Summary Generation Complete

✓ PostgreSQL Complete

✓ Redis Complete

✓ Celery Complete

✓ Docker Compose Complete

DO NOT REBUILD PREVIOUS PHASES.

This phase focuses on engineering quality.

---

# PHASE 4 OBJECTIVE

Transform the working solution into a production-style engineering project.

Focus Areas:

1. Reliability
2. Observability
3. Docker Optimization
4. API Documentation
5. Testing
6. Security
7. Scalability Discussion
8. README
9. Architecture Diagrams
10. Technical Review Preparation

---

# SECTION 1: OBSERVABILITY

Create structured logging.

Do NOT use random print statements.

Use:

Python logging

or

structlog

---

# LOG FORMAT

Every log should contain:

timestamp

service_name

job_id

processing_stage

message

log_level

---

Example:

{
"timestamp":"...",
"service":"worker",
"job_id":"123",
"stage":"cleaning",
"message":"Cleaning started"
}

---

# REQUIRED LOG EVENTS

Job Created

Job Queued

Worker Started

CSV Parsed

Validation Started

Validation Completed

Cleaning Started

Cleaning Completed

Anomaly Detection Started

Anomaly Detection Completed

Classification Started

Classification Completed

Summary Started

Summary Completed

Job Completed

Job Failed

Retry Attempt

Database Error

LLM Error

---

# SECTION 2: HEALTH CHECKS

Create health endpoints.

GET /health

Basic health.

---

Create deeper checks.

GET /health/db

Verify PostgreSQL connection.

---

GET /health/redis

Verify Redis connection.

---

GET /health/full

Verify:

API

Postgres

Redis

Worker Connectivity

---

Response Example

{
"api":"healthy",
"postgres":"healthy",
"redis":"healthy"
}

---

# SECTION 3: DOCKER HARDENING

Optimize Dockerfiles.

Requirements:

Use slim images.

Example:

python:3.12-slim

---

Avoid unnecessary packages.

---

Use:

.dockerignore

Exclude:

.git

venv

**pycache**

.pytest_cache

uploads

---

# CONTAINER STARTUP ORDER

Use:

depends_on

Health checks

Ensure:

Postgres

↓

Redis

↓

API

↓

Worker

---

# DOCKER COMPOSE REQUIREMENTS

Single command:

docker compose up

Must fully start system.

No manual steps.

---

# SECTION 4: DATABASE HARDENING

Create indexes.

Required indexes:

jobs.status

jobs.created_at

transactions.job_id

transactions.account_id

transactions.is_anomaly

row_errors.job_id

job_summaries.job_id

---

# FUTURE SCALING INDEXES

Optional:

merchant

txn_id

category_final

---

# SECTION 5: API DOCUMENTATION

Use FastAPI OpenAPI.

Requirements:

All endpoints documented.

Request examples.

Response examples.

Error responses.

Status codes.

---

# REQUIRED STATUS CODES

200

201

400

404

422

500

---

# ERROR RESPONSE FORMAT

{
"error":"validation_failed",
"message":"Missing required column: amount"
}

Consistent everywhere.

---

# SECTION 6: TESTING

Create:

tests/

Structure:

tests/api

tests/services

tests/workers

tests/integration

---

# UNIT TESTS

Cleaning Service

Anomaly Service

Classification Parser

Summary Parser

Validation Service

---

# INTEGRATION TESTS

Upload CSV

Queue Job

Worker Processing

Results Retrieval

---

# TEST SCENARIOS

Perfect File

Missing Fields

Duplicate Rows

Invalid Date

Invalid Amount

LLM Failure

Worker Retry

Database Failure

Redis Failure

---

# COVERAGE TARGET

70%+

Not mandatory.

Good engineering signal.

---

# SECTION 7: SECURITY

Basic security only.

Do not over-engineer.

---

# FILE UPLOAD SECURITY

Validate extension.

Only CSV.

Reject others.

---

# FILE SIZE LIMIT

Example:

10 MB

Configurable.

---

# ENVIRONMENT VARIABLES

Never hardcode:

API keys

Database credentials

Redis URLs

---

Use .env

---

# SECRET MANAGEMENT

All secrets:

environment variables only

---

# SECTION 8: PERFORMANCE

Current Scale:

~100 rows

Works easily.

---

Future Scale:

100,000 rows

Need discussion.

Do NOT fully implement.

Document.

---

# SECTION 9: SCALING DISCUSSION

Assignment specifically asks:

What breaks at 100x scale?

Prepare answer.

---

# BOTTLENECK 1

Single Worker

Problem:

Processing becomes slow.

Future Solution:

Multiple Celery Workers

Tradeoff:

Higher infrastructure cost.

---

# BOTTLENECK 2

Large CSV Memory Usage

Problem:

Pandas loads entire file.

Future Solution:

Chunk Processing

Tradeoff:

More implementation complexity.

---

# BOTTLENECK 3

LLM Latency

Problem:

Large number of classification requests.

Future Solution:

Parallel Batch Processing

Caching

Tradeoff:

More operational complexity.

---

# BOTTLENECK 4

Database Writes

Problem:

Many row inserts.

Future Solution:

Bulk Inserts

Tradeoff:

Reduced per-row visibility.

---

# BOTTLENECK 5

Results Endpoint

Problem:

Huge payload.

Future Solution:

Pagination

Streaming

Tradeoff:

More API complexity.

---

# SECTION 10: TECHNICAL REVIEW PREPARATION

Assignment requires:

Architecture Walkthrough

Request Lifecycle

Scale Discussion

---

# PREPARE ARCHITECTURE EXPLANATION

Be able to explain:

User Upload

↓

FastAPI

↓

Job Creation

↓

Redis Queue

↓

Worker

↓

Validation

↓

Cleaning

↓

Anomaly Detection

↓

LLM Classification

↓

Summary Generation

↓

Database

↓

Polling

↓

Results

---

# PREPARE DATABASE EXPLANATION

Explain why:

jobs

transactions

row_errors

job_summaries

exist separately.

---

# PREPARE PARTIAL SUCCESS EXPLANATION

Example:

90 rows

82 valid

8 invalid

Job completed

row_errors stores failures

---

# PREPARE LLM EXPLANATION

LLM only used for:

Category Classification

Narrative Summary

Not used for:

Cleaning

Validation

Anomaly Detection

---

# SECTION 11: README

README must contain:

Project Overview

Architecture Diagram

Folder Structure

Setup

Environment Variables

Docker Startup

API Endpoints

Sample Requests

Sample Responses

Testing Instructions

Design Decisions

Scaling Discussion

Known Limitations

Future Improvements

---

# SECTION 12: ARCHITECTURE DIAGRAMS

Provide:

System Architecture Diagram

Request Lifecycle Diagram

Database Relationship Diagram

Worker Processing Diagram

Use:

Mermaid

draw.io

or both.

---

# FINAL DELIVERABLES

At completion of Phase 4:

✓ Production-style logging

✓ Health checks

✓ Docker hardening

✓ API documentation

✓ Tests

✓ Security basics

✓ Indexing

✓ README

✓ Architecture diagrams

✓ Scaling discussion

✓ Technical review preparation

✓ Interview preparation notes

Project now fully complete.

STOP.

No further implementation required.

# What Happens After Phase 4?

After Phase 4, do **not** ask Anti-Gravity to write more code.

Instead do:

### Final Verification Pass

Ask it to verify:

* Assignment requirement vs implementation matrix
* Missing endpoints
* Missing database fields
* Missing Docker configuration
* Missing tests
* Missing documentation
* Mermaid diagram validation
* API contract validation

Then create:

1. GitHub Repository
2. README
3. Architecture Diagram
4. 3-minute Technical Review Video Script

That becomes your final submission package.

At this point, your project plan is fully locked from:
**Phase 1 → Foundation**
**Phase 2 → Processing Engine**
**Phase 3 → AI Layer**
**Phase 4 → Production & Review Readiness**.

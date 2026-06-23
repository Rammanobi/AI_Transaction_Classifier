# ADR 002: Use Celery with Redis

## Context
CSV processing, deterministic cleaning, deduplication, and LLM classification/summarization are computationally intensive and time-consuming. Doing this synchronously in a FastAPI request cycle would lead to timeouts and poor UX.

## Decision
We chose Celery as the asynchronous task queue, backed by Redis as both the broker and result backend.

## Rationale
- **Decoupling**: API immediately returns a `job_id`, allowing the client to poll `/status` while the heavy lifting happens in the background.
- **Retries & Resilience**: Celery provides native mechanisms to retry tasks, handle crashes, and distribute workloads across multiple worker nodes.
- **Horizontal Scalability**: As load increases, we can spin up additional Celery worker containers to process jobs concurrently without altering the API layer.
- **Redis Speed**: Redis operates entirely in memory, making it the perfect low-latency broker for Celery.

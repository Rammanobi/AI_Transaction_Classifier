# ADR 001: Use PostgreSQL

## Context
The system requires a robust, ACID-compliant database to store raw transactions, cleaned transactions, anomaly flags, and multi-stage job states. We expect high volumes (up to 10M transactions/day) and need strong relational integrity.

## Decision
We chose PostgreSQL.

## Rationale
- **Reliability & ACID**: Ensures no transaction is lost during the complex multi-stage pipeline.
- **Async Support**: Native support for asynchronous drivers (`asyncpg`) which integrates perfectly with our FastAPI async stack.
- **JSONB Capabilities**: Allows us to store flexible data like `top_merchants` and `llm_raw_response` without rigid schema migrations.
- **Scale**: PostgreSQL can easily handle 10M+ rows per day with proper partitioning and indexing strategies.

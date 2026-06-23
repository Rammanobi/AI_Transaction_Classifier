# ADR 004: Use an explicit RowError Table

## Context
Real-world CSVs are messy. They contain missing columns, invalid dates, and string characters in numeric fields. If a single bad row crashes the entire job, the system is unusable.

## Decision
We implemented a `RowError` table and a "partial success" model. Invalid rows are caught, documented in the `row_errors` table with the exact reason (e.g., `invalid_date`), and the pipeline continues processing the remaining valid rows.

## Rationale
- **Observability**: Users can query the `/results` endpoint to see exactly *which* rows failed and *why*, rather than just receiving a generic "Job Failed" error.
- **Resilience**: A 10,000 row CSV with 1 bad row still yields 9,999 successful transactions.
- **Auditability**: We store the `raw_row_data` in the error table, meaning the user can reconstruct or fix the exact data that was rejected.

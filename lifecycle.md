# Life Cycle
sequenceDiagram

    participant User
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Queue as Redis
    participant Worker as Celery
    participant LLM

    User->>API: POST /jobs/upload

    API->>DB: Create Job

    API->>Queue: Enqueue Job

    API-->>User: Return job_id

    Queue->>Worker: Consume Job

    Worker->>DB: Update Status Processing

    Worker->>DB: Save Transactions

    Worker->>LLM: Classify Categories

    LLM-->>Worker: Categories

    Worker->>LLM: Generate Summary

    LLM-->>Worker: Narrative + Risk

    Worker->>DB: Save Summary

    Worker->>DB: Update Status Completed

    User->>API: GET /jobs/{id}/status

    API->>DB: Fetch Status

    DB-->>API: Status

    API-->>User: Status Response

    User->>API: GET /jobs/{id}/results

    API->>DB: Fetch Results

    DB-->>API: Results

    API-->>User: Full Report
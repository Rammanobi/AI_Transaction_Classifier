# AI Transaction Classifier Output & Architecture

Here is the final output file containing the cleaned, classified, and anomaly-detected transactions:
[output_transactions.csv](file:///c:/antigravity_par/ai_trans_classifier/output_transactions.csv)

---

## Complete Architecture & Data Flow

Below is the complete system architecture and data flow, reflecting the multi-container setup (FastAPI, Celery, Postgres, Redis, and OpenAI integration) that processes the transactions.

### System Architecture Diagram

```mermaid
graph TD
    %% User/Client
    Client[Client / cURL]

    %% API Layer (FastAPI)
    subgraph API Container [API Container - FastAPI]
        API_Endpoints[API Endpoints]
        UploadRoute[/jobs/upload]
        StatusRoute[/jobs/{id}/status]
        ResultsRoute[/jobs/{id}/results]
        API_Endpoints --- UploadRoute
        API_Endpoints --- StatusRoute
        API_Endpoints --- ResultsRoute
    end

    %% Message Broker
    Redis[(Redis Message Broker)]

    %% Worker Layer (Celery)
    subgraph Worker Container [Worker Container - Celery]
        TaskQueue[Celery Task Queue]
        Pipeline[process_csv_task]
        
        %% Services
        CSVParser[CSV Parser Service]
        Cleaner[Cleaning Service]
        Validator[Validation Service]
        Classifier[Classification Service]
        Anomaly[Anomaly Detection Service]
        Summarizer[Summary Service]
        
        Pipeline --> CSVParser
        Pipeline --> Cleaner
        Pipeline --> Validator
        Pipeline --> Classifier
        Pipeline --> Anomaly
        Pipeline --> Summarizer
    end

    %% Database Layer
    Postgres[(PostgreSQL Database)]
    
    %% External Integrations
    OpenAI[OpenAI LLM API]

    %% Connections
    Client -- "Upload CSV" --> UploadRoute
    Client -- "Poll Status" --> StatusRoute
    Client -- "Fetch CSV/JSON" --> ResultsRoute
    
    UploadRoute -- "Create Job, Publish Task" --> Redis
    UploadRoute -- "Save State" --> Postgres
    StatusRoute -- "Query State" --> Postgres
    ResultsRoute -- "Query Output" --> Postgres
    
    Redis -- "Consume Task" --> TaskQueue
    TaskQueue --> Pipeline
    
    CSVParser -- "Parse Data" --> Cleaner
    Cleaner -- "Normalize Data" --> Validator
    Validator -- "Flag Missing/Dupes" --> Classifier
    Classifier -- "Batch Prompting" --> OpenAI
    OpenAI -- "Predicted Categories" --> Classifier
    Classifier -- "Transactions" --> Anomaly
    Anomaly -- "Flag Anomalies" --> Summarizer
    Summarizer -- "Calculate Spend" --> Pipeline
    
    Pipeline -- "Insert Trans/Errors/Stats" --> Postgres
```

### Data Flow Structure

The data moves through a strict 6-stage asynchronous pipeline.

1.  **Ingestion & Queueing:**
    *   The user uploads `transactions.csv` to the FastAPI `/jobs/upload` endpoint.
    *   FastAPI saves the file to a shared Docker volume (`/tmp/uploads`), generates a UUID, inserts a `PENDING` job into PostgreSQL, and queues `process_csv_task` in Redis.
2.  **Parsing & Cleaning:**
    *   The Celery Worker picks up the task from Redis.
    *   `CSVParserService` loads the CSV, explicitly instructing pandas to avoid converting empty strings to floats (`keep_default_na=False`). It safely manages Python `None` conversions.
    *   `CleaningService` normalizes the dates (to ISO-8601), strings (currency, status, merchant), and decimals (amounts).
3.  **Validation:**
    *   `ValidationService` runs through every row verifying required fields (`txn_id`, `amount`, `date`).
    *   It also checks for duplicates based on `txn_id`.
    *   Any failures are shunted directly to the `row_errors` table and removed from the active data stream.
4.  **LLM Classification:**
    *   `ClassificationService` checks the validated rows for missing or anomalous categories.
    *   These rows are batched into a prompt with strict JSON output instructions and sent to the `gpt-3.5-turbo` API using the provided API key.
    *   The returned JSON arrays are parsed and seamlessly merged back into the `category_final` attribute of each transaction.
5.  **Anomaly Detection:**
    *   `AnomalyDetectionService` scans the classified rows to flag irregularities.
    *   It flags single transactions exceeding 3x the median spend of the specific `account_id`.
    *   It identifies currency mismatches (e.g., domestic merchants like Swiggy, Zomato, or Jio Recharge charging in USD).
6.  **Aggregation & Persistence:**
    *   `SummaryService` calculates accurate final spend totals, purposefully excluding `FAILED` and `PENDING` states so users see actual money spent.
    *   The Worker atomically inserts all successful rows into `transactions`, failures into `row_errors`, and totals into `job_summaries` before marking the PostgreSQL job as `COMPLETED`.
    *   The user can then fetch the output via the API endpoints or direct SQL export.

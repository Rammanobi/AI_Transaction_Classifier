<div align="center">
  
  <img src="https://img.icons8.com/color/96/000000/artificial-intelligence.png" alt="AI Icon"/>
  
  <h1>AI Transaction Classifier</h1>
  <p>
    <b>An asynchronous, highly-scalable, AI-powered financial data pipeline.</b>
  </p>

  <p>
    <a href="#-architecture">Architecture</a> •
    <a href="#-data-flow">Data Flow</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-api-usage">API Usage</a>
  </p>

</div>

<br/>

<div align="center">
  <i>This system robustly ingests, cleans, validates, and classifies raw CSV transaction data using <b>OpenAI's LLMs</b> while strictly guarding against anomalies, duplicates, and missing data.</i>
</div>

---

## 🏗️ Architecture

The system is built on a high-throughput, event-driven microservice architecture designed to handle thousands of transactions without blocking the API thread.

<table>
  <tr>
    <td><b>API Layer</b></td>
    <td><code>FastAPI</code></td>
    <td>Handles high-concurrency incoming HTTP requests instantly.</td>
  </tr>
  <tr>
    <td><b>Message Broker</b></td>
    <td><code>Redis</code></td>
    <td>Intercepts and queues workloads to decouple heavy processing.</td>
  </tr>
  <tr>
    <td><b>Worker Layer</b></td>
    <td><code>Celery</code></td>
    <td>Consumes tasks, manages CSV parsing, validation, and AI network calls.</td>
  </tr>
  <tr>
    <td><b>Database</b></td>
    <td><code>PostgreSQL</code></td>
    <td>Enforces strict relational integrity and persists final audited data.</td>
  </tr>
  <tr>
    <td><b>AI / LLM</b></td>
    <td><code>OpenAI API</code></td>
    <td>Dynamically classifies unknown transactions into standardized categories.</td>
  </tr>
</table>

<h3>Architecture Diagram</h3>

```mermaid
graph TD
    Client[Client / cURL]
    
    subgraph API Container [API Container - FastAPI]
        API_Endpoints[API Endpoints]
        UploadRoute[/jobs/upload]
        StatusRoute[/jobs/{id}/status]
        ResultsRoute[/jobs/{id}/results]
        API_Endpoints --- UploadRoute
        API_Endpoints --- StatusRoute
        API_Endpoints --- ResultsRoute
    end

    Redis[(Redis Message Broker)]

    subgraph Worker Container [Worker Container - Celery]
        TaskQueue[Celery Task Queue]
        Pipeline[process_csv_task]
        
        CSVParser[CSV Parser Service]
        Cleaner[Cleaning Service]
        Validator[Validation Service]
        Classifier[Classification Service]
        Anomaly[Anomaly Detection Service]
        Summarizer[Summary Service]
        
        Pipeline --> CSVParser --> Cleaner --> Validator --> Classifier --> Anomaly --> Summarizer
    end

    Postgres[(PostgreSQL Database)]
    OpenAI[OpenAI LLM API]

    Client -- "Upload CSV" --> UploadRoute
    UploadRoute -- "Create Job, Publish Task" --> Redis
    UploadRoute -- "Save State" --> Postgres
    
    Redis -- "Consume Task" --> TaskQueue
    TaskQueue --> Pipeline
    Classifier -- "Batch Prompting" --> OpenAI
    Pipeline -- "Insert Final Data" --> Postgres
```

---

## 🔄 Data Flow

<details open>
<summary><b>1. Ingestion</b></summary>
<p>
Users upload a CSV via the API. FastAPI instantly saves it to a shared volume, logs a <code>PENDING</code> job to PostgreSQL, and queues an asynchronous task in Redis.
</p>
</details>

<details open>
<summary><b>2. Parsing & Cleaning</b></summary>
<p>
Celery reads the file safely, strictly forbidding Pandas from generating phantom "nan" artifacts. Dates are standardized to ISO-8601, and currency strings are safely cast to numeric decimals.
</p>
</details>

<details open>
<summary><b>3. Strict Validation</b></summary>
<p>
Missing required fields (like <code>txn_id</code>) and exact duplicates are intercepted. Failures are shunted into a dedicated <code>row_errors</code> table to ensure only 100% clean data advances.
</p>
</details>

<details open>
<summary><b>4. LLM Classification</b></summary>
<p>
Valid rows missing categories are batched and routed to OpenAI. A strict JSON-enforced prompt guarantees accurate classification with robust fallback logic in case of network timeouts or LLM hallucinations.
</p>
</details>

<details open>
<summary><b>5. Anomaly Detection</b></summary>
<p>
Transactions are scrutinized mathematically (amounts exceeding 3x the account's median spend) and logically (domestic merchants charging in USD) and flagged accordingly.
</p>
</details>

<details open>
<summary><b>6. Aggregation & Persistence</b></summary>
<p>
The system calculates total user spend strictly excluding <code>FAILED</code> and <code>PENDING</code> transactions. The entire audited state is atomically committed to PostgreSQL.
</p>
</details>

---

## ⚡ Quick Start

### 1. Configure Environment
Create a `.env` file in the project root and inject your OpenAI key:
```env
OPENAI_API_KEY=your_actual_api_key_here
```

### 2. Boot Docker Services
Spin up the entire microservice stack (FastAPI, Celery, Postgres, Redis):
```bash
docker compose up -d --build
```

---

## 🌐 API Usage

<blockquote>
  <b>Upload a File</b>
</blockquote>

```bash
curl -X POST "http://localhost:8000/jobs/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@transactions.csv"
```
*Note the `job_id` returned in the JSON payload.*

<br/>

<blockquote>
  <b>Poll Job Status</b>
</blockquote>

```bash
curl -X GET "http://localhost:8000/jobs/{job_id}/status" \
  -H "accept: application/json"
```

<br/>

<blockquote>
  <b>Fetch Final Extracted Results</b>
</blockquote>

```bash
curl -X GET "http://localhost:8000/jobs/{job_id}/results" \
  -H "accept: application/json"
```

---
<div align="center">
  <i>Engineered for enterprise scale.</i>
</div>

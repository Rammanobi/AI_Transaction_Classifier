# Live Demo Script

Follow these steps to demonstrate the AI Transaction Classifier end-to-end.

## Step 1: Start the System
```bash
# Start Postgres, Redis, FastAPI, and Celery
docker compose up --build -d
```
*(Point out the multi-container architecture running locally)*

## Step 2: Upload a Messy CSV
We have prepared a dirty CSV that includes invalid dates, duplicate rows, missing categories, and anomalies.
```bash
curl -X POST "http://localhost:8000/jobs/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/dirty.csv"
```
*(Copy the returned `job_id` from the JSON response)*

## Step 3: Poll the Status
Show how the system is asynchronous.
```bash
curl -X GET "http://localhost:8000/jobs/<JOB_ID>/status" \
  -H "accept: application/json"
```
*(Show the `processing_stage` moving through: `uploaded` -> `validating` -> `classification` -> `completed`)*

## Step 4: Fetch the Results
Once the status is `completed`, fetch the full payload:
```bash
curl -X GET "http://localhost:8000/jobs/<JOB_ID>/results" \
  -H "accept: application/json" | jq .
```

## Step 5: Explain the Output
Walk the reviewer through the JSON response:
1. **Summary**: Point out the LLM-generated `narrative` and the `risk_level`.
2. **Anomalies**: Show how the deterministic engine caught the 3x median spike.
3. **Row Errors**: Show how the `32-99-2025` date was safely rejected without crashing the job.
4. **Transactions**: Show how the missing categories were filled in by the LLM (e.g. `Swiggy` -> `Food`).

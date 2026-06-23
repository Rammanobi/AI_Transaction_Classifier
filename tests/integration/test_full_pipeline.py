import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.job import ProcessingStage
from app.services.llm.openai_client import OpenAIClient

client = TestClient(app)

@pytest.fixture
def mock_csv(tmp_path):
    csv_content = """txn_id,date,merchant,amount,currency,status,account_id,notes
1,2025-06-01,Swiggy,15.50,USD,SUCCESS,A1,Test note
"""
    file_path = tmp_path / "test.csv"
    file_path.write_text(csv_content)
    return str(file_path)

@patch("app.workers.tasks.process.process_csv_task.delay")
@patch.object(OpenAIClient, "classify_batch")
@patch.object(OpenAIClient, "generate_summary")
def test_full_pipeline(mock_generate_summary, mock_classify_batch, mock_delay, mock_csv):
    # Setup mocks
    mock_classify_batch.return_value = [{"txn_id": "1", "category": "Food"}]
    mock_generate_summary.return_value = {"narrative": "Test summary", "risk_level": "low"}
    
    # 1. Upload CSV
    with open(mock_csv, "rb") as f:
        response = client.post("/jobs/upload", files={"file": ("test.csv", f, "text/csv")})
        
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    job_id = data["job_id"]
    
    assert mock_delay.called
    
    # In a real integration test against a live db, we would wait for the worker.
    # For this test, we are just verifying the API layer triggers the pipeline.
    # To test the worker, we would call `await _process_csv_async` directly,
    # but that requires a live database connection which we might not have in CI.
    
    # Verify Status endpoint
    status_response = client.get(f"/jobs/{job_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["job_id"] == job_id

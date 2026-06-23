from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class JobCreateResponse(BaseModel):
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    processing_stage: str
    row_count_raw: int
    row_count_valid: int
    row_count_invalid: int
    summary: Optional[Dict[str, Any]] = None

class JobResultsResponse(BaseModel):
    job: Dict[str, Any]
    summary: Optional[Dict[str, Any]]
    transactions: List[Dict[str, Any]]
    row_errors: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    category_breakdown: Dict[str, int]

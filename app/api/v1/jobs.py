import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.job import JobCreateResponse, JobStatusResponse, JobResultsResponse
from app.core.database import get_db
from app.services.storage.local_storage import LocalStorageService
from app.repositories.jobs import job_repo
from app.repositories.transactions import transaction_repo
from app.repositories.row_errors import row_error_repo
from app.repositories.job_summaries import job_summary_repo
from app.workers.tasks.process import process_csv_task
from app.models.job import ProcessingStage

router = APIRouter()
storage_service = LocalStorageService()

@router.post(
    "/upload", 
    response_model=JobCreateResponse,
    summary="Upload CSV for processing",
    description="Accepts a CSV file of financial transactions, creates an async processing job, and immediately returns a job ID for polling."
)
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Validation logic - checking size is optional but good, let's keep it simple
    job_id = str(uuid.uuid4())
    
    # Read and store file
    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
        
    file_path = storage_service.save_file(file_content, file.filename, job_id)
    
    # Create Job in DB
    job = await job_repo.create(db, obj_in={
        "id": job_id,
        "filename": file.filename,
        "file_path": file_path,
        "status": "pending",
        "processing_stage": ProcessingStage.uploaded
    })
    await db.commit()
    
    # Enqueue task
    process_csv_task.delay(job_id, file_path)
    
    return JobCreateResponse(job_id=job_id, status="pending")


@router.get(
    "/{job_id}/status", 
    response_model=JobStatusResponse,
    summary="Poll job status",
    description="Returns the current lifecycle stage of the job. Stages include uploaded, parsing, validating, cleaning, anomaly_detection, persisting, classification, summary_generation, and completed."
)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await job_repo.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    summary = await job_summary_repo.get_by_job_id(db, job_id)
    summary_dict = None
    if summary:
        summary_dict = {
            "total_spend_inr": float(summary.total_spend_inr) if summary.total_spend_inr is not None else 0,
            "total_spend_usd": float(summary.total_spend_usd) if summary.total_spend_usd is not None else 0,
            "top_merchants": summary.top_merchants,
            "anomaly_count": summary.anomaly_count,
            "narrative": summary.narrative,
            "risk_level": summary.risk_level
        }
        
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        processing_stage=job.processing_stage,
        row_count_raw=job.row_count_raw,
        row_count_valid=job.row_count_valid,
        row_count_invalid=job.row_count_invalid,
        summary=summary_dict
    )


@router.get(
    "/{job_id}/results",
    summary="Get job results",
    description="Returns the full payload once a job is complete. Includes valid transactions, parsed row errors, anomaly flags, and the LLM-generated narrative summary."
)
async def get_job_results(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await job_repo.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    transactions = await transaction_repo.get_by_job_id(db, job_id)
    row_errors = await row_error_repo.get_by_job_id(db, job_id)
    
    # Format transactions and extract anomalies
    tx_list = []
    anomalies_list = []
    anomaly_count = 0
    
    for tx in transactions:
        tx_dict = {
            "id": tx.id,
            "row_number": tx.row_number,
            "txn_id": tx.txn_id,
            "date": tx.date_clean,
            "merchant": tx.merchant_clean,
            "amount": float(tx.amount_clean) if tx.amount_clean is not None else None,
            "currency": tx.currency_clean,
            "status": tx.status_clean,
            "category": tx.category_final,
            "account_id": tx.account_id,
            "is_anomaly": tx.is_anomaly,
            "anomaly_reason": tx.anomaly_reason
        }
        tx_list.append(tx_dict)
        if tx.is_anomaly:
            anomalies_list.append(tx_dict)
            anomaly_count += 1
            
    re_list = []
    for re in row_errors:
        re_list.append({
            "row_number": re.row_number,
            "raw_row_data": re.raw_row_data,
            "error_stage": re.error_stage,
            "error_type": re.error_type,
            "error_message": re.error_message
        })

    summary = await job_summary_repo.get_by_job_id(db, job_id)
    summary_dict = None
    if summary:
        summary_dict = {
            "total_spend_inr": float(summary.total_spend_inr) if summary.total_spend_inr is not None else 0,
            "total_spend_usd": float(summary.total_spend_usd) if summary.total_spend_usd is not None else 0,
            "top_merchants": summary.top_merchants,
            "anomaly_count": summary.anomaly_count,
            "narrative": summary.narrative,
            "risk_level": summary.risk_level
        }

    category_breakdown = {}
    for tx in tx_list:
        cat = tx["category"] or "Other"
        category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

    return {
        "job": {
            "id": job.id, 
            "status": job.status,
            "processing_stage": job.processing_stage,
            "error_message": job.error_message
        },
        "summary": summary_dict,
        "transactions": tx_list,
        "row_errors": re_list,
        "anomalies": anomalies_list,
        "anomaly_count": anomaly_count,
        "category_breakdown": category_breakdown
    }


@router.get("/")
async def list_jobs(status: str = None, db: AsyncSession = Depends(get_db)):
    jobs = await job_repo.list_jobs(db, status)
    return [{
        "id": j.id,
        "filename": j.filename,
        "status": j.status,
        "created_at": j.created_at,
        "row_count_valid": j.row_count_valid
    } for j in jobs]

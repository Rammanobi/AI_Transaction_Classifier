import asyncio
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.repositories.jobs import job_repo
from app.repositories.transactions import transaction_repo
from app.repositories.row_errors import row_error_repo
from app.services.csv_parser_service import CSVParserService
from app.services.validation_service import ValidationService
from app.services.cleaning_service import CleaningService
from app.services.deduplication_service import DeduplicationService
from app.services.anomaly_detection_service import AnomalyDetectionService
from app.services.llm.classification_service import ClassificationService
from app.services.llm.summary_service import SummaryService
from app.models.job import ProcessingStage

async def _process_csv_async(job_id: str, file_path: str):
    async with AsyncSessionLocal() as db:
        job = await job_repo.get_by_id(db, job_id)
        if not job:
            return

        async def update_stage(stage: ProcessingStage):
            await job_repo.update(db, db_obj=job, obj_in={"processing_stage": stage})

        try:
            # 1. Parsing
            await update_stage(ProcessingStage.parsing)
            rows, error = CSVParserService.parse(file_path)
            
            if error or not rows:
                await job_repo.update(db, db_obj=job, obj_in={
                    "status": "failed",
                    "error_message": error or "Empty file",
                    "processing_stage": ProcessingStage.failed
                })
                await db.commit()
                return

            row_errors_data = []
            valid_cleaned_rows = []

            # 2. Validating and Cleaning
            await update_stage(ProcessingStage.validating)
            for row in rows:
                is_valid, err_type, err_msg = ValidationService.validate_row(row)
                if not is_valid:
                    row_errors_data.append({
                        "job_id": job_id,
                        "row_number": row.get("row_number"),
                        "raw_row_data": str(row),
                        "error_stage": "validation",
                        "error_type": err_type,
                        "error_message": err_msg
                    })
                else:
                    # Clean valid rows
                    cleaned_row = CleaningService.clean_row(row)
                    
                    # Post-cleaning validation (e.g. invalid dates or amounts)
                    if cleaned_row.get("date_clean") is None:
                        row_errors_data.append({
                            "job_id": job_id,
                            "row_number": row.get("row_number"),
                            "raw_row_data": str(row),
                            "error_stage": "cleaning",
                            "error_type": "invalid_date",
                            "error_message": f"Could not parse date: {cleaned_row.get('date_raw')}"
                        })
                    elif cleaned_row.get("amount_clean") is None:
                        row_errors_data.append({
                            "job_id": job_id,
                            "row_number": row.get("row_number"),
                            "raw_row_data": str(row),
                            "error_stage": "cleaning",
                            "error_type": "invalid_amount",
                            "error_message": f"Could not parse amount: {cleaned_row.get('amount_raw')}"
                        })
                    else:
                        valid_cleaned_rows.append(cleaned_row)

            # 3. Deduplication (after cleaning as requested)
            await update_stage(ProcessingStage.cleaning) # Use cleaning stage for dedupe
            seen_hashes = set()
            unique_valid_rows = []
            
            for row in valid_cleaned_rows:
                row_hash = DeduplicationService.generate_hash(row)
                if row_hash in seen_hashes:
                    row_errors_data.append({
                        "job_id": job_id,
                        "row_number": row.get("row_number"),
                        "raw_row_data": str(row),
                        "error_stage": "deduplication",
                        "error_type": "duplicate_row",
                        "error_message": "Exact duplicate row found"
                    })
                else:
                    seen_hashes.add(row_hash)
                    unique_valid_rows.append(row)

            # 4. Anomaly Detection
            await update_stage(ProcessingStage.anomaly_detection)
            final_transactions = AnomalyDetectionService.detect_anomalies(unique_valid_rows)

            # 5. Persisting
            await update_stage(ProcessingStage.persisting)
            
            row_count_raw = len(rows)
            row_count_valid = len(final_transactions)
            row_count_invalid = len(row_errors_data)

            # Check all-invalid-file behavior
            if row_count_raw > 0 and row_count_valid == 0:
                # All rows failed
                await job_repo.update(db, db_obj=job, obj_in={
                    "status": "failed",
                    "error_message": "All rows were invalid or duplicates",
                    "processing_stage": ProcessingStage.failed,
                    "row_count_raw": row_count_raw,
                    "row_count_valid": 0,
                    "row_count_invalid": row_count_invalid
                })
                # Still persist the errors so user knows why
                await row_error_repo.bulk_create(db, row_errors_data)
                await db.commit()
                return

            # Save valid transactions — strip raw CSV keys that are not Transaction model columns
            CSV_RAW_KEYS = {"date", "amount", "merchant", "currency", "status", "category", "notes"}
            for tx in final_transactions:
                tx["job_id"] = job_id
                for key in CSV_RAW_KEYS:
                    tx.pop(key, None)
            await transaction_repo.bulk_create(db, final_transactions)
            
            # Save row errors
            await row_error_repo.bulk_create(db, row_errors_data)

            # Update row counts on job before LLM (so summary has access to it on job object)
            job = await job_repo.update(db, db_obj=job, obj_in={
                "row_count_raw": row_count_raw,
                "row_count_valid": row_count_valid,
                "row_count_invalid": row_count_invalid
            })

            # 6. Classification (LLM)
            await update_stage(ProcessingStage.classification)
            classification_service = ClassificationService(db)
            await classification_service.run_classification(job_id)

            # 7. Summary Generation (LLM)
            await update_stage(ProcessingStage.summary_generation)
            summary_service = SummaryService(db)
            await summary_service.generate_and_save_summary(job)

            # 8. Completed
            await job_repo.update(db, db_obj=job, obj_in={
                "status": "completed",
                "processing_stage": ProcessingStage.completed
            })
            await db.commit()

        except Exception as e:
            # Catch all crash protector
            await job_repo.update(db, db_obj=job, obj_in={
                "status": "failed",
                "error_message": f"Worker crashed: {str(e)}",
                "processing_stage": ProcessingStage.failed
            })
            await db.commit()


@celery_app.task(name="process_csv_task")
def process_csv_task(job_id: str, file_path: str):
    asyncio.run(_process_csv_async(job_id, file_path))
    return {"status": "success", "job_id": job_id}

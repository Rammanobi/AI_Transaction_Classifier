import json
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import Job
from app.repositories.transactions import transaction_repo
from app.repositories.job_summaries import job_summary_repo
from app.services.llm.openai_client import OpenAIClient

class SummaryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_client = OpenAIClient()

    async def generate_and_save_summary(self, job: Job):
        transactions = await transaction_repo.get_by_job_id(self.db, job.id)
        anomaly_count = await transaction_repo.get_anomaly_count(self.db, job.id)
        
        # Calculate aggregates
        total_spend_inr = Decimal(0)
        total_spend_usd = Decimal(0)
        merchant_counts = {}
        
        for tx in transactions:
            if tx.status_clean != "SUCCESS":
                continue
                
            amt = tx.amount_clean or Decimal(0)
            if tx.currency_clean == "INR":
                total_spend_inr += amt
            elif tx.currency_clean == "USD":
                total_spend_usd += amt
                
            if tx.merchant_clean:
                merchant_counts[tx.merchant_clean] = merchant_counts.get(tx.merchant_clean, 0) + 1
                
        # Top 3 merchants
        sorted_merchants = sorted(merchant_counts.items(), key=lambda x: x[1], reverse=True)
        top_merchants = dict(sorted_merchants[:3])
        
        # Data for LLM
        summary_data = {
            "total_transactions": len(transactions),
            "total_spend_inr": float(total_spend_inr),
            "total_spend_usd": float(total_spend_usd),
            "top_merchants": top_merchants,
            "anomaly_count": anomaly_count,
            "row_count_raw": job.row_count_raw,
            "row_count_valid": job.row_count_valid,
            "row_count_invalid": job.row_count_invalid
        }
        
        try:
            llm_result = await self.llm_client.generate_summary(summary_data)
            narrative = llm_result.get("narrative", "Summary generation generated incomplete output.")
            risk_level = llm_result.get("risk_level", "medium")
            if risk_level not in ["low", "medium", "high"]:
                risk_level = "medium"
        except Exception as e:
            narrative = f"Summary generation unavailable due to LLM failure: {str(e)}"
            risk_level = "medium"
            
        # Create JobSummary
        await job_summary_repo.create(self.db, obj_in={
            "job_id": job.id,
            "total_spend_inr": total_spend_inr,
            "total_spend_usd": total_spend_usd,
            "top_merchants": top_merchants,
            "anomaly_count": anomaly_count,
            "narrative": narrative,
            "risk_level": risk_level
        })

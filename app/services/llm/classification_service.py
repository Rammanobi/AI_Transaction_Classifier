import json
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.transaction import Transaction
from app.repositories.transactions import transaction_repo
from app.services.llm.openai_client import OpenAIClient
from app.services.llm.prompt_builder import PromptBuilder

class ClassificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # If we had multiple providers, we'd select based on settings.LLM_PROVIDER
        self.llm_client = OpenAIClient()

    async def run_classification(self, job_id: str):
        """
        Fetches all transactions for the job where category_final IS NULL,
        chunks them, sends them to the LLM, and updates the database.
        """
        missing_category_txns = await transaction_repo.get_transactions_missing_category(self.db, job_id)
        if not missing_category_txns:
            return

        batch_size = settings.CLASSIFICATION_BATCH_SIZE
        
        for i in range(0, len(missing_category_txns), batch_size):
            batch = missing_category_txns[i:i+batch_size]
            
            # Prepare data for LLM
            batch_data = [
                {
                    "txn_id": tx.txn_id,
                    "merchant_clean": tx.merchant_clean,
                    "amount_clean": tx.amount_clean,
                    "currency_clean": tx.currency_clean
                }
                for tx in batch
            ]
            
            try:
                # This call handles its own retries
                results = await self.llm_client.classify_batch(batch_data)
                
                # Map results back
                result_map = {res.get("txn_id"): res.get("category") for res in results if isinstance(res, dict)}
                
                for tx in batch:
                    cat = result_map.get(tx.txn_id)
                    if cat in PromptBuilder.VALID_CATEGORIES:
                        tx.category_final = cat
                        tx.llm_category = cat
                    else:
                        tx.category_final = "Other" # Fallback
                        tx.llm_category = cat if cat else "Other"
                        
                    tx.llm_raw_response = json.dumps({"category": cat})
                    tx.llm_failed = False
                    
            except Exception as e:
                # If all retries fail, fallback to 'Other' and mark llm_failed
                for tx in batch:
                    tx.category_final = "Other"
                    tx.llm_failed = True
                    tx.llm_raw_response = str(e)
                    
            # Update the batch in DB
            self.db.add_all(batch)
            await self.db.flush()

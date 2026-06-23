from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository
from typing import List, Dict, Any

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)
    
    async def bulk_create(self, db: AsyncSession, records: List[Dict[str, Any]]):
        if not records:
            return
        objects = [self.model(**record) for record in records]
        db.add_all(objects)
        await db.flush()
        
    async def get_by_job_id(self, db: AsyncSession, job_id: str) -> List[Transaction]:
        query = select(self.model).filter(self.model.job_id == job_id).order_by(self.model.row_number)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_transactions_missing_category(self, db: AsyncSession, job_id: str) -> List[Transaction]:
        query = select(self.model).filter(
            self.model.job_id == job_id,
            self.model.category_final.is_(None)
        ).order_by(self.model.row_number)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_anomaly_count(self, db: AsyncSession, job_id: str) -> int:
        query = select(func.count(self.model.id)).filter(
            self.model.job_id == job_id,
            self.model.is_anomaly == True
        )
        result = await db.execute(query)
        return result.scalar() or 0

transaction_repo = TransactionRepository()

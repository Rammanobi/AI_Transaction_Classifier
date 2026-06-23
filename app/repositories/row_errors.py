from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.row_error import RowError
from app.repositories.base import BaseRepository
from typing import List, Dict, Any

class RowErrorRepository(BaseRepository[RowError]):
    def __init__(self):
        super().__init__(RowError)
    
    async def bulk_create(self, db: AsyncSession, records: List[Dict[str, Any]]):
        if not records:
            return
        objects = [self.model(**record) for record in records]
        db.add_all(objects)
        await db.flush()

    async def get_by_job_id(self, db: AsyncSession, job_id: str) -> List[RowError]:
        query = select(self.model).filter(self.model.job_id == job_id).order_by(self.model.row_number)
        result = await db.execute(query)
        return list(result.scalars().all())

row_error_repo = RowErrorRepository()

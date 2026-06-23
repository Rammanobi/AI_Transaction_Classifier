from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.job import Job
from app.repositories.base import BaseRepository
from typing import List, Optional

class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__(Job)
    
    async def get_by_id(self, db: AsyncSession, job_id: str) -> Optional[Job]:
        return await self.get(db, job_id)
        
    async def list_jobs(self, db: AsyncSession, status: Optional[str] = None) -> List[Job]:
        query = select(self.model)
        if status:
            query = query.filter(self.model.status == status)
        query = query.order_by(self.model.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

job_repo = JobRepository()

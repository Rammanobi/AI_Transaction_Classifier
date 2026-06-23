from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job_summary import JobSummary
from app.repositories.base import BaseRepository
from typing import Optional

class JobSummaryRepository(BaseRepository[JobSummary]):
    def __init__(self):
        super().__init__(JobSummary)
    
    async def get_by_job_id(self, db: AsyncSession, job_id: str) -> Optional[JobSummary]:
        query = select(self.model).filter(self.model.job_id == job_id)
        result = await db.execute(query)
        return result.scalars().first()

job_summary_repo = JobSummaryRepository()

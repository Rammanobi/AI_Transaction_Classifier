from sqlalchemy import Column, Integer, String, DateTime, func, Text
from app.models.base import Base

class RowError(Base):
    __tablename__ = "row_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    
    raw_row_data = Column(Text, nullable=True)
    error_stage = Column(String, nullable=False)
    error_type = Column(String, nullable=False)
    error_message = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

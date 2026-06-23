from sqlalchemy import Column, Integer, String, DateTime, func, Text, Enum
import enum
from app.models.base import Base

class ProcessingStage(str, enum.Enum):
    uploaded = "uploaded"
    parsing = "parsing"
    validating = "validating"
    cleaning = "cleaning"
    anomaly_detection = "anomaly_detection"
    classification = "classification"
    summary_generation = "summary_generation"
    persisting = "persisting"
    completed = "completed"
    failed = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=True)
    status = Column(String, nullable=False, index=True, default="pending")
    file_path = Column(String, nullable=True)
    
    row_count_raw = Column(Integer, default=0)
    row_count_valid = Column(Integer, default=0)
    row_count_invalid = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    error_message = Column(Text, nullable=True)
    processing_stage = Column(Enum(ProcessingStage), nullable=False, default=ProcessingStage.uploaded)

from sqlalchemy import Column, Integer, String, DateTime, func, Numeric, Text, JSON
from app.models.base import Base

class JobSummary(Base):
    __tablename__ = "job_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    
    total_spend_inr = Column(Numeric, nullable=True)
    total_spend_usd = Column(Numeric, nullable=True)
    
    top_merchants = Column(JSON, nullable=True)
    
    anomaly_count = Column(Integer, default=0)
    
    narrative = Column(Text, nullable=True)
    risk_level = Column(String, nullable=True)
    prompt_version = Column(String, nullable=True, default="v1")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

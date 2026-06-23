from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Numeric, Text
from app.models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    
    txn_id = Column(String, nullable=True)
    
    date_raw = Column(String, nullable=True)
    date_clean = Column(String, nullable=True)
    
    merchant_raw = Column(String, nullable=True)
    merchant_clean = Column(String, nullable=True)
    
    amount_raw = Column(String, nullable=True)
    amount_clean = Column(Numeric, nullable=True)
    
    currency_raw = Column(String, nullable=True)
    currency_clean = Column(String, nullable=True)
    
    status_raw = Column(String, nullable=True)
    status_clean = Column(String, nullable=True)
    
    category_raw = Column(String, nullable=True)
    category_final = Column(String, nullable=True)
    
    account_id = Column(String, nullable=True, index=True)
    notes_raw = Column(Text, nullable=True)
    
    is_anomaly = Column(Boolean, default=False, index=True)
    anomaly_reason = Column(String, nullable=True)
    
    llm_category = Column(String, nullable=True)
    llm_raw_response = Column(Text, nullable=True)
    llm_failed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

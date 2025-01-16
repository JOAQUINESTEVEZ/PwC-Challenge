from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db import Base

class FinancialTransaction(Base):
    __tablename__ = 'financial_transactions'
    
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    client_id = Column(UUID, ForeignKey('clients.id'))
    created_by = Column(UUID, ForeignKey('users.id'))
    transaction_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    description = Column(String)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship('Client')
    created_by_user = relationship('User')
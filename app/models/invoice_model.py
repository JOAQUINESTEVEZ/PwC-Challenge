from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db import Base

class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    client_id = Column(UUID, ForeignKey('clients.id'))
    created_by = Column(UUID, ForeignKey('users.id'))
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    amount_due = Column(DECIMAL(15, 2), nullable=False)
    amount_paid = Column(DECIMAL(15, 2), default=0.00)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = relationship('Client')
    created_by_user = relationship('User')
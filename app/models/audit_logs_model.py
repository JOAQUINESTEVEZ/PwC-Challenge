from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    changed_by = Column(UUID, ForeignKey('users.id'))
    table_name = Column(String(50), nullable=False)
    record_id = Column(UUID, nullable=False)
    change_type = Column(String(20), nullable=False)
    change_details = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    changed_by_user = relationship('User')
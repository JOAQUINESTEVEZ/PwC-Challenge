from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..db import Base

class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    role_id = Column(UUID, ForeignKey('roles.id'))
    resource = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role = relationship('Role', back_populates='permissions')
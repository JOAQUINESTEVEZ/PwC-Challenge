from sqlalchemy import Column, String, UUID
import uuid
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship('User', back_populates='role')
    permissions = relationship('Permission', back_populates='role')
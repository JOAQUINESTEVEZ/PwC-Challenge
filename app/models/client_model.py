from sqlalchemy import Column, String, UUID, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base
import uuid

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    industry = Column(String(50))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    address = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship('User', back_populates='client', cascade="all, delete-orphan")

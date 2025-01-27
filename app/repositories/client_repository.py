from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from ..models.client_model import Client as ClientModel
from ..entities.client import Client

class ClientRepository:
    """
    Repository for Client-specific database operations.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def _to_model(self, entity: Client) -> ClientModel:
        """Convert entity to model."""
        return ClientModel(
            id=entity.id,
            name=entity.name,
            industry=entity.industry,
            contact_email=entity.contact_email,
            contact_phone=entity.contact_phone,
            address=entity.address,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def _to_entity(self, model: ClientModel) -> Client:
        """Convert model to entity."""
        return Client(
            id=model.id,
            name=model.name,
            industry=model.industry,
            contact_email=model.contact_email,
            contact_phone=model.contact_phone,
            address=model.address,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    async def create(self, entity: Client) -> Client:
        """Create a new client in the database."""
        try:
            model = self._to_model(entity)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Failed to create client: {str(e)}")
    
    async def get_by_id(self, client_id: UUID) -> Optional[Client]:
        """Get a client by its ID from the database."""
        model = self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
        return self._to_entity(model) if model else None
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Client]:
        """Get all clients with pagination"""
        models = self.db.query(ClientModel).offset(skip).limit(limit).all()
        return [self._to_entity(model) for model in models]
    
    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """
        Get a client by name.
        
        Args:
            name: Name to search for
            
        Returns:
            Optional[Client]: Found client or None
        """
        model = self.db.query(ClientModel).filter(ClientModel.name == name).first()
        return self._to_entity(model) if model else None
    
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """
        Get a client by email.
        
        Args:
            email: Email to search for
            
        Returns:
            Optional[Client]: Found client or None
        """
        model = self.db.query(ClientModel).filter(ClientModel.contact_email == email).first()
        return self._to_entity(model) if model else None
    
    async def get_clients_by_industry(self, industry: str) -> List[Client]:
        """
        Get all clients in a specific industry.
        
        Args:
            industry: Industry to filter by
            
        Returns:
            List[Client]: List of clients in the industry
        """
        models = self.db.query(ClientModel).filter(ClientModel.industry == industry).all()
        return [self._to_entity(model) for model in models]

    async def search_clients(self, search_term: str) -> List[Client]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List[Client]: List of matching clients
        """
        models = self.db.query(ClientModel)\
            .filter(
                (ClientModel.name.ilike(f"%{search_term}%")) |
                (ClientModel.industry.ilike(f"%{search_term}%"))
            ).all()
        return [self._to_entity(model) for model in models]
    
    async def update(self, entity: Client) -> Client:
        """Update an existing client"""
        try:
            model = self._to_model(entity)
            self.db.merge(model)
            self.db.commit()

            updated_model = self.db.query(ClientModel).filter(ClientModel.id == entity.id).first()
            return self._to_entity(updated_model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error updating invoice: {str(e)}")
    
    async def delete(self, client_id: UUID) -> None:
        """Delete a client by ID"""
        try:
            model = self.db.query(ClientModel).filter(ClientModel.id == client_id).first()
            if model:
                self.db.delete(model)
                self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error deleting client: {str(e)}")

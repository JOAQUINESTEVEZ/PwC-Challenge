from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.client_model import Client
from ..schemas.client_schema import ClientCreate, ClientUpdate
from .base_repository import BaseRepository

class ClientRepository(BaseRepository[Client, ClientCreate, ClientUpdate]):
    """
    Repository for Client-specific database operations.
    """
    
    def get_client_by_name(self, name: str) -> Optional[Client]:
        """
        Get a client by name.
        
        Args:
            name: Name to search for
            
        Returns:
            Optional[Client]: Found client or None
        """
        return self.db.query(self.model).filter(self.model.name == name).first()
    
    def get_client_by_email(self, email: str) -> Optional[Client]:
        """
        Get a client by email.
        
        Args:
            email: Email to search for
            
        Returns:
            Optional[Client]: Found client or None
        """
        return self.db.query(self.model).filter(self.model.contact_email == email).first()
    
    def get_clients_by_industry(self, industry: str) -> List[Client]:
        """
        Get all clients in a specific industry.
        
        Args:
            industry: Industry to filter by
            
        Returns:
            List[Client]: List of clients in the industry
        """
        return self.db.query(self.model).filter(self.model.industry == industry).all()

    def search_clients(self, search_term: str) -> List[Client]:
        """
        Search clients by name or industry.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List[Client]: List of matching clients
        """
        return self.db.query(self.model)\
            .filter(
                (self.model.name.ilike(f"%{search_term}%")) |
                (self.model.industry.ilike(f"%{search_term}%"))
            ).all()
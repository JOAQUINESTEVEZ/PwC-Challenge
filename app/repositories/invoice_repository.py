from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
from ..models.invoice_model import Invoice
from ..schemas.invoice_schema import InvoiceCreate, InvoiceUpdate
from .base_repository import BaseRepository

class InvoiceRepository(BaseRepository[Invoice, InvoiceCreate, InvoiceUpdate]):
    """Repository for Invoice specific database operations."""
    
    def get_by_client_id(self, client_id: UUID, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get all invoices for a specific client."""
        return self.db.query(self.model)\
            .filter(self.model.client_id == client_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def search_invoices(self, 
                     client_id: Optional[UUID] = None,
                     status: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None,
                     min_amount: Optional[float] = None,
                     max_amount: Optional[float] = None,
                     is_overdue: Optional[bool] = None) -> List[Invoice]:
        """Search invoices with various filters."""
        query = self.db.query(self.model)
        
        if client_id:
            query = query.filter(self.model.client_id == client_id)
            
        if status:
            query = query.filter(self.model.status == status)
            
        if start_date:
            query = query.filter(self.model.invoice_date >= start_date)
            
        if end_date:
            query = query.filter(self.model.invoice_date <= end_date)
            
        if min_amount is not None:
            query = query.filter(self.model.amount_due >= min_amount)
            
        if max_amount is not None:
            query = query.filter(self.model.amount_due <= max_amount)
            
        if is_overdue is not None:
            current_date = date.today()
            if is_overdue:
                query = query.filter(
                    self.model.due_date < current_date,
                    self.model.status != "PAID"
                )
            else:
                query = query.filter(
                    or_(
                        self.model.due_date >= current_date,
                        self.model.status == "PAID"
                    )
                )
            
        return query.all()

    def get_unpaid_invoices(self, client_id: Optional[UUID] = None) -> List[Invoice]:
        """Get all unpaid invoices, optionally filtered by client."""
        query = self.db.query(self.model)\
            .filter(self.model.status != "PAID")
            
        if client_id:
            query = query.filter(self.model.client_id == client_id)
            
        return query.all()

    def get_overdue_invoices(self) -> List[Invoice]:
        """Get all overdue invoices."""
        current_date = date.today()
        return self.db.query(self.model)\
            .filter(
                self.model.due_date < current_date,
                self.model.status != "PAID"
            )\
            .all()
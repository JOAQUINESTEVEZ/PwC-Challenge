from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from decimal import Decimal

from ..interfaces.repositories.invoice_repository import IInvoiceRepository
from ..models.invoice_model import Invoice as InvoiceModel
from ..entities.invoice import Invoice, InvoiceStatus
from ..interfaces.repositories.cache_repository import ICacheRepository

class InvoiceRepository(IInvoiceRepository):
    """Repository for Invoice specific database operations."""
    
    def __init__(self, db: Session, cache: ICacheRepository):
        """Initialize repository with database session."""
        self.db = db
        self.cache = cache

    def _to_model(self, entity: Invoice) -> InvoiceModel:
        """Convert domain entity to database model."""
        return InvoiceModel(
            id=entity.id,
            client_id=entity.client_id,
            created_by=entity.created_by,
            invoice_date=entity.invoice_date,
            due_date=entity.due_date,
            amount_due=entity.amount_due,
            amount_paid=entity.amount_paid,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def _to_entity(self, model: InvoiceModel) -> Invoice:
        """Convert database model to domain entity."""
        return Invoice(
            id=model.id,
            client_id=model.client_id,
            created_by=model.created_by,
            invoice_date=model.invoice_date,
            due_date=model.due_date,
            amount_due=model.amount_due,
            amount_paid=model.amount_paid,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def create(self, entity: Invoice) -> Invoice:
        """Create a new invoice."""
        try:
            model = self._to_model(entity)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error creating invoice: {str(e)}")

    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get an invoice by ID."""
        model = self.db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
        return self._to_entity(model) if model else None

    async def update(self, entity: Invoice) -> Invoice:
        """Update an existing invoice."""
        try:
            model = self._to_model(entity)
            self.db.merge(model)
            self.db.commit()
            
            # Refresh and return updated entity
            updated_model = self.db.query(InvoiceModel).filter(InvoiceModel.id == entity.id).first()
            return self._to_entity(updated_model)
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error updating invoice: {str(e)}")

    async def delete(self, invoice_id: UUID) -> None:
        """Delete an invoice."""
        try:
            model = self.db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
            if model:
                self.db.delete(model)
                self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Error deleting invoice: {str(e)}")

    async def search(
        self,
        client_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        is_overdue: Optional[bool] = None
    ) -> List[Invoice]:
        """Search invoices with filters."""
        query = self.db.query(InvoiceModel)
        
        if client_id:
            query = query.filter(InvoiceModel.client_id == client_id)
        if status:
            query = query.filter(InvoiceModel.status == status)
        if start_date:
            query = query.filter(InvoiceModel.invoice_date >= start_date)
        if end_date:
            query = query.filter(InvoiceModel.invoice_date <= end_date)
        if min_amount is not None:
            query = query.filter(InvoiceModel.amount_due >= min_amount)
        if max_amount is not None:
            query = query.filter(InvoiceModel.amount_due <= max_amount)
        if is_overdue:
            current_date = date.today()
            query = query.filter(and_(
                InvoiceModel.due_date < current_date,
                InvoiceModel.status != InvoiceStatus.PAID
            ))

        models = query.all()
        return [self._to_entity(model) for model in models]

    async def get_overdue(self, client_id: Optional[UUID] = None) -> List[Invoice]:
        """Get overdue invoices with caching."""
        cache_key = f"overdue:{client_id if client_id else 'all'}"
        
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            print(f"Key: {cache_key}")
            print(f"Data: {cached_data}")
            return [Invoice.from_dict(item) for item in cached_data]

        # Get from database
        query = self.db.query(InvoiceModel).filter(and_(
            InvoiceModel.due_date < date.today(),
            InvoiceModel.status != InvoiceStatus.PAID
        ))

        if client_id:
            query = query.filter(InvoiceModel.client_id == client_id)

        models = query.all()
        invoices = [self._to_entity(model) for model in models]
        
        # Cache for 5 minutes since overdue status can change
        await self.cache.set(
            cache_key, 
            [invoice.to_dict() for invoice in invoices], 
            ttl=300
        )
        
        return invoices
    
    async def get_by_client_id(self, client_id: UUID) -> List[Invoice]:
        """Get all invoices for a specific client."""
        models = self.db.query(InvoiceModel).filter(InvoiceModel.client_id == client_id).all()
        return [self._to_entity(model) for model in models]
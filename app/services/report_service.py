from sqlalchemy.orm import Session
from uuid import UUID
from ..entities.client import Client
from ..entities.financial_transaction import FinancialTransaction
from ..entities.invoice import Invoice
from ..repositories.client_repository import ClientRepository
from ..repositories.financial_transaction_repository import FinancialTransactionRepository
from ..repositories.invoice_repository import InvoiceRepository
from ..utils.pdf_generator import generate_financial_report
from io import BytesIO

class ReportService:
    """
    Service for generating various types of reports.
    Handles report generation business logic and data gathering.
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with database session and repositories.
        
        Args:
            db: Database session
        """
        self.client_repository = ClientRepository(db)
        self.transaction_repository = FinancialTransactionRepository(db)
        self.invoice_repository = InvoiceRepository(db)

    async def _get_client_data(self, client_id: UUID) -> Client:
        """
        Get client data with validation.
        
        Args:
            client_id: UUID of client
            
        Returns:
            Client: Client record
            
        Raises:
            ValueError: If client not found
        """
        client = await self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with id '{client_id}' not found")
        return client

    async def _get_client_transactions(self, client_id: UUID) -> list[FinancialTransaction]:
        """
        Get client transactions ordered by date.
        
        Args:
            client_id: UUID of client
            
        Returns:
            list[FinancialTransaction]: List of ordered transactions
        """
        return await self.transaction_repository.get_by_client_id(
            client_id=client_id
        )

    async def _get_client_invoices(self, client_id: UUID) -> list[Invoice]:
        """
        Get client invoices ordered by date.
        
        Args:
            client_id: UUID of client
            
        Returns:
            list[Invoice]: List of ordered invoices
        """
        return await self.invoice_repository.get_by_client_id(
            client_id=client_id
        )

    async def generate_client_financial_report(self, client_id: UUID) -> BytesIO:
        """
        Generate a complete financial report for a client.
        
        Args:
            client_id: UUID of client
            
        Returns:
            BytesIO: PDF report buffer
            
        Raises:
            ValueError: If client not found or report generation fails
        """
        # Get and validate client
        client = await self._get_client_data(client_id)
        
        # Get transactions and invoices
        transactions = await self._get_client_transactions(client_id)
        invoices = await self._get_client_invoices(client_id)
        
        try:
            # Generate PDF using utility function
            return generate_financial_report(
                client_name=client.name,
                transactions=transactions,
                invoices=invoices
            )
        except Exception as e:
            raise ValueError(f"Failed to generate report: {str(e)}")
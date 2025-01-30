from uuid import UUID
from io import BytesIO

from ..interfaces.services.report_service import IReportService
from ..interfaces.repositories.client_repository import IClientRepository
from ..interfaces.repositories.financial_transaction_repository import IFinancialTransactionRepository
from ..interfaces.repositories.invoice_repository import IInvoiceRepository
from ..entities.client import Client
from ..entities.financial_transaction import FinancialTransaction
from ..entities.invoice import Invoice
from ..utils.pdf_generator import generate_financial_report

class ReportService(IReportService):
    """
    Service for generating various types of reports.
    Handles report generation business logic and data gathering.
    """
    
    def __init__(self, client_repository: IClientRepository, transaction_repository: IFinancialTransactionRepository, invoice_repository: IInvoiceRepository):
        """
        Initialize service with database session and repositories.
        
        Args:
            db: Database session
        """
        self.client_repository = client_repository
        self.transaction_repository = transaction_repository
        self.invoice_repository = invoice_repository

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

    async def generate_client_financial_report(
            self,
            client_id: UUID,
            include_transactions: bool = True,
            include_invoices: bool = True
        ) -> BytesIO:
        """
        Generate a complete financial report for a client.
        
        Args:
            client_id: UUID of client
            include_transactions: Whether to include transactions section
            include_invoices: Whether to include invoices section
            
        Returns:
            BytesIO: PDF report buffer
            
        Raises:
            ValueError: If client not found or report generation fails
        """
        # Get and validate client
        client = await self._get_client_data(client_id)
        
        # Get transactions and invoices
        if include_transactions:
            transactions = await self._get_client_transactions(client_id)
        if include_invoices:
            invoices = await self._get_client_invoices(client_id)
        
        try:
            # Generate PDF using utility function
            return generate_financial_report(
                client_name=client.name,
                transactions=transactions if include_transactions else None,
                invoices=invoices if include_invoices else None
            )
        except Exception as e:
            raise ValueError(f"Failed to generate report: {str(e)}")
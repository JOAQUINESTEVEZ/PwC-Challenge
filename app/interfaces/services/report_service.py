# interfaces/service/report_service.py
from abc import ABC, abstractmethod
from uuid import UUID
from io import BytesIO

class IReportService(ABC):
    
    @abstractmethod
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
        pass
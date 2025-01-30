# interfaces/controller/report_controller.py
from abc import ABC, abstractmethod
from uuid import UUID
from io import BytesIO
from ...entities.user import User

class IReportController(ABC):
    @abstractmethod
    async def generate_client_financial_report(
        self, 
        client_id: UUID, 
        current_user: User,
        include_transactions: bool = True,
        include_invoices: bool = True
    ) -> BytesIO:
        """
        Generate a financial report for a client.
        
        Args:
            client_id: UUID of client
            current_user: Current authenticated user
            include_transactions: Whether to include transactions section
            include_invoices: Whether to include invoices section
            
        Returns:
            BytesIO: PDF report buffer
            
        Raises:
            HTTPException: If client not found or access denied
        """
        pass
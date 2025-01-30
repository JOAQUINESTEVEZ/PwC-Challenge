from uuid import UUID
from fastapi import HTTPException, status
from io import BytesIO

from ..interfaces.controllers.report_controller import IReportController
from ..interfaces.services.report_service import IReportService
from ..entities.user import User

class ReportController(IReportController):
    """
    Controller for handling report generation operations.
    Manages access control and coordinates between routes and services.
    """
    
    def __init__(self, report_service: IReportService):
        """
        Initialize controller with database session.
        
        Args:
            db: Database session
        """
        self.report_service = report_service

    def _check_client_access(self, client_id: UUID, current_user: User) -> None:
        """
        Check if user has access to client reports.
        
        Args:
            client_id: UUID of client
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If access is denied
        """
        if current_user.role.name == "client" and str(client_id) != str(current_user.client_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "about:blank",
                    "title": "Access denied",
                    "status": 403,
                    "detail": "You can only access your own reports",
                    "instance": f"/clients/{client_id}/report"
                }
            )

    async def generate_client_financial_report(self, 
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
        # Check access first
        self._check_client_access(client_id, current_user)
        
        try:
            return await self.report_service.generate_client_financial_report(
                client_id,
                include_transactions=include_transactions,
                include_invoices=include_invoices
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "type": "about:blank",
                    "title": "Not Found",
                    "status": 404,
                    "detail": str(e),
                    "instance": f"/clients/{client_id}/report"
                }
            )
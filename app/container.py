from dependency_injector import containers, providers
from sqlalchemy.orm import Session
from redis import asyncio as aioredis

from .config import settings
from .db import SessionLocal
from .utils.redis_config import get_redis

# Repositories
from .repositories.client_repository import ClientRepository
from .repositories.invoice_repository import InvoiceRepository
from .repositories.financial_transaction_repository import FinancialTransactionRepository
from .repositories.user_repository import UserRepository
from .repositories.audit_log_repository import AuditLogRepository
from .repositories.permission_repository import PermissionRepository
from .repositories.cache_repository import RedisCacheRepository

# Services
from .services.client_service import ClientService
from .services.invoice_service import InvoiceService
from .services.financial_transaction_service import FinancialTransactionService
from .services.report_service import ReportService
from .services.auth_service import AuthService
from .services.audit_log_service import AuditService
from .services.permission_service import PermissionService

# Controllers
from .controllers.client_controller import ClientController
from .controllers.invoice_controller import InvoiceController
from .controllers.financial_transaction_controller import FinancialTransactionController
from .controllers.report_controller import ReportController
from .controllers.auth_controller import AuthController

# Interfaces
from .interfaces.repositories.client_repository import IClientRepository
from .interfaces.repositories.invoice_repository import IInvoiceRepository
from .interfaces.repositories.financial_transaction_repository import IFinancialTransactionRepository
from .interfaces.repositories.user_repository import IUserRepository
from .interfaces.repositories.audit_log_repository import IAuditLogRepository
from .interfaces.repositories.permission_repository import IPermissionRepository
from .interfaces.repositories.cache_repository import ICacheRepository

from .interfaces.services.client_service import IClientService
from .interfaces.services.invoice_service import IInvoiceService
from .interfaces.services.financial_transaction_service import IFinancialTransactionService
from .interfaces.services.report_service import IReportService
from .interfaces.services.auth_service import IAuthService
from .interfaces.services.audit_service import IAuditService
from .interfaces.services.permission_service import IPermissionService

from .interfaces.controllers.client_controller import IClientController
from .interfaces.controllers.invoice_controller import IInvoiceController
from .interfaces.controllers.financial_transaction_controller import IFinancialTransactionController
from .interfaces.controllers.report_controller import IReportController
from .interfaces.controllers.auth_controller import IAuthController

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Database
    db = providers.Singleton(SessionLocal)

    # Redis client
    redis = providers.Resource(
        get_redis
    )

    # Cache Repositories
    client_cache: providers.Factory[ICacheRepository] = providers.Factory(
        RedisCacheRepository,
        redis_client=redis,
        namespace="client"
    )

    permission_cache: providers.Factory[ICacheRepository] = providers.Factory(
        RedisCacheRepository,
        redis_client=redis,
        namespace="permission"
    )

    invoice_cache: providers.Factory[ICacheRepository] = providers.Factory(
        RedisCacheRepository,
        redis_client=redis,
        namespace="invoice"
    )
    
    # Repositories
    permission_repository: providers.Factory[IPermissionRepository] = providers.Factory(
        PermissionRepository,
        db=db,
        cache=permission_cache
    )

    audit_repository: providers.Factory[IAuditLogRepository] = providers.Factory(
        AuditLogRepository,
        db=db
    )

    user_repository: providers.Factory[IUserRepository] = providers.Factory(
        UserRepository,
        db=db
    )

    client_repository: providers.Factory[IClientRepository] = providers.Factory(
        ClientRepository,
        db=db,
        cache=client_cache
    )

    invoice_repository: providers.Factory[IInvoiceRepository] = providers.Factory(
        InvoiceRepository,
        db=db,
        cache=invoice_cache
    )

    transaction_repository: providers.Factory[IFinancialTransactionRepository] = providers.Factory(
        FinancialTransactionRepository,
        db=db
    )

    # Services
    permission_service: providers.Factory[IPermissionService] = providers.Factory(
        PermissionService,
        permission_repository=permission_repository
    )

    audit_service: providers.Factory[IAuditService] = providers.Factory(
        AuditService,
        audit_log_repository=audit_repository
    )

    auth_service: providers.Factory[IAuthService] = providers.Factory(
        AuthService,
        user_repository=user_repository,
        client_repository=client_repository,
        audit_service=audit_service
    )

    client_service: providers.Factory[IClientService] = providers.Factory(
        ClientService,
        client_repository=client_repository,
        audit_service=audit_service
    )

    invoice_service: providers.Factory[IInvoiceService] = providers.Factory(
        InvoiceService,
        invoice_repository=invoice_repository,
        audit_service=audit_service
    )

    transaction_service: providers.Factory[IFinancialTransactionService] = providers.Factory(
        FinancialTransactionService,
        transaction_repository=transaction_repository,
        audit_service=audit_service
    )

    report_service: providers.Factory[IReportService] = providers.Factory(
        ReportService,
        client_repository=client_repository,
        transaction_repository=transaction_repository,
        invoice_repository=invoice_repository
    )

    # Controllers
    auth_controller: providers.Factory[IAuthController] = providers.Factory(
        AuthController,
        auth_service=auth_service
    )

    client_controller: providers.Factory[IClientController] = providers.Factory(
        ClientController,
        client_service=client_service
    )

    invoice_controller: providers.Factory[IInvoiceController] = providers.Factory(
        InvoiceController,
        invoice_service=invoice_service
    )

    transaction_controller: providers.Factory[IFinancialTransactionController] = providers.Factory(
        FinancialTransactionController,
        transaction_service=transaction_service
    )

    report_controller: providers.Factory[IReportController] = providers.Factory(
        ReportController,
        report_service=report_service
    )

    # Add wiring configuration at the class level
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.routes.auth_route",
            "app.routes.client_route",
            "app.routes.financial_transaction_route", 
            "app.routes.invoice_route",
            "app.dependencies.auth"
        ]
    )
import pytest
from datetime import date, datetime
from decimal import Decimal
from pydantic import ValidationError
from uuid import UUID
from app.schemas import (
    UserCreate, UserUpdate, RoleCreate, RoleUpdate,
    ClientCreate, ClientUpdate,
    FinancialTransactionCreate, FinancialTransactionUpdate,
    InvoiceCreate, InvoiceUpdate, LoginRequest, LoginResponse, AuditLog, AuditLogCreate
)

class TestUserSchemas:
    def test_valid_user_create(self):
        """Test valid user creation data validation"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "role_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert len(user.password) >= 8

    def test_user_create_validation_errors(self):
        """Test user creation validation errors"""
        invalid_cases = [
            (
                {"username": "t", "email": "test@example.com", "password": "pass123"},
                "username too short"
            ),
            (
                {"username": "test", "email": "invalid-email", "password": "pass123"},
                "invalid email"
            ),
            (
                {"username": "test", "email": "test@example.com", "password": "short"},
                "password too short"
            )
        ]
        
        for invalid_data, error_context in invalid_cases:
            with pytest.raises(ValidationError):
                UserCreate(**invalid_data)

    def test_user_update_partial_fields(self):
        """Test that UserUpdate allows partial updates"""
        # Only updating email
        update_data = {"email": "new@example.com"}
        update = UserUpdate(**update_data)
        assert update.email == "new@example.com"
        assert update.username is None
        assert update.password is None

class TestClientSchemas:
    def test_client_create_validation(self):
        """Test client creation data validation"""
        valid_data = {
            "name": "Test Corp",
            "industry": "Technology",
            "contact_email": "contact@testcorp.com",
            "contact_phone": "1234567890",
            "address": "123 Test St"
        }
        client = ClientCreate(**valid_data)
        assert client.name == "Test Corp"
        assert client.industry == "Technology"
        assert client.contact_email == "contact@testcorp.com"

    def test_client_create_optional_fields(self):
        """Test client creation with optional fields"""
        minimal_data = {
            "name": "Test Corp"
        }
        client = ClientCreate(**minimal_data)
        assert client.name == "Test Corp"
        assert client.industry is None
        assert client.contact_email is None

    def test_client_update_validation(self):
        """Test client update data validation"""
        # Testing partial update
        update_data = {
            "name": "Existing client name",
            "industry": "Finance"
        }
        update = ClientUpdate(**update_data)
        assert update.industry == "Finance"
        assert update.name == "Existing client name"
        assert update.contact_email is None

class TestFinancialSchemas:
    def test_transaction_create_validation(self):
        """Test financial transaction creation data validation"""
        valid_data = {
            "client_id": "550e8400-e29b-41d4-a716-446655440000",
            "transaction_date": date.today(),
            "amount": Decimal("1000.50"),
            "description": "Test transaction",
            "category": "Income",
            "created_by": "550e8400-e29b-41d4-a716-446655440001"
        }
        transaction = FinancialTransactionCreate(**valid_data)
        assert isinstance(transaction.client_id, UUID)
        assert isinstance(transaction.amount, Decimal)
        assert transaction.amount == Decimal("1000.50")

    def test_invoice_amount_validation(self):
        """Test invoice amount validation"""
        with pytest.raises(ValidationError):
            InvoiceCreate(
                client_id="550e8400-e29b-41d4-a716-446655440000",
                invoice_date=date.today(),
                due_date=date.today(),
                amount_due=Decimal("-100.00"),  # Negative amount should fail
                status="pending"
            )

class TestAuditLogSchemas:
    def test_audit_log_create_validation(self):
        """Test audit log creation data validation"""
        valid_data = {
            "changed_by": "550e8400-e29b-41d4-a716-446655440000",
            "table_name": "users",
            "record_id": "550e8400-e29b-41d4-a716-446655440001",
            "change_type": "UPDATE",
            "change_details": "Updated email field from old@example.com to new@example.com"
        }
        audit_log = AuditLogCreate(**valid_data)
        assert isinstance(audit_log.changed_by, UUID)
        assert audit_log.table_name == "users"
        assert isinstance(audit_log.record_id, UUID)
        assert audit_log.change_type == "UPDATE"
        assert audit_log.change_details == "Updated email field from old@example.com to new@example.com"

    def test_audit_log_validation_errors(self):
        """Test audit log validation errors"""
        invalid_cases = [
            (
                {
                    "changed_by": "550e8400-e29b-41d4-a716-446655440000",
                    "table_name": "x" * 51,  # Exceeds max_length of 50
                    "record_id": "550e8400-e29b-41d4-a716-446655440001",
                    "change_type": "UPDATE",
                    "change_details": "Test details"
                },
                "table_name too long"
            ),
            (
                {
                    "changed_by": "550e8400-e29b-41d4-a716-446655440000",
                    "table_name": "users",
                    "record_id": "550e8400-e29b-41d4-a716-446655440001",
                    "change_type": "x" * 21,  # Exceeds max_length of 20
                    "change_details": "Test details"
                },
                "change_type too long"
            ),
            (
                {
                    "changed_by": "invalid-uuid",  # Invalid UUID format
                    "table_name": "users",
                    "record_id": "550e8400-e29b-41d4-a716-446655440001",
                    "change_type": "UPDATE",
                    "change_details": "Test details"
                },
                "invalid UUID format"
            )
        ]
        
        for invalid_data, error_context in invalid_cases:
            with pytest.raises(ValidationError):
                AuditLogCreate(**invalid_data)

    def test_audit_log_full_model(self):
        """Test full AuditLog model with timestamp and ID"""
        valid_data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "changed_by": "550e8400-e29b-41d4-a716-446655440001",
            "table_name": "users",
            "record_id": "550e8400-e29b-41d4-a716-446655440002",
            "change_type": "INSERT",
            "change_details": "Created new user record",
            "timestamp": datetime.now()
        }
        audit_log = AuditLog(**valid_data)
        assert isinstance(audit_log.id, UUID)
        assert isinstance(audit_log.changed_by, UUID)
        assert isinstance(audit_log.timestamp, datetime)
        assert audit_log.table_name == "users"
        assert audit_log.change_type == "INSERT"
        assert audit_log.change_details == "Created new user record"

class TestAuthSchemas:
    def test_login_request_schema(self):
        """Test login request schema validation"""
        valid_data = {
            "username": "test_username",
            "password": "test_password"
        }
        login_request = LoginRequest(**valid_data)
        assert login_request.username == "test_username"
        assert login_request.password == "test_password"

    def test_login_response_schema(self):
        """Test login response schema validation"""
        valid_data = {
            "access_token": "test_access_token"
        }
        login_response = LoginResponse(**valid_data)
        assert login_response.access_token == "test_access_token"
        assert login_response.token_type == "bearer"

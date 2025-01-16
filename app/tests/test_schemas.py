import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError
from uuid import UUID
from app.schemas import (
    UserCreate, UserUpdate, RoleCreate, RoleUpdate,
    ClientCreate, ClientUpdate,
    FinancialTransactionCreate, FinancialTransactionUpdate,
    InvoiceCreate, InvoiceUpdate
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
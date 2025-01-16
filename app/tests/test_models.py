import pytest
from sqlalchemy import inspect
from app.models import User, Role, Client, FinancialTransaction, Invoice, AuditLog

class TestUserModel:
    """Test User model properties and relationships"""
    
    def test_user_table_name(self):
        """Test that User model has correct table name"""
        assert User.__tablename__ == "users"

    def test_user_required_columns(self):
        """Test that User model has all required columns"""
        columns = [c.name for c in inspect(User).columns]
        required_columns = [
            "id", "username", "email", "password_hash", 
            "role_id", "created_at", "updated_at"
        ]
        for column in required_columns:
            assert column in columns

    def test_user_relationships(self):
        """Test User model relationship definitions"""
        assert hasattr(User, 'role')
        relationship = inspect(User).relationships['role']
        assert relationship.mapper.class_ == Role

class TestClientModel:
    """Test Client model properties"""
    
    def test_client_table_name(self):
        """Test that Client model has correct table name"""
        assert Client.__tablename__ == "clients"

    def test_client_columns(self):
        """Test that Client model has all required columns"""
        columns = [c.name for c in inspect(Client).columns]
        required_columns = [
            "id", "name", "industry", "contact_email",
            "contact_phone", "address", "created_at", "updated_at"
        ]
        for column in required_columns:
            assert column in columns

class TestFinancialTransactionModel:
    """Test FinancialTransaction model properties and relationships"""
    
    def test_transaction_relationships(self):
        """Test FinancialTransaction model relationship definitions"""
        assert hasattr(FinancialTransaction, 'client')
        assert hasattr(FinancialTransaction, 'created_by_user')
        
        client_relationship = inspect(FinancialTransaction).relationships['client']
        assert client_relationship.mapper.class_ == Client
        
        user_relationship = inspect(FinancialTransaction).relationships['created_by_user']
        assert user_relationship.mapper.class_ == User

class TestInvoiceModel:
    """Test Invoice model properties and relationships"""

    def test_invoice_table_name(self):
        """Test that Invoice model has correct table name"""
        assert Invoice.__tablename__ == "invoices"

    def test_invoice_columns(self):
        """Test that Invoice model has all required columns"""
        columns = [c.name for c in inspect(Invoice).columns]
        required_columns = [
            "id", "client_id", "created_by", "invoice_date",
            "due_date", "amount_due", "amount_paid", "status",
            "created_at", "updated_at"
        ]
        for column in required_columns:
            assert column in columns

    def test_invoice_relationships(self):
        """Test Invoice model relationship definitions"""
        assert hasattr(Invoice, 'client')
        assert hasattr(Invoice, 'created_by_user')
        
        client_relationship = inspect(Invoice).relationships['client']
        assert client_relationship.mapper.class_ == Client
        
        user_relationship = inspect(Invoice).relationships['created_by_user']
        assert user_relationship.mapper.class_ == User


class TestAuditLogModel:
    """Test AuditLog model properties and relationships"""

    def test_audit_log_table_name(self):
        """Test that AuditLog model has correct table name"""
        assert AuditLog.__tablename__ == "audit_logs"

    def test_audit_log_columns(self):
        """Test that AuditLog model has all required columns"""
        columns = [c.name for c in inspect(AuditLog).columns]
        required_columns = [
            "id", "changed_by", "table_name", "record_id", 
            "change_type", "change_details", "timestamp"
        ]
        for column in required_columns:
            assert column in columns

    def test_audit_log_relationships(self):
        """Test AuditLog model relationship definitions"""
        assert hasattr(AuditLog, 'changed_by_user')
        
        user_relationship = inspect(AuditLog).relationships['changed_by_user']
        assert user_relationship.mapper.class_ == User

import pytest
from sqlalchemy import inspect
from app.models import User, Role, Client, FinancialTransaction, Invoice

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
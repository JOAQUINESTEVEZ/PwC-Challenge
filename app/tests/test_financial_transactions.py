import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, datetime
import uuid

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_tokens(client):
    """Get tokens for existing users"""
    tokens = {}
    
    # Get admin token
    response = client.post(
        "/auth/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    tokens["admin"] = response.json()["access_token"]
    
    # Get finance token
    response = client.post(
        "/auth/login",
        data={
            "username": "test_finance",
            "password": "testfinance123"
        }
    )
    tokens["finance"] = response.json()["access_token"]
    
    # Get auditor token
    response = client.post(
        "/auth/login",
        data={
            "username": "test_auditor",
            "password": "testauditor123"
        }
    )
    tokens["auditor"] = response.json()["access_token"]
    
    return tokens

@pytest.fixture
def sample_client_ids():
    return {
        "tech": "a30f6cf1-c914-4951-94c1-bea5a57006b2",  # TechWorld Inc.
        "health": "21be3212-0a2f-4750-9c7c-08f24c677a02",  # Healthy Living Co.
        "eco": "40d5c0a0-7e68-4655-9b39-b2d330f9be60",  # Eco Builders Co.
    }

def test_create_transaction_as_admin(client, test_tokens, sample_client_ids):
    """Test creating a transaction as admin"""
    transaction_data = {
        "client_id": sample_client_ids["tech"],
        "transaction_date": str(date.today()),
        "amount": 1000.50,
        "description": "Software license payment",
        "category": "License"
    }
    
    response = client.post(
        "/finance/transactions",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=transaction_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert float(data["amount"]) == 1000.50
    assert data["client_id"] == sample_client_ids["tech"]
    return data["id"]

def test_create_transaction_as_finance(client, test_tokens, sample_client_ids):
    """Test creating a transaction as finance role"""
    transaction_data = {
        "client_id": sample_client_ids["health"],
        "transaction_date": str(date.today()),
        "amount": 500.75,
        "description": "Healthcare consultation",
        "category": "Consultation"
    }
    
    response = client.post(
        "/finance/transactions",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=transaction_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED

def test_create_transaction_as_auditor(client, test_tokens, sample_client_ids):
    """Test creating a transaction as auditor (should fail)"""
    transaction_data = {
        "client_id": sample_client_ids["eco"],
        "transaction_date": str(date.today()),
        "amount": 250.25,
        "description": "Audit attempt transaction",
        "category": "Test"
    }
    
    response = client.post(
        "/finance/transactions",
        headers={"Authorization": f"Bearer {test_tokens['auditor']}"},
        json=transaction_data
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_transactions_as_admin(client, test_tokens):
    """Test getting all transactions as admin"""
    response = client.get(
        "/finance/transactions",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_transactions_with_filters(client, test_tokens):
    """Test getting transactions with filters"""
    response = client.get(
        "/finance/transactions?min_amount=500&category=License",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert all(float(t["amount"]) >= 500 for t in data)
        assert all(t["category"] == "License" for t in data)

def test_update_transaction_flow(client, test_tokens, sample_client_ids):
    """Test complete update flow: create, update, and verify"""
    # First create a transaction
    transaction_data = {
        "client_id": sample_client_ids["tech"],
        "transaction_date": str(date.today()),
        "amount": 750.25,
        "description": "Initial tech service",
        "category": "Service"
    }
    
    create_response = client.post(
        "/finance/transactions",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=transaction_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    transaction_id = create_response.json()["id"]
    
    # Update the transaction
    update_data = {
        "amount": 800.50,
        "description": "Updated tech service with support"
    }
    
    update_response = client.put(
        f"/finance/transactions/{transaction_id}",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=update_data
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated_data = update_response.json()
    assert float(updated_data["amount"]) == 800.50
    assert updated_data["description"] == "Updated tech service with support"

def test_delete_transaction_flow(client, test_tokens, sample_client_ids):
    """Test complete delete flow: create, delete, and verify"""
    # First create a transaction
    transaction_data = {
        "client_id": sample_client_ids["health"],
        "transaction_date": str(date.today()),
        "amount": 600.75,
        "description": "Healthcare consultation for deletion",
        "category": "Consultation"
    }
    
    create_response = client.post(
        "/finance/transactions",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=transaction_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    transaction_id = create_response.json()["id"]
    
    # Delete the transaction
    delete_response = client.delete(
        f"/finance/transactions/{transaction_id}",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"}
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    get_response = client.get(
        f"/finance/transactions/{transaction_id}",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_access(client, sample_client_ids):
    """Test accessing endpoints without token"""
    response = client.get("/finance/transactions")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_search_with_date_range(client, test_tokens):
    """Test searching transactions with date range"""
    response = client.get(
        f"/finance/transactions?start_date={date.today()}&end_date={date.today()}",
        headers={"Authorization": f"Bearer {test_tokens['auditor']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
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

def test_create_client_as_admin(client, test_tokens):
    """Test creating a client as admin"""
    client_data = {
        "name": f"Test Company {uuid.uuid4()}",  # Unique name
        "industry": "Software",
        "contact_email": "contact@testcompany.com",
        "contact_phone": "+1234567890",
        "address": "123 Test Avenue"
    }
    
    response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=client_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == client_data["name"]
    return data["id"]  # Return ID for use in other tests

def test_create_client_as_finance(client, test_tokens):
    """Test creating a client as finance role"""
    client_data = {
        "name": f"Finance Test Company {uuid.uuid4()}",  # Unique name
        "industry": "Finance",
        "contact_email": "finance@testcompany.com",
        "contact_phone": "+1234567890",
        "address": "456 Finance Avenue"
    }
    
    response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=client_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED

def test_create_client_as_auditor(client, test_tokens):
    """Test creating a client as auditor (should fail)"""
    client_data = {
        "name": "Auditor Test Company",
        "industry": "Audit",
        "contact_email": "audit@testcompany.com",
        "contact_phone": "+1234567890",
        "address": "789 Audit Avenue"
    }
    
    response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['auditor']}"},
        json=client_data
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_clients_as_admin(client, test_tokens):
    """Test getting all clients as admin"""
    response = client.get(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_clients_as_finance(client, test_tokens):
    """Test getting all clients as finance"""
    response = client.get(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_get_clients_as_auditor(client, test_tokens):
    """Test getting all clients as auditor"""
    response = client.get(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['auditor']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_update_client_flow(client, test_tokens):
    """Test complete update flow: create, update, and verify"""
    # First create a client
    client_data = {
        "name": f"Update Test Company {uuid.uuid4()}",
        "industry": "Technology",
        "contact_email": "update@testcompany.com",
        "contact_phone": "+1234567890",
        "address": "123 Update Avenue"
    }
    
    create_response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=client_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_client = create_response.json()
    client_id = create_response.json()["id"]
    
    # Update the client
    update_data = {
        "name": created_client["name"],
        "industry": "Updated Industry",
        "contact_email": created_client["contact_email"],
        "contact_phone": "+1987654321",
        "address": created_client["address"]
    }
    
    update_response = client.put(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=update_data
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated_data = update_response.json()
    assert updated_data["industry"] == update_data["industry"]
    assert updated_data["contact_phone"] == update_data["contact_phone"]
    # Verify other fields remained unchanged
    assert updated_data["name"] == client_data["name"]
    assert updated_data["contact_email"] == client_data["contact_email"]
    assert updated_data["address"] == client_data["address"]

def test_delete_client_flow(client, test_tokens):
    """Test complete delete flow: create and delete"""
    # First create a client
    client_data = {
        "name": f"Delete Test Company {uuid.uuid4()}",
        "industry": "Technology",
        "contact_email": "delete@testcompany.com",
        "contact_phone": "+1234567890",
        "address": "123 Delete Avenue"
    }
    
    create_response = client.post(
        "/clients",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=client_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    client_id = create_response.json()["id"]
    
    # Delete the client
    delete_response = client.delete(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    get_response = client.get(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_search_clients(client, test_tokens):
    """Test searching clients"""
    response = client.get(
        "/clients?search=Software",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_pagination(client, test_tokens):
    """Test client pagination"""
    response = client.get(
        "/clients?skip=0&limit=2",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 2

def test_unauthorized_access(client):
    """Test accessing endpoints without token"""
    response = client.get("/clients")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
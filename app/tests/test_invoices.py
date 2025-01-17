import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from datetime import date, timedelta
from decimal import Decimal
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
    """Real client IDs from the database"""
    return {
        "tech": "a30f6cf1-c914-4951-94c1-bea5a57006b2",  # TechWorld Inc.
        "health": "21be3212-0a2f-4750-9c7c-08f24c677a02",  # Healthy Living Co.
        "eco": "40d5c0a0-7e68-4655-9b39-b2d330f9be60",  # Eco Builders Co.
    }

def test_create_invoice_as_admin(client, test_tokens, sample_client_ids):
    """Test creating an invoice as admin"""
    invoice_data = {
        "client_id": sample_client_ids["tech"],
        "invoice_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('1500.75')),
        "amount_paid": str(Decimal('0.00')),
        "status": "PENDING"
    }
    
    response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=invoice_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert Decimal(data["amount_due"]) == Decimal('1500.75')
    assert data["status"] == "PENDING"
    return data["id"]

def test_create_invoice_as_finance(client, test_tokens, sample_client_ids):
    """Test creating an invoice as finance role"""
    invoice_data = {
        "client_id": sample_client_ids["health"],
        "invoice_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('2500.50')),
        "amount_paid": str(Decimal('0.00')),
        "status": "PENDING"
    }
    
    response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=invoice_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED

def test_create_invoice_as_auditor(client, test_tokens, sample_client_ids):
    """Test creating an invoice as auditor (should fail)"""
    invoice_data = {
        "client_id": sample_client_ids["eco"],
        "invoice_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('1000.00')),
        "amount_paid": str(Decimal('0.00')),
        "status": "PENDING"
    }
    
    response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['auditor']}"},
        json=invoice_data
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_update_payment_flow(client, test_tokens, sample_client_ids):
    """Test complete payment flow: create invoice, update payment, verify status"""
    # First create an invoice
    invoice_data = {
        "client_id": sample_client_ids["tech"],
        "invoice_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('3000.00')),
        "amount_paid": str(Decimal('0.00')),
        "status": "PENDING"
    }
    
    create_response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=invoice_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    invoice_id = create_response.json()["id"]
    
    # Make partial payment
    update_data = {
        "amount_paid": str(Decimal('1500.00'))
    }
    
    partial_response = client.put(
        f"/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=update_data
    )
    assert partial_response.status_code == status.HTTP_200_OK
    partial_data = partial_response.json()
    assert Decimal(partial_data["amount_paid"]) == Decimal('1500.00')
    assert partial_data["status"] == "PARTIALLY_PAID"
    
    # Complete payment
    final_update = {
        "amount_paid": str(Decimal('3000.00'))
    }
    
    final_response = client.put(
        f"/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=final_update
    )
    assert final_response.status_code == status.HTTP_200_OK
    final_data = final_response.json()
    assert Decimal(final_data["amount_paid"]) == Decimal('3000.00')
    assert final_data["status"] == "PAID"

def test_invalid_payment_amount(client, test_tokens, sample_client_ids):
    """Test attempting to pay more than amount due"""
    # Create invoice
    invoice_data = {
        "client_id": sample_client_ids["health"],
        "invoice_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('1000.00')),
        "amount_paid": str(Decimal('0.00')),
        "status": "PENDING"
    }
    
    create_response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=invoice_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    invoice_id = create_response.json()["id"]
    
    # Try to overpay
    update_data = {
        "amount_paid": str(Decimal('1200.00'))
    }
    
    response = client.put(
        f"/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"},
        json=update_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_delete_paid_invoice(client, test_tokens, sample_client_ids):
    """Test attempting to delete a paid invoice (should fail)"""
    # Create and pay invoice
    invoice_data = {
        "client_id": sample_client_ids["eco"],
        "invoice_date": date.today().isoformat(),
        "due_date": (date.today() + timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('500.00')),
        "amount_paid": str(Decimal('500.00')),
        "status": "PAID"
    }
    
    create_response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=invoice_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    invoice_id = create_response.json()["id"]
    
    # Try to delete
    response = client.delete(
        f"/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_overdue_invoices(client, test_tokens, sample_client_ids):
    """Test getting overdue invoices"""
    # Create an overdue invoice
    invoice_data = {
        "client_id": sample_client_ids["tech"],
        "invoice_date": (date.today() - timedelta(days=60)).isoformat(),
        "due_date": (date.today() - timedelta(days=30)).isoformat(),
        "amount_due": str(Decimal('1000.00')),
        "amount_paid": str(Decimal('0.00')),
        "status": "PENDING"
    }
    
    create_response = client.post(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"},
        json=invoice_data
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    
    response = client.get(
        "/invoices/overdue",
        headers={"Authorization": f"Bearer {test_tokens['finance']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_search_invoices(client, test_tokens):
    """Test searching invoices with filters"""
    response = client.get(
        "/invoices?min_amount=1000&status=PENDING",
        headers={"Authorization": f"Bearer {test_tokens['admin']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert all(Decimal(inv["amount_due"]) >= Decimal('1000') for inv in data)
        assert all(inv["status"] == "PENDING" for inv in data)

def test_unauthorized_access(client):
    """Test accessing endpoints without token"""
    response = client.get("/invoices")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_invoices_as_auditor(client, test_tokens):
    """Test getting all invoices as auditor"""
    response = client.get(
        "/invoices",
        headers={"Authorization": f"Bearer {test_tokens['auditor']}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from app.db.database import Base, get_db
from app.models.client import Client

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_client_valid_payload():
    """Test creating a client with valid payload"""
    response = client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 250000
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cliente_nome"] == "João Silva"
    assert data["cliente_email"] == "joao.silva@example.com"
    assert data["valor_patrimonio"] == 250000
    assert data["status"] == "Aguardando Análise"
    assert data["prioridade"] == "prioridade_normal"

def test_create_client_duplicate_email():
    """Test that duplicate email is rejected"""
    # Create first client
    client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 250000
        }
    )
    
    # Try to create another client with same email
    response = client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "Maria Santos",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Abertura de conta",
            "valor_patrimonio": 150000
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_webhook_processing_high_priority():
    """Test webhook processing for high priority client (patrimonio >= 200000)"""
    # Create a client first
    create_response = client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 250000  # High patrimonio
        }
    )
    assert create_response.status_code == 201
    
    # Process webhook
    webhook_response = client.post(
        "/api/v1/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_123",
            "card_id": "card_456",
            "cliente_email": "joao.silva@example.com",
            "timestamp": "2026-05-18T12:00:00Z"
        }
    )
    assert webhook_response.status_code == 200
    data = webhook_response.json()
    assert data["status"] == "Processado"
    assert data["priority"] == "prioridade_alta"  # Should be high priority
    assert data["message"] == "Webhook processed successfully"

def test_webhook_processing_low_priority():
    create_response = client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 150000
        }
    )
    assert create_response.status_code == 201

    webhook_response = client.post(
        "/api/v1/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_124",
            "card_id": "card_457",
            "cliente_email": "joao.silva@example.com",
            "timestamp": "2026-05-18T12:00:00Z"
        }
    )
    assert webhook_response.status_code == 200
    data = webhook_response.json()
    assert data["status"] == "Processado"
    assert data["priority"] == "prioridade_normal"
    assert data["message"] == "Webhook processed successfully"

def test_webhook_idempotency():
    """Test that duplicate webhook events are ignored (idempotency)"""
    # Create a client first
    client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 250000
        }
    )
    
    # Process webhook first time
    response1 = client.post(
        "/api/v1/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_duplicate",
            "card_id": "card_duplicate",
            "cliente_email": "joao.silva@example.com",
            "timestamp": "2026-05-18T12:00:00Z"
        }
    )
    assert response1.status_code == 200
    assert response1.json()["message"] == "Webhook processed successfully"
    
    # Process same webhook again (should be ignored)
    response2 = client.post(
        "/api/v1/webhooks/pipefy/card-updated",
        json={
            "event_id": "evt_duplicate",  # Same event_id
            "card_id": "card_duplicate",
            "cliente_email": "joao.silva@example.com",
            "timestamp": "2026-05-18T12:00:00Z"
        }
    )
    assert response2.status_code == 200
    assert response2.json()["message"] == "Event already processed"
    assert response2.json()["status"] == "ignored"

def test_get_clients():
    """Test retrieving list of clients"""
    # Create a couple of clients
    client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "João Silva",
            "cliente_email": "joao.silva@example.com",
            "tipo_solicitacao": "Atualização cadastral",
            "valor_patrimonio": 250000
        }
    )
    
    client.post(
        "/api/v1/clientes",
        json={
            "cliente_nome": "Maria Santos",
            "cliente_email": "maria.santos@example.com",
            "tipo_solicitacao": "Abertura de conta",
            "valor_patrimonio": 150000
        }
    )
    
    # Get clients list
    response = client.get("/api/v1/clientes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Check that we have both clients
    emails = [c["cliente_email"] for c in data]
    assert "joao.silva@example.com" in emails
    assert "maria.santos@example.com" in emails
import pytest
from app.pipefy_service import PipefyService

def test_get_create_card_payload():
    """Test that the create card payload is properly formatted"""
    client_data = {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000
    }
    
    payload = PipefyService.get_create_card_payload(client_data)
    
    # Check that all client data is present in the payload
    assert "João Silva" in payload
    assert "joao.silva@example.com" in payload
    assert "Atualização cadastral" in payload
    assert "250000" in payload
    
    # Check that it contains the mutation structure
    assert "createCard" in payload
    assert "pipe_id" in payload
    assert "fields_attributes" in payload

def test_get_update_status_payload():
    """Test that the update status payload is properly formatted"""
    card_id = "card_123"
    payload = PipefyService.get_update_status_payload(card_id)
    
    assert card_id in payload
    assert "updateCardField" in payload
    assert "field_status_id" in payload
    assert "Processado" in payload

def test_get_update_priority_payload():
    """Test that the update priority payload is properly formatted"""
    card_id = "card_123"
    priority = "prioridade_alta"
    payload = PipefyService.get_update_priority_payload(card_id, priority)
    
    assert card_id in payload
    assert "updateCardField" in payload
    assert "field_prioridade_id" in payload
    assert priority in payload
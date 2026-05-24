from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientResponse, WebhookPayload
from app.services.client_service import (
    get_client_by_email,
    create_client, 
    update_client_status_and_priority,
    get_clients
)
from app.pipefy_service import PipefyService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/clientes", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_cliente_endpoint(cliente: ClientCreate, db: Session = Depends(get_db)):
    db_client = get_client_by_email(db, email=cliente.cliente_email)
    if db_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_client = create_client(db=db, client=cliente)

    pipefy_mutation = PipefyService.get_create_card_payload(cliente.model_dump())
    logger.info(f"Pipefy CREATE_CARD mutation structured: {pipefy_mutation}")

    return db_client

@router.post("/webhooks/pipefy/card-updated", status_code=status.HTTP_200_OK)
def pipefy_webhook_endpoint(payload: WebhookPayload, db: Session = Depends(get_db)):
    existing_client = db.query(Client).filter(Client.event_id == payload.event_id).first()
    if existing_client:
        logger.info(f"Event {payload.event_id} already processed. Skipping.")
        return {"message": "Event already processed", "status": "ignored"}

    db_client = get_client_by_email(db, email=payload.cliente_email)
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if db_client.valor_patrimonio >= 200000:
        priority = "prioridade_alta"
    else:
        priority = "prioridade_normal"

    updated_client = update_client_status_and_priority(
        db=db,
        email=payload.cliente_email,
        status="Processado",
        priority=priority
    )

    if updated_client:
        updated_client.event_id = payload.event_id
        db.commit()
        db.refresh(updated_client)

    status_mutation = PipefyService.get_update_status_payload(payload.card_id)
    priority_mutation = PipefyService.get_update_priority_payload(payload.card_id, priority)

    logger.info(f"Pipefy UPDATE_STATUS mutation structured: {status_mutation}")
    logger.info(f"Pipefy UPDATE_PRIORITY mutation structured: {priority_mutation}")

    return {
        "message": "Webhook processed successfully",
        "client_id": updated_client.id,
        "status": updated_client.status,
        "priority": updated_client.prioridade,
        "event_id": payload.event_id
    }

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "client-management-pipefy"}

@router.get("/clientes", response_model=List[ClientResponse])
def get_clientes_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # TODO: add pagination metadata to response
    clientes = get_clients(db=db, skip=skip, limit=limit)
    return clientes
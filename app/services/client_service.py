from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from typing import Optional

def get_client_by_email(db: Session, email: str) -> Optional[Client]:
    return db.query(Client).filter(Client.cliente_email == email).first()

def get_client(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: ClientCreate) -> Client:
    db_client = Client(
        cliente_nome=client.cliente_nome,
        cliente_email=client.cliente_email,
        tipo_solicitacao=client.tipo_solicitacao,
        valor_patrimonio=client.valor_patrimonio,
        status="Aguardando Análise"
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: int, client_update: ClientUpdate) -> Optional[Client]:
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        update_data = client_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
    return db_client

def update_client_status_and_priority(db: Session, email: str, status: str, priority: str) -> Optional[Client]:
    db_client = get_client_by_email(db, email)
    if db_client:
        db_client.status = status
        db_client.prioridade = priority
        db.commit()
        db.refresh(db_client)
    return db_client
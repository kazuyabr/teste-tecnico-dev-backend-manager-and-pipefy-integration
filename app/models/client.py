from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nome = Column(String, index=True)
    cliente_email = Column(String, unique=True, index=True)
    tipo_solicitacao = Column(String)
    valor_patrimonio = Column(Float)
    status = Column(String, default="Aguardando Análise")
    prioridade = Column(String, default="prioridade_normal")
    event_id = Column(String, nullable=True)  # For webhook idempotency
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
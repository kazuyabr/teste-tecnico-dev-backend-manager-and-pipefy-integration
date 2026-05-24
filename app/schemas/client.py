from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    cliente_nome: str = Field(..., min_length=1, max_length=100)
    cliente_email: EmailStr
    tipo_solicitacao: str = Field(..., min_length=1, max_length=100)
    valor_patrimonio: float = Field(..., gt=0)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    status: Optional[str] = None
    prioridade: Optional[str] = None

class ClientResponse(ClientBase):
    id: int
    status: str
    prioridade: str
    event_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class WebhookPayload(BaseModel):
    event_id: str = Field(..., min_length=1)
    card_id: str = Field(..., min_length=1)
    cliente_email: EmailStr
    timestamp: datetime
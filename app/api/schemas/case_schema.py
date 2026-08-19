from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CaseBase(BaseModel):
    external_name: str
    display_name: str
    source_path: str

class CaseCreateRequest(CaseBase):
    """Payload esperado quando o usuário deseja registrar um novo caso."""
    pass

class CaseResponse(CaseBase):
    """Payload devolvido pela API contendo os dados do caso persistido."""
    id: uuid.UUID
    status: str
    
    # Configuração para que o Pydantic consiga ler o objeto do SQLAlchemy
    class Config:
        from_attributes = True
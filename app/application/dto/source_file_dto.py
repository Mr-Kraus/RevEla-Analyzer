from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class SourceFileDTO(BaseModel):
    """Objeto de transferência de dados para os metadados de arquivos originais."""
    id: UUID
    case_id: UUID
    filename: str
    extension: str
    size: int
    modified_at: datetime
    sha256: str
    dataset_code: Optional[str] = None  # CORREÇÃO C3: Agora permite None como no Domain
    status: str
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.domain.enums.case_status import CaseStatus

class CaseDTO(BaseModel):
    """Objeto de transferência de dados para a entidade Case."""
    id: UUID
    external_name: str
    display_name: str
    source_path: str
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
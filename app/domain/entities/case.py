from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from app.domain.enums.case_status import CaseStatus

class Case(BaseModel):
    """
    Entidade central do Domínio.
    """
    id: UUID = Field(default_factory=uuid4)
    external_name: str  # Nome técnico exato da pasta de origem (ex: "C01.São Tome2025...")
    display_name: str   # Nome amigável para a GUI (ex: "Caso Base C01")
    source_path: str    # Caminho absoluto no disco
    status: CaseStatus = CaseStatus.DISCOVERED
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class SimulationRun(BaseModel):
    """Representa uma execução específica de Monte Carlo atrelada a um Caso."""
    id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    results_directory: Optional[str] = None
    simulated_years: Optional[int] = None
    analysis_type: Optional[str] = None  # Ex: "STA", "OPE"
    system_representation: Optional[str] = None
    imported_at: datetime = Field(default_factory=datetime.now)
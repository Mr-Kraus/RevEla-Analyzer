import uuid
from typing import Optional
from pydantic import BaseModel

class ReliabilityResult(BaseModel):
    """
    Entidade de Domínio que representa os resultados numéricos de confiabilidade.
    Pode ser Global (is_global=True) ou associado a uma barra (bus_external_id preenchido).
    """
    id: uuid.UUID
    simulation_run_id: uuid.UUID
    is_global: bool
    bus_external_id: Optional[str] = None
    
    # Indicadores
    lolp: float
    lole: float
    epns: float
    eens: float
    lolf: float
    lold: float
    lolc: float
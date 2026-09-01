from pydantic import BaseModel
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class RawSettingsDTO:
    parameters: Dict[str, Any] = field(default_factory=dict)
    analysis_type: str = "N/A"
    system_representation: str = "N/A"
    convergence_beta: str = "N/A"

class RawSystemBlockDTO(BaseModel):
    """Representa um bloco bruto extraído do Template System.csv (ex: BARRAS)."""
    block_name: str
    headers: List[str]
    records: List[Dict[str, str]]
    

class RawSystemDTO(BaseModel):
    """Representa a topologia inteira extraída do Template System.csv."""
    blocks: Dict[str, RawSystemBlockDTO]
    carga_nominal: float = 0.0

class RawReliabilityIndicesDTO(BaseModel):
    """Representa as matrizes de resultados agrupadas por âncoras (ex: TOTAL_GLOBAL, BY_BUS)."""
    blocks: Dict[str, List[List[str]]]
    simulated_years: int = 0
    confidence_intervals: Dict[str, Any] = field(default_factory=dict)
    regional_indices: dict = None
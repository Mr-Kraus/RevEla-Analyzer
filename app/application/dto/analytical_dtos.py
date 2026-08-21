from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import uuid


# --- 1. DTO de Indicador Base ---
class IndicatorDTO(BaseModel):
    code: str
    name: str
    value: float
    unit: str
    category: str
    description: str = ""

# --- 2. DTO de Análise Global ---
class GlobalAnalysisDTO(BaseModel):
    simulation_id: uuid.UUID
    case_name: str
    indicators: Dict[str, IndicatorDTO]

# --- 3. DTOs de Ranking ---
class RankingItemDTO(BaseModel):
    rank_position: int
    element_id: str
    element_name: str
    region_name: Optional[str] = "Região Principal"
    value: float

class RankingDTO(BaseModel):
    indicator: str
    top_elements: List[RankingItemDTO]

# --- 4. DTO de Análise de Caso (Detalhada) ---
class CaseAnalysisDTO(BaseModel):
    simulation_id: uuid.UUID
    case_name: str
    region_aggregations: Dict[str, Dict[str, float]] = Field(description="Ex: {'Region1': {'epns': 10.5}}")
    top_critical_buses: RankingDTO
    technology_distribution: Dict[str, float] = Field(default_factory=dict)

# --- 5. DTOs de Comparação ---
class ComparisonDeltaDTO(BaseModel):
    val_a: float
    val_b: float
    absolute_difference: float
    percentage_difference: float

class ComparisonDTO(BaseModel):
    base_simulation_id: uuid.UUID
    target_simulation_id: uuid.UUID
    indicator: str
    global_comparison: ComparisonDeltaDTO
    element_comparisons: List[Dict[str, Any]] = Field(
        description="Lista de deltas detalhados por elemento (ex: Barras). Formato livre por flexibilidade."
    )
class MultiCompareRequestDTO(BaseModel):
    case_ids: List[str]
    granularity: str  # "GLOBAL", "REGION", "BUS"
    element_id: Optional[str] = "ALL"  # "ALL" ou ID específico

class MultiCompareElementDataDTO(BaseModel):
    element_name: str
    values_by_case: Dict[str, Dict[str, Optional[float]]] # { sim_id: { "LOLP": 0.01, "LOLE": 2.5 } }

class MultiCompareResponseDTO(BaseModel):
    indicators: List[str]
    units: Dict[str, str]
    granularity: str
    elements: List[MultiCompareElementDataDTO]
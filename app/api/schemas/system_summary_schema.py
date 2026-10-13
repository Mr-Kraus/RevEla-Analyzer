from pydantic import BaseModel
from typing import List, Dict

class SystemSummaryParamDTO(BaseModel):
    nome: str
    valor: float
    unidade: str

class SystemSummaryResponse(BaseModel):
    system_summary: List[SystemSummaryParamDTO]
    generation_tech: Dict[str, float]
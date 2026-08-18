from pydantic import BaseModel, Field
from typing import List, Optional

class AnalyticalFilterDTO(BaseModel):
    """
    Padroniza os filtros que podem ser aplicados em qualquer consulta analítica (M03.12).
    """
    region_external_ids: Optional[List[str]] = Field(default_factory=list)
    bus_external_ids: Optional[List[str]] = Field(default_factory=list)
    generator_external_ids: Optional[List[str]] = Field(default_factory=list)
    # Futuro expansível para Line e Transformer
from pydantic import BaseModel
from typing import List
from app.domain.enums.granularity_enum import TimeSeriesGranularity

class ENSAggregationResponse(BaseModel):
    case_name: str
    granularity: TimeSeriesGranularity
    unit: str
    ens_generation: List[float]
    ens_transmission: List[float]
    ens_gen_trans: List[float]
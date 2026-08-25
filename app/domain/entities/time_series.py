from pydantic import BaseModel
from typing import List, Optional
import uuid

class TimeSeriesMetadata(BaseModel):
    id: uuid.UUID
    simulation_run_id: uuid.UUID
    name: str
    series_type: str        # Ex: "Load", "Solar", "Hydro"
    data_position: str      # Ex: "Input", "Output"
    unit_x: Optional[str] = "Hour"
    unit_y: Optional[str] = "MW" # ou pu, %, dependendo da série

class DataTimeSeries(BaseModel):
    id: uuid.UUID
    metadata_id: uuid.UUID
    values: List[float]     # O array gigante que vai para o Postgres
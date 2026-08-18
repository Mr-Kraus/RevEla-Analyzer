from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

class Region(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    external_id: str
    name: str

class Bus(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    region_id: Optional[UUID] = None
    external_id: str
    name: str
    nominal_voltage_kv: Optional[float] = None  # TODO - REQUIRES CONFIRMATION (Formato exato no CSV)

class Generator(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    bus_id: Optional[UUID] = None
    external_id: str
    name: str
    technology: Optional[str] = None
    nominal_power_mw: Optional[float] = None
    # TODO - REQUIRES CONFIRMATION: Validar se 'failure_rate' e 'mttr_hours' estão no Template System ou em outro CSV.
    failure_rate_percent: Optional[float] = None 
    mttr_hours: Optional[float] = None

class TransmissionLine(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    from_bus_id: UUID
    to_bus_id: UUID
    external_id: str
    name: Optional[str] = None
    capacity_mw: Optional[float] = None

class Transformer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    system_id: UUID
    from_bus_id: UUID
    to_bus_id: UUID
    external_id: str
    name: Optional[str] = None
    capacity_mva: Optional[float] = None

class System(BaseModel):
    """Agregador topológico principal da simulação."""
    id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    simulation_run_id: UUID
    external_name: Optional[str] = None
    nominal_load_mw: Optional[float] = None
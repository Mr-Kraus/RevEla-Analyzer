from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class CaseDiscoveryDetailsDTO(BaseModel):
    system_templates: List[str]
    result_directories: List[str]
    warnings: List[str]
    errors: List[str]

class CaseBase(BaseModel):
    external_name: str
    display_name: str
    source_path: str

class CaseCreateRequest(BaseModel):
    source_path: str

class CaseResponse(CaseBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    discovery_details: Optional[CaseDiscoveryDetailsDTO] = None
    
    class Config:
        from_attributes = True
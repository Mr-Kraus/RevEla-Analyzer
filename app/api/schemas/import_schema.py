from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class ImportJobResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional

class SourceFile(BaseModel):
    id: UUID4 # [cite: 373]
    case_id: UUID4 # [cite: 374]
    path: str # [cite: 375]
    relative_path: str # [cite: 376]
    filename: str # [cite: 377]
    extension: str # [cite: 378]
    size: int # [cite: 379]
    modified_at: datetime # [cite: 380]
    sha256: str # [cite: 381]
    dataset_code: Optional[str] = None # [cite: 382]
    status: str # [cite: 383]
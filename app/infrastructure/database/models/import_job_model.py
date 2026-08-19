import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class ImportJobModel(Base):
    __tablename__ = "import_job"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"))
    
    # Status pode ser: PENDING, RUNNING, SUCCESS, FAILED
    status: Mapped[str] = mapped_column(String, default="PENDING") 
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str] = mapped_column(String, nullable=True)
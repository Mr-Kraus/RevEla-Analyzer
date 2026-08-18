from sqlalchemy import BigInteger, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid

from .base import Base

class SourceFileModel(Base):
    __tablename__ = "source_file"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    
    path: Mapped[str] = mapped_column(String, nullable=False)
    relative_path: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # C2/C3: Alinhado com o DTO e Domain (agora pode ser nulo)
    dataset_code: Mapped[str | None] = mapped_column(String, nullable=True) 
    
    status: Mapped[str] = mapped_column(String, nullable=False)

    case = relationship("CaseModel", back_populates="source_files")
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base
from app.domain.enums.case_status import CaseStatus

class CaseModel(Base):
    __tablename__ = "case"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    source_path: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[CaseStatus] = mapped_column(SQLEnum(CaseStatus), default=CaseStatus.DISCOVERED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    # Relacionamentos (carregamento preguiçoso/lazy default)
    simulations = relationship("SimulationRunModel", back_populates="case", cascade="all, delete-orphan")
    source_files = relationship("SourceFileModel", back_populates="case", cascade="all, delete-orphan")
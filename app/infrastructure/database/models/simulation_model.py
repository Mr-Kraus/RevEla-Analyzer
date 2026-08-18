from sqlalchemy import String, Integer, DateTime, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
import uuid

from .base import Base

class SimulationRunModel(Base):
    __tablename__ = "simulation_run"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    
    results_directory: Mapped[str | None] = mapped_column(String, nullable=True)
    simulated_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    simulation_time: Mapped[timedelta | None] = mapped_column(Interval, nullable=True)
    
    analysis_type: Mapped[str | None] = mapped_column(String, nullable=True)
    system_representation: Mapped[str | None] = mapped_column(String, nullable=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    case = relationship("CaseModel")
import uuid
from sqlalchemy import ForeignKey, String, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from sqlalchemy import JSON
from typing import Optional

class ReliabilityResultModel(Base):
    """Tabela para armazenar os indicadores de confiabilidade do M02."""
    __tablename__ = "reliability_result"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("simulation_run.id", ondelete="CASCADE"), nullable=False)
    confidence_intervals: Mapped[dict] = mapped_column(JSON, nullable=True)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    bus_external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    region_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    lolp: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lole: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    epns: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    eens: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lolf: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lolc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    simulation_run = relationship("SimulationRunModel")
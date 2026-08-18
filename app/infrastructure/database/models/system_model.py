import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class SystemModel(Base):
    __tablename__ = "system"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("simulation_run.id", ondelete="CASCADE"), nullable=False)
    
    external_name: Mapped[str] = mapped_column(String, nullable=False)
    nominal_load_mw: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # REQUISITO M02.3/M02.4: Cascata Total (Salva a raiz, salva os galhos automaticamente)
    regions = relationship("RegionModel", back_populates="system", cascade="all, delete-orphan")
    buses = relationship("BusModel", back_populates="system", cascade="all, delete-orphan")
    generators = relationship("GeneratorModel", back_populates="system", cascade="all, delete-orphan")
    transmission_lines = relationship("TransmissionLineModel", back_populates="system", cascade="all, delete-orphan")
    transformers = relationship("TransformerModel", back_populates="system", cascade="all, delete-orphan")
    
    case = relationship("CaseModel")
    simulation_run = relationship("SimulationRunModel")
import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class GeneratorModel(Base):
    __tablename__ = "generator"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("system.id", ondelete="CASCADE"), index=True)
    bus_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bus.id", ondelete="SET NULL"), nullable=True, index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    technology: Mapped[str] = mapped_column(String, nullable=True)
    
    nominal_capacity_mw: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    failure_rate_percent: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    repair_time_hours: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)

    system = relationship("SystemModel", back_populates="generators")


class TransmissionLineModel(Base):
    __tablename__ = "transmission_line"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("system.id", ondelete="CASCADE"), index=True)
    from_bus_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    to_bus_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    
    # Parâmetros elétricos e de confiabilidade
    r_pu: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    x_pu: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    capacity_mva: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    failure_rate: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    repair_time: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)

    system = relationship("SystemModel", back_populates="transmission_lines")
    from_bus = relationship("BusModel", foreign_keys=[from_bus_id])
    to_bus = relationship("BusModel", foreign_keys=[to_bus_id])


class TransformerModel(Base):
    __tablename__ = "transformer"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("system.id", ondelete="CASCADE"), index=True)
    from_bus_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    to_bus_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    
    # Parâmetros elétricos e de confiabilidade
    r_pu: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    x_pu: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    capacity_mva: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    failure_rate: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    repair_time: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)

    system = relationship("SystemModel", back_populates="transformers")
    from_bus = relationship("BusModel", foreign_keys=[from_bus_id])
    to_bus = relationship("BusModel", foreign_keys=[to_bus_id])
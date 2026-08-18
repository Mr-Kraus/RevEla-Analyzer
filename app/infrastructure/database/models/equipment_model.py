import uuid
from sqlalchemy import String, Numeric, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class GeneratorModel(Base):
    __tablename__ = "generator"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("system.id", ondelete="CASCADE"), index=True)
    bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bus.id", ondelete="SET NULL"), nullable=True, index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    technology: Mapped[str] = mapped_column(String, nullable=True)
    
    # Substituindo 'nominal_power_mw' por 'nominal_capacity_mw' conforme o domínio
    nominal_capacity_mw: Mapped[float] = mapped_column(Numeric, nullable=True)
    
    # Substituindo 'failure_rate' por 'failure_rate_percent' conforme o domínio
    failure_rate_percent: Mapped[float] = mapped_column(Numeric, nullable=True)
    
    # Substituindo 'mttr_hours' por 'repair_time_hours' conforme o domínio
    repair_time_hours: Mapped[float] = mapped_column(Numeric, nullable=True)

    # Removidos: number_of_units e mobilizable (não existem no domínio M01)

    system = relationship("SystemModel", back_populates="generators")

class TransmissionLineModel(Base):
    __tablename__ = "transmission_line"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("system.id", ondelete="CASCADE"), index=True)
    from_bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    to_bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    capacity_mw: Mapped[float] = mapped_column(Numeric, nullable=True)

    system = relationship("SystemModel", back_populates="transmission_lines")

class TransformerModel(Base):
    __tablename__ = "transformer"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("system.id", ondelete="CASCADE"), index=True)
    from_bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    to_bus_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bus.id", ondelete="CASCADE"), index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    capacity_mva: Mapped[float] = mapped_column(Numeric, nullable=True)

    system = relationship("SystemModel", back_populates="transformers")
import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class TimeSeriesMetadataModel(Base):
    __tablename__ = "time_series_metadata"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_run.id", ondelete="CASCADE"))
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    series_type: Mapped[str] = mapped_column(String, nullable=False) # Ex: 'Load Curve', 'Hydro'
    data_position: Mapped[str] = mapped_column(String, nullable=False) # 'Input' ou 'Output'
    unit_x: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unit_y: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relacionamentos
    simulation_run = relationship("SimulationRunModel")
    data_series = relationship("DataTimeSeriesModel", back_populates="metadata_ref", cascade="all, delete-orphan", uselist=False)
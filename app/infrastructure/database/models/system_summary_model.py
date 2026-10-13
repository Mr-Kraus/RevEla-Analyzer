import uuid
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class SystemSummaryModel(Base):
    __tablename__ = "system_summary"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_run.id", ondelete="CASCADE"), unique=True)
    
    system_name: Mapped[str] = mapped_column(String, nullable=True)
    number_of_interconnected_systems: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_interconnections: Mapped[int] = mapped_column(Integer, nullable=True)
    
    rated_load_mw: Mapped[float] = mapped_column(Float, nullable=True)
    peak_load_mw: Mapped[float] = mapped_column(Float, nullable=True)
    mean_load_mw: Mapped[float] = mapped_column(Float, nullable=True)
    annual_total_demand_twh: Mapped[float] = mapped_column(Float, nullable=True)
    short_term_load_uncertainty: Mapped[float] = mapped_column(Float, nullable=True)
    long_term_load_uncertainty: Mapped[float] = mapped_column(Float, nullable=True)
    
    rated_load_generation_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    mean_load_generation_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    
    number_of_reservoirs: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_wind_regions: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_solar_regions: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Armazenará a tabela "Generators information" inteira como JSON
    generators_information: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Relacionamento
    simulation_run = relationship("SimulationRunModel")
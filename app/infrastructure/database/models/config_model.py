import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class SimulationConfigModel(Base):
    __tablename__ = "simulation_config"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("simulation_run.id", ondelete="CASCADE"), index=True)
    source_file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_file.id", ondelete="SET NULL"), nullable=True)
    
    parameter_key: Mapped[str] = mapped_column(String, nullable=False)
    parameter_value: Mapped[str] = mapped_column(String, nullable=True)
    value_type: Mapped[str] = mapped_column(String, nullable=True)

    # Relacionamento
    simulation_run = relationship("SimulationRunModel", backref="configurations")
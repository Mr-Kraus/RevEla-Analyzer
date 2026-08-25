import uuid
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.base import Base

class DataTimeSeriesModel(Base):
    __tablename__ = "data_time_series"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    metadata_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("time_series_metadata.id", ondelete="CASCADE"), unique=True)
    
    # Armazena a série temporal completa (ex: 8760 horas) em um único array otimizado
    values: Mapped[List[float]] = mapped_column(ARRAY(FLOAT), nullable=False)

    # Relacionamento
    metadata_ref = relationship("TimeSeriesMetadataModel", back_populates="data_series")
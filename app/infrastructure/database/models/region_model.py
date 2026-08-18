import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class RegionModel(Base):
    """Tabela para armazenar as Regiões Elétricas do Sistema."""
    __tablename__ = "region"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("system.id", ondelete="CASCADE"), index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    system = relationship("SystemModel", back_populates="regions")
    buses = relationship("BusModel", back_populates="region")
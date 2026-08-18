import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class BusModel(Base):
    """Tabela para armazenar as Barras (Nós) do Sistema."""
    __tablename__ = "bus"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("system.id", ondelete="CASCADE"), index=True)
    region_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("region.id", ondelete="SET NULL"), nullable=True, index=True)
    
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    base_kv: Mapped[float] = mapped_column(Float, nullable=True)

    system = relationship("SystemModel", back_populates="buses")
    region = relationship("RegionModel", back_populates="buses")

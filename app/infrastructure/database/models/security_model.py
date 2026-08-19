import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.infrastructure.database.models.base import Base

# Tabelas de Associação para relacionamentos Muitos-para-Muitos
user_role_table = Table(
    "user_role",
    Base.metadata,
    # CORREÇÃO 1: Apontando para app_user.id
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)

role_permission_table = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", PG_UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", PG_UUID(as_uuid=True), ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
)

class PermissionModel(Base):
    __tablename__ = "permission"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

class RoleModel(Base):
    __tablename__ = "role"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    
    permissions = relationship("PermissionModel", secondary=role_permission_table)

class UserModel(Base):
    # CORREÇÃO 2: Nome da tabela 100% seguro contra palavras reservadas
    __tablename__ = "app_user"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    roles = relationship("RoleModel", secondary=user_role_table)
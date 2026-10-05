
"""
Database seed for RevEla Analyzer.

Creates the default administrator user when the application
database is initialized for the first time.

This operation is idempotent:
- If the administrator already exists, nothing is changed.
- The administrator password is NOT overwritten on subsequent starts.
"""

import logging

from sqlalchemy import select


from app.infrastructure.database.session.database import SessionLocal
from app.infrastructure.database.models.security_model import UserModel
from app.api.security.password import get_password_hash

logger = logging.getLogger(__name__)


DEFAULT_ADMIN_NAME = "Administrador"
DEFAULT_ADMIN_EMAIL = "admin@revela.com"
DEFAULT_ADMIN_PASSWORD = "senha123"


def ensure_default_admin() -> None:
    """
    Ensure that the default administrator exists.

    The function does not modify an existing administrator.
    This prevents the user's password from being reset every
    time RevEla starts.
    """

    db = SessionLocal()

    try:
        stmt = select(UserModel).where(
            UserModel.email == DEFAULT_ADMIN_EMAIL
        )

        existing_user = db.execute(stmt).scalar_one_or_none()

        if existing_user is not None:
            logger.info(
                "Usuário administrador já existe: %s",
                DEFAULT_ADMIN_EMAIL,
            )
            return

        admin_user = UserModel(
            name=DEFAULT_ADMIN_NAME,
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=get_password_hash(DEFAULT_ADMIN_PASSWORD),
            is_active=True,
        )

        db.add(admin_user)
        db.commit()

        logger.info(
            "Usuário administrador criado com sucesso: %s",
            DEFAULT_ADMIN_EMAIL,
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Falha ao criar o usuário administrador."
        )

        raise

    finally:
        db.close()


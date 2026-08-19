from typing import Generator
from app.infrastructure.database.session.database import SessionLocal

def get_db() -> Generator:
    """
    Injeção de dependência para rotas do FastAPI.
    Abre uma sessão com o banco e garante que ela será fechada após a requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Criação do Engine do PostgreSQL
engine = create_engine(
    settings.database_url,
    echo=(settings.app_env == "development"), # Loga as queries SQL apenas em dev
    pool_pre_ping=True
)

# Fábrica de Sessões para injetar nos Repositórios
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def get_db_session():
    """Dependência para obter a sessão do banco (útil no FastAPI ou nos Services)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
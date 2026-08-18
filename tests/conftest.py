import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings

@pytest.fixture(scope="session")
def db_engine():
    """Cria a engine do banco uma única vez para a sessão de testes."""
    engine = create_engine(settings.database_url)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fornece uma sessão limpa para cada teste e faz rollback no final."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
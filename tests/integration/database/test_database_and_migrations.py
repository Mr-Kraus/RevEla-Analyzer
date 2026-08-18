import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timezone

# Importações do Alembic para rodar migrations via código
from alembic.config import Config
from alembic import command

from config.settings import settings
from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel

# Configuração do Alembic
alembic_cfg = Config("alembic.ini")

@pytest.fixture(scope="module")
def db_engine():
    """Cria a engine apontando para o banco de dados configurado no .env"""
    engine = create_engine(settings.database_url)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Fornece uma sessão transacional que é desfeita (rollback) após o teste."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

def test_cp14_migrations_upgrade_downgrade_reproducibility():
    """
    CHECKPOINT 14: Testa se o banco consegue ir do zero ao HEAD,
    fazer downgrade completo e subir novamente sem corromper o estado.
    """
    # 1. Garante que o banco está no HEAD (estrutura atual)
    command.upgrade(alembic_cfg, "head")
    
    # 2. Faz o downgrade completo (derruba todas as tabelas)
    command.downgrade(alembic_cfg, "base")
    
    # 3. Faz o upgrade novamente para provar reprodutibilidade
    command.upgrade(alembic_cfg, "head")
    
    assert True

def test_cp13_database_constraints_and_foreign_keys(db_session):
    """
    CHECKPOINT 13: Testa se as constraints de Foreign Key e integridade
    foram aplicadas corretamente no PostgreSQL.
    """
    # Garante que as migrations estão aplicadas
    command.upgrade(alembic_cfg, "head")
    
    # Tenta inserir uma SimulationRun órfã (com case_id inexistente)
    orphan_simulation = SimulationRunModel(
        id=uuid.uuid4(),
        case_id=uuid.uuid4(), # ID falso, não existe na tabela Case
        analysis_type="STA",
        imported_at=datetime.now(timezone.utc)  # <--- CORREÇÃO: Satisfaz o NOT NULL para forçar o erro de FK
    )
    
    db_session.add(orphan_simulation)
    
    # O PostgreSQL DEVE rejeitar essa inserção por causa da Foreign Key.
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
        
    # Verifica o erro pela classe nativa do psycopg ou pela tradução em português
    error_msg = str(exc_info.value).lower()
    assert "foreignkeyviolation" in error_msg or "chave estrangeira" in error_msg
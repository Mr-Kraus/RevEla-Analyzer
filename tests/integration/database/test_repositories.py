import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.domain.entities.case import Case
from app.domain.entities.source_file import SourceFile
from app.domain.enums.case_status import CaseStatus
from app.infrastructure.database.repositories.postgres_case_repository import PostgresCaseRepository
from app.infrastructure.database.repositories.postgres_source_file_repository import PostgresSourceFileRepository
from datetime import datetime, timezone

def test_case_repository_crud(db_session: Session):
    """Testa Create, Get, Update e Ausência no PostgresCaseRepository."""
    repo = PostgresCaseRepository(db_session)
    
    # 1. Teste de Ausência
    assert repo.get_by_id(uuid4()) is None

    # 2. Teste de Criação (Create)
    new_case = Case(
        id=uuid4(),
        external_name="C01_Test",
        display_name="Caso Teste",
        source_path="/caminho/teste"
    )
    saved_case = repo.save(new_case)
    assert saved_case.id == new_case.id
    assert saved_case.status == CaseStatus.DISCOVERED

    # 3. Teste de Leitura (Get)
    fetched_case = repo.get_by_id(new_case.id)
    assert fetched_case is not None
    assert fetched_case.external_name == "C01_Test"

    # 4. Teste de Atualização (Update)
    fetched_case.status = CaseStatus.READY
    updated_case = repo.save(fetched_case)
    assert updated_case.status == CaseStatus.READY

def test_source_file_repository_relationship(db_session: Session):
    """Testa a criação de um SourceFile atrelado a um Case (Relacionamento)."""
    case_repo = PostgresCaseRepository(db_session)
    sf_repo = PostgresSourceFileRepository(db_session)

    # Cria o Caso pai
    case = Case(id=uuid4(), external_name="C02_Test", display_name="C02", source_path="/caminho")
    case_repo.save(case)

    # Cria o Arquivo vinculado
    sf = SourceFile(
        id=uuid4(),
        case_id=case.id,
        path="/caminho/arquivo.csv",
        relative_path="arquivo.csv",
        filename="arquivo.csv",
        extension="csv",
        size=1024,
        modified_at=datetime.now(timezone.utc),
        sha256="abc123hash",
        dataset_code="TEMPLATE_SYSTEM",
        status="REGISTERED"
    )
    saved_sf = sf_repo.save(sf)
    
    assert saved_sf.id == sf.id
    
    # Testa a listagem por caso
    files_in_case = sf_repo.list_by_case(case.id)
    assert len(files_in_case) == 1
    assert files_in_case[0].filename == "arquivo.csv"
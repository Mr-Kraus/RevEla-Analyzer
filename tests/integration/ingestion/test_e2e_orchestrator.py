import pytest
from pathlib import Path

from app.application.services.case_ingestion_orchestrator import CaseIngestionOrchestrator
from app.application.use_cases.discover_case_use_case import DiscoverCaseUseCase
from app.application.use_cases.validate_case_use_case import ValidateCaseUseCase
from app.application.use_cases.register_case_use_case import RegisterCaseUseCase
from app.application.use_cases.register_source_files_use_case import RegisterSourceFilesUseCase

from app.ingestion.discovery.case_discovery import CaseDiscovery
from app.ingestion.validators.case_validator import CaseValidator
from app.ingestion.registry.dataset_registry import DatasetRegistry
from app.ingestion.registry.source_file_registrar import SourceFileRegistrar

from app.infrastructure.database.repositories.postgres_case_repository import PostgresCaseRepository
from app.infrastructure.database.repositories.postgres_source_file_repository import PostgresSourceFileRepository

GOLDEN_CASE_PATH = Path("tests/fixtures/C01")

def test_e2e_case_ingestion_with_real_db(db_session):
    """Garante que o orquestrador consegue ingerir um caso real e persistir no banco."""
    if not GOLDEN_CASE_PATH.exists():
        pytest.skip("Golden Case não encontrado em tests/fixtures/C01.")

    # 1. Inicializa dependências de Infra/Banco
    case_repo = PostgresCaseRepository(db_session)
    sf_repo = PostgresSourceFileRepository(db_session)

    # 2. Inicializa dependências de Ingestion (Serviços)
    registry = DatasetRegistry()
    discovery_svc = CaseDiscovery()
    validator_svc = CaseValidator(registry)
    registrar_svc = SourceFileRegistrar(registry)

    # 3. Inicializa dependências de Application (Use Cases)
    discover_uc = DiscoverCaseUseCase(discovery_svc)
    validate_uc = ValidateCaseUseCase(validator_svc)
    reg_case_uc = RegisterCaseUseCase(case_repo)
    reg_sf_uc = RegisterSourceFilesUseCase(sf_repo, registrar_svc)

    # 4. Monta o Orquestrador
    orchestrator = CaseIngestionOrchestrator(
        discover_use_case=discover_uc,
        validate_use_case=validate_uc,
        register_case_use_case=reg_case_uc,
        register_source_files_use_case=reg_sf_uc,
        session=db_session
    )

    # 5. EXECUÇÃO
    case_dto, report = orchestrator.process(target_path=GOLDEN_CASE_PATH)

    # 6. ASSERÇÕES
    assert report.is_valid is True
    assert case_dto.external_name == "C01"

    # Confirma se realmente foi para o banco de dados
    saved_case = case_repo.get_by_external_name("C01")
    assert saved_case is not None

    saved_files = sf_repo.list_by_case(saved_case.id)
    assert len(saved_files) > 0
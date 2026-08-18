import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from pathlib import Path
from datetime import datetime, timezone

from app.application.use_cases.discover_case_use_case import DiscoverCaseUseCase
from app.application.use_cases.register_case_use_case import RegisterCaseUseCase
from app.application.use_cases.register_source_files_use_case import RegisterSourceFilesUseCase
from app.domain.entities.case import Case
from app.ingestion.discovery.case_candidate import CaseCandidate

def test_discover_case_use_case():
    """Garante que o Use Case chama o serviço de Discovery corretamente."""
    mock_discovery_service = MagicMock()
    candidate = CaseCandidate(root_path=Path("dummy"), case_name="Dummy")
    mock_discovery_service.discover.return_value = candidate

    use_case = DiscoverCaseUseCase(mock_discovery_service)
    result = use_case.execute(Path("/dummy/path"))

    assert result == candidate
    mock_discovery_service.discover.assert_called_once()

def test_register_case_use_case():
    """Garante que o Use Case cria a Entidade e retorna o DTO corretamente."""
    mock_case_repo = MagicMock()
    
    # 1. Configura a verificação de Idempotência: Simula que o caso NÃO existe ainda
    mock_case_repo.get_by_external_name.return_value = None

    # 2. O mock de salvamento retorna exatamente o que recebeu
    mock_case_repo.save.side_effect = lambda case: case

    use_case = RegisterCaseUseCase(mock_case_repo)
    dto = use_case.execute(external_name="C01", source_path="/path", display_name="Meu Caso")

    assert dto.external_name == "C01"
    assert dto.display_name == "Meu Caso"
    mock_case_repo.get_by_external_name.assert_called_once_with("C01")
    mock_case_repo.save.assert_called_once()

def test_register_source_files_use_case():
    """Garante que o Use Case gera as entidades via Registrar e persiste via Repository."""
    mock_sf_repo = MagicMock()
    mock_registrar = MagicMock()

    mock_file = MagicMock()
    mock_file.id = uuid4()
    mock_file.case_id = uuid4()
    mock_file.filename = "Template.csv"
    mock_file.extension = "csv"
    mock_file.size = 1024
    mock_file.modified_at = datetime.now(timezone.utc)
    mock_file.dataset_code = "TEMPLATE_SYSTEM"
    mock_file.status = "REGISTERED"
    mock_file.sha256 = "abc123fakhash456" 

    mock_registrar.register_candidate_files.return_value = [mock_file]
    
    # 1. Configura a verificação de Idempotência: Simula que o arquivo NÃO existe no banco
    mock_sf_repo.get_by_hash.return_value = None

    # 2. Retorna a própria entidade no momento do save
    mock_sf_repo.save.side_effect = lambda sf: sf

    use_case = RegisterSourceFilesUseCase(mock_sf_repo, mock_registrar)
    
    candidate = CaseCandidate(root_path=Path("dummy"), case_name="Dummy")
    dtos = use_case.execute(candidate, mock_file.case_id)

    assert len(dtos) == 1
    assert dtos[0].filename == "Template.csv"
    mock_sf_repo.get_by_hash.assert_called_once_with("abc123fakhash456")
    mock_sf_repo.save.assert_called_once()
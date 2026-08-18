import pytest
from unittest.mock import MagicMock
# IMPORT CORRIGIDO PARA O NOVO CAMINHO:
from app.application.services.case_ingestion_orchestrator import CaseIngestionOrchestrator
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.ingestion.validators.validation_report import ValidationReport
from app.domain.exceptions.base_exceptions import ValidationError


def test_orchestrator_rollback_on_validation_failure(tmp_path):
    """Garante que o orquestrador acione o rollback se a validação falhar."""
    mock_discover = MagicMock()
    mock_validate = MagicMock()
    mock_register_case = MagicMock()
    mock_register_files = MagicMock()
    mock_session = MagicMock()

    candidate = CaseCandidate(root_path=tmp_path, case_name="Caso_Invalido")
    mock_discover.execute.return_value = candidate

    invalid_report = ValidationReport(is_valid=False, errors=["Template System.csv ausente"])
    mock_validate.execute.return_value = invalid_report

    orchestrator = CaseIngestionOrchestrator(
        discover_use_case=mock_discover,
        validate_use_case=mock_validate,
        register_case_use_case=mock_register_case,
        register_source_files_use_case=mock_register_files,
        session=mock_session
    )

    with pytest.raises(ValidationError):
        orchestrator.process(str(tmp_path))

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
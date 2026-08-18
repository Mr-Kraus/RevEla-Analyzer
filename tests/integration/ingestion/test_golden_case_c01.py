import pytest
from pathlib import Path

from app.ingestion.discovery.case_discovery import CaseDiscovery
from app.ingestion.validators.case_validator import CaseValidator
from app.ingestion.registry.dataset_registry import DatasetRegistry

GOLDEN_CASE_PATH = Path("tests/fixtures/C01")

def test_c01_golden_case_discovery_and_validation():
    """
    CHECKPOINT 17 e 18: Valida a leitura da pasta real do C01.
    Garante a presença explícita dos datasets obrigatórios exigidos no M01.
    """
    if not GOLDEN_CASE_PATH.exists():
        pytest.skip(f"Golden Case não encontrado em {GOLDEN_CASE_PATH}.")

    registry = DatasetRegistry()

    # 1. Discovery
    discovery = CaseDiscovery()
    candidate = discovery.discover(GOLDEN_CASE_PATH)
    assert not candidate.has_errors(), f"Erros no Discovery: {candidate.errors}"

    # 2. Validation utilizando o Registry
    validator = CaseValidator(registry)
    report = validator.validate(candidate)
    assert report.is_valid is True, f"Erros de Validação no C01: {report.errors}"

    # 3. Verificação explícita dos Datasets Obrigatórios exigidos no M01
    found_codes = set()
    for file_path in candidate.detected_templates + candidate.detected_result_files:
        definition = registry.get_definition_for_file(file_path.name)
        if definition:
            found_codes.add(definition.dataset_code)

    required_codes = registry.get_all_required_codes()
    for req_code in required_codes:
        assert req_code in found_codes, f"Dataset obrigatório '{req_code}' não foi identificado na pasta do C01"
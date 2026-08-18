import pytest
from pathlib import Path
from app.ingestion.discovery.case_discovery import CaseDiscovery

def test_discovery_valid_case_structure(tmp_path):
    """Simula a pasta do C01 e verifica se o Discovery acha os arquivos."""
    # 1. Setup da pasta simulada na memória (Golden Case Mock)
    case_dir = tmp_path / "C01_Golden_Case"
    case_dir.mkdir()
    (case_dir / "Template System.csv").touch()
    (case_dir / "Template Settings.csv").touch()

    results_dir = case_dir / "Results_STA_STR_1%"
    results_dir.mkdir()
    (results_dir / "Final Reliability Indices.csv").touch()
    (results_dir / "Generation - annual.csv").touch()

    # 2. Execução
    discovery = CaseDiscovery()
    candidate = discovery.discover(case_dir)

    # 3. Asserções (Validação)
    assert not candidate.has_errors()
    assert candidate.case_name == "C01_Golden_Case"
    assert len(candidate.detected_templates) == 2
    assert len(candidate.detected_result_directories) == 1
    assert len(candidate.detected_result_files) == 2

def test_discovery_invalid_directory():
    """Garante que o sistema reporta erro se a pasta não existir."""
    discovery = CaseDiscovery()
    candidate = discovery.discover(Path("/caminho/ficticio/inexistente"))

    assert candidate.has_errors()
    assert "não existe" in candidate.errors[0]
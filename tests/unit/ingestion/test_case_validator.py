import pytest
from pathlib import Path
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.ingestion.validators.case_validator import CaseValidator
from app.ingestion.registry.dataset_registry import DatasetRegistry

def test_validator_success_valid_case(tmp_path):
    """Garante que um caso com estrutura completa seja considerado válido."""
    case_dir = tmp_path / "C01_Valid"
    case_dir.mkdir()

    # Cria os 3 arquivos obrigatórios exigidos pelo Registry no M01
    sys_file = case_dir / "Template System.csv"
    sys_file.write_text("dados")
    
    cfg_file = case_dir / "Simulation Config.csv"
    cfg_file.write_text("dados")

    results_dir = case_dir / "Results_STA"
    results_dir.mkdir()
    rel_file = results_dir / "Final Reliability Indices.csv"
    rel_file.write_text("dados")

    candidate = CaseCandidate(root_path=case_dir, case_name="C01_Valid")
    candidate.detected_templates.extend([sys_file, cfg_file])
    candidate.detected_result_directories.append(results_dir)
    candidate.detected_result_files.append(rel_file)

    # Agora passamos o registry para o Validator!
    registry = DatasetRegistry()
    validator = CaseValidator(registry)
    report = validator.validate(candidate)

    assert report.is_valid is True, f"Falhou com os erros: {report.errors}"
    assert len(report.errors) == 0

def test_validator_fails_missing_system_template(tmp_path):
    """Garante que a ausência de datasets obrigatórios invalide o caso."""
    case_dir = tmp_path / "C02_Incomplete"
    case_dir.mkdir()

    results_dir = case_dir / "Results_STA"
    results_dir.mkdir()

    candidate = CaseCandidate(root_path=case_dir, case_name="C02_Incomplete")
    candidate.detected_result_directories.append(results_dir)

    registry = DatasetRegistry()
    validator = CaseValidator(registry)
    report = validator.validate(candidate)

    assert report.is_valid is False
    assert len(report.errors) > 0

def test_validator_detects_empty_files(tmp_path):
    """Garante que arquivos de 0 bytes gerem avisos e não sejam contabilizados."""
    case_dir = tmp_path / "C03_Empty"
    case_dir.mkdir()

    system_file = case_dir / "Template System.csv"
    system_file.touch() # Cria arquivo vazio (0 bytes)

    results_dir = case_dir / "Results_STA"
    results_dir.mkdir()

    candidate = CaseCandidate(root_path=case_dir, case_name="C03_Empty")
    candidate.detected_templates.append(system_file)
    candidate.detected_result_directories.append(results_dir)

    registry = DatasetRegistry()
    validator = CaseValidator(registry)
    report = validator.validate(candidate)

    # O arquivo vazio é ignorado, logo o Validator vai reclamar que o Template System está ausente
    assert report.is_valid is False 
    assert len(report.warnings) > 0
    assert system_file in report.unsupported_files
import pytest
from app.ingestion.registry.dataset_registry import DatasetRegistry
from app.ingestion.registry.dataset_definition import DatasetDefinition

def test_registry_initializes_with_core_datasets():
    """Garante que os arquivos vitais já nascem cadastrados no sistema."""
    registry = DatasetRegistry()
    codes = registry.get_all_required_codes()
    assert "TEMPLATE_SYSTEM" in codes
    assert "SIMULATION_CONFIG" in codes
    assert "FINAL_RELIABILITY_INDICES" in codes

def test_registry_matches_filename_pattern():
    """Garante que o fnmatch detecta os nomes exatos ou com wildcards."""
    registry = DatasetRegistry()
    definition = registry.get_definition_for_file("Template System.csv")
    assert definition is not None
    assert definition.dataset_code == "TEMPLATE_SYSTEM"

def test_registry_returns_none_for_unknown_file():
    """Garante que arquivos inúteis não sejam catalogados."""
    registry = DatasetRegistry()
    definition = registry.get_definition_for_file("relatorio_aleatorio.txt")
    assert definition is None
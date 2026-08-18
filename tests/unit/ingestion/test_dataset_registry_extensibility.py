import pytest
from app.ingestion.registry.dataset_registry import DatasetRegistry
from app.ingestion.registry.dataset_definition import DatasetDefinition

def test_registry_can_be_extended_without_modifying_core():
    """Prova que novos padrões de arquivos podem ser adicionados dinamicamente."""
    registry = DatasetRegistry()
    
    # Simula a adição de um novo dataset de versão futura do ReLeVa
    nova_definicao = DatasetDefinition(
        dataset_code="NEW_WIND_UNCERTAINTY",
        filename_pattern="Wind_Uncertainty_*.csv",
        dataset_family="Uncertainty",
        dataset_type="RESULT",
        required=False,
        priority=99,
        parser_identifier="NewWindParser"
    )
    
    registry.register(nova_definicao)
    
    # Verifica se o sistema reconhece o novo arquivo sem hardcode
    match = registry.get_definition_for_file("Wind_Uncertainty_2026.csv")
    
    assert match is not None
    assert match.dataset_code == "NEW_WIND_UNCERTAINTY"
    assert match.parser_identifier == "NewWindParser"
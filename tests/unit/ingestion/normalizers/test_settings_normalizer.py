import pytest
from app.ingestion.parsers.raw_dtos import RawSettingsDTO
from app.ingestion.normalizers.settings_normalizer import SettingsNormalizer

def test_settings_normalizer_maps_correct_fields():
    """Garante que o normalizador mapeia as chaves do ReLeVa para as propriedades do Domínio."""
    
    # Simula o dado bruto cuspido pelo nosso TemplateSettingsParser
    raw_dto = RawSettingsDTO(
        parameters={
            "NUM_MAX_YEARS": "10000", # String proposital para testar o cast para int
            "ANALYSIS_TYPE": "STA",
            "SYST_REP": "STR",
            "LIXO_IRRELEVANTE": "IGNORAR"
        }
    )
    
    normalizer = SettingsNormalizer()
    result = normalizer.normalize(raw_dto)
    
    # Asserções
    assert result["simulated_years"] == 10000  # Converteu para Inteiro
    assert result["analysis_type"] == "STA"
    assert result["system_representation"] == "STR"
    
    # O campo irrelevante não deve estar no resultado final
    assert "LIXO_IRRELEVANTE" not in result
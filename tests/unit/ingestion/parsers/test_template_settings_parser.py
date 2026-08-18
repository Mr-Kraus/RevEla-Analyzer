import pytest
from pathlib import Path
from app.ingestion.parsers.template_settings_parser import TemplateSettingsParser

def test_template_settings_parser_extracts_key_values(tmp_path):
    """Garante que o parser lê o padrão do ReLeVa ignorando os ; extras."""
    
    # Simula o texto EXATO que você colou da engenharia reversa
    releva_mock_content = """NUM_MAX_YEARS;10000;;;
ANALYSIS_TYPE;STA;;;
SAME_YEAR;false;;;
CE_ALFA;0.99;;;
"""
    mock_file = tmp_path / "Template Settings.csv"
    mock_file.write_text(releva_mock_content, encoding="utf-8")
    
    parser = TemplateSettingsParser()
    raw_dto = parser.parse(mock_file)
    
    # Asserções para garantir que ele limpou o lixo e inferiu tipos básicos
    assert raw_dto.parameters["NUM_MAX_YEARS"] == 10000
    assert raw_dto.parameters["ANALYSIS_TYPE"] == "STA"
    assert raw_dto.parameters["SAME_YEAR"] is False
    assert raw_dto.parameters["CE_ALFA"] == 0.99
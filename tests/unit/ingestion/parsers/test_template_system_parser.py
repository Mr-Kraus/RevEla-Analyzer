import pytest
from pathlib import Path
from app.ingestion.parsers.template_system_parser import TemplateSystemParser

def test_template_system_parser_state_machine(tmp_path):
    """
    Testa a capacidade da máquina de estados ler os blocos estilo C++
    e resolver problemas como colunas com nomes duplicados (VOLTAGE).
    """
    
    # O 'r' antes das aspas indica 'Raw String', impedindo o aviso de Syntax do '\V'
    releva_mock_content = r"""(27-04-2026) Representação Caso Base_TAP_on;;;;;;;;;;;;;;;;;;;;
<CLGERA>;;;;;;;;;;;;;;;;;;;;
2;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;
CLAS;NAME;FRATE;MTTR;;;;;;;;;
;;(Occ./Year);hours;;;;;;;;;
<VAL>;;;;;;;;;;;;;;;;;;;;
1;GTSA I - Hyundai;1.5806;43.4498;;;;;;;;;
2;GTSA II - ABC;1.5806;43.4498;;;;;;;;;
<\VAL>;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;
<BARRAS>;;;;;;;;;;;;;;;;;;;;
2;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;
ID;NAME;SLACK;VOLTAGE;VOLTAGE;VOLTAGE;REGION;;;;;;;;;
;;;pu;kV;Degress;;;;;;;;;;;;
<VAL>;;;;;;;;;;;;;;;;;;;;
1;PC1 S TOME;0;1;6;-1.4;1;;;;;;;;;
2;PC2 V S AMAR;0;1;30;-0.25;2;;;;;;;;;
<\VAL>;;;;;;;;;;;;;;;;;;;;
"""
    mock_file = tmp_path / "Template System.csv"
    mock_file.write_text(releva_mock_content, encoding="utf-8")
    
    parser = TemplateSystemParser()
    raw_dto = parser.parse(mock_file)
    
    # 1. Deve ter encontrado exatamente os 2 blocos
    assert len(raw_dto.blocks) == 2
    assert "CLGERA" in raw_dto.blocks
    assert "BARRAS" in raw_dto.blocks
    
    # 2. Testa o bloco CLGERA
    clgera = raw_dto.blocks["CLGERA"]
    assert len(clgera.records) == 2
    assert clgera.records[0]["NAME"] == "GTSA I - Hyundai"
    assert clgera.records[1]["FRATE"] == "1.5806"
    
    # 3. Testa o bloco BARRAS e as colunas duplicadas (VOLTAGE)
    barras = raw_dto.blocks["BARRAS"]
    assert len(barras.records) == 2
    assert barras.records[0]["VOLTAGE"] == "1"      # pu
    assert barras.records[0]["VOLTAGE_2"] == "6"    # kV
    assert barras.records[0]["VOLTAGE_3"] == "-1.4" # Degress
    assert barras.records[0]["NAME"] == "PC1 S TOME"
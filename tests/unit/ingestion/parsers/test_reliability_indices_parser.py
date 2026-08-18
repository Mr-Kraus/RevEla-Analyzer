import pytest
from pathlib import Path
from app.ingestion.parsers.reliability_indices_parser import ReliabilityIndicesParser

def test_reliability_indices_parser_extracts_anchors_and_cleans_nan(tmp_path):
    """
    Testa se o parser acha os blocos (Global, Bus) 
    e substitui adequadamente a flag '-nan(ind)'.
    """
    
    # Texto EXATO extraído da engenharia reversa
    releva_mock_content = """Simulated years;100
Simulation Time;00:01:56.02 

Total Global Indices:;;;;;95.00% Confidence (left);95.00% Confidence (right)
LOLP (prob.);=;1.7231251677990434E-02;1.3357E+00%;;1.6780053117045640E-02;1.7682450238935228E-02
LOLE (h/year);=;150.945765;1.3357%;;146.993265;154.898264

Main System Indices by Bus:
;LOLP (prob.);LOLE (h/year);EPNS (MW);EENS (MWh/year);LOLF (occ./year);LOLD (h/occ.);LOLC ($/year);
Bus 4%PC-4 GUEGUE;2.4783580534459951E-06;0.021710;0.000001;0.00;0.020000;1.085521;7.180086;
Bus 1%PC1 S TOME;0.0000000000000000E+00;0.000000;0.000000;0.00;0.000000;-nan(ind);0.000000;
"""
    mock_file = tmp_path / "Final Reliability Indices.csv"
    mock_file.write_text(releva_mock_content, encoding="utf-8")
    
    parser = ReliabilityIndicesParser()
    raw_dto = parser.parse(mock_file)
    
    # 1. Âncoras encontradas?
    assert "TOTAL_GLOBAL" in raw_dto.blocks
    assert "BY_BUS" in raw_dto.blocks
    
    # 2. Global possui os resultados?
    global_data = raw_dto.blocks["TOTAL_GLOBAL"]
    assert global_data[0][0] == "LOLP (prob.)"
    assert global_data[1][2] == "150.945765"
    
    # 3. Limpeza Matemática do C++ (-nan(ind) virou NaN?)
    bus_data = raw_dto.blocks["BY_BUS"]
    # A linha do "Bus 1%PC1" é o índice 2 (índice 0 é cabeçalho, índice 1 é o Bus 4)
    # A coluna do "LOLD" é o índice 6 na string (depois de dar split por ';')
    assert bus_data[2][6] == "NaN"
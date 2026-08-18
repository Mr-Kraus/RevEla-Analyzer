import pytest
import math
from app.ingestion.parsers.raw_dtos import RawReliabilityIndicesDTO
from app.ingestion.normalizers.reliability_indices_normalizer import ReliabilityIndicesNormalizer

def test_reliability_indices_normalizer_extracts_metrics():
    """Garante que o normalizador mapeia os valores globais e por barra, lidando com NaN."""
    
    # Simula o DTO gerado pelo ReliabilityIndicesParser
    raw_dto = RawReliabilityIndicesDTO(
        blocks={
            "TOTAL_GLOBAL": [
                ["LOLP (prob.)", "=", "1.7231E-02"],
                ["LOLE (h/year)", "=", "150.945"]
            ],
            "BY_BUS": [
                ["", "LOLP", "LOLE", "EPNS", "EENS", "LOLF", "LOLD", "LOLC"], # Header
                ["Bus 4%PC-4 GUEGUE", "2.478E-06", "0.021", "0.01", "0.0", "0.02", "1.08", "7.18"],
                ["Bus 1%PC1 S TOME", "0.0", "0.0", "0.0", "0.0", "0.0", "NaN", "0.0"] # O temido NaN
            ]
        }
    )
    
    normalizer = ReliabilityIndicesNormalizer()
    results = normalizer.normalize(raw_dto)
    
    # 1. Verifica Global Indices
    global_idx = results["global_indices"]
    assert global_idx["lolp"] == 0.017231
    assert global_idx["lole"] == 150.945
    
    # 2. Verifica Bus Indices
    bus_idx = results["bus_indices"]
    assert len(bus_idx) == 2
    
    # Barramento 4
    assert bus_idx[0]["bus_external_id"] == "4"
    assert bus_idx[0]["lolp"] == 2.478e-06
    assert bus_idx[0]["lole"] == 0.021
    
    # Barramento 1 (Testando o math.nan)
    assert bus_idx[1]["bus_external_id"] == "1"
    assert math.isnan(bus_idx[1]["lold"])
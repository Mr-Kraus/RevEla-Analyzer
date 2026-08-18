import pytest
from app.ingestion.parsers.raw_dtos import RawSystemDTO, RawSystemBlockDTO
from app.ingestion.normalizers.system_normalizer import SystemNormalizer

def test_system_normalizer_extracts_buses_and_infers_regions():
    """Garante que strings viram floats, e que as regiões são extraídas a partir das barras."""
    
    # Simula o DTO bruto gerado pelo TemplateSystemParser
    raw_dto = RawSystemDTO(
        blocks={
            "CLGERA": RawSystemBlockDTO(
                block_name="CLGERA",
                headers=["CLAS", "NAME", "FRATE", "MTTR", "RATED POW."],
                records=[
                    {"CLAS": "1", "NAME": "GTSA I - Hyundai", "FRATE": "1.5806", "MTTR": "43.4498", "RATED POW.": "1.7"}
                ]
            ),
            "BARRAS": RawSystemBlockDTO(
                block_name="BARRAS",
                headers=["ID", "NAME", "SLACK", "VOLTAGE", "VOLTAGE_2", "VOLTAGE_3", "REGION"],
                records=[
                    {"ID": "1", "NAME": "PC1 S TOME", "VOLTAGE_2": "6", "REGION": "1"},
                    {"ID": "2", "NAME": "PC2 V S AMAR", "VOLTAGE_2": "30", "REGION": "2"},
                    {"ID": "3", "NAME": "PC3 TRINDAD", "VOLTAGE_2": "30", "REGION": "1"} # Mesma região do PC1
                ]
            )
        }
    )
    
    normalizer = SystemNormalizer()
    topology = normalizer.normalize(raw_dto)
    
    # 1. Verifica Classes de Geração
    assert len(topology["generation_classes"]) == 1
    assert topology["generation_classes"][0]["failure_rate_percent"] == 1.5806 # Virou float!
    assert topology["generation_classes"][0]["nominal_capacity_mw"] == 1.7
    
    # 2. Verifica Barras
    assert len(topology["buses"]) == 3
    assert topology["buses"][0]["voltage_kv"] == 6.0 # Virou float!
    assert topology["buses"][1]["voltage_kv"] == 30.0
    
    # 3. Verifica Inferência de Regiões (Foram declaradas 3 barras, mas só 2 regiões únicas: 1 e 2)
    assert len(topology["regions"]) == 2
    reg_ids = [r["external_id"] for r in topology["regions"]]
    assert "1" in reg_ids
    assert "2" in reg_ids
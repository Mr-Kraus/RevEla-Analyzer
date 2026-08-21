import logging
from typing import Dict, Any, List
from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawSystemDTO

logger = logging.getLogger(__name__)

class SystemNormalizer(BaseNormalizer):
    def normalize(self, raw_data: RawSystemDTO, **kwargs) -> Dict[str, Any]:
        logger.debug("Iniciando normalização da Topologia do Sistema...")
        
        canonical_topology = {
            "regions": [],
            "buses": [],
            "generation_classes": [],
            "transmission_lines": [],
            "transformers": [],
            # INJETA A CARGA AQUI PARA O USE CASE / MAPPER LER:
            "nominal_load_mw": getattr(raw_data, 'carga_nominal', 0.0) 
        }

        blocks = raw_data.blocks
        unique_regions = set()

        if "CLGERA" in blocks:
            for record in blocks["CLGERA"].records:
                try:
                    canonical_topology["generation_classes"].append({
                        "external_id": str(record.get("CLAS", "")).strip(),
                        "name": str(record.get("NAME", "")).strip(),
                        "failure_rate_percent": self._safe_float(record.get("FRATE")),
                        "repair_time_hours": self._safe_float(record.get("MTTR")),
                        "nominal_capacity_mw": self._safe_float(record.get("RATED POW."))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar classe de geração: {e}")

        if "BARRAS" in blocks:
            for record in blocks["BARRAS"].records:
                try:
                    region_ext_id = str(record.get("REGION", "")).strip()
                    if region_ext_id and region_ext_id != "0":
                        unique_regions.add(region_ext_id)

                    canonical_topology["buses"].append({
                        "external_id": str(record.get("ID", "")).strip(),
                        "name": str(record.get("NAME", "")).strip(),
                        "region_external_id": region_ext_id,
                        "voltage_kv": self._safe_float(record.get("VOLTAGE_2"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar barra: {e}")

        if "LINHAS" in blocks:
            for record in blocks["LINHAS"].records:
                try:
                    canonical_topology["transmission_lines"].append({
                        "external_id": str(record.get("ID", "")).strip(),
                        "name": str(record.get("NAME", "")).strip(),
                        "from_bus_ext_id": str(record.get("FROM BUS", "")).strip(),
                        "to_bus_ext_id": str(record.get("TO BUS", "")).strip(),
                        "r_pu": self._safe_float(record.get("R")),
                        "x_pu": self._safe_float(record.get("X")),
                        "capacity_mva": self._safe_float(record.get("CAP.")),
                        "failure_rate": self._safe_float(record.get("FRATE")),
                        "repair_time": self._safe_float(record.get("MTTR"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar linha: {e}")

        if "TRAFOS" in blocks:
            for record in blocks["TRAFOS"].records:
                try:
                    canonical_topology["transformers"].append({
                        "external_id": str(record.get("ID", "")).strip(),
                        "name": str(record.get("NAME", "")).strip(),
                        "from_bus_ext_id": str(record.get("FROM BUS", "")).strip(),
                        "to_bus_ext_id": str(record.get("TO BUS", "")).strip(),
                        "r_pu": self._safe_float(record.get("R")),
                        "x_pu": self._safe_float(record.get("X")),
                        "capacity_mva": self._safe_float(record.get("CAP.")),
                        "failure_rate": self._safe_float(record.get("FRATE")),
                        "repair_time": self._safe_float(record.get("MTTR"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar trafo: {e}")
                    
        for reg_id in unique_regions:
            canonical_topology["regions"].append({
                "external_id": reg_id,
                "name": f"Region {reg_id}"
            })

        logger.info(f"Topologia normalizada: Carga={canonical_topology['nominal_load_mw']} MW")
        return canonical_topology

    def _safe_float(self, value: str) -> float:
        if not value: return 0.0
        try: return float(str(value).replace(',', '.'))
        except ValueError: return 0.0
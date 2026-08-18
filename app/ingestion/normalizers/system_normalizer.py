import logging
from typing import Dict, Any, List
from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawSystemDTO

logger = logging.getLogger(__name__)

class SystemNormalizer(BaseNormalizer):
    """
    Normaliza os blocos brutos do 'Template System.csv'.
    Transforma as strings do parser em dados tipados (float, int) e constrói
    as relações canônicas da topologia elétrica (Regiões, Barras, Geradores, etc).
    """

    def normalize(self, raw_data: RawSystemDTO, **kwargs) -> Dict[str, Any]:
        logger.debug("Iniciando normalização da Topologia do Sistema...")
        
        canonical_topology = {
            "regions": [],
            "buses": [],
            "generation_classes": []
        }

        blocks = raw_data.blocks

        # 1. Normalização de Classes de Geração (<CLGERA>)
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
                    logger.warning(f"Erro ao normalizar classe de geração: {record}. Erro: {e}")

        # 2. Normalização de Barras (<BARRAS>) e Inferência de Regiões
        # No ReLeVa, as Regiões geralmente são deduzidas da coluna REGION nas Barras
        unique_regions = set()
        
        if "BARRAS" in blocks:
            for record in blocks["BARRAS"].records:
                try:
                    region_ext_id = str(record.get("REGION", "")).strip()
                    if region_ext_id and region_ext_id != "0":
                        unique_regions.add(region_ext_id)

                    # Nota: Pelo nosso parser, VOLTAGE_2 é a tensão em kV (a 1ª era pu)
                    canonical_topology["buses"].append({
                        "external_id": str(record.get("ID", "")).strip(),
                        "name": str(record.get("NAME", "")).strip(),
                        "region_external_id": region_ext_id,
                        "voltage_kv": self._safe_float(record.get("VOLTAGE_2"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar barra: {record}. Erro: {e}")

        # M02-F03: Normalização de Linhas de Transmissão (<LINHAS>)
        canonical_topology["transmission_lines"] = []
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
                    logger.warning(f"Erro ao normalizar linha: {record}. Erro: {e}")

        # M02-F03: Normalização de Transformadores (<TRAFOS>)
        canonical_topology["transformers"] = []
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
                    logger.warning(f"Erro ao normalizar trafo: {record}. Erro: {e}")
                    
        # Cria os registros canônicos para as regiões encontradas
        for reg_id in unique_regions:
            canonical_topology["regions"].append({
                "external_id": reg_id,
                "name": f"Region {reg_id}" # O ReLeVa muitas vezes não dá nome, só ID
            })

        logger.info(
            f"Topologia normalizada: {len(canonical_topology['regions'])} regiões, "
            f"{len(canonical_topology['buses'])} barras, "
            f"{len(canonical_topology['generation_classes'])} classes de geração."
        )
        return canonical_topology

    def _safe_float(self, value: str) -> float:
        """Converte string para float com segurança, retornando 0.0 em caso de falha."""
        if not value:
            return 0.0
        try:
            # Substitui vírgula por ponto para evitar erros de locale
            return float(str(value).replace(',', '.'))
        except ValueError:
            return 0.0
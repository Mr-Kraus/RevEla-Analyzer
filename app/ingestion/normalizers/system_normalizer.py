import logging
from typing import Dict, Any, List
from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawSystemDTO

logger = logging.getLogger(__name__)

class SystemNormalizer(BaseNormalizer):
    
    def _get_val(self, record: dict, *possible_keys) -> str:
        """
        Função blindada: Procura o valor no dicionário usando sinônimos 
        e ignorando maiúsculas/minúsculas ou espaços em branco.
        """
        key_map = {k.strip().lower(): k for k in record.keys()}
        for pk in possible_keys:
            if pk.strip().lower() in key_map:
                return str(record[key_map[pk.strip().lower()]]).strip()
        return ""

    def normalize(self, raw_data: RawSystemDTO, **kwargs) -> Dict[str, Any]:
        logger.debug("Iniciando normalização da Topologia do Sistema...")
        
        canonical_topology = {
            "regions": [],
            "buses": [],
            "generator_classes": [], # Catálogo de Máquinas
            "generators": [],        # Instâncias Físicas
            "transmission_lines": [],
            "transformers": [],
            "nominal_load_mw": getattr(raw_data, 'carga_nominal', 0.0) 
        }

        blocks = raw_data.blocks
        unique_regions = set()
        
        # 1. CATÁLOGO DE GERAÇÃO (CLGERA -> generator_classes)
        catalogo_ids = set()
        if "CLGERA" in blocks:
            for record in blocks["CLGERA"].records:
                try:
                    ext_id = self._get_val(record, "CLAS", "CLASS")
                    if not ext_id: continue
                    
                    canonical_topology["generator_classes"].append({
                        "external_id": ext_id,
                        "name": self._get_val(record, "NAME", "NOME"),
                        "failure_rate_percent": self._safe_float(self._get_val(record, "FRATE")),
                        "repair_time_hours": self._safe_float(self._get_val(record, "MTTR")),
                        "nominal_capacity_mw": self._safe_float(self._get_val(record, "RATED POW.", "Pot.Efetiva"))
                    })
                    catalogo_ids.add(ext_id)
                except Exception as e:
                    logger.warning(f"Erro ao normalizar classe de geração: {e}")

        # 2. INSTÂNCIAS DE GERAÇÃO (TERMI, HIDRO, SOLAR... -> generators)
        tecnologias = {
            "TERMI": "TERMI", 
            "HIDRO": "HIDRO", 
            "SOLAR": "SOLAR", 
            "EOLIC": "EOLIC",
            "MINIH": "MINIH",
            "COGER": "COGER",
            "CCOMB": "CCOMB"
        }
        
        for tag_bloco, tec_label in tecnologias.items():
            if tag_bloco in blocks:
                for record in blocks[tag_bloco].records:
                    try:
                        class_id = self._get_val(record, "CLASS", "CLAS")
                        if class_id in catalogo_ids:
                            canonical_topology["generators"].append({
                                "external_id": self._get_val(record, "ID"),
                                "name": self._get_val(record, "NAME", "NOME"),
                                "technology": tec_label,
                                "class_external_id": class_id,
                                "bus_ext_id": self._get_val(record, "BUS") # Captura a barra se existir
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao normalizar instância de geração ({tec_label}): {e}")

        # 3. BARRAS DO SISTEMA
        if "BARRAS" in blocks:
            for record in blocks["BARRAS"].records:
                try:
                    ext_id = self._get_val(record, "ID")
                    if not ext_id: continue

                    region_ext_id = self._get_val(record, "REGION", "REGIAO")
                    if region_ext_id and region_ext_id != "0":
                        unique_regions.add(region_ext_id)

                    canonical_topology["buses"].append({
                        "external_id": ext_id,
                        "name": self._get_val(record, "NAME", "NOME"),
                        "region_external_id": region_ext_id,
                        "voltage_kv": self._safe_float(self._get_val(record, "VOLTAGE_2", "Tensao_2", "Tensao"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar barra: {e}")

        # 4. LINHAS DE TRANSMISSÃO
        if "LINHAS" in blocks:
            for record in blocks["LINHAS"].records:
                try:
                    ext_id = self._get_val(record, "ID")
                    if not ext_id: continue

                    canonical_topology["transmission_lines"].append({
                        "external_id": ext_id,
                        "name": self._get_val(record, "NAME", "NOME"),
                        "from_bus_ext_id": self._get_val(record, "FROM BUS"),
                        "to_bus_ext_id": self._get_val(record, "TO BUS"),
                        "r_pu": self._safe_float(self._get_val(record, "R")),
                        "x_pu": self._safe_float(self._get_val(record, "X")),
                        "capacity_mva": self._safe_float(self._get_val(record, "CAP.", "Capacidade")),
                        "failure_rate": self._safe_float(self._get_val(record, "FRATE", "Frate Perm.", "Frate")),
                        "repair_time": self._safe_float(self._get_val(record, "MTTR"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar linha: {e}")

        # 5. TRANSFORMADORES
        if "TRAFOS" in blocks:
            for record in blocks["TRAFOS"].records:
                try:
                    ext_id = self._get_val(record, "ID")
                    if not ext_id: continue

                    canonical_topology["transformers"].append({
                        "external_id": ext_id,
                        "name": self._get_val(record, "NAME", "NOME"),
                        "from_bus_ext_id": self._get_val(record, "FROM BUS"),
                        "to_bus_ext_id": self._get_val(record, "TO BUS"),
                        "r_pu": self._safe_float(self._get_val(record, "R")),
                        "x_pu": self._safe_float(self._get_val(record, "X")),
                        "capacity_mva": self._safe_float(self._get_val(record, "CAP.", "Capacidade")),
                        "failure_rate": self._safe_float(self._get_val(record, "FRATE", "FRate Perm.", "Frate")),
                        "repair_time": self._safe_float(self._get_val(record, "MTTR"))
                    })
                except Exception as e:
                    logger.warning(f"Erro ao normalizar trafo: {e}")
                    
        # Constrói o array de Regiões
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
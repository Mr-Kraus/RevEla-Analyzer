import logging
from typing import Dict, Any, List
import math

from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawReliabilityIndicesDTO

logger = logging.getLogger(__name__)

class ReliabilityIndicesNormalizer(BaseNormalizer):
    def normalize(self, raw_data: RawReliabilityIndicesDTO, **kwargs) -> Dict[str, Any]:
        logger.debug("Iniciando normalização dos Índices de Confiabilidade...")
        
        canonical_results = {
            "global_indices": {},
            "region_indices": [], # <-- NOVA LISTA PARA REGIÕES
            "bus_indices": [],
            "simulated_years": getattr(raw_data, 'simulated_years', 0)
        }

        blocks = raw_data.blocks

        # --- 1. GLOBAL INDICES ---
        if "TOTAL_GLOBAL" in blocks:
            for row in blocks["TOTAL_GLOBAL"]:
                if len(row) >= 3:
                    metric_name = row[0].strip()
                    value_str = row[2].strip()
                    
                    if "LOLP" in metric_name: canonical_results["global_indices"]["lolp"] = self._safe_float(value_str)
                    elif "LOLE" in metric_name: canonical_results["global_indices"]["lole"] = self._safe_float(value_str)
                    elif "EPNS" in metric_name: canonical_results["global_indices"]["epns"] = self._safe_float(value_str)
                    elif "EENS" in metric_name: canonical_results["global_indices"]["eens"] = self._safe_float(value_str)
                    elif "LOLF" in metric_name: canonical_results["global_indices"]["lolf"] = self._safe_float(value_str)
                    elif "LOLD" in metric_name: canonical_results["global_indices"]["lold"] = self._safe_float(value_str)
                    elif "LOLC" in metric_name: canonical_results["global_indices"]["lolc"] = self._safe_float(value_str)
            
            canonical_results["global_indices"]["confidence_intervals"] = getattr(raw_data, 'confidence_intervals', {})

        # --- 2. REGION INDICES (Leitura Horizontal) ---
        if "BY_REGION" in blocks and len(blocks["BY_REGION"]) > 1:
            region_headers = blocks["BY_REGION"][0]
            
            # Mapeia os índices das colunas onde os nomes das regiões estão
            col_mappings = {}
            for idx, header in enumerate(region_headers):
                clean_header = header.strip()
                if clean_header.startswith("Region"):
                    col_mappings[idx] = clean_header

            # Cria um dicionário temporário para agrupar as métricas por região
            temp_regions = {r_name: {"region_name": r_name} for r_name in col_mappings.values()}

            # Itera sobre as linhas de valores pulando o cabeçalho [1:]
            for row in blocks["BY_REGION"][1:]:
                for col_idx, r_name in col_mappings.items():
                    # No CSV, a estrutura é: [NomeMétrica] [Sinal=] [Valor]
                    # Portanto, se o nome da região está na coluna X, o valor está na coluna X+2
                    if col_idx + 2 < len(row): 
                        metric_name = row[col_idx].strip()
                        val_str = row[col_idx + 2]
                        
                        if "LOLP" in metric_name: temp_regions[r_name]["lolp"] = self._safe_float(val_str)
                        elif "LOLE" in metric_name: temp_regions[r_name]["lole"] = self._safe_float(val_str)
                        elif "EPNS" in metric_name: temp_regions[r_name]["epns"] = self._safe_float(val_str)
                        elif "EENS" in metric_name: temp_regions[r_name]["eens"] = self._safe_float(val_str)
                        elif "LOLF" in metric_name: temp_regions[r_name]["lolf"] = self._safe_float(val_str)
                        elif "LOLD" in metric_name: temp_regions[r_name]["lold"] = self._safe_float(val_str)
                        elif "LOLC" in metric_name: temp_regions[r_name]["lolc"] = self._safe_float(val_str)

            # Transforma de dicionário para lista e anexa nos resultados canônicos
            canonical_results["region_indices"] = list(temp_regions.values())

        # --- 3. BUS INDICES ---
        if "BY_BUS" in blocks:
            for row in blocks["BY_BUS"][1:]:
                if len(row) >= 8:
                    bus_identifier = row[0].strip()
                    bus_ext_id = bus_identifier.split('%')[0].replace("Bus ", "").strip() if "%" in bus_identifier else bus_identifier

                    canonical_results["bus_indices"].append({
                        "bus_external_id": bus_ext_id,
                        "lolp": self._safe_float(row[1]),
                        "lole": self._safe_float(row[2]),
                        "epns": self._safe_float(row[3]),
                        "eens": self._safe_float(row[4]),
                        "lolf": self._safe_float(row[5]),
                        "lold": self._safe_float(row[6]),
                        "lolc": self._safe_float(row[7])
                    })

        logger.info(f"Resultados normalizados com {canonical_results['simulated_years']} anos simulados.")
        logger.info("============== RASTREADOR: NORMALIZER ==============")
        logger.info(f"Regiões extraídas: {len(canonical_results.get('region_indices', []))}")
        for r in canonical_results.get("region_indices", []):
            logger.info(f" -> {r.get('region_name')}: LOLP = {r.get('lolp')}")
        logger.info("====================================================")
        
        return canonical_results
        return canonical_results

    def _safe_float(self, value: str) -> float:
        if not value: return 0.0
        val_clean = value.strip().upper()
        if val_clean == "NAN": return math.nan
        try: return float(value.replace(',', '.'))
        except ValueError: return 0.0
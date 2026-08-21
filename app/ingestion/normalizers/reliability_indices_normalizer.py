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
            "bus_indices": [],
            # INJETA OS ANOS SIMULADOS PARA O USE CASE:
            "simulated_years": getattr(raw_data, 'simulated_years', 0)
        }

        blocks = raw_data.blocks

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
            
            # INJETA OS INTERVALOS DE CONFIANÇA DENTRO DE GLOBAL_INDICES
            canonical_results["global_indices"]["confidence_intervals"] = getattr(raw_data, 'confidence_intervals', {})

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
        return canonical_results

    def _safe_float(self, value: str) -> float:
        if not value: return 0.0
        val_clean = value.strip().upper()
        if val_clean == "NAN": return math.nan
        try: return float(value.replace(',', '.'))
        except ValueError: return 0.0
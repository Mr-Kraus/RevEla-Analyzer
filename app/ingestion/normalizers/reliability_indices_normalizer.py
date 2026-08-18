import logging
from typing import Dict, Any, List
import math

from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawReliabilityIndicesDTO

logger = logging.getLogger(__name__)

class ReliabilityIndicesNormalizer(BaseNormalizer):
    """
    Normaliza os blocos de matrizes brutos do 'Final Reliability Indices.csv'.
    Responsabilidade: Converter matrizes de strings em DTOs canônicos tipados
    para Resultados Globais e Resultados por Barra.
    """

    def normalize(self, raw_data: RawReliabilityIndicesDTO, **kwargs) -> Dict[str, Any]:
        logger.debug("Iniciando normalização dos Índices de Confiabilidade...")
        
        canonical_results = {
            "global_indices": {},
            "bus_indices": []
        }

        blocks = raw_data.blocks

        # 1. Normalização dos Resultados Globais (TOTAL_GLOBAL)
        if "TOTAL_GLOBAL" in blocks:
            global_data = blocks["TOTAL_GLOBAL"]
            # Exemplo de linha: ['LOLP (prob.)', '=', '1.7231251677990434E-02', '1.3357E+00%', '', '1.678...', '1.768...']
            for row in global_data:
                if len(row) >= 3:
                    metric_name = row[0].strip()
                    value_str = row[2].strip()
                    
                    if "LOLP" in metric_name:
                        canonical_results["global_indices"]["lolp"] = self._safe_float(value_str)
                    elif "LOLE" in metric_name:
                        canonical_results["global_indices"]["lole"] = self._safe_float(value_str)
                    elif "EPNS" in metric_name:
                        canonical_results["global_indices"]["epns"] = self._safe_float(value_str)
                    elif "EENS" in metric_name:
                        canonical_results["global_indices"]["eens"] = self._safe_float(value_str)
                    elif "LOLF" in metric_name:
                        canonical_results["global_indices"]["lolf"] = self._safe_float(value_str)
                    elif "LOLD" in metric_name:
                        canonical_results["global_indices"]["lold"] = self._safe_float(value_str)
                    elif "LOLC" in metric_name:
                        canonical_results["global_indices"]["lolc"] = self._safe_float(value_str)

        # 2. Normalização dos Resultados por Barra (BY_BUS)
        if "BY_BUS" in blocks:
            bus_data = blocks["BY_BUS"]
            # A primeira linha (índice 0) é o cabeçalho.
            # Exemplo de dado: ['Bus 4%PC-4 GUEGUE', '2.478E-06', '0.0217', ...]
            for row in bus_data[1:]:
                if len(row) >= 8:
                    bus_identifier = row[0].strip()
                    # Extrair apenas o ID da string 'Bus 4%PC-4 GUEGUE' -> '4'
                    bus_ext_id = ""
                    if "%" in bus_identifier:
                        prefix = bus_identifier.split('%')[0]
                        bus_ext_id = prefix.replace("Bus ", "").strip()
                    else:
                        bus_ext_id = bus_identifier # Fallback caso o formato mude

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

        logger.info(
            f"Resultados normalizados: {len(canonical_results['global_indices'])} métricas globais, "
            f"{len(canonical_results['bus_indices'])} barras."
        )
        return canonical_results

    def _safe_float(self, value: str) -> float:
        """Converte string para float. Se for 'NaN' explícito, retorna float('nan'). Se falhar, retorna 0.0."""
        if not value:
            return 0.0
        val_clean = value.strip().upper()
        if val_clean == "NAN":
            return math.nan
            
        try:
            return float(value.replace(',', '.'))
        except ValueError:
            return 0.0
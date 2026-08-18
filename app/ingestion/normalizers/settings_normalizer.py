import logging
from typing import Dict, Any
from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawSettingsDTO

logger = logging.getLogger(__name__)

class SettingsNormalizer(BaseNormalizer):
    def normalize(self, raw_data: RawSettingsDTO, **kwargs) -> Dict[str, Any]:
        params = raw_data.parameters
        
        normalized_data = {
            "simulated_years": self._safe_int(params.get("NUM_MAX_YEARS")),
            "analysis_type": params.get("ANALYSIS_TYPE"),
            "system_representation": params.get("SYST_REP"),
            "confidence_level": self._safe_float(params.get("CONFIDENCE")),
            # FASE F04: Dicionário embutido para configurações de convergência (JSON)
            "convergence_configuration": {
                "ce_num_samples": self._safe_int(params.get("CE_NUM_SAMPLES")),
                "ce_max_iterations": self._safe_int(params.get("CE_NUM_MAX_ITE")),
                "ce_ro": self._safe_float(params.get("CE_RO")),
                "ce_alfa": self._safe_float(params.get("CE_ALFA")),
                "ce_gamma": self._safe_float(params.get("CE_GAMMA"))
            }
        }
        return normalized_data

    def _safe_int(self, value: Any) -> int:
        try:
            return int(value) if value else 0
        except ValueError:
            return 0
            
    def _safe_float(self, value: Any) -> float:
        try:
            return float(str(value).replace(',', '.')) if value else 0.0
        except ValueError:
            return 0.0
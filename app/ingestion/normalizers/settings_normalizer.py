import logging
from typing import List, Dict, Any
from app.ingestion.normalizers.base_normalizer import BaseNormalizer
from app.ingestion.parsers.raw_dtos import RawSettingsDTO

logger = logging.getLogger(__name__)

class SettingsNormalizer(BaseNormalizer):
    """
    Transforma o DTO bruto de Settings em uma lista de configurações 
    prontas para inserção na tabela (Entity-Attribute-Value).
    """

    def normalize(self, raw_data: RawSettingsDTO, **kwargs) -> List[Dict[str, Any]]:
        logger.debug("Iniciando normalização das Configurações do Sistema...")
        
        normalized_configs = []
        
        # Mapeamento de Ouro: Traduz a sigla do CSV para o nome bonito exigido pela Interface
        important_keys_map = {
            "ANALYSIS_TYPE": "Analysis Type",
            "SYST_REP": "System Representation",
            "COEF_BETA": "Convergence Beta"
        }

        for raw_key, raw_val in raw_data.parameters.items():
            param_name = important_keys_map.get(raw_key, raw_key)
            
            normalized_configs.append({
                "parameter_key": param_name,          
                "parameter_value": str(raw_val),     
                "value_type": type(raw_val).__name__  
            })
            
        logger.info(f"Configurações normalizadas: {len(normalized_configs)} registros prontos para o banco.")
        return normalized_configs
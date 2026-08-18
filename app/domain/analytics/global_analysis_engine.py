from typing import Dict, Any, List, Optional
import uuid
from app.domain.indicators.indicator_catalog import IndicatorCatalog

class GlobalAnalysisEngine:
    """
    Engine responsável pela extração, formatação e validação das análises globais do sistema.
    Suporta a consulta de indicadores globais enriquecidos com metadados do Catálogo de Indicadores.
    """

    @staticmethod
    def process_global_indicators(
        simulation_id: uuid.UUID,
        global_result_model: Any,  # Instância do ReliabilityResultModel
        case_name: str = ""
    ) -> Dict[str, Any]:
        """
        Processa os resultados globais de uma simulação e enriquece com dados do IndicatorCatalog.
        Retorna um dicionário estruturado contendo Valor, Unidade, Categoria, Caso e Simulação.
        """
        if not global_result_model:
            return {
                "simulation_id": simulation_id,
                "case_name": case_name,
                "indicators": {}
            }

        indicators_summary = {}
        target_codes = ["LOLP", "LOLE", "EPNS", "EENS", "LOLF", "LOLD", "LOLC"]

        for code in target_codes:
            attr_name = code.lower()
            if hasattr(global_result_model, attr_name):
                val = getattr(global_result_model, attr_name)
                val_float = float(val) if val is not None else 0.0
                
                # Consulta a definição oficial do Catálogo (M03.2)
                catalog_def = IndicatorCatalog.get(code)
                
                indicators_summary[code] = {
                    "code": code,
                    "name": catalog_def.name,
                    "value": val_float,
                    "unit": catalog_def.unit.value,
                    "category": catalog_def.category.value,
                    "description": catalog_def.description
                }

        return {
            "simulation_id": simulation_id,
            "case_name": case_name,
            "indicators": indicators_summary
        }
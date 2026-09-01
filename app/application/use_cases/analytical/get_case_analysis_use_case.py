import uuid
from typing import Dict
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.domain.analytics.ranking_engine import RankingEngine
from app.application.dto.analytical_dtos import CaseAnalysisDTO, RankingDTO, RankingItemDTO
from app.application.dto.filter_dto import AnalyticalFilterDTO

class GetCaseAnalysisUseCase:
    """Orquestra a análise detalhada de um caso (Ranking de Barras, Risco por Região)."""

    def __init__(self, repository: AnalyticalIndicatorRepository):
        self.repository = repository

    def execute(self, simulation_id: uuid.UUID, indicator: str = "epns", case_name: str = "Unknown Case", filters: AnalyticalFilterDTO = None) -> CaseAnalysisDTO:
        indicator_clean = indicator.lower()
        
        # 1. Busca os dados granulares (A query blindada do repositório)
        bus_results_raw = self.repository.get_top_buses_by_indicator(simulation_id, indicator_clean, limit=1500)
        
        # 2. Processa Agregações na Estrutura Exata do DTO: Dict[str, Dict[str, float]]
        region_aggregations_dict: Dict[str, Dict[str, float]] = {}
        for bus in bus_results_raw:
            reg_name = str(bus.get("region_name", "Região Desconhecida"))
            val = float(bus.get("value", 0.0))
            
            # Monta a estrutura: {"Região Sul": {"epns": 150.5}}
            if reg_name not in region_aggregations_dict:
                region_aggregations_dict[reg_name] = {indicator_clean: 0.0}
            elif indicator_clean not in region_aggregations_dict[reg_name]:
                region_aggregations_dict[reg_name][indicator_clean] = 0.0
                
            region_aggregations_dict[reg_name][indicator_clean] += val
        
        # 3. Processa Ranking (Barras mais críticas isoladas)
        top_buses_raw = RankingEngine.rank_critical_buses(bus_results_raw, indicator="value", top_n=1500)
        
        # 4. Empacota as barras no modelo oficial do Pydantic
        ranking_items = [
            RankingItemDTO(
                rank_position=tb.get("rank_position", idx + 1),
                element_id=str(tb.get("bus_external_id", tb.get("element_id", ""))),
                element_name=str(tb.get("bus_name", tb.get("element_name", ""))),
                region_name=str(tb.get("region_name", "Região Principal")), 
                value=float(tb.get("value", 0.0))
            ) for idx, tb in enumerate(top_buses_raw)
        ]

        ranking_dto = RankingDTO(indicator=indicator_clean, top_elements=ranking_items)

        # 5. Retorna o pacote compatível com o CaseAnalysisDTO
        return CaseAnalysisDTO(
            simulation_id=simulation_id,
            case_name=case_name,
            region_aggregations=region_aggregations_dict,  # <--- Estrutura Aninhada Correta
            top_critical_buses=ranking_dto
        )
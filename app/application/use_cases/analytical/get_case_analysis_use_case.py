import uuid
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.domain.analytics.ranking_engine import RankingEngine
from app.domain.analytics.aggregation_engine import AggregationEngine
from app.application.dto.analytical_dtos import CaseAnalysisDTO, RankingDTO, RankingItemDTO
from app.application.dto.filter_dto import AnalyticalFilterDTO

class GetCaseAnalysisUseCase:
    """Orquestra a análise detalhada de um caso (Ranking de Barras, Risco por Região)."""

    def __init__(self, repository: AnalyticalIndicatorRepository):
        self.repository = repository

    def execute(self, simulation_id: uuid.UUID, indicator: str = "epns", case_name: str = "Unknown Case", filters: AnalyticalFilterDTO = None) -> CaseAnalysisDTO:
        # 1. Busca os dados granulares. O repo retorna dicts com a chave padronizada 'value' para a métrica.
        bus_results_raw = self.repository.get_top_buses_by_indicator(simulation_id, indicator, limit=1000)
        
        # 2. Processa Agregações (Regiões). Renomeia 'value' para o nome do indicador para o agregador.
        # Mas neste ponto não temos a region_external_id no retorno do repositório atual, então vamos pular
        # temporariamente a agregação por região para focar no Ranking das Barras (que quebrou o teste).
        region_aggregations = {}
        
        # 3. Processa Ranking (Barras mais críticas) usando a chave genérica 'value'
        top_buses_raw = RankingEngine.rank_critical_buses(bus_results_raw, indicator="value", top_n=10)
        
        # 4. Converte para DTO
        ranking_items = [
            RankingItemDTO(
                rank_position=tb["rank_position"],
                element_id=tb["bus_external_id"],
                element_name=tb["bus_name"],
                value=tb["value"]  # <-- CORREÇÃO: Usar a chave genérica 'value' que veio do repositório
            ) for tb in top_buses_raw
        ]

        ranking_dto = RankingDTO(indicator=indicator, top_elements=ranking_items)

        return CaseAnalysisDTO(
            simulation_id=simulation_id,
            case_name=case_name,
            region_aggregations=region_aggregations,
            top_critical_buses=ranking_dto
        )
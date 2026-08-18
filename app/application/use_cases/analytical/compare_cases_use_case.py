import uuid
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.domain.analytics.comparison_engine import ComparisonEngine
from app.application.dto.analytical_dtos import ComparisonDTO, ComparisonDeltaDTO

class CompareCasesUseCase:
    """Orquestra a comparação entre dois cenários."""

    def __init__(self, repository: AnalyticalIndicatorRepository):
        self.repository = repository

    def execute(self, base_sim_id: uuid.UUID, target_sim_id: uuid.UUID, indicator: str = "epns") -> ComparisonDTO:
        # 1. Busca os dados globais de A e B
        global_a = self.repository.get_global_results(base_sim_id)
        global_b = self.repository.get_global_results(target_sim_id)
        
        # Extrai como dicionário simples (neste exemplo, simulamos conversão direta)
        dict_a = {indicator: getattr(global_a, indicator, 0.0)} if global_a else {}
        dict_b = {indicator: getattr(global_b, indicator, 0.0)} if global_b else {}

        # 2. Compara via Engine
        global_delta_raw = ComparisonEngine.compare_global_indicators(dict_a, dict_b, [indicator])
        
        # 3. Busca e compara Barras
        buses_a = self.repository.get_top_buses_by_indicator(base_sim_id, indicator, limit=1000)
        buses_b = self.repository.get_top_buses_by_indicator(target_sim_id, indicator, limit=1000)
        
        bus_comparisons = ComparisonEngine.compare_buses(buses_a, buses_b, indicator)

        # 4. Constrói o DTO de saída
        delta = global_delta_raw.get(indicator, {})
        global_comparison_dto = ComparisonDeltaDTO(
            val_a=delta.get("val_a", 0.0),
            val_b=delta.get("val_b", 0.0),
            absolute_difference=delta.get("absolute_difference", 0.0),
            percentage_difference=delta.get("percentage_difference", 0.0)
        )

        return ComparisonDTO(
            base_simulation_id=base_sim_id,
            target_simulation_id=target_sim_id,
            indicator=indicator,
            global_comparison=global_comparison_dto,
            element_comparisons=bus_comparisons
        )
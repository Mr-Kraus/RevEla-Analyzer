import uuid
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.domain.analytics.global_analysis_engine import GlobalAnalysisEngine
from app.application.dto.analytical_dtos import GlobalAnalysisDTO, IndicatorDTO

class GetGlobalIndicatorsUseCase:
    """Orquestra a busca e formatação dos indicadores globais de um caso."""
    
    def __init__(self, repository: AnalyticalIndicatorRepository):
        self.repository = repository

    def execute(self, simulation_id: uuid.UUID, case_name: str = "Unknown Case") -> GlobalAnalysisDTO:
        # 1. Consulta no Banco (Repository)
        global_result_model = self.repository.get_global_results(simulation_id)
        
        # 2. Processa na Engine de Domínio
        raw_analysis = GlobalAnalysisEngine.process_global_indicators(
            simulation_id=simulation_id,
            global_result_model=global_result_model,
            case_name=case_name
        )
        
        # 3. Mapeia para DTOs Blindados
        indicators_dto = {
            key: IndicatorDTO(**val) 
            for key, val in raw_analysis["indicators"].items()
        }
        
        return GlobalAnalysisDTO(
            simulation_id=simulation_id,
            case_name=case_name,
            indicators=indicators_dto
        )
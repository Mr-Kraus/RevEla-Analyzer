import uuid
from app.infrastructure.database.repositories.postgres_system_summary_repository import PostgresSystemSummaryRepository
from app.api.schemas.system_summary_schema import SystemSummaryResponse, SystemSummaryParamDTO

class GetSystemSummaryUseCase:
    def __init__(self, summary_repo: PostgresSystemSummaryRepository):
        self.summary_repo = summary_repo

    def execute(self, simulation_run_id: uuid.UUID) -> SystemSummaryResponse:
        model = self.summary_repo.get_by_simulation_id(simulation_run_id)

        if not model:
            return SystemSummaryResponse(system_summary=[], generation_tech={})

        # 1. Monta a lista para a Tabela System Summary
        summary_list = [
            SystemSummaryParamDTO(nome="Rated load", valor=model.rated_load_mw or 0.0, unidade="MW"),
            SystemSummaryParamDTO(nome="Peak load", valor=model.peak_load_mw or 0.0, unidade="MW"),
            SystemSummaryParamDTO(nome="Mean load", valor=model.mean_load_mw or 0.0, unidade="MW"),
            SystemSummaryParamDTO(nome="Annual total demand", valor=model.annual_total_demand_twh or 0.0, unidade="TWh"),
            SystemSummaryParamDTO(nome="Rated load/gen capacity", valor=model.rated_load_generation_ratio or 0.0, unidade="%")
        ]

        # 2. Monta o dicionário para o Gráfico de Rosquinha (Ignorando a linha 'Total')
        gen_tech = {}
        if model.generators_information and "data" in model.generators_information:
            for gen in model.generators_information["data"]:
                tech = gen.get("Technology", "Unknown")
                cap = float(gen.get("Capacity (MW)", 0.0))
                
                if tech.lower() != "total" and cap > 0:
                    gen_tech[tech] = cap

        return SystemSummaryResponse(
            system_summary=summary_list,
            generation_tech=gen_tech
        )
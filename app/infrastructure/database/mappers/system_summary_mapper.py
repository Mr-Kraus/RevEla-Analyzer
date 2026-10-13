import uuid
from app.ingestion.parsers.raw_dtos import RawSystemSummaryDTO
from app.infrastructure.database.models.system_summary_model import SystemSummaryModel

class SystemSummaryMapper:
    @staticmethod
    def to_model(sim_run_id: uuid.UUID, raw_dto: RawSystemSummaryDTO) -> SystemSummaryModel:
        
        # Função auxiliar para extrair floats com segurança
        def get_float(key: str) -> float:
            val = raw_dto.general_info.get(key, "0")
            try:
                return float(val.replace(',', '.'))
            except ValueError:
                return 0.0
                
        def get_int(key: str) -> int:
            val = raw_dto.general_info.get(key, "0")
            try:
                return int(float(val.replace(',', '.'))) # float() fallback caso venha 1.0
            except ValueError:
                return 0

        return SystemSummaryModel(
            id=uuid.uuid4(),
            simulation_run_id=sim_run_id,
            system_name=raw_dto.general_info.get("System", "Unknown"),
            number_of_interconnected_systems=get_int("Number of interconnected systems"),
            number_of_interconnections=get_int("Number of Interconnections"),
            rated_load_mw=get_float("Rated load (MW)"),
            peak_load_mw=get_float("Peak load (MW)"),
            mean_load_mw=get_float("Mean load (MW)"),
            annual_total_demand_twh=get_float("Annual total demand (TWh)"),
            short_term_load_uncertainty=get_float("Short-term load uncertainty"),
            long_term_load_uncertainty=get_float("Long-term load uncertainty"),
            rated_load_generation_ratio=get_float("Rated load/generation capacity ratio (%)"),
            mean_load_generation_ratio=get_float("Mean load/generation capacity ratio (%)"),
            number_of_reservoirs=get_int("Number of reservoirs"),
            number_of_wind_regions=get_int("Number of wind regions"),
            number_of_solar_regions=get_int("Number of solar regions"),
            generators_information={"data": raw_dto.generators_info}
        )
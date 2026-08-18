from app.domain.entities.simulation_run import SimulationRun
from app.infrastructure.database.models.simulation_model import SimulationRunModel

class SimulationRunMapper:
    @staticmethod
    def to_domain(model: SimulationRunModel) -> SimulationRun:
        return SimulationRun(
            id=model.id,
            case_id=model.case_id,
            results_directory=model.results_directory,
            simulated_years=model.simulated_years,
            analysis_type=model.analysis_type,
            system_representation=model.system_representation,
            imported_at=model.imported_at
        )

    @staticmethod
    def to_orm(entity: SimulationRun) -> SimulationRunModel:
        return SimulationRunModel(
            id=entity.id,
            case_id=entity.case_id,
            results_directory=entity.results_directory,
            simulated_years=entity.simulated_years,
            analysis_type=entity.analysis_type,
            system_representation=entity.system_representation,
            imported_at=entity.imported_at
        )
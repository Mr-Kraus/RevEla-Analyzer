from app.domain.entities.system_topology import System
from app.infrastructure.database.models.system_model import SystemModel

class SystemMapper:
    @staticmethod
    def to_domain(model: SystemModel) -> System:
        return System(
            id=model.id,
            case_id=model.case_id,
            simulation_run_id=model.simulation_run_id,
            external_name=model.external_name,
            nominal_load_mw=model.nominal_load_mw
        )

    @staticmethod
    def to_orm(entity: System) -> SystemModel:
        return SystemModel(
            id=entity.id,
            case_id=entity.case_id,
            simulation_run_id=entity.simulation_run_id,
            external_name=entity.external_name,
            nominal_load_mw=entity.nominal_load_mw
        )
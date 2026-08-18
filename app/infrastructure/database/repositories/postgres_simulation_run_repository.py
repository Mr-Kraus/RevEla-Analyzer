from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.simulation_run import SimulationRun
from app.domain.interfaces.simulation_repository import SimulationRunRepository
from app.domain.exceptions.base_exceptions import RepositoryError
from app.infrastructure.database.models.simulation_model import SimulationRunModel

# A IMPORTAÇÃO QUE FALTAVA (CORREÇÃO C1)
from app.infrastructure.database.mappers.simulation_run_mapper import SimulationRunMapper


class PostgresSimulationRunRepository(SimulationRunRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, simulation_run: SimulationRun) -> SimulationRun:
        try:
            model = self.session.get(SimulationRunModel, simulation_run.id)
            if not model:
                model = SimulationRunMapper.to_orm(simulation_run)
                self.session.add(model)
            else:
                model.analysis_type = simulation_run.analysis_type
                model.results_directory = simulation_run.results_directory
                model.simulated_years = simulation_run.simulated_years
                model.system_representation = simulation_run.system_representation
                model.imported_at = simulation_run.imported_at
                
            self.session.flush()
            return SimulationRunMapper.to_domain(model)
        except Exception as e:
            raise RepositoryError(f"Erro ao salvar SimulationRun: {str(e)}") from e

    def get_by_id(self, run_id: UUID) -> Optional[SimulationRun]:
        try:
            model = self.session.get(SimulationRunModel, run_id)
            return SimulationRunMapper.to_domain(model) if model else None
        except Exception as e:
            raise RepositoryError(f"Erro ao buscar SimulationRun por ID: {str(e)}") from e

    def list_by_case(self, case_id: UUID) -> List[SimulationRun]:
        try:
            stmt = select(SimulationRunModel).where(SimulationRunModel.case_id == case_id)
            models = self.session.execute(stmt).scalars().all()
            return [SimulationRunMapper.to_domain(m) for m in models]
        except Exception as e:
            raise RepositoryError(f"Erro ao listar SimulationRuns por Caso: {str(e)}") from e
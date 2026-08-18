from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.system_topology import System
from app.domain.interfaces.system_repository import SystemRepository
from app.domain.exceptions.base_exceptions import RepositoryError
from app.infrastructure.database.models.system_model import SystemModel

# A IMPORTAÇÃO QUE FALTAVA (CORREÇÃO C1)
from app.infrastructure.database.mappers.system_mapper import SystemMapper


class PostgresSystemRepository(SystemRepository):
    def __init__(self, session: Session):
        self.session = session

    def save_system(self, system: System) -> System:
        try:
            model = self.session.get(SystemModel, system.id)
            if not model:
                model = SystemMapper.to_orm(system)
                self.session.add(model)
            else:
                model.external_name = system.external_name
                model.nominal_load_mw = system.nominal_load_mw
                
            self.session.flush()
            return SystemMapper.to_domain(model)
        except Exception as e:
            raise RepositoryError(f"Erro ao salvar System: {str(e)}") from e

    def get_by_simulation(self, simulation_run_id: UUID) -> Optional[System]:
        try:
            stmt = select(SystemModel).where(SystemModel.simulation_run_id == simulation_run_id)
            model = self.session.execute(stmt).scalar_one_or_none()
            return SystemMapper.to_domain(model) if model else None
        except Exception as e:
            raise RepositoryError(f"Erro ao buscar System por simulation_run_id: {str(e)}") from e
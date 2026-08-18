from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.case import Case
from app.domain.interfaces.case_repository import CaseRepository
from app.domain.exceptions.base_exceptions import RepositoryError
from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.mappers.case_mapper import CaseMapper

class PostgresCaseRepository(CaseRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, case: Case) -> Case:
        try:
            model = self.session.get(CaseModel, case.id)
            if model:
                model.external_name = case.external_name
                model.display_name = case.display_name
                model.source_path = case.source_path
                model.status = case.status
                model.updated_at = case.updated_at
            else:
                model = CaseMapper.to_orm(case)
                self.session.add(model)
            
            self.session.flush()
            return CaseMapper.to_domain(model)
        except Exception as e:
            raise RepositoryError(f"Erro ao salvar Caso no PostgreSQL: {str(e)}") from e

    def get_by_id(self, case_id: UUID) -> Optional[Case]:
        try:
            model = self.session.get(CaseModel, case_id)
            return CaseMapper.to_domain(model) if model else None
        except Exception as e:
            raise RepositoryError(f"Erro ao buscar Caso por ID: {str(e)}") from e

    def get_by_external_name(self, external_name: str) -> Optional[Case]:
        try:
            stmt = select(CaseModel).where(CaseModel.external_name == external_name)
            model = self.session.execute(stmt).scalar_one_or_none()
            return CaseMapper.to_domain(model) if model else None
        except Exception as e:
            raise RepositoryError(f"Erro ao buscar Caso por nome externo: {str(e)}") from e

    def list_all(self) -> List[Case]:
        try:
            stmt = select(CaseModel)
            models = self.session.execute(stmt).scalars().all()
            return [CaseMapper.to_domain(m) for m in models]
        except Exception as e:
            raise RepositoryError(f"Erro ao listar Casos: {str(e)}") from e
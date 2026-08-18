from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.source_file import SourceFile
from app.domain.interfaces.source_file_repository import SourceFileRepository
from app.domain.exceptions.base_exceptions import RepositoryError
from app.infrastructure.database.models.source_file_model import SourceFileModel
from app.infrastructure.database.mappers.source_file_mapper import SourceFileMapper

class PostgresSourceFileRepository(SourceFileRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, source_file: SourceFile) -> SourceFile:
        try:
            model = self.session.get(SourceFileModel, source_file.id)
            if model:
                model.status = source_file.status
                model.file_hash = source_file.sha256
            else:
                model = SourceFileMapper.to_orm(source_file)
                self.session.add(model)
            
            self.session.flush()
            return SourceFileMapper.to_domain(model)
        except Exception as e:
            raise RepositoryError(f"Erro ao salvar SourceFile no PostgreSQL: {str(e)}") from e

    def get_by_hash(self, file_hash: str) -> Optional[SourceFile]:
        try:
            stmt = select(SourceFileModel).where(SourceFileModel.file_hash == file_hash)
            model = self.session.execute(stmt).scalar_one_or_none()
            return SourceFileMapper.to_domain(model) if model else None
        except Exception as e:
            raise RepositoryError(f"Erro ao buscar SourceFile por Hash: {str(e)}") from e

    def list_by_case(self, case_id: UUID) -> List[SourceFile]:
        try:
            stmt = select(SourceFileModel).where(SourceFileModel.case_id == case_id)
            models = self.session.execute(stmt).scalars().all()
            return [SourceFileMapper.to_domain(m) for m in models]
        except Exception as e:
            raise RepositoryError(f"Erro ao listar SourceFiles por Caso: {str(e)}") from e
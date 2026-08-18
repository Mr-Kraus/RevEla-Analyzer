from app.domain.entities.case import Case
from app.infrastructure.database.models.case_model import CaseModel

class CaseMapper:
    @staticmethod
    def to_domain(model: CaseModel) -> Case:
        return Case(
            id=model.id,
            external_name=model.external_name,
            display_name=model.display_name or model.external_name,
            source_path=model.source_path,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_orm(entity: Case) -> CaseModel:
        return CaseModel(
            id=entity.id,
            external_name=entity.external_name,
            display_name=entity.display_name,
            source_path=entity.source_path,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
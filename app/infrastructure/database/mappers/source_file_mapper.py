from app.domain.entities.source_file import SourceFile
from app.infrastructure.database.models.source_file_model import SourceFileModel

class SourceFileMapper:
    @staticmethod
    def to_domain(model: SourceFileModel) -> SourceFile:
        return SourceFile(
            id=model.id,
            case_id=model.case_id,
            path=model.path,
            relative_path=model.relative_path,
            filename=model.filename,
            extension=model.filename.split(".")[-1] if "." in model.filename else "",
            size=model.file_size,
            modified_at=model.modified_at,
            sha256=model.file_hash,
            dataset_code=model.dataset_code,
            status=model.status
        )

    @staticmethod
    def to_orm(entity: SourceFile) -> SourceFileModel:
        return SourceFileModel(
            id=entity.id,
            case_id=entity.case_id,
            path=entity.path,
            relative_path=entity.relative_path,
            filename=entity.filename,
            file_hash=entity.sha256,
            file_size=entity.size,
            modified_at=entity.modified_at,
            dataset_code=entity.dataset_code,
            status=entity.status
        )
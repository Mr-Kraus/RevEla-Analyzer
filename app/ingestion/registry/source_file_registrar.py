import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.domain.entities.source_file import SourceFile
from app.domain.exceptions.base_exceptions import IngestionError
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.ingestion.registry.dataset_registry import DatasetRegistry
from app.application.interfaces.ingestion_services import ISourceFileRegistrarService

logger = logging.getLogger(__name__)


class SourceFileRegistrar(ISourceFileRegistrarService):
    """
    Responsável por processar arquivos validados, calcular hashes SHA-256
    e gerar entidades SourceFile. Política de Erro: Falha individual aciona
    IngestionError para garantir Rollback Total no Orquestrador.
    Implementa ISourceFileRegistrarService.
    """

    def __init__(self, registry: DatasetRegistry):
        self.registry = registry

    def register_candidate_files(self, candidate: CaseCandidate, case_id: uuid.UUID) -> List[SourceFile]:
        logger.info(f"Iniciando o registro de arquivos para o caso: {candidate.case_name}")
        source_files = []
        all_files = candidate.detected_templates + candidate.detected_result_files

        for file_path in all_files:
            try:
                source_file = self._create_source_file_entity(file_path, candidate.root_path, case_id)
                source_files.append(source_file)
                logger.debug(f"SOURCE_FILE_REGISTERED: {source_file.filename} | Code: {source_file.dataset_code}")
            except Exception as e:
                error_msg = f"Falha crítica no processamento do arquivo '{file_path.name}': {str(e)}"
                logger.error(error_msg)
                raise IngestionError(error_msg) from e

        logger.info(f"Registro concluído. {len(source_files)} arquivo(s) processado(s).")
        return source_files

    def _create_source_file_entity(self, file_path: Path, root_path: Path, case_id: uuid.UUID) -> SourceFile:
        definition = self.registry.get_definition_for_file(file_path.name)
        dataset_code = definition.dataset_code if definition else "UNKNOWN"

        stat = file_path.stat()
        file_size = stat.st_size
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        absolute_path = str(file_path.absolute())
        relative_path = str(file_path.relative_to(root_path))
        file_hash = self._calculate_sha256(file_path)

        return SourceFile(
            id=uuid.uuid4(),
            case_id=case_id,
            path=absolute_path,
            relative_path=relative_path,
            filename=file_path.name,
            extension=file_path.suffix.lower().lstrip("."),
            size=file_size,
            modified_at=modified_at,
            sha256=file_hash,
            dataset_code=dataset_code,
            status="REGISTERED"
        )

    def _calculate_sha256(self, file_path: Path, chunk_size: int = 8192) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
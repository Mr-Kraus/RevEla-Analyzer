from typing import List
from uuid import UUID
import logging
from app.domain.interfaces.source_file_repository import SourceFileRepository
from app.ingestion.registry.source_file_registrar import SourceFileRegistrar
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.application.dto.source_file_dto import SourceFileDTO

logger = logging.getLogger(__name__)

class RegisterSourceFilesUseCase:
    """Gera metadados (hashes) dos arquivos válidos e os persiste na base de dados (Idempotente)."""
    def __init__(self, source_file_repository: SourceFileRepository, registrar: SourceFileRegistrar):
        self.source_file_repository = source_file_repository
        self.registrar = registrar

    def execute(self, candidate: CaseCandidate, case_id: UUID) -> List[SourceFileDTO]:
        source_files = self.registrar.register_candidate_files(candidate, case_id)
        
        saved_dtos = []
        for sf in source_files:
            # Verifica idempotência pelo Hash SHA-256
            existing_sf = self.source_file_repository.get_by_hash(sf.sha256)
            
            if existing_sf and existing_sf.case_id == case_id:
                logger.debug(f"Arquivo '{sf.filename}' já registrado com hash idêntico. Pulando persistência.")
                saved_sf = existing_sf
            else:
                saved_sf = self.source_file_repository.save(sf)
                
            saved_dtos.append(
                SourceFileDTO(
                    id=saved_sf.id,
                    case_id=saved_sf.case_id,
                    filename=saved_sf.filename,
                    extension=saved_sf.extension,
                    size=saved_sf.size,
                    modified_at=saved_sf.modified_at,
                    sha256=saved_sf.sha256,
                    dataset_code=saved_sf.dataset_code,
                    status=saved_sf.status
                )
            )
        
        return saved_dtos
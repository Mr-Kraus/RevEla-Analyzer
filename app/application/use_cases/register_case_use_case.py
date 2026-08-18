from uuid import uuid4
from typing import Optional
import logging
from app.domain.entities.case import Case
from app.domain.interfaces.case_repository import CaseRepository
from app.application.dto.case_dto import CaseDTO

logger = logging.getLogger(__name__)

class RegisterCaseUseCase:
    """Cria a entidade Case formal no domínio e a persiste no banco de dados, garantindo idempotência."""
    def __init__(self, case_repository: CaseRepository):
        self.case_repository = case_repository

    def execute(self, external_name: str, source_path: str, display_name: Optional[str] = None) -> CaseDTO:
        # Verifica idempotência: O caso já existe?
        existing_case = self.case_repository.get_by_external_name(external_name)
        
        if existing_case:
            logger.info(f"Caso '{external_name}' já existe. Atualizando caminho de origem se necessário.")
            existing_case.source_path = source_path
            if display_name:
                existing_case.display_name = display_name
            saved_case = self.case_repository.save(existing_case)
        else:
            logger.info(f"Registrando novo caso: '{external_name}'")
            new_case = Case(
                id=uuid4(),
                external_name=external_name,
                display_name=display_name or external_name,
                source_path=source_path
            )
            saved_case = self.case_repository.save(new_case)
        
        return CaseDTO(
            id=saved_case.id,
            external_name=saved_case.external_name,
            display_name=saved_case.display_name,
            source_path=saved_case.source_path,
            status=saved_case.status,
            created_at=saved_case.created_at,
            updated_at=saved_case.updated_at
        )
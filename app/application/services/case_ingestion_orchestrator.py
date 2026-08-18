import logging
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.application.use_cases.discover_case_use_case import DiscoverCaseUseCase
from app.application.use_cases.validate_case_use_case import ValidateCaseUseCase
from app.application.use_cases.register_case_use_case import RegisterCaseUseCase
from app.application.use_cases.register_source_files_use_case import RegisterSourceFilesUseCase
from app.application.dto.case_dto import CaseDTO
from app.ingestion.validators.validation_report import ValidationReport
from app.domain.exceptions.base_exceptions import IngestionError, ValidationError

logger = logging.getLogger(__name__)

class CaseIngestionOrchestrator:
    """
    Serviço da Aplicação responsável por orquestrar a ingestão de um Caso.
    Fluxo: Discovery -> Validation -> Register Case -> Register SourceFiles -> Commit
    """
    def __init__(
        self,
        discover_use_case: DiscoverCaseUseCase,
        validate_use_case: ValidateCaseUseCase,
        register_case_use_case: RegisterCaseUseCase,
        register_source_files_use_case: RegisterSourceFilesUseCase,
        session: Session
    ):
        self.discover_use_case = discover_use_case
        self.validate_use_case = validate_use_case
        self.register_case_use_case = register_case_use_case
        self.register_source_files_use_case = register_source_files_use_case
        self.session = session

    def process(self, target_path: str, display_name: Optional[str] = None) -> Tuple[CaseDTO, ValidationReport]:
        logger.info(f"INGESTION_STARTED para o caminho: {target_path}")

        try:
            candidate = self.discover_use_case.execute(target_path)
            
            report = self.validate_use_case.execute(candidate)
            if not report.is_valid:
                logger.error(f"INGESTION_FAILED: Falha na validação do caso {candidate.case_name}")
                raise ValidationError(f"O caso '{candidate.case_name}' é inválido: {'; '.join(report.errors)}")

            case_dto = self.register_case_use_case.execute(
                external_name=candidate.case_name,
                source_path=str(candidate.root_path.absolute()),
                display_name=display_name
            )

            self.register_source_files_use_case.execute(candidate, case_dto.id)

            self.session.commit()
            logger.info(f"INGESTION_COMPLETED com sucesso para o caso: {case_dto.external_name}")

            return case_dto, report

        except Exception as e:
            self.session.rollback()
            logger.exception(f"INGESTION_FAILED: Transação desfeita para {target_path}")
            if isinstance(e, (ValidationError, IngestionError)):
                raise
            raise IngestionError(f"Erro inesperado durante orquestração: {str(e)}") from e
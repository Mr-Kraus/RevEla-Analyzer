from app.ingestion.validators.case_validator import CaseValidator
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.ingestion.validators.validation_report import ValidationReport

class ValidateCaseUseCase:
    """Submete um candidato a caso às regras de integridade física e estrutural."""
    def __init__(self, validator_service: CaseValidator):
        self.validator_service = validator_service

    def execute(self, candidate: CaseCandidate) -> ValidationReport:
        return self.validator_service.validate(candidate)
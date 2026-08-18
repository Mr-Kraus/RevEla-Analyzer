import logging
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.ingestion.validators.validation_report import ValidationReport
from app.ingestion.registry.dataset_registry import DatasetRegistry
from app.application.interfaces.ingestion_services import ICaseValidatorService

logger = logging.getLogger(__name__)


class CaseValidator(ICaseValidatorService):
    """
    Valida a integridade física dos arquivos e cruza a estrutura do candidato
    com as exigências de datasets obrigatórios registradas no DatasetRegistry.
    Implementa ICaseValidatorService.
    """

    def __init__(self, registry: DatasetRegistry):
        self.registry = registry

    def validate(self, candidate: CaseCandidate) -> ValidationReport:
        logger.info(f"CASE_VALIDATION_STARTED para o caso: {candidate.case_name}")

        report = ValidationReport(is_valid=True)

        if candidate.has_errors():
            report.is_valid = False
            report.errors.extend(candidate.errors)
            logger.error("CASE_VALIDATION_COMPLETED (Falha originada no Discovery)")
            return report

        # 1. Validação física dos arquivos (0 bytes / extensões)
        self._validate_physical_files(candidate, report)

        # 2. Validação coerente contra os required=True do DatasetRegistry
        self._validate_required_datasets(candidate, report)

        if report.errors:
            report.is_valid = False
            logger.error(f"CASE_VALIDATION_COMPLETED com {len(report.errors)} erro(s).")
        else:
            logger.info("CASE_VALIDATION_COMPLETED com sucesso.")

        return report

    def _validate_physical_files(self, candidate: CaseCandidate, report: ValidationReport) -> None:
        all_files = candidate.detected_templates + candidate.detected_result_files

        for file_path in all_files:
            try:
                if file_path.stat().st_size == 0:
                    report.warnings.append(f"Arquivo vazio detectado e ignorado: {file_path.name}")
                    report.unsupported_files.append(file_path)
                    continue

                if not file_path.name.lower().endswith(".csv"):
                    report.warnings.append(f"Extensão não suportada ignorada: {file_path.name}")
                    report.unsupported_files.append(file_path)
                else:
                    report.detected_files.append(file_path)

            except OSError as e:
                report.errors.append(f"Falha de leitura no arquivo {file_path.name}: {str(e)}")

    def _validate_required_datasets(self, candidate: CaseCandidate, report: ValidationReport) -> None:
        """Cruza os arquivos encontrados com os códigos obrigatórios no Registry."""
        all_files = candidate.detected_templates + candidate.detected_result_files
        found_codes = set()

        for file_path in all_files:
            definition = self.registry.get_definition_for_file(file_path.name)
            if definition:
                found_codes.add(definition.dataset_code)

        required_codes = self.registry.get_all_required_codes()
        for req_code in required_codes:
            if req_code not in found_codes:
                report.errors.append(f"Dataset obrigatório ausente conforme Registry: '{req_code}'")
                report.missing_files.append(req_code)
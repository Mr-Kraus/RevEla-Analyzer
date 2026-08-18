from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from pathlib import Path
from app.ingestion.discovery.case_candidate import CaseCandidate
from app.ingestion.validators.validation_report import ValidationReport
from app.domain.entities.source_file import SourceFile

class ICaseDiscoveryService(ABC):
    @abstractmethod
    def discover(self, target_path: Path) -> CaseCandidate:
        pass

class ICaseValidatorService(ABC):
    @abstractmethod
    def validate(self, candidate: CaseCandidate) -> ValidationReport:
        pass

class ISourceFileRegistrarService(ABC):
    @abstractmethod
    def register_candidate_files(self, candidate: CaseCandidate, case_id: UUID) -> List[SourceFile]:
        pass
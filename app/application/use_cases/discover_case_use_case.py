from pathlib import Path
from app.ingestion.discovery.case_discovery import CaseDiscovery
from app.ingestion.discovery.case_candidate import CaseCandidate

class DiscoverCaseUseCase:
    """Invoca o serviço de varredura no sistema de arquivos para mapear o caso."""
    def __init__(self, discovery_service: CaseDiscovery):
        self.discovery_service = discovery_service

    def execute(self, target_path: str) -> CaseCandidate:
        return self.discovery_service.discover(Path(target_path))
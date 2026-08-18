from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.source_file import SourceFile

class SourceFileRepository(ABC):
    @abstractmethod
    def save(self, source_file: SourceFile) -> SourceFile:
        """Registra o metadado de um arquivo lido."""
        pass

    @abstractmethod
    def get_by_hash(self, file_hash: str) -> Optional[SourceFile]:
        """Busca um arquivo pelo seu hash SHA-256 para checar duplicidade."""
        pass

    @abstractmethod
    def list_by_case(self, case_id: UUID) -> List[SourceFile]:
        """Lista todos os arquivos mapeados dentro de um caso."""
        pass
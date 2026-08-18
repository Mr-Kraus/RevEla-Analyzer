from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.case import Case

class CaseRepository(ABC):
    @abstractmethod
    def save(self, case: Case) -> Case:
        """Salva um novo caso ou atualiza um existente."""
        pass

    @abstractmethod
    def get_by_id(self, case_id: UUID) -> Optional[Case]:
        """Busca um caso pelo seu ID único."""
        pass

    @abstractmethod
    def get_by_external_name(self, external_name: str) -> Optional[Case]:
        """Busca um caso pelo nome da pasta original."""
        pass

    @abstractmethod
    def list_all(self) -> List[Case]:
        """Lista todos os casos registrados no sistema."""
        pass
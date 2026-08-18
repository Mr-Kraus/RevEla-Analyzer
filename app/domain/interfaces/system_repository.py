from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.domain.entities.system_topology import System

class SystemRepository(ABC):
    @abstractmethod
    def save_system(self, system: System) -> System:
        """Persiste a entidade agregadora System."""
        pass

    @abstractmethod
    def get_by_simulation(self, simulation_run_id: UUID) -> Optional[System]:
        """Busca o sistema elétrico associado a uma execução de simulação."""
        pass
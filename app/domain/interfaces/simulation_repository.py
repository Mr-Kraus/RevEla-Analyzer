from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.simulation_run import SimulationRun

class SimulationRunRepository(ABC):
    @abstractmethod
    def save(self, simulation_run: SimulationRun) -> SimulationRun:
        """Persiste ou atualiza uma execução de simulação."""
        pass

    @abstractmethod
    def get_by_id(self, run_id: UUID) -> Optional[SimulationRun]:
        """Busca uma execução pelo ID."""
        pass

    @abstractmethod
    def list_by_case(self, case_id: UUID) -> List[SimulationRun]:
        """Lista todas as execuções associadas a um Caso."""
        pass
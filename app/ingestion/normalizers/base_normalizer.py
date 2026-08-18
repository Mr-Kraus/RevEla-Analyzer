from abc import ABC, abstractmethod
from typing import Any

class BaseNormalizer(ABC):
    """
    Interface base obrigatória para todos os Normalizadores.
    Responsabilidade: Transformar DTOs Brutos (Raw DTOs) em Entidades de Domínio ou DTOs Canônicos.
    """
    
    @abstractmethod
    def normalize(self, raw_data: Any, **kwargs) -> Any:
        """
        Recebe os dados brutos do Parser e retorna as estruturas tipadas do sistema.
        O **kwargs permite passar IDs de contexto (ex: case_id, system_id).
        """
        pass
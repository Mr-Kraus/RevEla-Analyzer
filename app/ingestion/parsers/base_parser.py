from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseParser(ABC):
    """Interface base obrigatória para todos os Parsers do RevEla Analyzer."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> Any:
        """Lê o arquivo físico e retorna um Raw DTO correspondente."""
        pass
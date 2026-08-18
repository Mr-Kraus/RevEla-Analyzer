from dataclasses import dataclass, field
from typing import List
from pathlib import Path

@dataclass
class ValidationReport:
    """
    Consolida o resultado da validação estrutural e física de um candidato a caso.
    """
    is_valid: bool
    detected_files: List[Path] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)
    unsupported_files: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
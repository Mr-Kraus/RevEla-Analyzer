from dataclasses import dataclass, field
from typing import List
from pathlib import Path

@dataclass
class CaseCandidate:
    """
    Representa um caso descoberto no sistema de arquivos antes da validação profunda.
    """
    root_path: Path
    case_name: str
    detected_templates: List[Path] = field(default_factory=list)
    detected_result_directories: List[Path] = field(default_factory=list)
    detected_result_files: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
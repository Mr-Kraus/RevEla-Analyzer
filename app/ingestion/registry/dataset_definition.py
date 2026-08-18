from dataclasses import dataclass
import fnmatch

@dataclass
class DatasetDefinition:
    """
    Define as propriedades e regras de um dataset conhecido pelo RevEla Analyzer.
    """
    dataset_code: str
    filename_pattern: str
    dataset_family: str
    dataset_type: str  # Ex: 'TEMPLATE' ou 'RESULT'
    required: bool
    priority: int
    parser_identifier: str
    version: str = "1.0"

    def matches(self, filename: str) -> bool:
        """
        Verifica se um nome de arquivo se enquadra nesta definição de dataset.
        Utiliza fnmatch para permitir padrões como 'Generation - *.csv'.
        """
        return fnmatch.fnmatch(filename.lower(), self.filename_pattern.lower())
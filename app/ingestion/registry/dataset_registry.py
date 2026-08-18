import logging
from typing import List, Optional
from app.ingestion.registry.dataset_definition import DatasetDefinition

logger = logging.getLogger(__name__)

class DatasetRegistry:
    """
    Catálogo central que mapeia padrões de arquivos aos seus respectivos
    tipos de dados e parsers.
    """
    def __init__(self):
        self._datasets: List[DatasetDefinition] = []
        self._initialize_core_datasets()

    def register(self, definition: DatasetDefinition) -> None:
        """Registra uma nova definição de dataset e reordena por prioridade."""
        self._datasets.append(definition)
        self._datasets.sort(key=lambda x: x.priority)

    def get_definition_for_file(self, filename: str) -> Optional[DatasetDefinition]:
        """
        Procura no catálogo a definição correspondente ao nome do arquivo.
        Retorna a primeira que der 'match' com base na prioridade.
        """
        for definition in self._datasets:
            if definition.matches(filename):
                return definition
        return None

    def get_all_required_codes(self) -> List[str]:
        """Retorna os códigos dos datasets que são obrigatórios para a ingestão."""
        return [ds.dataset_code for ds in self._datasets if ds.required]

    def _initialize_core_datasets(self) -> None:
        """
        Popula o Registry com as definições fundamentais baseadas no PRD.
        A prioridade dita a ordem de parsing (ex: System antes de Results).
        """
        # 1. Topologia Elétrica (Obrigatório)
        self.register(DatasetDefinition(
            dataset_code="TEMPLATE_SYSTEM",
            filename_pattern="Template System.csv",
            dataset_family="Topology",
            dataset_type="TEMPLATE",
            required=True,
            priority=10,
            parser_identifier="SystemTemplateParser"
        ))

        # 2. Configuração de Simulação (Obrigatório)
        self.register(DatasetDefinition(
            dataset_code="SIMULATION_CONFIG",
            filename_pattern="Simulation Config.csv",
            dataset_family="Configuration",
            dataset_type="RESULT",
            required=True,
            priority=20,
            parser_identifier="SimulationConfigParser"
        ))

        # 3. Confiabilidade Global (Obrigatório)
        self.register(DatasetDefinition(
            dataset_code="FINAL_RELIABILITY_INDICES",
            filename_pattern="Final Reliability Indices.csv",
            dataset_family="Reliability",
            dataset_type="RESULT",
            required=True,
            priority=30,
            parser_identifier="ReliabilityParser"
        ))

        # 4. Geração (Opcional para o primeiro fluxo, mas já mapeado)
        self.register(DatasetDefinition(
            dataset_code="GENERATION_RESULTS",
            filename_pattern="Generation - *.csv",
            dataset_family="Generation",
            dataset_type="RESULT",
            required=False,
            priority=40,
            parser_identifier="GenerationResultParser"
        ))
        
        # 5. Transmissão (Opcional)
        self.register(DatasetDefinition(
            dataset_code="TRANSMISSION_RESULTS",
            filename_pattern="Transmission - *.csv",
            dataset_family="Transmission",
            dataset_type="RESULT",
            required=False,
            priority=50,
            parser_identifier="TransmissionResultParser"
        ))
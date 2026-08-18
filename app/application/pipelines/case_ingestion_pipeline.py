import logging
import uuid
from pathlib import Path
from sqlalchemy.orm import Session

from app.ingestion.parsers.template_settings_parser import TemplateSettingsParser
from app.ingestion.parsers.template_system_parser import TemplateSystemParser
from app.ingestion.parsers.reliability_indices_parser import ReliabilityIndicesParser

from app.ingestion.normalizers.settings_normalizer import SettingsNormalizer
from app.ingestion.normalizers.system_normalizer import SystemNormalizer
from app.ingestion.normalizers.reliability_indices_normalizer import ReliabilityIndicesNormalizer

from app.application.use_cases.persist_parsed_data_use_case import PersistParsedDataUseCase

logger = logging.getLogger(__name__)

class CaseIngestionPipeline:
    """Implementa o fluxo definitivo da Fase 9: Do CSV até o Banco."""
    
    def __init__(self, session: Session):
        self.session = session
        self.persist_use_case = PersistParsedDataUseCase(session)

    def run(self, case_id: uuid.UUID, simulation_run_id: uuid.UUID, case_folder: Path) -> bool:
        logger.info(f"Iniciando Pipeline Completo para o Caso: {case_folder.name}")
        
        try:
            # 1. Parsing
            raw_settings = TemplateSettingsParser().parse(case_folder / "Template Settings.csv")
            raw_system = TemplateSystemParser().parse(case_folder / "Template System.csv")
            
            # Como a pasta pode variar, busca o arquivo de resultados
            results_files = list(case_folder.rglob("*Final Reliability Indices.csv"))
            if not results_files:
                raise FileNotFoundError("Arquivo 'Final Reliability Indices.csv' não encontrado no caso.")
                
            raw_results = ReliabilityIndicesParser().parse(results_files[0])
            
            # 2. Normalization
            canon_settings = SettingsNormalizer().normalize(raw_settings)
            canon_system = SystemNormalizer().normalize(raw_system)
            canon_results = ReliabilityIndicesNormalizer().normalize(raw_results)
            
            # 3. Persistence (Transação Única)
            self.persist_use_case.execute(
                case_id=case_id,
                simulation_run_id=simulation_run_id,
                settings_dto=canon_settings,
                topology_dto=canon_system,
                results_dto=canon_results
            )
            return True
            
        except Exception as e:
            logger.error(f"Pipeline falhou: {e}")
            return False
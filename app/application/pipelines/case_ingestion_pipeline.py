import logging
import uuid
import traceback
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.ingestion.parsers.template_settings_parser import TemplateSettingsParser
from app.ingestion.parsers.template_system_parser import TemplateSystemParser
from app.ingestion.parsers.reliability_indices_parser import ReliabilityIndicesParser

from app.ingestion.normalizers.settings_normalizer import SettingsNormalizer
from app.ingestion.normalizers.system_normalizer import SystemNormalizer
from app.ingestion.normalizers.reliability_indices_normalizer import ReliabilityIndicesNormalizer

from app.application.use_cases.persist_parsed_data_use_case import PersistParsedDataUseCase
from app.infrastructure.database.models.simulation_model import SimulationRunModel

logger = logging.getLogger(__name__)

class CaseIngestionPipeline:
    """Implementa o fluxo definitivo da Fase 9: Do CSV até o Banco."""
    
    def __init__(self, session: Session):
        self.session = session
        self.persist_use_case = PersistParsedDataUseCase(session)

    def run(self, case_id: uuid.UUID, simulation_run_id: uuid.UUID, case_folder: Path) -> bool:
        """
        Executa o pipeline de ingestão completo: 
        1. Cria a simulação pai
        2. Faz o Parsing e Normalização dos CSVs
        3. Chama o caso de uso de Persistência para gravar e comitar os resultados
        """
        logger.info(f"Iniciando Pipeline Completo para o Caso: {case_folder.name}")
        
        try:
            # =====================================================================
            # PASSO 1: CRIAR O REGISTRO PAI DA SIMULAÇÃO
            # =====================================================================
            new_simulation = SimulationRunModel(
                id=simulation_run_id,
                case_id=case_id,
                imported_at=datetime.now() # Preenchendo o campo obrigatório do banco
            )
            self.session.add(new_simulation)
            
            # O 'flush' envia a simulação para a base de dados para garantir o UUID, 
            # permitindo que os relacionamentos de Foreign Key das etapas seguintes funcionem.
            self.session.flush() 

            # =====================================================================
            # PASSO 2: EXTRAÇÃO E NORMALIZAÇÃO DOS DADOS (Parsers e Normalizers)
            # =====================================================================
            # Lógica de Parsing (Leitura dos arquivos físicos em raw DTOs)
            raw_settings = TemplateSettingsParser().parse(case_folder / "Template Settings.csv")
            raw_system = TemplateSystemParser().parse(case_folder / "Template System.csv")
            
            # Busca dinâmica pelo arquivo de resultados de confiabilidade (suportando subpastas como 'Results_STA')
            results_files = list(case_folder.rglob("*Final Reliability Indices.csv"))
            if not results_files:
                raise FileNotFoundError("Arquivo 'Final Reliability Indices.csv' não encontrado no caso.")
                
            raw_results = ReliabilityIndicesParser().parse(results_files[0])
            
            # Lógica de Normalização (Conversão de raw DTOs para Canonical DTOs)
            canon_settings = SettingsNormalizer().normalize(raw_settings)
            canon_system = SystemNormalizer().normalize(raw_system)
            canon_results = ReliabilityIndicesNormalizer().normalize(raw_results)

            # =====================================================================
            # PASSO 3: PERSISTIR RESULTADOS E CONFIRMAR A TRANSAÇÃO
            # =====================================================================
            # O PersistParsedDataUseCase irá receber os DTOs limpos, aplicar os Mappers de
            # topologia/indicadores e fará o COMMIT de toda a operação de forma segura.
            self.persist_use_case.execute(
                case_id=case_id,
                simulation_run_id=simulation_run_id,
                settings_dto=canon_settings,
                topology_dto=canon_system,
                results_dto=canon_results
            )
            
            # Nota: O `persist_use_case.execute()` já possui um `self.session.commit()` 
            # na última linha, portanto não precisamos comitar novamente aqui.
            return True

        except Exception as e:
            # Se der qualquer erro (falta de ficheiro, erro de conversão, erro de SQL),
            # anula tudo o que foi feito nesta tentativa.
            self.session.rollback()
            logger.error(f"Erro crítico no pipeline de ingestão: {e}")
            print(f"Erro crítico no pipeline de ingestão: {e}")
            print(traceback.format_exc()) # Imprime o erro detalhado no terminal
            return False
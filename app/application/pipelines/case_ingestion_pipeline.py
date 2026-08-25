import logging
import uuid
import traceback
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from app.ingestion.parsers.template_settings_parser import TemplateSettingsParser
from app.ingestion.parsers.template_system_parser import TemplateSystemParser
from app.ingestion.parsers.reliability_indices_parser import ReliabilityIndicesParser
from app.ingestion.parsers.system_parser_factory import SystemParserFactory

from app.ingestion.normalizers.settings_normalizer import SettingsNormalizer
from app.ingestion.normalizers.system_normalizer import SystemNormalizer
from app.ingestion.normalizers.reliability_indices_normalizer import ReliabilityIndicesNormalizer

from app.application.use_cases.persist_parsed_data_use_case import PersistParsedDataUseCase
from app.infrastructure.database.models.simulation_model import SimulationRunModel

# IMPORTS DA ESTEIRA DE SÉRIES TEMPORAIS
from app.infrastructure.database.repositories.postgres_time_series_repository import PostgresTimeSeriesRepository
from app.ingestion.parsers.time_series_parser import TimeSeriesParser
from app.application.use_cases.persist_time_series_use_case import PersistTimeSeriesUseCase

logger = logging.getLogger(__name__)

class CaseIngestionPipeline:
    """Implementa o fluxo definitivo da Fase 9: Do CSV até o Banco, agora com Séries Temporais."""
    
    def __init__(self, session: Session):
        self.session = session
        self.persist_use_case = PersistParsedDataUseCase(session)
        
        # Inicializando a esteira de Séries Temporais
        self.ts_repo = PostgresTimeSeriesRepository(session)
        self.persist_ts_use_case = PersistTimeSeriesUseCase(self.ts_repo)

    def run(self, case_id: uuid.UUID, simulation_run_id: uuid.UUID, case_folder: Path, software_version: str = "RELEVA") -> bool:
        """
        Executa o pipeline de ingestão completo: 
        1. Cria a simulação pai
        2. Faz o Parsing e Normalização dos CSVs
        3. Persiste a topologia e resultados de confiabilidade
        4. Extrai e persiste as Séries Temporais (Carga, Solar, Hidro, etc.)
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
            self.session.flush() 

            # =====================================================================
            # PASSO 2: EXTRAÇÃO E NORMALIZAÇÃO DOS DADOS (Parsers e Normalizers)
            # =====================================================================
            settings_files = list(case_folder.rglob("Template Settings.csv"))
            if not settings_files:
                raise FileNotFoundError("Arquivo 'Template Settings.csv' não encontrado em nenhuma subpasta.")
            raw_settings = TemplateSettingsParser().parse(settings_files[0])

            system_files = list(case_folder.rglob("Template System.csv"))
            if not system_files:
                raise FileNotFoundError("Arquivo 'Template System.csv' não encontrado em nenhuma subpasta.")
            parser = SystemParserFactory.get_parser(software_version)
            raw_system = parser.parse(system_files[0])
            
            results_files = list(case_folder.rglob("*Final Reliability Indices.csv"))
            if not results_files:
                raise FileNotFoundError("Arquivo 'Final Reliability Indices.csv' não encontrado no caso.")
            raw_results = ReliabilityIndicesParser().parse(results_files[0])
            
            canon_settings = SettingsNormalizer().normalize(raw_settings)
            canon_system = SystemNormalizer().normalize(raw_system)
            canon_results = ReliabilityIndicesNormalizer().normalize(raw_results)

            # =====================================================================
            # PASSO 3: PERSISTIR RESULTADOS DE CONFIABILIDADE E TOPOLOGIA
            # =====================================================================
            self.persist_use_case.execute(
                case_id=case_id,
                simulation_run_id=simulation_run_id,
                settings_dto=canon_settings,
                topology_dto=canon_system,
                results_dto=canon_results
            )
            
            # =====================================================================
            # PASSO 4: EXTRAÇÃO E PERSISTÊNCIA DAS SÉRIES TEMPORAIS
            # =====================================================================
            all_parsed_series = []
            
            # Mapeamento do nome do arquivo físico para o Tipo de Série
            ts_files_map = {
                "Template Load.csv": "Load",
                "Template Solar.csv": "Solar",
                "Template Hydro.csv": "Hydro",
                "Template Wind.csv": "Wind",
                "Template Small-Hydro.csv": "Small-Hydro"
            }

            # Varre o diretório dinamicamente procurando os templates
            for filename, series_type in ts_files_map.items():
                found_files = list(case_folder.rglob(filename))
                
                if found_files:
                    filepath = str(found_files[0])
                    logger.info(f"Lendo arquivo de série temporal: {filename}")
                    try:
                        # Extrai os blocos <VALOR> ou <VAL> do arquivo
                        parsed_data = TimeSeriesParser.parse_file(filepath, series_type)
                        all_parsed_series.extend(parsed_data)
                    except Exception as e:
                        logger.warning(f"Aviso: Falha ao ler '{filename}': {e}. A série foi ignorada.")

            # Se encontrou alguma matriz de dados, envia para o Use Case salvar atomicamente
            if all_parsed_series:
                logger.info(f"Persistindo {len(all_parsed_series)} matrizes de séries temporais...")
                self.persist_ts_use_case.execute(simulation_run_id, all_parsed_series)

            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Erro crítico no pipeline de ingestão: {e}")
            print(f"Erro crítico no pipeline de ingestão: {e}")
            print(traceback.format_exc()) 
            return False
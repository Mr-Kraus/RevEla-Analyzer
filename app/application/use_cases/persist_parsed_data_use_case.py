import logging
import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session

# Importação corrigida para refletir a localização real na infraestrutura
from app.infrastructure.database.mappers.dto_mappers import ReliabilityResultDtoMapper, SystemTopologyMapper
from app.infrastructure.database.repositories.postgres_reliability_repository import PostgresReliabilityRepository
from app.infrastructure.database.models.simulation_model import SimulationRunModel # <-- Importação Adicionada!

logger = logging.getLogger(__name__)

class PersistParsedDataUseCase:
    """
    Coordena a persistência de configurações, topologia e indicadores.
    Garante a regra do M02 (Fase 8): Tudo deve ocorrer em UMA ÚNICA TRANSAÇÃO.
    """
    def __init__(self, session: Session):
        self.session = session
        self.reliability_repo = PostgresReliabilityRepository(session)

    def execute(self, case_id: uuid.UUID, simulation_run_id: uuid.UUID, 
                settings_dto: Dict[str, Any], topology_dto: Dict[str, Any], results_dto: Dict[str, Any]) -> None:
        
        logger.info(f"Iniciando transação de persistência para Simulação: {simulation_run_id}")
        
        try:
            logger.info("============== RASTREADOR - USE CASE ==============")
            logger.info(f"Carga no topology_dto: {topology_dto.get('nominal_load_mw', 'NÃO CHEGOU')}")
            logger.info(f"Anos no results_dto: {results_dto.get('simulated_years', 'NÃO CHEGOU')}")
            logger.info(f"Confianca no results_dto (global): {results_dto.get('global_indices', {}).get('confidence_intervals', 'NÃO CHEGOU')}")
            logger.info("===================================================")
            
            # FASE 5: Persistência de Configurações
            logger.debug("Mapeando configurações...")

            # FASE 4: Persistência de Topologia (Cascade fará a mágica)
            logger.debug("Mapeando topologia em cascata...")
            system_orm = SystemTopologyMapper.to_orm_models(case_id, simulation_run_id, topology_dto)
            self.session.add(system_orm)

            # FASE 6: Persistência de Indicadores
            logger.debug("Mapeando indicadores de confiabilidade...")
            results_entities = []
            
            # Globais
            # ... [código existente]
            # Globais
            if "global_indices" in results_dto and results_dto["global_indices"]:
                results_entities.append(
                    ReliabilityResultDtoMapper.to_domain(simulation_run_id, True, results_dto["global_indices"])
                )
            
            # Recupera a simulação atual para atualizar Anos e Tipo
            simulation_run = self.session.get(SimulationRunModel, simulation_run_id)
            if simulation_run:
                simulation_run.simulated_years = results_dto.get("simulated_years", 0)
                simulation_run.analysis_type = settings_dto.get("analysis_type", "STA")
            regioes_para_salvar = results_dto.get("region_indices", [])
            logger.info("============== RASTREADOR: USE CASE ==============")
            logger.info(f"Regiões recebidas para salvar no banco: {len(regioes_para_salvar)}")
            logger.info("==================================================")
            # =========================================================
            # NOVA FASE: Por Região
            # =========================================================
            for region_res in results_dto.get("region_indices", []):
                results_entities.append(
                    ReliabilityResultDtoMapper.to_domain(
                        simulation_run_id,                       # 1º: ID da simulação
                        False,                                   # 2º: is_global
                        region_res,                              # 3º: Os dados/métricas
                        None,                                    # 4º: Barra (Nulo, pois é região)
                        region_res.get("region_name")            # 5º: Região
                    )
                )

            # =========================================================
            # FASE: Por Barra
            # =========================================================
            for bus_res in results_dto.get("bus_indices", []):
                results_entities.append(
                    ReliabilityResultDtoMapper.to_domain(
                        simulation_run_id,                       # 1º: ID da simulação
                        False,                                   # 2º: is_global
                        bus_res,                                 # 3º: Os dados/métricas
                        bus_res.get("bus_external_id"),          # 4º: Barra
                        None                                     # 5º: Região (Nulo, pois é barra)
                    )
                )
                
            self.reliability_repo.save_all(results_entities)

            # FASE 8: COMMIT TOTAL (Tudo ou Nada)
            self.session.commit()
            logger.info("Transação concluída com sucesso! Banco de dados populado.")

        except Exception as e:
            # FASE 8: ROLLBACK
            self.session.rollback()
            logger.error(f"Falha na persistência. Rollback executado. Erro: {str(e)}")
            raise e
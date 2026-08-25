import uuid
from typing import List, Dict, Any

from app.infrastructure.database.repositories.postgres_time_series_repository import PostgresTimeSeriesRepository
from app.infrastructure.database.mappers.time_series_dto_mapper import TimeSeriesDtoMapper

class PersistTimeSeriesUseCase:
    def __init__(self, repository: PostgresTimeSeriesRepository):
        self.repository = repository
        
    def execute(self, simulation_run_id: uuid.UUID, parsed_series_list: List[Dict[str, Any]]):
        meta_entities = []
        data_entities = []
        
        for series_dto in parsed_series_list:
            # Garante a posição padrão se não enviada pelo parser
            if "data_position" not in series_dto:
                series_dto["data_position"] = "Input"
                
            # 1. Cria a Entidade de Metadado
            meta_entity = TimeSeriesDtoMapper.to_domain_metadata(simulation_run_id, series_dto)
            meta_entities.append(meta_entity)
            
            # 2. Cria a Entidade de Dados (amarrada ao ID do Metadado recém-criado)
            data_entity = TimeSeriesDtoMapper.to_domain_data(meta_entity.id, series_dto["raw_values"])
            data_entities.append(data_entity)
            
        # Envia tudo para o repositório salvar atomicamente
        self.repository.save_time_series_bulk(meta_entities, data_entities)
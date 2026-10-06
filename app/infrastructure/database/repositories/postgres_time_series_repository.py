from sqlalchemy.orm import Session
from typing import List
import uuid
from app.domain.entities.time_series import TimeSeriesMetadata, DataTimeSeries
from app.infrastructure.database.models.time_series_metadata_model import TimeSeriesMetadataModel
from app.infrastructure.database.models.data_time_series_model import DataTimeSeriesModel

class PostgresTimeSeriesRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_time_series_bulk(self, metadata_entities: List[TimeSeriesMetadata], data_entities: List[DataTimeSeries]):
        # Conversão de Entidade de Domínio para Modelo ORM (SQLAlchemy)
        meta_models = [TimeSeriesMetadataModel(**m.dict()) for m in metadata_entities]
        data_models = [DataTimeSeriesModel(**d.dict()) for d in data_entities]
        
        try:
            # 1. Salva os metadados e envia ao banco para garantir que as Chaves Estrangeiras existam
            self.session.add_all(meta_models)
            self.session.flush() 
            
            # 2. Salva as matrizes de dados e efetiva a transação
            self.session.add_all(data_models)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_ens_series_by_simulation(self, simulation_id: uuid.UUID) -> dict:
        """Busca as séries temporais de ENS (G, T e G+T) de uma simulação."""
        from sqlalchemy import select
        from app.infrastructure.database.models.time_series_metadata_model import TimeSeriesMetadataModel
        from app.infrastructure.database.models.data_time_series_model import DataTimeSeriesModel
        
        # Faz o JOIN entre Metadados e os Arrays de Dados
        stmt = (
            select(TimeSeriesMetadataModel, DataTimeSeriesModel)
            .join(DataTimeSeriesModel, TimeSeriesMetadataModel.id == DataTimeSeriesModel.metadata_id)
            .where(TimeSeriesMetadataModel.simulation_run_id == simulation_id)
            .where(TimeSeriesMetadataModel.series_type == "ENS")
        )
        
        results = self.session.execute(stmt).all()
        
        ens_dict = {}
        for metadata, data in results:
            ens_dict[metadata.name] = {
                "unit_y": metadata.unit_y,
                "values": data.values
            }
            
        return ens_dict
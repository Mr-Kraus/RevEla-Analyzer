import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.region_model import RegionModel

class AnalyticalIndicatorRepository:
    """
    Repositório de leitura focado em extrair métricas, rankings e comparações 
    do banco de dados para a Camada Analítica (M03).
    """
    
    def __init__(self, session: Session):
        self.session = session

    def get_global_results(self, simulation_id: uuid.UUID) -> Optional[ReliabilityResultModel]:
        """Busca os indicadores globais de uma simulação específica."""
        stmt = select(ReliabilityResultModel).where(
            ReliabilityResultModel.simulation_run_id == simulation_id,
            ReliabilityResultModel.is_global == True
        )
        return self.session.execute(stmt).scalars().first()

    def get_bus_results(self, simulation_id: uuid.UUID) -> List[ReliabilityResultModel]:
        """Busca os indicadores de todas as barras para uma simulação."""
        stmt = select(ReliabilityResultModel).where(
            ReliabilityResultModel.simulation_run_id == simulation_id,
            ReliabilityResultModel.is_global == False
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_top_buses_by_indicator(self, simulation_id: uuid.UUID, indicator_column: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ranking Engine Base: Retorna as piores barras baseadas em um indicador específico (ex: 'epns').
        Cruza os dados com a tabela BusModel para trazer o nome/external_id da barra.
        """
        # Garante que a coluna solicitada existe no modelo para evitar SQL Injection
        if not hasattr(ReliabilityResultModel, indicator_column):
            raise ValueError(f"Indicador '{indicator_column}' não existe no modelo.")

        column_attr = getattr(ReliabilityResultModel, indicator_column)
        
        stmt = (
            select(
                BusModel.external_id,
                BusModel.name,
                column_attr.label("indicator_value")
            )
            .join(BusModel, ReliabilityResultModel.bus_external_id == BusModel.external_id)
            .where(
                ReliabilityResultModel.simulation_run_id == simulation_id,
                ReliabilityResultModel.is_global == False
            )
            .order_by(desc(column_attr))
            .limit(limit)
        )
        
        results = self.session.execute(stmt).all()
        
        # Converte as tuplas retornadas pelo SQLAlchemy em dicionários amigáveis
        return [
            {
                "bus_external_id": row.external_id,
                "bus_name": row.name,
                "value": row.indicator_value
            }
            for row in results
        ]
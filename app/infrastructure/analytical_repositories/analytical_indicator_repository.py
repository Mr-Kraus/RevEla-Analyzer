import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.infrastructure.database.models.system_model import SystemModel

class AnalyticalIndicatorRepository:
    """
    Repositório de leitura focado em extrair métricas, rankings e comparações 
    do banco de dados para a Camada Analítica (M03).
    """
    
    def __init__(self, session: Session):
        self.session = session

    def get_global_results(self, simulation_id: uuid.UUID) -> Optional[ReliabilityResultModel]:
        stmt = select(ReliabilityResultModel).where(
            ReliabilityResultModel.simulation_run_id == simulation_id,
            ReliabilityResultModel.is_global == True
        )
        return self.session.execute(stmt).scalars().first()

    def get_bus_results(self, simulation_id: uuid.UUID) -> List[ReliabilityResultModel]:
        stmt = select(ReliabilityResultModel).where(
            ReliabilityResultModel.simulation_run_id == simulation_id,
            ReliabilityResultModel.is_global == False
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_top_buses_by_indicator(self, simulation_id: uuid.UUID, indicator_column: str, limit: int = 1500) -> List[Dict[str, Any]]:
        # Garante que a coluna esteja em minúsculo para evitar ValueError
        indicator_column = indicator_column.lower()
        if not hasattr(ReliabilityResultModel, indicator_column):
            raise ValueError(f"Indicador '{indicator_column}' não existe no modelo.")

        column_attr = getattr(ReliabilityResultModel, indicator_column)
        
        # Query Blindada: Faz a ponte via SystemModel usando o system_id correto!
        stmt = (
            select(
                BusModel.external_id.label("bus_external_id"),
                BusModel.name.label("bus_name"),
                RegionModel.external_id.label("region_external_id"),
                RegionModel.name.label("region_name"),
                column_attr.label("indicator_value")
            )
            .select_from(ReliabilityResultModel)
            .join(SimulationRunModel, ReliabilityResultModel.simulation_run_id == SimulationRunModel.id)
            .join(SystemModel, SystemModel.case_id == SimulationRunModel.case_id)
            # A MÁGICA ACONTECE AQUI: Cruzamento exato usando system_id
            .join(BusModel, (ReliabilityResultModel.bus_external_id == BusModel.external_id) & (BusModel.system_id == SystemModel.id))
            .outerjoin(RegionModel, BusModel.region_id == RegionModel.id)
            .where(
                ReliabilityResultModel.simulation_run_id == simulation_id,
                ReliabilityResultModel.is_global == False,
                column_attr > 0
            )
            .order_by(desc(column_attr))
        )
        
        if limit:
            stmt = stmt.limit(limit)
            
        results = self.session.execute(stmt).all()
        
        return [
            {
                "bus_external_id": str(row.bus_external_id),
                "bus_name": str(row.bus_name),
                "region_external_id": str(row.region_external_id) if row.region_external_id else "0",
                "region_name": str(row.region_name) if row.region_name else "Região Desconhecida",
                "value": float(row.indicator_value)
            }
            for row in results
        ]
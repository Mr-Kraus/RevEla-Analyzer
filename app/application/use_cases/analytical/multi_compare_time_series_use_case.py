import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.infrastructure.database.models.time_series_metadata_model import TimeSeriesMetadataModel
from app.infrastructure.database.models.data_time_series_model import DataTimeSeriesModel

class MultiCompareTimeSeriesUseCase:
    def __init__(self, session: Session):
        self.session = session

    def execute(self, case_ids: List[uuid.UUID], series_type: str = "Load") -> Dict[str, Any]:
        # Busca as simulações atreladas aos casos
        simulations = self.session.query(SimulationRunModel.id, SimulationRunModel.case_id)\
            .filter(SimulationRunModel.case_id.in_(case_ids)).all()
        
        sim_case_map = {str(sim.id): str(sim.case_id) for sim in simulations}
        sim_ids = list(sim_case_map.keys())

        # Busca os Metadados e os Dados (fazendo JOIN)
        results = self.session.query(TimeSeriesMetadataModel, DataTimeSeriesModel)\
            .join(DataTimeSeriesModel, DataTimeSeriesModel.metadata_id == TimeSeriesMetadataModel.id)\
            .filter(
                TimeSeriesMetadataModel.simulation_run_id.in_(sim_ids),
                TimeSeriesMetadataModel.series_type == series_type
            ).all()

        # Agrupa os resultados por case_id
        grouped_data = {str(cid): [] for cid in case_ids}
        
        for meta, data in results:
            case_id = sim_case_map.get(str(meta.simulation_run_id))
            if case_id:
                grouped_data[case_id].append({
                    "series_id": str(meta.id),
                    "series_name": meta.name,
                    "unit_y": meta.unit_y,
                    "values": data.values
                })

        return {"time_series": grouped_data}
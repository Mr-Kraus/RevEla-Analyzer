import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel

class AnalyticalCaseRepository:
    """Repositório de leitura (M03-F04) para buscar rodadas de simulação e cenários comparativos."""
    
    def __init__(self, session: Session):
        self.session = session

    def get_simulations_by_case(self, case_id: uuid.UUID) -> List[Dict[str, Any]]:
        stmt = select(SimulationRunModel).where(SimulationRunModel.case_id == case_id)
        sims = self.session.execute(stmt).scalars().all()
        return [{"simulation_id": s.id, "analysis_type": s.analysis_type} for s in sims]

    def get_case_metadata(self, simulation_id: uuid.UUID) -> Dict[str, str]:
        """Busca o nome do caso ao qual a simulação pertence."""
        stmt = (
            select(CaseModel.external_name)
            .join(SimulationRunModel, SimulationRunModel.case_id == CaseModel.id)
            .where(SimulationRunModel.id == simulation_id)
        )
        case_name = self.session.execute(stmt).scalar_one_or_none()
        return {"case_name": case_name or "Unknown"}
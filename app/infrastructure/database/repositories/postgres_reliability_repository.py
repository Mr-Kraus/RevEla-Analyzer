from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.reliability_result import ReliabilityResult
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel

class PostgresReliabilityRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_all(self, results: List[ReliabilityResult]) -> None:
        """Salva uma lista de resultados de confiabilidade no banco de dados em lote."""
        models = [
            ReliabilityResultModel(
                id=r.id,
                simulation_run_id=r.simulation_run_id,
                is_global=r.is_global,
                bus_external_id=r.bus_external_id,
                lolp=r.lolp,
                lole=r.lole,
                epns=r.epns,
                eens=r.eens,
                lolf=r.lolf,
                lold=r.lold,
                lolc=r.lolc,
                confidence_intervals=getattr(r, 'confidence_intervals', {})
            ) for r in results
        ]
        self.session.add_all(models)
        # O commit não é feito aqui! Será feito no UseCase (Fase 8).
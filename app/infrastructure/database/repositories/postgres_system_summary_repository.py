import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.infrastructure.database.models.system_summary_model import SystemSummaryModel

class PostgresSystemSummaryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_simulation_id(self, simulation_run_id: uuid.UUID) -> SystemSummaryModel:
        stmt = select(SystemSummaryModel).where(SystemSummaryModel.simulation_run_id == simulation_run_id)
        return self.session.execute(stmt).scalar_one_or_none()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from app.api.dependencies.db_dependency import get_db
from app.api.schemas.base_schema import APIResponse
from app.infrastructure.database.repositories.postgres_system_summary_repository import PostgresSystemSummaryRepository
from app.application.use_cases.analytical.get_system_summary_use_case import GetSystemSummaryUseCase

# Importamos o modelo da simulação para poder fazer a conversão case_id -> simulation_id
from app.infrastructure.database.models.simulation_model import SimulationRunModel 

router = APIRouter(prefix="/analysis", tags=["Analysis - System Summary"])

@router.get("/case/{case_id}/system-summary", response_model=APIResponse)
def get_system_summary(case_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retorna os dados do System Summary formatados para a tabela e o gráfico de geração (Rosquinha).
    Busca automaticamente a simulação pai atrelada ao case_id.
    """
    # 1. Busca a simulação (SimulationRun) associada a este caso
    stmt = select(SimulationRunModel).where(SimulationRunModel.case_id == case_id).order_by(SimulationRunModel.imported_at.desc())
    simulation = db.execute(stmt).scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Nenhuma simulação encontrada para este caso.")

    # 2. Executa o Use Case com o simulation_id correto
    repo = PostgresSystemSummaryRepository(db)
    use_case = GetSystemSummaryUseCase(repo)
    
    try:
        response_dto = use_case.execute(simulation.id)
        
        return APIResponse(
            success=True,
            data=response_dto.model_dump(),
            message="System Summary carregado com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
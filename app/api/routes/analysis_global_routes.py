from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
from typing import Optional, List

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel
from app.api.schemas.base_schema import APIResponse

from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.application.use_cases.analytical.get_global_indicators_use_case import GetGlobalIndicatorsUseCase

router = APIRouter(prefix="/analysis", tags=["Analysis - Global"])

@router.get("/global/{simulation_id}", response_model=APIResponse)
def get_global_analysis(
    simulation_id: uuid.UUID,
    indicators: Optional[List[str]] = Query(None, description="Lista de indicadores (ex: LOLE, EPNS)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retorna os indicadores globais do sistema para uma dada simulação.
    """
    repo = AnalyticalIndicatorRepository(db)
    use_case = GetGlobalIndicatorsUseCase(repo)
    
    try:
        # CORREÇÃO: Removido o argumento 'indicators' que não existia no UseCase do M03
        result_dto = use_case.execute(
            simulation_id=simulation_id,
            case_name="API Request"
        )
        
        return APIResponse(
            success=True,
            data=result_dto.model_dump(),
            message="Indicadores globais calculados com sucesso."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
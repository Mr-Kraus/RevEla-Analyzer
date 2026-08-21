from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from typing import List
from pydantic import BaseModel

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel
from app.api.schemas.base_schema import APIResponse

from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.application.use_cases.analytical.compare_cases_use_case import CompareCasesUseCase

router = APIRouter(prefix="/analysis/compare", tags=["Analysis - Comparison"])

# Schema de Entrada Específico para o POST
class CompareRequest(BaseModel):
    baseline_simulation_id: uuid.UUID
    target_simulation_ids: List[uuid.UUID]
    indicator: str

@router.post("", response_model=APIResponse)
def compare_simulations(
    request: CompareRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Compara uma simulação base (baseline) contra N outras simulações (targets) para um indicador.
    """
    repo = AnalyticalIndicatorRepository(db)
    use_case = CompareCasesUseCase(repo)
    
    try:
        # Pega apenas o primeiro target para a comparação de 1 para 1 (O UseCase atual do M03 só faz 1x1)
        # Se você atualizou o UseCase no M03 para aceitar listas (M03-F09), ajuste aqui!
        if not request.target_simulation_ids:
             raise ValueError("Pelo menos um target_simulation_id deve ser fornecido.")
             
        target_id = request.target_simulation_ids[0]
        
        result_dto = use_case.execute(
            request.baseline_simulation_id,
            target_id,
            request.indicator
        )
        
        return APIResponse(
            success=True,
            data=result_dto.model_dump(),
            message="Comparação matemática realizada com sucesso."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
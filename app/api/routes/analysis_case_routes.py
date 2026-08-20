from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel
from app.api.schemas.base_schema import APIResponse

from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.application.use_cases.analytical.get_case_analysis_use_case import GetCaseAnalysisUseCase

router = APIRouter(prefix="/analysis/case", tags=["Analysis - Detailed Case"])

@router.get("/{simulation_id}", response_model=APIResponse)
def get_case_analysis(
    simulation_id: uuid.UUID,
    indicator: str = Query(..., description="Indicador obrigatório para pivotar a análise (ex: EPNS)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retorna a análise detalhada de um caso, incluindo quebras por região, barra e rankings.
    """
    repo = AnalyticalIndicatorRepository(db)
    use_case = GetCaseAnalysisUseCase(repo)
    
    try:
        # CORREÇÃO: Removendo top_n e filters para respeitar a assinatura original do M03
        result_dto = use_case.execute(
            simulation_id=simulation_id,
            indicator=indicator
        )
        
        return APIResponse(
            success=True,
            data=result_dto.model_dump(),
            message=f"Análise detalhada do indicador {indicator} calculada."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{simulation_id}/topology", response_model=APIResponse)
def get_simulation_topology(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retorna os nós (barras) e arestas (linhas de transmissão) para o Grafo Interativo da Aba 4.
    """
    repo = AnalyticalIndicatorRepository(db)
    
    try:
        # Busca os dados de nós e arestas diretamente do repositório
        topology_data = repo.get_topology(simulation_id)
        
        return APIResponse(
            success=True,
            data=topology_data,
            message="Topologia da rede carregada com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
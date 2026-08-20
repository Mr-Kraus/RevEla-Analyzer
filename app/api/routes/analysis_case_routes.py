from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
from app.infrastructure.analytical_repositories.analytical_global_repository import AnalyticalGlobalRepository

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel
from app.api.schemas.base_schema import APIResponse
from app.infrastructure.analytical_repositories.analytical_topology_repository import AnalyticalTopologyRepository
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
    """Retorna os nós e arestas reais para a Aba 4."""
    # CORREÇÃO: Chamando o repositório de Topologia (que possui a tabela de equipamentos)
    repo = AnalyticalTopologyRepository(db)
    
    try:
        topology_data = repo.get_topology(simulation_id)
        return APIResponse(
            success=True,
            data=topology_data,
            message="Topologia da rede carregada com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{simulation_id}/transmission", response_model=APIResponse)
def get_case_transmission_analysis(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retorna o inventário detalhado e indicadores de transmissão (Linhas e Transformadores).
    """
    repo = AnalyticalTopologyRepository(db)
    try:
        data = repo.get_transmission_details(simulation_id)
        return APIResponse(
            success=True,
            data=data,
            message="Análise de transmissão carregada com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{simulation_id}/generation", response_model=APIResponse)
def get_case_generation_analysis(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retorna o inventário detalhado e indicadores do Parque Gerador.
    """
    repo = AnalyticalTopologyRepository(db)
    try:
        data = repo.get_generation_details(simulation_id)
        return APIResponse(
            success=True,
            data=data,
            message="Análise de geração carregada com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/{case_id}/global", response_model=APIResponse)
def get_case_global_analysis(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    repo = AnalyticalGlobalRepository(db)
    try:
        data = repo.get_global_metrics(case_id)
        return APIResponse(success=True, data=data, message="Análise global carregada.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
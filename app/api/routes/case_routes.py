from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import uuid
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from sqlalchemy import select

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel
from app.api.schemas.base_schema import APIResponse
from app.api.schemas.case_schema import CaseCreateRequest, CaseResponse
from app.application.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Case Management"])

@router.post("", response_model=APIResponse[CaseResponse])
def create_case(
    request: CaseCreateRequest, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # Proteção!
):
    """Cria um novo registro de caso (Necessita Autenticação)."""
    service = CaseService(db)
    new_case = service.create_case(request)
    
    return APIResponse(
        success=True, 
        data=CaseResponse.model_validate(new_case), 
        message="Caso registrado com sucesso."
    )

@router.get("", response_model=APIResponse[List[CaseResponse]])
def list_cases(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # Proteção!
):
    """Lista todos os casos cadastrados no sistema (Necessita Autenticação)."""
    service = CaseService(db)
    cases = service.list_all_cases()
    
    # Converte os modelos do banco para o schema de saída
    data = [CaseResponse.model_validate(c) for c in cases]
    return APIResponse(success=True, data=data, message="Listagem concluída.")

@router.get("/{case_id}/simulations")
def get_case_simulations(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Lista todas as execuções de simulação associadas a um caso."""
    stmt = select(SimulationRunModel).where(SimulationRunModel.case_id == case_id)
    simulations = db.execute(stmt).scalars().all()
    
    # Retorna uma lista simples para copiarmos o ID rapidamente
    data = [
        {
            "simulation_id": sim.id, 
            "imported_at": sim.imported_at
        } for sim in simulations
    ]
    
    return APIResponse(success=True, data=data, message="Simulações recuperadas.")
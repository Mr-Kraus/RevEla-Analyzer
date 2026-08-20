from pydantic import BaseModel
from typing import List, Optional

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

@router.delete("/{case_id}", response_model=APIResponse)
def delete_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Exclui um caso e todos os seus dados associados (Topologia, Resultados, Arquivos) em cascata.
    """
    case_service = CaseService(db)
    
    try:
        success = case_service.delete_case(case_id)
        if not success:
            raise HTTPException(status_code=404, detail="Caso não encontrado.")
            
        return APIResponse(
            success=True,
            data={"deleted_case_id": str(case_id)},
            message="Caso excluído com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir caso: {str(e)}")
    
class CaseUpdateSchema(BaseModel):
    display_name: str

class RegionAliasSchema(BaseModel):
    id: uuid.UUID
    alias: Optional[str] = None

# 1. Atualizar o nome do Caso
@router.patch("/{case_id}", response_model=APIResponse)
def update_case_name(
    case_id: uuid.UUID,
    payload: CaseUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    case_model = db.get(CaseModel, case_id)
    if not case_model:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")
    
    case_model.display_name = payload.display_name
    db.commit()
    return APIResponse(success=True, data={"id": str(case_id)}, message="Nome do caso atualizado.")

# 2. Listar Regiões de um Caso
@router.get("/{case_id}/regions", response_model=APIResponse)
def get_case_regions(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    stmt = (
        select(RegionModel.id, RegionModel.external_id, RegionModel.name, RegionModel.alias)
        .join(SystemModel, RegionModel.system_id == SystemModel.id)
        .where(SystemModel.case_id == case_id)
    )
    results = db.execute(stmt).all()
    regions = [
        {"id": str(r.id), "external_id": r.external_id, "name": r.name, "alias": r.alias or ""}
        for r in results
    ]
    return APIResponse(success=True, data=regions, message="Regiões carregadas.")

# 3. Atualizar Apelidos das Regiões em Lote
@router.put("/{case_id}/regions", response_model=APIResponse)
def update_region_aliases(
    case_id: uuid.UUID,
    payload: List[RegionAliasSchema],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    for item in payload:
        region = db.get(RegionModel, item.id)
        if region:
            region.alias = item.alias.strip() if item.alias else None
    db.commit()
    return APIResponse(success=True, data={}, message="Apelidos das regiões atualizados.")
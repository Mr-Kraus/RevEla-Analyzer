import uuid
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.api.schemas.base_schema import APIResponse
from app.api.schemas.case_schema import CaseCreateRequest, CaseResponse
from app.application.pipelines.case_ingestion_pipeline import CaseIngestionPipeline
from app.application.services.case_service import CaseService
from app.ingestion.discovery.case_discovery import CaseDiscovery

from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.infrastructure.database.models.security_model import UserModel
from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.repositories.postgres_case_repository import PostgresCaseRepository

router = APIRouter(prefix="/cases", tags=["Case Management"])

@router.post("", response_model=APIResponse)
def discover_and_create_case(
    request: CaseCreateRequest, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    discovery_service = CaseDiscovery()
    candidate = discovery_service.discover(Path(request.source_path))
    
    if candidate.has_errors():
        return APIResponse(
            success=False,
            data={"errors": candidate.errors},
            message="Falha crítica na descoberta do diretório."
        )
        
    templates_names = [p.name for p in candidate.system_templates]
    results_names = [p.name for p in candidate.result_directories]
    
    case_repo = PostgresCaseRepository(db)
    new_case = case_repo.create(
        external_name=candidate.case_name,
        display_name=candidate.case_name,
        source_path=str(candidate.root_path),
        status="DISCOVERED"
    )
    db.commit()
    
    response_data = {
        "id": str(new_case.id),
        "external_name": new_case.external_name,
        "display_name": new_case.display_name,
        "source_path": new_case.source_path,
        "status": new_case.status,
        "created_at": new_case.created_at.isoformat(),
        "discovery_details": {
            "system_templates": templates_names,
            "result_directories": results_names,
            "warnings": candidate.warnings,
            "errors": candidate.errors
        }
    }
    
    return APIResponse(
        success=True,
        data=response_data,
        message="Caso descoberto com sucesso. Aguardando seleção de templates e resultados pelo usuário."
    )

@router.get("", response_model=APIResponse[List[CaseResponse]])
def list_cases(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = CaseService(db)
    cases = service.list_all_cases()
    data = [CaseResponse.model_validate(c) for c in cases]
    return APIResponse(success=True, data=data, message="Listagem concluída.")

@router.get("/{case_id}/simulations")
def get_case_simulations(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    stmt = select(SimulationRunModel).where(SimulationRunModel.case_id == case_id)
    simulations = db.execute(stmt).scalars().all()
    data = [{"simulation_id": sim.id, "imported_at": sim.imported_at} for sim in simulations]
    return APIResponse(success=True, data=data, message="Simulações recuperadas.")

@router.delete("/{case_id}", response_model=APIResponse)
def delete_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    case_service = CaseService(db)
    try:
        success = case_service.delete_case(case_id)
        if not success:
            raise HTTPException(status_code=404, detail="Caso não encontrado.")
        return APIResponse(success=True, data={"deleted_case_id": str(case_id)}, message="Caso excluído com sucesso.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir caso: {str(e)}")
    
class CaseUpdateSchema(BaseModel):
    display_name: str

class RegionAliasSchema(BaseModel):
    id: uuid.UUID
    alias: Optional[str] = None

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
    regions = [{"id": str(r.id), "external_id": r.external_id, "name": r.name, "alias": r.alias or ""} for r in results]
    return APIResponse(success=True, data=regions, message="Regiões carregadas.")

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

class CaseImportRequest(BaseModel):
    software_version: str = "RELEVA"
    selected_template: str = ""
    selected_results: str = ""

@router.post("/{case_id}/import", response_model=APIResponse)
def import_case_files(
    case_id: uuid.UUID,
    payload: CaseImportRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    case_model = db.get(CaseModel, case_id)
    if not case_model:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")

    pipeline = CaseIngestionPipeline(db)
    simulation_run_id = uuid.uuid4()
    
    success = pipeline.run(
        case_id=case_id, 
        simulation_run_id=simulation_run_id, 
        case_folder=Path(case_model.source_path),
        software_version=payload.software_version
    )
    
    if success:
        case_model.status = "READY"
        db.commit()
        return APIResponse(success=True, data={}, message="Ingestão concluída com sucesso.")
    else:
        case_model.status = "FAILED"
        db.commit()
        return APIResponse(success=False, data={}, message="Falha durante a ingestão dos dados.")
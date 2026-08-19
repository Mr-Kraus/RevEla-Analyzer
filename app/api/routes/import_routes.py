from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies.db_dependency import get_db
from app.api.dependencies.auth_dependency import get_current_user
from app.infrastructure.database.models.security_model import UserModel
from app.api.schemas.base_schema import APIResponse
from app.api.schemas.import_schema import ImportJobResponse
from app.application.services.import_service import ImportService
from app.infrastructure.database.models.import_job_model import ImportJobModel
from sqlalchemy import select

router = APIRouter(prefix="/cases", tags=["Ingestion & Import"])

@router.post("/{case_id}/import", response_model=APIResponse[ImportJobResponse])
def start_case_import(
    case_id: uuid.UUID,
    background_tasks: BackgroundTasks, # FastAPI injeta isso sozinho!
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Inicia a importação dos arquivos CSV de um Caso em segundo plano."""
    service = ImportService(db)
    try:
        job = service.start_import(case_id, background_tasks)
        return APIResponse(
            success=True, 
            data=ImportJobResponse.model_validate(job), 
            message="Importação iniciada com sucesso. Acompanhe pelo Job ID."
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/jobs/{job_id}", response_model=APIResponse[ImportJobResponse])
def get_job_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Consulta o status atual de uma tarefa de importação."""
    job = db.execute(select(ImportJobModel).where(ImportJobModel.id == job_id)).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
        
    return APIResponse(success=True, data=ImportJobResponse.model_validate(job), message="Status recuperado.")
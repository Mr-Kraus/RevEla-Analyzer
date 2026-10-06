from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies.db_dependency import get_db
from app.api.schemas.base_schema import APIResponse
from app.domain.enums.granularity_enum import TimeSeriesGranularity

from app.infrastructure.database.repositories.postgres_time_series_repository import PostgresTimeSeriesRepository
from app.infrastructure.database.repositories.postgres_case_repository import PostgresCaseRepository
from app.application.use_cases.analytical.get_ens_aggregation_use_case import GetENSAggregationUseCase

router = APIRouter(prefix="/analysis", tags=["Analysis - Time Series"])

@router.get("/case/{case_id}/simulation/{simulation_id}/ens", response_model=APIResponse)
def get_ens_aggregated(
    case_id: uuid.UUID,
    simulation_id: uuid.UUID,
    granularity: TimeSeriesGranularity = Query(TimeSeriesGranularity.MONTHLY, description="Granularidade: hourly, weekly, monthly, yearly"),
    db: Session = Depends(get_db)
):
    """
    Retorna as três séries de ENS (Geração, Transmissão, Mista) calculando a média
    de acordo com a granularidade solicitada.
    """
    ts_repo = PostgresTimeSeriesRepository(db)
    case_repo = PostgresCaseRepository(db)
    use_case = GetENSAggregationUseCase(ts_repo, case_repo)
    
    try:
        response_dto = use_case.execute(case_id, simulation_id, granularity)
        
        return APIResponse(
            success=True,
            data=response_dto.model_dump(),
            message=f"Séries de ENS agregadas por {granularity.value} calculadas com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
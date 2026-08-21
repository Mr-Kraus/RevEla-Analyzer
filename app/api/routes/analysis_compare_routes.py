from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies.db_dependency import get_db
from app.application.dto.analytical_dtos import MultiCompareRequestDTO, MultiCompareResponseDTO
from app.application.use_cases.analytical.multi_compare_cases_use_case import MultiCompareCasesUseCase

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/multi-compare", response_model=MultiCompareResponseDTO)
def multi_compare_cases(
    payload: MultiCompareRequestDTO,
    db: Session = Depends(get_db)
):
    """Retorna dados de múltiplos casos em lote (Global, Regiões ou Barras)."""
    try:
        use_case = MultiCompareCasesUseCase(db)
        return use_case.execute(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
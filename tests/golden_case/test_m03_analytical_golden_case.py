import pytest
import uuid
from pathlib import Path

from app.application.pipelines.case_ingestion_pipeline import CaseIngestionPipeline
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.application.use_cases.analytical.get_global_indicators_use_case import GetGlobalIndicatorsUseCase
from app.application.use_cases.analytical.get_case_analysis_use_case import GetCaseAnalysisUseCase
from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from datetime import datetime

GOLDEN_CASE_PATH = Path("tests/fixtures/C01")

def test_m03_analytical_golden_case(db_session):
    """
    Fase M03.16: Golden Case Analítico.
    Ingere o C01 (caso já não esteja) e valida formalmente as saídas da camada de negócio.
    """
    if not GOLDEN_CASE_PATH.exists():
        pytest.skip("Golden Case C01 não encontrado em tests/fixtures/C01")

    case_id = uuid.uuid4()
    sim_id = uuid.uuid4()

    # Setup dos pais no banco
    db_session.add(CaseModel(id=case_id, external_name="C01", display_name="Golden C01", source_path=str(GOLDEN_CASE_PATH)))
    db_session.add(SimulationRunModel(id=sim_id, case_id=case_id, imported_at=datetime.now()))
    db_session.commit()

    # Executa a ingestão (M02) para ter dados reais no banco
    pipeline = CaseIngestionPipeline(session=db_session)
    assert pipeline.run(case_id=case_id, simulation_run_id=sim_id, case_folder=GOLDEN_CASE_PATH) is True

    # Validação Analítica via Use Cases (M03.11)
    repo = AnalyticalIndicatorRepository(db_session)
    
    # 1. Valida Global Indicators (LOLE, EPNS do C01)
    global_uc = GetGlobalIndicatorsUseCase(repo)
    global_dto = global_uc.execute(sim_id, case_name="C01")
    
    assert "LOLE" in global_dto.indicators
    assert "EPNS" in global_dto.indicators
    assert global_dto.indicators["LOLE"].value > 0.0

    # 2. Valida Case Analysis e Rankings (Top Barras e Regiões)
    case_uc = GetCaseAnalysisUseCase(repo)
    case_dto = case_uc.execute(sim_id, indicator="epns", case_name="C01")
    
    assert case_dto.simulation_id == sim_id
    assert len(case_dto.top_critical_buses.top_elements) > 0
   
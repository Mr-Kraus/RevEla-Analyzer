import pytest
import uuid
from datetime import datetime
from pathlib import Path

from app.application.pipelines.case_ingestion_pipeline import CaseIngestionPipeline
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.infrastructure.analytical_repositories.analytical_topology_repository import AnalyticalTopologyRepository
from app.application.use_cases.analytical.get_global_indicators_use_case import GetGlobalIndicatorsUseCase
from app.application.use_cases.analytical.get_case_analysis_use_case import GetCaseAnalysisUseCase

from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.domain.analytics.analytical_validator import AnalyticalValidator

GOLDEN_CASE_PATH = Path("tests/fixtures/C01")

def test_m03_full_analytical_golden_case(db_session):
    """
    Fases M03-F11, F12 e F13: Golden Case e End-to-End.
    Engloba a gravação, a validação de consistência e a extração completa.
    """
    if not GOLDEN_CASE_PATH.exists():
        pytest.skip("Golden Case C01 não encontrado.")

    case_id = uuid.uuid4()
    sim_id = uuid.uuid4()

    # 1. SETUP: Insere Case e Simulação
    db_session.add(CaseModel(id=case_id, external_name="C01", display_name="Golden C01", source_path=str(GOLDEN_CASE_PATH)))
    db_session.add(SimulationRunModel(id=sim_id, case_id=case_id, imported_at=datetime.now()))
    db_session.commit()

    # 2. INGESTÃO: Roda a pipeline para popular o banco
    pipeline = CaseIngestionPipeline(session=db_session)
    assert pipeline.run(case_id=case_id, simulation_run_id=sim_id, case_folder=GOLDEN_CASE_PATH) is True

    # 3. REPOSITÓRIOS ANALÍTICOS (M03-F03 e F04)
    ind_repo = AnalyticalIndicatorRepository(db_session)
    topo_repo = AnalyticalTopologyRepository(db_session)

   # 4. VALIDAÇÃO DE CONSISTÊNCIA (M03-F10)
    raw_buses = ind_repo.get_bus_results(sim_id)
    raw_buses_dict = [
        {
            "bus_external_id": b.bus_external_id,
            "lolp": b.lolp,
            "lole": b.lole,
            "epns": b.epns,
            "eens": b.eens,
            "lolf": b.lolf,
            "lold": b.lold,
            "lolc": b.lolc
        } 
        for b in raw_buses
    ]
    audit_report = AnalyticalValidator.audit_batch_results(raw_buses_dict)
    
    # Se quiser ver qual erro deu no console caso falhe de novo, podemos printar:
    if not audit_report["is_consistent"]:
        print(f"ERROS DO VALIDADOR: {audit_report['details'][:3]}") # Printa os 3 primeiros erros
        
    assert audit_report["is_consistent"] is True, "Inconsistências encontradas nos resultados das barras!"

    # 5. USE CASES E DTOs (M03-F12)
    # 5.1 Global Indicators
    global_uc = GetGlobalIndicatorsUseCase(ind_repo)
    global_dto = global_uc.execute(sim_id, case_name="C01")
    assert "LOLE" in global_dto.indicators
    assert "EPNS" in global_dto.indicators
    assert global_dto.indicators["LOLE"].value >= 0.0

    # 5.2 Case Analysis (Rankings de Barras)
    case_uc = GetCaseAnalysisUseCase(ind_repo)
    case_dto = case_uc.execute(sim_id, indicator="epns", case_name="C01")
    assert len(case_dto.top_critical_buses.top_elements) > 0

    # 6. TESTE DE COBERTURA DE EXCEÇÕES (M03-F13)
    # Deve lidar graciosamente ou levantar erro esperado com simulação fantasma
    fake_sim_id = uuid.uuid4()
    fake_dto = global_uc.execute(fake_sim_id, case_name="Ghost")
    assert len(fake_dto.indicators) == 0

    # 7. TESTE TOPOLÓGICO ESPECIALIZADO (M03-F05 e F06)
    generators = topo_repo.get_generators(sim_id)
    assert len(generators) > 0
    
    # Valida se o formato do DTO topológico está correto
    assert "capacity_mva" in generators[0]
import uuid
from datetime import datetime
from app.infrastructure.analytical_repositories.analytical_indicator_repository import AnalyticalIndicatorRepository
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel

def test_analytical_repository_queries(db_session):
    case_id = uuid.uuid4()
    sim_id = uuid.uuid4()
    
    # 1. SETUP: Insere os Pais para não tomar erro de Foreign Key
    db_session.add(CaseModel(id=case_id, external_name="MOCK", display_name="Mock Case", source_path=""))
    db_session.add(SimulationRunModel(id=sim_id, case_id=case_id, imported_at=datetime.now()))
    db_session.commit()

    # 2. Insere um registro global simulado para teste de integração
    mock_res = ReliabilityResultModel(
        id=uuid.uuid4(),
        simulation_run_id=sim_id,
        is_global=True,
        lolp=0.05,
        lole=45.0,
        epns=2.1,
        eens=18.5,
        lolf=10.0,
        lold=1.5,
        lolc=0.0
    )
    db_session.add(mock_res)
    db_session.commit()

    # 3. Testa o Repositório
    repo = AnalyticalIndicatorRepository(db_session)
    result = repo.get_global_results(sim_id)

    assert result is not None
    assert float(result.lole) == 45.0
    assert result.is_global is True
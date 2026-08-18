import pytest
import uuid
from datetime import datetime, timezone
from app.domain.entities.case import Case
from app.domain.entities.simulation_run import SimulationRun
from app.domain.entities.system_topology import System
from app.infrastructure.database.repositories.postgres_case_repository import PostgresCaseRepository
from app.infrastructure.database.repositories.postgres_simulation_run_repository import PostgresSimulationRunRepository
from app.infrastructure.database.repositories.postgres_system_repository import PostgresSystemRepository

def test_simulation_run_and_system_crud(db_session):
    case_repo = PostgresCaseRepository(db_session)
    sim_repo = PostgresSimulationRunRepository(db_session)
    sys_repo = PostgresSystemRepository(db_session)

    # 1. Setup: Criar um caso pai para satisfazer a Chave Estrangeira
    case_id = uuid.uuid4()
    case = Case(id=case_id, external_name="C03_Test", display_name="C03", source_path="/dummy")
    case_repo.save(case)

    # 2. Testar Inserção e Busca de SimulationRun
    sim_id = uuid.uuid4()
    sim_run = SimulationRun(
        id=sim_id,
        case_id=case_id,
        analysis_type="STA",
        imported_at=datetime.now(timezone.utc)
    )
    saved_sim = sim_repo.save(sim_run)
    assert saved_sim.id == sim_id

    fetched_sim = sim_repo.get_by_id(sim_id)
    assert fetched_sim.analysis_type == "STA"

    # 3. Testar Inserção e Busca de System
    sys_id = uuid.uuid4()
    system = System(
        id=sys_id,
        case_id=case_id,
        simulation_run_id=sim_id,
        external_name="SYS_01",
        nominal_load_mw=150.5
    )
    saved_sys = sys_repo.save_system(system)
    assert saved_sys.id == sys_id

    fetched_sys = sys_repo.get_by_simulation(sim_id)
    assert fetched_sys.external_name == "SYS_01"
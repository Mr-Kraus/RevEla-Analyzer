import pytest
import uuid
from datetime import datetime
from pathlib import Path

from app.application.pipelines.case_ingestion_pipeline import CaseIngestionPipeline
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel

from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel

GOLDEN_CASE_PATH = Path("tests/fixtures/C01")

def test_m02_pipeline_end_to_end_with_real_db(db_session):
    """
    Fases 10 e 11 (CP-M02-01 a CP-M02-10): Teste oficial de integração.
    Garante que o Pipeline lê o C01 real e grava fisicamente no PostgreSQL.
    """
    if not GOLDEN_CASE_PATH.exists():
        pytest.skip("Golden Case C01 não encontrado em tests/fixtures/C01")

    # 1. SETUP: Criar e inserir os "Pais" reais no banco de dados para evitar erro de Foreign Key
    mock_case_id = uuid.uuid4()
    mock_sim_id = uuid.uuid4()

    # Criação do Caso 
    mock_case = CaseModel(
        id=mock_case_id,
        external_name="C01",
        display_name="Caso de Teste C01",
        source_path=str(GOLDEN_CASE_PATH)
    )
    db_session.add(mock_case)

    # CORREÇÃO: Adicionado o campo 'imported_at' obrigatório para a simulação
    mock_sim = SimulationRunModel(
        id=mock_sim_id,
        case_id=mock_case_id,
        imported_at=datetime.now()
    )
    db_session.add(mock_sim)

    # Commita os pais no banco ANTES de rodar o pipeline
    db_session.commit()

    # 2. EXECUÇÃO DO PIPELINE E2E
    pipeline = CaseIngestionPipeline(session=db_session)
    success = pipeline.run(
        case_id=mock_case_id,
        simulation_run_id=mock_sim_id,
        case_folder=GOLDEN_CASE_PATH
    )

    # 3. VERIFICAÇÃO (Fase 10: Buscando contagens reais no banco)
    assert success is True, "Pipeline falhou e retornou False."

    # CP-M02-01: Persistência de System
    system_count = db_session.query(SystemModel).filter_by(simulation_run_id=mock_sim_id).count()
    assert system_count == 1, "Deveria ter persistido exatamente 1 sistema para a simulação."

    # CP-M02-02: Persistência de Region
    region_count = db_session.query(RegionModel).count()
    assert region_count > 0, "Deveria ter persistido as regiões lidas do arquivo."

    # CP-M02-03: Persistência de Bus
    bus_count = db_session.query(BusModel).count()
    assert bus_count > 0, "Deveria ter persistido as barras no banco de dados."

    # CP-M02-04: Persistência de Generator (Nossas classes de geração)
    gen_count = db_session.query(GeneratorModel).count()
    assert gen_count > 0, "Deveria ter persistido os geradores/classes de geração."

    # CP-M02-07: Persistência de ReliabilityResult (Indicadores Globais e por Barra)
    results_count = db_session.query(ReliabilityResultModel).filter_by(simulation_run_id=mock_sim_id).count()
    assert results_count > 0, "Deveria ter persistido os indicadores matemáticos."
    
    # Verifica se os globais e os por-barra foram separados corretamente
    global_results = db_session.query(ReliabilityResultModel).filter_by(is_global=True).count()
    bus_results = db_session.query(ReliabilityResultModel).filter_by(is_global=False).count()
    
    assert global_results == 1, "Deve existir apenas 1 registro Global de resultados por simulação."
    assert bus_results > 0, "Devem existir múltiplos registros associados às Barras."
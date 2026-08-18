import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from app.ingestion.registry.dataset_registry import DatasetRegistry
from app.ingestion.registry.source_file_registrar import SourceFileRegistrar
from app.application.use_cases.register_source_files_use_case import RegisterSourceFilesUseCase
from app.ingestion.discovery.case_candidate import CaseCandidate

def test_source_file_registration_flow(tmp_path):
    """
    Testa: arquivo normal, arquivo 'grande' (comportamento de chunk), 
    cálculo de SHA-256, dataset conhecido e desconhecido.
    """
    # 1. Setup: Criando arquivos falsos no disco
    case_dir = tmp_path / "C01_Test"
    case_dir.mkdir()
    
    # Arquivo conhecido (Template System)
    file_known = case_dir / "Template System.csv"
    file_known.write_text("ID;Name;Type\n1;Bus1;Load")
    
    # Arquivo desconhecido
    file_unknown = case_dir / "Relatorio_Aleatorio.csv"
    file_unknown.write_text("Dados irrelevantes")
    
    # Arquivo "Grande" (escrevendo alguns chunks para simular tamanho)
    file_large = case_dir / "Simulation Config.csv"
    with open(file_large, "wb") as f:
        f.write(b"0" * (1024 * 10))  # 10 KB de zeros
        
    candidate = CaseCandidate(root_path=case_dir, case_name="C01_Test")
    candidate.detected_templates = [file_known]
    candidate.detected_result_files = [file_unknown, file_large]
    
    # 2. Configurando o Registry e o Registrar
    registry = DatasetRegistry()
    registrar = SourceFileRegistrar(registry)
    mock_repository = MagicMock()
    
    # Configura o mock do repositório para apenas retornar o que recebeu
    mock_repository.save.side_effect = lambda sf: sf 
    
    use_case = RegisterSourceFilesUseCase(mock_repository, registrar)
    
    # 3. Execução
    case_id = uuid4()
    saved_dtos = use_case.execute(candidate, case_id)
    
    # 4. Asserções
    assert len(saved_dtos) == 3
    assert mock_repository.save.call_count == 3
    
    # Valida arquivo conhecido
    dto_known = next(dto for dto in saved_dtos if dto.filename == "Template System.csv")
    assert dto_known.dataset_code == "TEMPLATE_SYSTEM"
    assert dto_known.size > 0
    assert len(dto_known.sha256) == 64 # Hash SHA-256 tem 64 caracteres hexadecimais
    
    # Valida arquivo desconhecido
    dto_unknown = next(dto for dto in saved_dtos if dto.filename == "Relatorio_Aleatorio.csv")
    assert dto_unknown.dataset_code == "UNKNOWN" # Registry não o encontrou
    
    # Valida arquivo "grande"
    dto_large = next(dto for dto in saved_dtos if dto.filename == "Simulation Config.csv")
    assert dto_large.size == 10240
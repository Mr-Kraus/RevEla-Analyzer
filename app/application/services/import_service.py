from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import uuid
import traceback
from pathlib import Path

from app.infrastructure.database.models.import_job_model import ImportJobModel
from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.case_model import CaseStatus 


from app.infrastructure.database.session.database import SessionLocal
from app.application.pipelines.case_ingestion_pipeline import CaseIngestionPipeline

class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def start_import(self, case_id: uuid.UUID, background_tasks) -> ImportJobModel:
        """Cria o Job de importação e delega o processamento pesado para o Background."""
        # 1. Verifica se o caso existe
        stmt = select(CaseModel).where(CaseModel.id == case_id)
        case = self.db.execute(stmt).scalar_one_or_none()
        if not case:
            raise ValueError("Caso não encontrado.")

        # 2. Cria o registro do Job
        new_job = ImportJobModel(case_id=case_id, status="RUNNING")
        self.db.add(new_job)
        
        # 3. Atualiza o status do Caso
        case.status = CaseStatus.INGESTING
        self.db.commit()
        self.db.refresh(new_job)

        # 4. Lança a tarefa em Background e devolve a resposta para o usuário imediatamente!
        background_tasks.add_task(self._process_ingestion, new_job.id, case_id, case.source_path)
        
        return new_job

    @staticmethod
    def _process_ingestion(job_id: uuid.UUID, case_id: uuid.UUID, source_path: str):
        """
        Esta função roda invisível no fundo!
        Como ela roda em outra Thread, precisamos abrir uma nova conexão com o banco.
        """
        db: Session = SessionLocal()
        try:
            job = db.execute(select(ImportJobModel).where(ImportJobModel.id == job_id)).scalar_one()
            case = db.execute(select(CaseModel).where(CaseModel.id == case_id)).scalar_one()

            # Chama a sua maravilhosa Pipeline do M02
            pipeline = CaseIngestionPipeline(session=db)
            
            # Aqui geramos um ID de simulação dinâmico e rodamos a ingestão na pasta do caso
            sim_id = uuid.uuid4()
            success = pipeline.run(case_id=case_id, simulation_run_id=sim_id, case_folder=Path(source_path))

            if success:
                job.status = "SUCCESS"
                case.status = CaseStatus.READY
            else:
                job.status = "FAILED"
                job.error_message = "Erro interno na validação da Ingestão."
                case.status = CaseStatus.FAILED

        except Exception as e:
            # Captura qualquer erro, grava no banco e evita que a API "morra"
            job.status = "FAILED"
            job.error_message = str(e)
            
            case = db.execute(select(CaseModel).where(CaseModel.id == case_id)).scalar_one()
            case.status = CaseStatus.FAILED
            print(f"ERRO DE INGESTÃO: {traceback.format_exc()}")
            
        finally:
            job.finished_at = datetime.now()
            db.commit()
            db.close() # Sempre fechar a porta ao sair!
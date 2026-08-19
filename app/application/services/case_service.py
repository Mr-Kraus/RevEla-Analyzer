from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from app.infrastructure.database.models.case_model import CaseModel

# IMPORTAÇÃO CORRIGIDA: Traga o CaseStatus (ajuste o caminho se no seu projeto ele estiver em outra pasta, como app.domain.enums)
from app.infrastructure.database.models.case_model import CaseStatus 

from app.api.schemas.case_schema import CaseCreateRequest

class CaseService:
    def __init__(self, db: Session):
        self.db = db

    def create_case(self, case_data: CaseCreateRequest) -> CaseModel:
        """Registra um novo caso no banco de dados com status PENDING."""
        new_case = CaseModel(
            external_name=case_data.external_name,
            display_name=case_data.display_name,
            source_path=case_data.source_path,
            # CORREÇÃO: Usando o objeto Enum do Python em vez de texto!
            status=CaseStatus.DISCOVERED 
        )
        self.db.add(new_case)
        self.db.commit()
        self.db.refresh(new_case)
        return new_case

    def list_all_cases(self) -> list[CaseModel]:
        """Retorna todos os casos cadastrados."""
        stmt = select(CaseModel).order_by(CaseModel.external_name)
        return list(self.db.execute(stmt).scalars().all())
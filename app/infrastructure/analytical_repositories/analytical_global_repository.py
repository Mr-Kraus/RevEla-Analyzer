import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel

class AnalyticalGlobalRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_global_metrics(self, case_id: uuid.UUID) -> dict:
        case = self.session.get(CaseModel, case_id)
        if not case:
            return {}

        # Busca Sistema e Simulação
        sys_info = self.session.execute(
            select(SystemModel, SimulationRunModel)
            .join(SimulationRunModel, SystemModel.simulation_run_id == SimulationRunModel.id)
            .where(SystemModel.case_id == case_id)
        ).first()

        if not sys_info:
            return {}
            
        system, sim_run = sys_info

        # Busca Resultados Globais
        global_res = self.session.execute(
            select(ReliabilityResultModel)
            .where(ReliabilityResultModel.simulation_run_id == sim_run.id)
            .where(ReliabilityResultModel.is_global == True)
        ).scalar_one_or_none()

        # Agregações de Infraestrutura
        bus_count = self.session.execute(select(func.count(BusModel.id)).where(BusModel.system_id == system.id)).scalar() or 0
        gen_capacity = self.session.execute(select(func.sum(GeneratorModel.nominal_capacity_mw)).where(GeneratorModel.system_id == system.id)).scalar() or 0.0

        # Formatação Segura
        def s_fmt(val): return float(val or 0.0)

        return {
            "case_id": str(case_id),
            "case_name": case.display_name or case.external_name,
            "indicators": {
                "LOLP": {"value": s_fmt(global_res.lolp) if global_res else 0.0, "unit": "%"},
                "LOLE": {"value": s_fmt(global_res.lole) if global_res else 0.0, "unit": "h/ano"},
                "EPNS": {"value": s_fmt(global_res.epns) if global_res else 0.0, "unit": "MW"},
                "EENS": {"value": s_fmt(global_res.eens) if global_res else 0.0, "unit": "MWh/ano"},
                "LOLF": {"value": s_fmt(global_res.lolf) if global_res else 0.0, "unit": "occ/ano"},
                "LOLD": {"value": s_fmt(global_res.lold) if global_res else 0.0, "unit": "h/occ"},
                "LOLC": {"value": s_fmt(global_res.lolc) if global_res else 0.0, "unit": "$/ano"}
            },
            "general_info": {
                "Anos Simulados": str(sim_run.simulated_years or "N/A"),
                "Tipo de Análise": str(sim_run.analysis_type or "N/A"),
                "Data de Importação": sim_run.imported_at.strftime("%d/%m/%Y") if sim_run.imported_at else "N/A",
                "Convergência": "Padrão", # Placeholder para expansão futura
                "Número de Barras": str(bus_count),
                "Potência Instalada (MW)": f"{gen_capacity:.2f}",
                "Carga do Sistema (MW)": f"{system.nominal_load_mw or 0.0:.2f}"
            }
        }
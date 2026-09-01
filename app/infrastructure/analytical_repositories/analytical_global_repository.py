import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel
from app.infrastructure.database.models.config_model import SimulationConfigModel

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

        # Agregações de Infraestrutura seguras
        bus_count = self.session.execute(select(func.count(BusModel.id)).where(BusModel.system_id == system.id)).scalar() or 0
        gen_count = self.session.execute(select(func.count(GeneratorModel.id)).where(GeneratorModel.system_id == system.id)).scalar() or 0
        gen_capacity = self.session.execute(select(func.sum(GeneratorModel.nominal_capacity_mw)).where(GeneratorModel.system_id == system.id)).scalar() or 0.0


        # BUSCA DINÂMICA DO BETA NA TABELA EAV
        configs = self.session.execute(
            select(SimulationConfigModel)
            .where(SimulationConfigModel.simulation_run_id == sim_run.id)
        ).scalars().all()

        config_dict = {cfg.parameter_key: cfg.parameter_value for cfg in configs}
        
        beta_value = (
            config_dict.get("Convergence Beta") or 
            config_dict.get("COEF_BETA") or 
            config_dict.get("Convergência") or 
            sim_run.convergence_beta or 
            "N/A"
        )
        if beta_value == "Padrão":
            beta_value = "N/A"

        analysis_type_val = (
            config_dict.get("Analysis Type") or 
            config_dict.get("ANALYSIS_TYPE") or 
            sim_run.analysis_type or 
            "N/A"
        )

        sys_rep_val = (
            config_dict.get("System Representation") or 
            config_dict.get("SYST_REP") or 
            "N/A"
        )

        conf_dict = global_res.confidence_intervals if global_res and hasattr(global_res, 'confidence_intervals') and global_res.confidence_intervals else {}

        def s_fmt(val): return float(val or 0.0)

        return {
            "case_id": str(case_id),
            "case_name": case.display_name or case.external_name,
            "indicators": {
                "LOLP": {"value": s_fmt(global_res.lolp) if global_res else 0.0, "unit": "%", "conf": conf_dict.get("LOLP", "N/A")},
                "LOLE": {"value": s_fmt(global_res.lole) if global_res else 0.0, "unit": "h/ano", "conf": conf_dict.get("LOLE", "N/A")},
                "EPNS": {"value": s_fmt(global_res.epns) if global_res else 0.0, "unit": "MW", "conf": conf_dict.get("EPNS", "N/A")},
                "EENS": {"value": s_fmt(global_res.eens) if global_res else 0.0, "unit": "MWh/ano", "conf": conf_dict.get("EENS", "N/A")},
                "LOLF": {"value": s_fmt(global_res.lolf) if global_res else 0.0, "unit": "occ/ano", "conf": conf_dict.get("LOLF", "N/A")},
                "LOLD": {"value": s_fmt(global_res.lold) if global_res else 0.0, "unit": "h/occ", "conf": conf_dict.get("LOLD", "N/A")},
                "LOLC": {"value": s_fmt(global_res.lolc) if global_res else 0.0, "unit": "$/ano", "conf": conf_dict.get("LOLC", "N/A")}
            },
            "general_info": {
                "Número de Barras": str(bus_count),
                "Convergência (Beta)": str(beta_value),
                "Tipo de Análise": str(analysis_type_val),
                "Representação do Sistema": str(sys_rep_val),
                "Anos Simulados": str(sim_run.simulated_years or "N/A"),
                "Data de Importação": sim_run.imported_at.strftime("%d/%m/%Y") if sim_run.imported_at else "N/A",
                "Potência Instalada (MW)": f"{gen_capacity:.2f}",
                "Carga do Sistema (MW)": f"{system.nominal_load_mw or 0.0:.2f}"
            }
        }
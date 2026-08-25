from typing import List
from sqlalchemy.orm import Session
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.region_model import RegionModel
from app.application.dto.analytical_dtos import (
    MultiCompareRequestDTO, MultiCompareResponseDTO, MultiCompareElementDataDTO
)
from app.infrastructure.database.models.simulation_model import SimulationRunModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.system_model import SystemModel
import networkx as nx
from app.infrastructure.database.models.case_model import CaseModel
from app.infrastructure.database.models.equipment_model import TransmissionLineModel, GeneratorModel, TransformerModel

class MultiCompareCasesUseCase:
    def __init__(self, db_session: Session):
        self.session = db_session

    def execute(self, request: MultiCompareRequestDTO) -> MultiCompareResponseDTO:
        indicators = ["LOLP", "LOLE", "EPNS", "EENS", "LOLF", "LOLD", "LOLC"]
        units = {
            "LOLP": "%", "LOLE": "h/yr", "EPNS": "MW", 
            "EENS": "MWh/yr", "LOLF": "occ/yr", "LOLD": "h/occ", "LOLC": "$/yr"
        }

        # --- MAPEAMENTO DE NOMES DAS BARRAS ---
        bus_name_map = {}
        if request.granularity.upper() == "BUS":
            buses = self.session.query(BusModel.external_id, BusModel.name)\
                .join(SystemModel, SystemModel.id == BusModel.system_id)\
                .join(SimulationRunModel, SimulationRunModel.id == SystemModel.simulation_run_id)\
                .filter(SimulationRunModel.case_id.in_(request.case_ids)).all()
            for b_ext, b_name in buses:
                bus_name_map[str(b_ext).strip()] = b_name

        # --- 1. COLETA DE METADADOS E TOPOLOGIA (SUPER TABELA) ---
        case_informations = {}
        system_summaries = {}

        for cid in request.case_ids:
            case_orm = self.session.query(CaseModel).filter_by(id=cid).first()
            sim_orm = self.session.query(SimulationRunModel).filter_by(case_id=cid).first()
            
            if not case_orm or not sim_orm: continue
                
            cid_str = str(cid)
            
            # Case Informations
            case_informations[cid_str] = {
                "Analysis Type": getattr(sim_orm, 'analysis_type', 'STA'),
                "System Representation": "AC", # Ou puxe de uma tabela de Configuração, se houver
                "Convergence Beta": "1%",      # Ou puxe de uma tabela de Configuração, se houver
                "Import Date": case_orm.created_at.strftime("%Y-%m-%d %H:%M") if case_orm.created_at else "-",
                "Last Update": case_orm.updated_at.strftime("%Y-%m-%d %H:%M") if case_orm.updated_at else "-"
            }

            # System Summary (Topologia e Grafos)
            sys_orm = self.session.query(SystemModel).filter_by(simulation_run_id=sim_orm.id).first()
            if sys_orm:
                n_buses = self.session.query(BusModel).filter_by(system_id=sys_orm.id).count()
                n_gens = self.session.query(GeneratorModel).filter_by(system_id=sys_orm.id).count()
                n_trafos = self.session.query(TransformerModel).filter_by(system_id=sys_orm.id).count()
                n_lines = self.session.query(TransmissionLineModel).filter_by(system_id=sys_orm.id).count()
                
                # Montagem do Grafo para cálculo de Radiais e Malhas
                lines = self.session.query(TransmissionLineModel).filter_by(system_id=sys_orm.id).all()
                G = nx.Graph()
                for line in lines:
                    G.add_edge(line.from_bus_id, line.to_bus_id)
                
                radial_count = sum(1 for node, degree in G.degree() if degree == 1)
                
                interconnected_buses = set()
                for cycle in nx.cycle_basis(G):
                    interconnected_buses.update(cycle)
                
                system_summaries[cid_str] = {
                    "Total Buses": n_buses,
                    "Total Generators": n_gens,
                    "Total Transformers": n_trafos,
                    "Total Lines": n_lines,
                    "Radial Buses": radial_count,
                    "Interconnected Buses": len(interconnected_buses)
                }

        # --- 2. COLETA DOS INDICADORES DE CONFIABILIDADE ---
        query = self.session.query(ReliabilityResultModel, SimulationRunModel.case_id).join(
            SimulationRunModel, ReliabilityResultModel.simulation_run_id == SimulationRunModel.id
        ).filter(
            SimulationRunModel.case_id.in_(request.case_ids)
        )

        granularity = request.granularity.upper()
        if granularity == "GLOBAL":
            query = query.filter(ReliabilityResultModel.is_global == True)
        elif granularity == "REGION":
            query = query.filter(
                ReliabilityResultModel.region_name.isnot(None),
                ReliabilityResultModel.bus_external_id.is_(None)
            )
            if request.element_id and request.element_id != "ALL":
                query = query.filter(ReliabilityResultModel.region_name == request.element_id)
        elif granularity == "BUS":
            query = query.filter(ReliabilityResultModel.bus_external_id.isnot(None))
            if request.element_id and request.element_id != "ALL":
                query = query.filter(ReliabilityResultModel.bus_external_id == request.element_id)

        db_results = query.all()

        grouped = {}
        for row, case_id in db_results:
            cid_str = str(case_id)

            if granularity == "GLOBAL":
                el_name = "Global System"
            elif granularity == "REGION":
                el_name = str(row.region_name)
            elif granularity == "BUS":
                ext_id = str(row.bus_external_id).strip()
                b_name = bus_name_map.get(ext_id, "Unknown")
                el_name = f"{ext_id} - {b_name}"
            else:
                el_name = str(row.bus_external_id)

            if el_name not in grouped:
                grouped[el_name] = {c_id: {} for c_id in request.case_ids}

            grouped[el_name][cid_str] = {
                "LOLP": row.lolp,
                "LOLE": row.lole,
                "EPNS": row.epns,
                "EENS": row.eens,
                "LOLF": row.lolf,
                "LOLD": row.lold,
                "LOLC": row.lolc
            }

        # --- 3. MONTAGEM DA RESPOSTA ---
        elements_dto = []
        for el_name, cases_values in grouped.items():
            elements_dto.append(
                MultiCompareElementDataDTO(
                    element_name=el_name,
                    values_by_case=cases_values
                )
            )

        return MultiCompareResponseDTO(
            indicators=indicators,
            units=units,
            granularity=granularity,
            case_informations=case_informations,
            system_summaries=system_summaries,
            elements=elements_dto
        )
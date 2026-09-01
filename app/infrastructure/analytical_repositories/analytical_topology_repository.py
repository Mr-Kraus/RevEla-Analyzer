import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, or_, func
from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import (
    GeneratorModel, 
    GeneratorClassModel, 
    TransmissionLineModel, 
    TransformerModel
)
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel

class AnalyticalTopologyRepository:
    """Repositório exclusivo de leitura para análise da infraestrutura e topologia elétrica."""
    
    def __init__(self, session: Session):
        self.session = session

    def _get_sys_id(self, case_id: uuid.UUID):
        """Método auxiliar para resolver o ID do sistema seja por case_id ou simulation_run_id."""
        stmt = select(SystemModel.id).where(SystemModel.case_id == case_id)
        sys_id = self.session.execute(stmt).scalar_one_or_none()
        if not sys_id:
            stmt = select(SystemModel.id).where(SystemModel.simulation_run_id == case_id)
            sys_id = self.session.execute(stmt).scalar_one_or_none()
        return sys_id

    def get_topology(self, case_id: uuid.UUID) -> dict:
        stmt_info = select(SystemModel.id, SystemModel.simulation_run_id).where(SystemModel.case_id == case_id)
        sys_info = self.session.execute(stmt_info).first()
        
        if not sys_info:
            stmt_info = select(SystemModel.id, SystemModel.simulation_run_id).where(SystemModel.simulation_run_id == case_id)
            sys_info = self.session.execute(stmt_info).first()
            if not sys_info:
                raise ValueError("Nenhum sistema encontrado para esta análise.")
                
        sys_id = sys_info[0]
        sim_run_id = sys_info[1]

        region_display = func.coalesce(RegionModel.alias, RegionModel.name).label("region_name")

        stmt_buses = (
            select(
                BusModel.external_id, BusModel.name, BusModel.base_kv,
                region_display,
                ReliabilityResultModel.lolp, ReliabilityResultModel.lole,
                ReliabilityResultModel.epns, ReliabilityResultModel.eens,
                ReliabilityResultModel.lolf, ReliabilityResultModel.lold,
                ReliabilityResultModel.lolc
            )
            .select_from(BusModel)
            .outerjoin(RegionModel, BusModel.region_id == RegionModel.id)
            .outerjoin(
                ReliabilityResultModel, 
                (ReliabilityResultModel.bus_external_id == BusModel.external_id) & 
                (ReliabilityResultModel.simulation_run_id == sim_run_id)
            )
            .where(BusModel.system_id == sys_id)
        )
        buses_results = self.session.execute(stmt_buses).all()

        nodes = []
        def safe_fmt(val, dec=4): return f"{float(val or 0):.{dec}f}"

        for row in buses_results:
            title_html = (
                f"<b>Barra:</b> {row.name or row.external_id}<br>"
                f"<b>Região:</b> {row.region_name or 'Geral'}<br>"
                f"<b>Tensão Base:</b> {row.base_kv or 0} kV<br>"
                f"<hr style='margin: 8px 0; border: 1px solid #BDC3C7'>"
                f"<b>LOLP:</b> {safe_fmt(row.lolp, 6)}<br>"
                f"<b>LOLE:</b> {safe_fmt(row.lole, 4)} h/ano<br>"
                f"<b>EPNS:</b> {safe_fmt(row.epns, 4)} MW<br>"
                f"<b>EENS:</b> {safe_fmt(row.eens, 4)} MWh/ano<br>"
                f"<b>LOLF:</b> {safe_fmt(row.lolf, 4)} occ/ano<br>"
                f"<b>LOLD:</b> {safe_fmt(row.lold, 4)} h/occ<br>"
                f"<b>LOLC:</b> {safe_fmt(row.lolc, 2)} $/ano"
            )
            nodes.append({
                "id": str(row.external_id),
                "label": str(row.name or row.external_id),
                "group": str(row.region_name) if row.region_name else "Geral",
                "title": title_html 
            })

        FromBus = aliased(BusModel)
        ToBus = aliased(BusModel)
        edges = []

        stmt_lines = (
            select(
                FromBus.external_id.label("from_ext"), ToBus.external_id.label("to_ext"),
                TransmissionLineModel.name, TransmissionLineModel.external_id,
                TransmissionLineModel.capacity_mva, TransmissionLineModel.r_pu, 
                TransmissionLineModel.x_pu, TransmissionLineModel.failure_rate, TransmissionLineModel.repair_time
            )
            .select_from(TransmissionLineModel)
            .join(FromBus, TransmissionLineModel.from_bus_id == FromBus.id)
            .join(ToBus, TransmissionLineModel.to_bus_id == ToBus.id)
            .where(TransmissionLineModel.system_id == sys_id)
            .where(TransmissionLineModel.capacity_mva < 9999)
        )
        lines_results = self.session.execute(stmt_lines).all()

        for row in lines_results:
            title_html = (
                f"<b>Equipamento:</b> Linha de Transmissão<br>"
                f"<b>Capacidade:</b> {safe_fmt(row.capacity_mva, 2)} MVA<br>"
                f"<b>Impedância:</b> {safe_fmt(row.r_pu, 5)} + j{safe_fmt(row.x_pu, 5)} pu<br>"
                f"<b>Taxa de Falha:</b> {safe_fmt(row.failure_rate, 4)} f/ano<br>"
                f"<b>T. de Reparo:</b> {safe_fmt(row.repair_time, 2)} h"
            )
            edges.append({
                "from": str(row.from_ext), "to": str(row.to_ext),
                "label": str(row.name or row.external_id or ""),
                "title": title_html
            })

        stmt_trafos = (
            select(
                FromBus.external_id.label("from_ext"), ToBus.external_id.label("to_ext"),
                TransformerModel.name, TransformerModel.external_id,
                TransformerModel.capacity_mva, TransformerModel.r_pu, 
                TransformerModel.x_pu, TransformerModel.failure_rate, TransformerModel.repair_time
            )
            .select_from(TransformerModel)
            .join(FromBus, TransformerModel.from_bus_id == FromBus.id)
            .join(ToBus, TransformerModel.to_bus_id == ToBus.id)
            .where(TransformerModel.system_id == sys_id)
            .where(TransformerModel.capacity_mva < 9999)
        )
        trafos_results = self.session.execute(stmt_trafos).all()

        for row in trafos_results:
            title_html = (
                f"<b>Equipamento:</b> Transformador<br>"
                f"<b>Capacidade:</b> {safe_fmt(row.capacity_mva, 2)} MVA<br>"
                f"<b>Impedância:</b> {safe_fmt(row.r_pu, 5)} + j{safe_fmt(row.x_pu, 5)} pu<br>"
                f"<b>Taxa de Falha:</b> {safe_fmt(row.failure_rate, 4)} f/ano<br>"
                f"<b>T. de Reparo:</b> {safe_fmt(row.repair_time, 2)} h"
            )
            edges.append({
                "from": str(row.from_ext), "to": str(row.to_ext),
                "label": str(row.name or row.external_id or ""),
                "title": title_html
            })

        return {"nodes": nodes, "edges": edges}

    def get_transmission_details(self, case_id: uuid.UUID) -> dict:
        sys_id = self._get_sys_id(case_id)
        if not sys_id:
            return {"summary": {}, "lines": [], "transformers": []}

        FromBus = aliased(BusModel)
        ToBus = aliased(BusModel)

        stmt_lines = (
            select(
                TransmissionLineModel.external_id, TransmissionLineModel.name,
                FromBus.name.label("from_bus_name"), FromBus.external_id.label("from_bus_ext"),
                ToBus.name.label("to_bus_name"), ToBus.external_id.label("to_bus_ext"),
                TransmissionLineModel.r_pu, TransmissionLineModel.x_pu,
                TransmissionLineModel.capacity_mva, TransmissionLineModel.failure_rate, TransmissionLineModel.repair_time
            )
            .select_from(TransmissionLineModel)
            .join(FromBus, TransmissionLineModel.from_bus_id == FromBus.id)
            .join(ToBus, TransmissionLineModel.to_bus_id == ToBus.id)
            .where(TransmissionLineModel.system_id == sys_id)
            .where(TransmissionLineModel.capacity_mva < 9999)
        )
        lines_raw = self.session.execute(stmt_lines).all()

        lines = []
        total_line_mva = 0.0
        total_line_failure = 0.0

        for r in lines_raw:
            cap = float(r.capacity_mva or 0.0)
            fail = float(r.failure_rate or 0.0)
            total_line_mva += cap
            total_line_failure += fail
            lines.append({
                "external_id": str(r.external_id), "name": str(r.name or r.external_id),
                "from_bus": f"{r.from_bus_name} ({r.from_bus_ext})",
                "to_bus": f"{r.to_bus_name} ({r.to_bus_ext})",
                "r_pu": float(r.r_pu or 0.0), "x_pu": float(r.x_pu or 0.0),
                "capacity_mva": cap, "failure_rate": fail, "repair_time": float(r.repair_time or 0.0)
            })

        stmt_trafos = (
            select(
                TransformerModel.external_id, TransformerModel.name,
                FromBus.name.label("from_bus_name"), FromBus.external_id.label("from_bus_ext"),
                ToBus.name.label("to_bus_name"), ToBus.external_id.label("to_bus_ext"),
                TransformerModel.r_pu, TransformerModel.x_pu,
                TransformerModel.capacity_mva, TransformerModel.failure_rate, TransformerModel.repair_time
            )
            .select_from(TransformerModel)
            .join(FromBus, TransformerModel.from_bus_id == FromBus.id)
            .join(ToBus, TransformerModel.to_bus_id == ToBus.id)
            .where(TransformerModel.system_id == sys_id)
            .where(TransformerModel.capacity_mva < 9999)
        )
        trafos_raw = self.session.execute(stmt_trafos).all()

        transformers = []
        total_trafo_mva = 0.0

        for r in trafos_raw:
            cap = float(r.capacity_mva or 0.0)
            total_trafo_mva += cap
            transformers.append({
                "external_id": str(r.external_id), "name": str(r.name or r.external_id),
                "from_bus": f"{r.from_bus_name} ({r.from_bus_ext})",
                "to_bus": f"{r.to_bus_name} ({r.to_bus_ext})",
                "r_pu": float(r.r_pu or 0.0), "x_pu": float(r.x_pu or 0.0),
                "capacity_mva": cap, "failure_rate": float(r.failure_rate or 0.0), "repair_time": float(r.repair_time or 0.0)
            })

        avg_failure = (total_line_failure / len(lines)) if lines else 0.0

        return {
            "summary": {
                "total_lines": len(lines), "total_transformers": len(transformers),
                "total_capacity_mva": round(total_line_mva + total_trafo_mva, 2), "avg_failure_rate": round(avg_failure, 4)
            },
            "lines": lines, "transformers": transformers
        }

    def get_generation_details(self, case_id: uuid.UUID) -> dict:
        """Retorna as instâncias individuais e suas respectivas classes."""
        sys_id = self._get_sys_id(case_id)
        if not sys_id:
            return {"summary": {}, "generators": []}

        # Cruzamento corrigido: Instância -> Catálogo -> Barra
        stmt_gen = (
            select(
                GeneratorModel.external_id,
                GeneratorModel.name,
                GeneratorModel.technology,
                GeneratorClassModel.nominal_capacity_mw,
                GeneratorClassModel.failure_rate_percent,
                GeneratorClassModel.repair_time_hours,
                BusModel.name.label("bus_name"),
                BusModel.external_id.label("bus_ext")
            )
            .select_from(GeneratorModel)
            .join(GeneratorClassModel, GeneratorModel.generator_class_id == GeneratorClassModel.id)
            .outerjoin(BusModel, GeneratorModel.bus_id == BusModel.id)
            .where(GeneratorModel.system_id == sys_id)
            .where(GeneratorClassModel.nominal_capacity_mw < 9999)
        )
        gens_raw = self.session.execute(stmt_gen).all()

        generators = []
        total_mw = 0.0
        total_fail = 0.0

        for r in gens_raw:
            cap = float(r.nominal_capacity_mw or 0.0)
            fail = float(r.failure_rate_percent or 0.0)
            total_mw += cap
            total_fail += fail
            
            bus_str = f"{r.bus_name} ({r.bus_ext})" if r.bus_ext else "Não Vinculada"

            generators.append({
                "external_id": str(r.external_id),
                "name": str(r.name or r.external_id),
                "technology": str(r.technology or "-"),
                "bus": bus_str,
                "capacity_mw": cap,
                "failure_rate": fail,
                "repair_time": float(r.repair_time_hours or 0.0)
            })

        avg_fail = (total_fail / len(generators)) if generators else 0.0

        return {
            "summary": {
                "total_generators": len(generators),
                "total_capacity_mw": round(total_mw, 2),
                "avg_failure_rate": round(avg_fail, 4)
            },
            "generators": generators
        }

    def get_power_plants_summary(self, case_id: uuid.UUID) -> list:
        """Agrupa os geradores por Barra e Tecnologia para representar Usinas (Power Plants)."""
        sys_id = self._get_sys_id(case_id)
        if not sys_id:
            return []

        stmt = (
            select(
                BusModel.name.label("bus_name"),
                BusModel.external_id.label("bus_ext"),
                GeneratorModel.technology,
                func.count(GeneratorModel.id).label("unit_count"),
                func.sum(GeneratorClassModel.nominal_capacity_mw).label("total_capacity")
            )
            .select_from(GeneratorModel)
            .join(GeneratorClassModel, GeneratorModel.generator_class_id == GeneratorClassModel.id)
            .outerjoin(BusModel, GeneratorModel.bus_id == BusModel.id)
            .where(GeneratorModel.system_id == sys_id)
            .where(GeneratorClassModel.nominal_capacity_mw < 9999)
            .group_by(BusModel.name, BusModel.external_id, GeneratorModel.technology)
        )
        plants_raw = self.session.execute(stmt).all()
        
        return [
            {
                "power_plant_name": f"Usina {r.technology} - {r.bus_name or 'Desconhecida'}",
                "bus": f"{r.bus_name} ({r.bus_ext})" if r.bus_ext else "Não Vinculada",
                "technology": r.technology,
                "unit_count": r.unit_count,
                "total_capacity_mw": float(r.total_capacity or 0.0)
            } for r in plants_raw
        ]

    def get_energy_matrix(self, case_id: uuid.UUID) -> dict:
        """Retorna a matriz energética consolidada (Soma de Capacidade por Tecnologia)."""
        sys_id = self._get_sys_id(case_id)
        if not sys_id:
            return {}

        stmt = (
            select(
                GeneratorModel.technology,
                func.count(GeneratorModel.id).label("total_units"),
                func.sum(GeneratorClassModel.nominal_capacity_mw).label("total_capacity")
            )
            .select_from(GeneratorModel)
            .join(GeneratorClassModel, GeneratorModel.generator_class_id == GeneratorClassModel.id)
            .where(GeneratorModel.system_id == sys_id)
            .where(GeneratorClassModel.nominal_capacity_mw < 9999)
            .group_by(GeneratorModel.technology)
            .order_by(func.sum(GeneratorClassModel.nominal_capacity_mw).desc())
        )
        matrix_raw = self.session.execute(stmt).all()
        
        matrix = []
        system_total_mw = sum(float(r.total_capacity or 0.0) for r in matrix_raw)

        for r in matrix_raw:
            cap = float(r.total_capacity or 0.0)
            matrix.append({
                "technology": r.technology,
                "total_units": r.total_units,
                "capacity_mw": round(cap, 2),
                "participation_percent": round((cap / system_total_mw * 100) if system_total_mw > 0 else 0, 2)
            })

        return {
            "total_system_capacity": round(system_total_mw, 2),
            "breakdown": matrix
        }
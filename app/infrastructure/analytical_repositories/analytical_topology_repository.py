import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, or_

from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel, TransmissionLineModel, TransformerModel
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel

class AnalyticalTopologyRepository:
    """Repositório exclusivo de leitura para análise da infraestrutura e topologia elétrica."""
    
    def __init__(self, session: Session):
        self.session = session

    def _get_system_id(self, simulation_id: uuid.UUID) -> uuid.UUID:
        """Obtém o system_id associado à simulação atual."""
        stmt = (
            select(BusModel.system_id)
            .join(ReliabilityResultModel, ReliabilityResultModel.bus_external_id == BusModel.external_id)
            .where(ReliabilityResultModel.simulation_run_id == simulation_id)
            .limit(1)
        )
        sys_id = self.session.execute(stmt).scalar_one_or_none()
        if not sys_id:
            stmt_fallback = select(SystemModel.id).limit(1)
            sys_id = self.session.execute(stmt_fallback).scalar_one_or_none()
            if not sys_id:
                raise ValueError(f"Nenhum sistema encontrado para a simulação {simulation_id}")
        return sys_id

    def get_generators(self, simulation_id: uuid.UUID) -> List[Dict[str, Any]]:
        sys_id = self._get_system_id(simulation_id)
        stmt = select(GeneratorModel).where(GeneratorModel.system_id == sys_id)
        results = self.session.execute(stmt).scalars().all()
        
        parsed_generators = []
        for g in results:
            cap = getattr(g, "nominal_capacity_mw", getattr(g, "rated_power_mw", getattr(g, "capacity_mw", 0)))
            parsed_generators.append({
                "external_id": g.external_id,
                "name": getattr(g, "name", f"Gen_{g.external_id}"),
                "capacity_mva": float(cap or 0)
            })
        return parsed_generators

    def get_lines(self, simulation_id: uuid.UUID) -> List[Dict[str, Any]]:
        sys_id = self._get_system_id(simulation_id)
        stmt = select(TransmissionLineModel).where(TransmissionLineModel.system_id == sys_id)
        results = self.session.execute(stmt).scalars().all()
        return [{"external_id": l.external_id, "name": l.name, "failure_rate": float(getattr(l, "failure_rate_percent", 0) or 0)} for l in results]

    def get_transformers(self, simulation_id: uuid.UUID) -> List[Dict[str, Any]]:
        sys_id = self._get_system_id(simulation_id)
        stmt = select(TransformerModel).where(TransformerModel.system_id == sys_id)
        results = self.session.execute(stmt).scalars().all()
        return [{"external_id": t.external_id, "name": t.name, "failure_rate": float(getattr(t, "failure_rate_percent", 0) or 0)} for t in results]

    def get_topology(self, simulation_id: uuid.UUID) -> dict:
        sys_id = self._get_system_id(simulation_id)

        # 1. BUSCA AS BARRAS (NÓS)
        stmt_buses = (
            select(BusModel.external_id, BusModel.name, RegionModel.name.label("region_name"))
            .select_from(BusModel)
            .outerjoin(RegionModel, BusModel.region_id == RegionModel.id)
            .where(BusModel.system_id == sys_id)
        )
        buses_results = self.session.execute(stmt_buses).all()

        nodes = []
        for row in buses_results:
            nodes.append({
                "id": str(row.external_id),
                "label": str(row.name or row.external_id),
                "group": str(row.region_name) if row.region_name else "Geral"
            })

        # 2. BUSCA AS ARESTAS (Com Outer Join para diagnóstico)
        FromBus = aliased(BusModel)
        ToBus = aliased(BusModel)
        edges = []

        # 2a. Linhas de Transmissão
        stmt_lines = (
            select(
                TransmissionLineModel.name,
                TransmissionLineModel.external_id,
                FromBus.external_id.label("from_ext"),
                ToBus.external_id.label("to_ext")
            )
            .select_from(TransmissionLineModel)
            .outerjoin(FromBus, TransmissionLineModel.from_bus_id == FromBus.id)
            .outerjoin(ToBus, TransmissionLineModel.to_bus_id == ToBus.id)
            .where(TransmissionLineModel.system_id == sys_id)
        )
        lines_results = self.session.execute(stmt_lines).all()
        
        linhas_banco = len(lines_results)
        linhas_validas = 0

        for row in lines_results:
            if row.from_ext and row.to_ext:
                linhas_validas += 1
                edges.append({
                    "from": str(row.from_ext),
                    "to": str(row.to_ext),
                    "label": str(row.name or row.external_id or "")
                })

        # 2b. Transformadores
        stmt_trafos = (
            select(
                TransformerModel.name,
                TransformerModel.external_id,
                FromBus.external_id.label("from_ext"),
                ToBus.external_id.label("to_ext")
            )
            .select_from(TransformerModel)
            .outerjoin(FromBus, TransformerModel.from_bus_id == FromBus.id)
            .outerjoin(ToBus, TransformerModel.to_bus_id == ToBus.id)
            .where(TransformerModel.system_id == sys_id)
        )
        trafos_results = self.session.execute(stmt_trafos).all()

        trafos_banco = len(trafos_results)
        trafos_validos = 0

        for row in trafos_results:
            if row.from_ext and row.to_ext:
                trafos_validos += 1
                edges.append({
                    "from": str(row.from_ext),
                    "to": str(row.to_ext),
                    "label": str(row.name or row.external_id or "")
                })

        print(f"DEBUG DB: Linhas Totais no Banco={linhas_banco} | Validas para Desenho={linhas_validas}")
        print(f"DEBUG DB: Trafos Totais no Banco={trafos_banco} | Validos para Desenho={trafos_validos}")

        return {
            "nodes": nodes,
            "edges": edges
        }
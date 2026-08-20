import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel, TransmissionLineModel, TransformerModel
from app.infrastructure.database.models.system_model import SystemModel

class AnalyticalTopologyRepository:
    """Repositório exclusivo de leitura (M03-F03) para análise da infraestrutura elétrica."""
    
    def __init__(self, session: Session):
        self.session = session

    def _get_system_id(self, simulation_id: uuid.UUID) -> uuid.UUID:
        stmt = select(SystemModel.id).where(SystemModel.simulation_run_id == simulation_id)
        sys_id = self.session.execute(stmt).scalar_one_or_none()
        if not sys_id:
            raise ValueError(f"Nenhum sistema encontrado para a simulação {simulation_id}")
        return sys_id

    def get_generators(self, simulation_id: uuid.UUID) -> List[Dict[str, Any]]:
        sys_id = self._get_system_id(simulation_id)
        stmt = select(GeneratorModel).where(GeneratorModel.system_id == sys_id)
        results = self.session.execute(stmt).scalars().all()
        
        parsed_generators = []
        for g in results:
            # Tenta buscar pelo nome da coluna que você definiu no seu model:
            # rated_power_mw, capacity_mw, ou capacity_mva
            cap = getattr(g, "rated_power_mw", getattr(g, "capacity_mw", getattr(g, "capacity_mva", 0)))
            
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
        return [{"external_id": l.external_id, "name": l.name, "failure_rate": float(l.failure_rate or 0)} for l in results]

    def get_transformers(self, simulation_id: uuid.UUID) -> List[Dict[str, Any]]:
        sys_id = self._get_system_id(simulation_id)
        stmt = select(TransformerModel).where(TransformerModel.system_id == sys_id)
        results = self.session.execute(stmt).scalars().all()
        return [{"external_id": t.external_id, "name": t.name, "failure_rate": float(t.failure_rate or 0)} for t in results]
    

    def get_topology(self, simulation_id: uuid.UUID) -> dict:
        """
        Retorna nós e arestas para renderização no PyVis/PyQt6.
        """
        # 1. Busca as barras associadas a esta simulação ou caso
        stmt_buses = (
            select(BusModel.external_id, BusModel.name, RegionModel.name.label("region_name"))
            .select_from(BusModel)
            .outerjoin(RegionModel, BusModel.region_id == RegionModel.id)
        )
        buses_results = self.session.execute(stmt_buses).all()

        nodes = []
        for row in buses_results:
            nodes.append({
                "id": str(row.external_id),
                "label": str(row.name),
                "group": str(row.region_name) if row.region_name else "Geral"
            })

        # 2. Busca as linhas de transmissão (Se a sua tabela de linhas existir)
        # Nota: Se ainda não tiver a tabela de linhas, deixe 'edges = []' por enquanto.
        edges = []
        # Exemplo se houver um BranchModel:
        # branches = self.session.execute(select(BranchModel.from_bus_id, BranchModel.to_bus_id)).all()
        # for b in branches:
        #     edges.append({"from": str(b.from_bus_id), "to": str(b.to_bus_id)})

        return {
            "nodes": nodes,
            "edges": edges
        }


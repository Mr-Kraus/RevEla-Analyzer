import uuid
import math
from typing import Dict, Any
import logging

from app.domain.entities.reliability_result import ReliabilityResult
from app.infrastructure.database.models.equipment_model import TransmissionLineModel, TransformerModel
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel

logger = logging.getLogger(__name__)

class ReliabilityResultDtoMapper:
    """Converte o Canonical DTO de Índices em Entidade de Domínio."""
    
    @staticmethod
    def to_domain(
        simulation_run_id: uuid.UUID, 
        is_global: bool, 
        dto: Dict[str, Any], 
        bus_ext_id: str = None
    ) -> ReliabilityResult:
        
        def clean_nan(val):
            if val is None or math.isnan(val):
                return 0.0
            return val

        return ReliabilityResult(
            id=uuid.uuid4(),
            simulation_run_id=simulation_run_id,
            is_global=is_global,
            bus_external_id=bus_ext_id,
            lolp=clean_nan(dto.get("lolp", 0.0)),
            lole=clean_nan(dto.get("lole", 0.0)),
            epns=clean_nan(dto.get("epns", 0.0)),
            eens=clean_nan(dto.get("eens", 0.0)),
            lolf=clean_nan(dto.get("lolf", 0.0)),
            lold=clean_nan(dto.get("lold", 0.0)),
            lolc=clean_nan(dto.get("lolc", 0.0))
        )
    
class SystemTopologyMapper:
    """Mapeia os DTOs canônicos de topologia diretamente para os Modelos ORM para inserção otimizada."""
    
    @staticmethod
    def to_orm_models(case_id: uuid.UUID, simulation_run_id: uuid.UUID, topology_dto: Dict[str, Any]) -> SystemModel:
        system_model = SystemModel(
            id=uuid.uuid4(),
            case_id=case_id,
            simulation_run_id=simulation_run_id,
            external_name="SYSTEM_M02",
            nominal_load_mw=0.0
        )
        
        region_models = {
            reg["external_id"]: RegionModel(
                id=uuid.uuid4(),
                external_id=reg["external_id"],
                name=reg["name"]
            ) for reg in topology_dto.get("regions", [])
        }
        system_model.regions = list(region_models.values())
        
        bus_models = {}
        for bus in topology_dto.get("buses", []):
            reg_ext_id = bus["region_external_id"]
            region_id = region_models[reg_ext_id].id if reg_ext_id in region_models else None
            
            b_model = BusModel(
                id=uuid.uuid4(),
                external_id=str(bus["external_id"]).strip(),
                name=bus["name"],
                base_kv=bus["voltage_kv"],
                region_id=region_id
            )
            bus_models[str(bus["external_id"]).strip()] = b_model
            system_model.buses.append(b_model)
            
        for gen in topology_dto.get("generation_classes", []):
            system_model.generators.append(
                GeneratorModel(
                    id=uuid.uuid4(),
                    external_id=str(gen["external_id"]).strip(),
                    name=gen["name"],
                    nominal_capacity_mw=gen["nominal_capacity_mw"],
                    failure_rate_percent=gen["failure_rate_percent"],
                    repair_time_hours=gen["repair_time_hours"]
                )
            )

        # 5. Mapeia Linhas de Transmissão passando OS OBJETOS (from_bus)
        # para o SQLAlchemy criar o grafo de dependências corretamente!
        for line in topology_dto.get("transmission_lines", []):
            from_ext = str(line["from_bus_ext_id"]).strip()
            to_ext = str(line["to_bus_ext_id"]).strip()
            
            from_bus = bus_models.get(from_ext)
            to_bus = bus_models.get(to_ext)
            
            if from_bus and to_bus:
                system_model.transmission_lines.append(
                    TransmissionLineModel(
                        id=uuid.uuid4(),
                        external_id=str(line["external_id"]).strip(),
                        name=line["name"],
                        from_bus=from_bus, # <-- MÁGICA: Ao invés de ID, passa a classe!
                        to_bus=to_bus,     # <-- O SQLAlchemy força salvar o Bus antes!
                        r_pu=line.get("r_pu", 0.0),
                        x_pu=line.get("x_pu", 0.0),
                        capacity_mva=line.get("capacity_mva", 0.0),
                        failure_rate=line.get("failure_rate", 0.0),
                        repair_time=line.get("repair_time", 0.0)
                    )
                )
            else:
                logger.warning(
                    f"Ingestão ignorou a Linha {line.get('external_id')} "
                    f"(From Bus: {from_ext}, To Bus: {to_ext}): Barra(s) não encontrada(s) no sistema."
                )

        # 6. Mapeia Transformadores passando OS OBJETOS
        for trafo in topology_dto.get("transformers", []):
            from_ext = str(trafo["from_bus_ext_id"]).strip()
            to_ext = str(trafo["to_bus_ext_id"]).strip()
            
            from_bus = bus_models.get(from_ext)
            to_bus = bus_models.get(to_ext)
            
            if from_bus and to_bus:
                system_model.transformers.append(
                    TransformerModel(
                        id=uuid.uuid4(),
                        external_id=str(trafo["external_id"]).strip(),
                        name=trafo["name"],
                        from_bus=from_bus, # <-- MÁGICA
                        to_bus=to_bus,
                        r_pu=trafo.get("r_pu", 0.0),
                        x_pu=trafo.get("x_pu", 0.0),
                        capacity_mva=trafo.get("capacity_mva", 0.0),
                        failure_rate=trafo.get("failure_rate", 0.0),
                        repair_time=trafo.get("repair_time", 0.0)
                    )
                )
            else:
                logger.warning(
                    f"Ingestão ignorou o Trafo {trafo.get('external_id')} "
                    f"(From Bus: {from_ext}, To Bus: {to_ext}): Barra(s) não encontrada(s) no sistema."
                )
                    
        return system_model
import uuid
import math
from typing import Dict, Any
from app.domain.entities.reliability_result import ReliabilityResult
# Assumindo que você tem entidades Region e Bus definidas no domínio
# from app.domain.entities.system_topology import Region, Bus
from app.infrastructure.database.models.equipment_model import TransmissionLineModel, TransformerModel
from app.infrastructure.database.models.system_model import SystemModel
from app.infrastructure.database.models.region_model import RegionModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.equipment_model import GeneratorModel

class ReliabilityResultDtoMapper:
    """Converte o Canonical DTO de Índices em Entidade de Domínio."""
    
    @staticmethod
    def to_domain(
        simulation_run_id: uuid.UUID, 
        is_global: bool, 
        dto: Dict[str, Any], 
        bus_ext_id: str = None
    ) -> ReliabilityResult:
        
        # Função interna de segurança: Banco de dados relacional odeia 'NaN', converteremos para 0.0
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
        # 1. Cria a Raiz
        system_model = SystemModel(
            id=uuid.uuid4(),
            case_id=case_id,
            simulation_run_id=simulation_run_id,
            external_name="SYSTEM_M02",
            nominal_load_mw=0.0
        )
        
        # 2. Cria as Regiões
        region_models = {
            reg["external_id"]: RegionModel(
                id=uuid.uuid4(),
                external_id=reg["external_id"],
                name=reg["name"]
            ) for reg in topology_dto.get("regions", [])
        }
        system_model.regions = list(region_models.values())
        
        # 3. Cria as Barras
        bus_models = {}
        for bus in topology_dto.get("buses", []):
            reg_ext_id = bus["region_external_id"]
            region_id = region_models[reg_ext_id].id if reg_ext_id in region_models else None
            
            b_model = BusModel(
                id=uuid.uuid4(),
                external_id=bus["external_id"],
                name=bus["name"],
                base_kv=bus["voltage_kv"],
                region_id=region_id
            )
            bus_models[bus["external_id"]] = b_model
            system_model.buses.append(b_model)
            
        # 4. Cria os Geradores (Classes de Geração mapeadas temporariamente como Geradores genéricos)
        for gen in topology_dto.get("generation_classes", []):
            system_model.generators.append(
                GeneratorModel(
                    id=uuid.uuid4(),
                    external_id=gen["external_id"],
                    name=gen["name"],
                    nominal_capacity_mw=gen["nominal_capacity_mw"],
                    failure_rate_percent=gen["failure_rate_percent"],
                    repair_time_hours=gen["repair_time_hours"]
                )
            )
        # 5. Mapeia Linhas de Transmissão vinculando as Barras reais (From/To)
        for line in topology_dto.get("transmission_lines", []):
            from_bus = bus_models.get(line["from_bus_ext_id"])
            to_bus = bus_models.get(line["to_bus_ext_id"])
            
            if from_bus and to_bus:
                system_model.transmission_lines.append(
                    TransmissionLineModel(
                        id=uuid.uuid4(),
                        external_id=line["external_id"],
                        name=line["name"],
                        from_bus_id=from_bus.id,
                        to_bus_id=to_bus.id,
                        r_pu=line.get("r_pu", 0.0),
                        x_pu=line.get("x_pu", 0.0),
                        capacity_mva=line.get("capacity_mva", 0.0)
                    )
                )

        # 6. Mapeia Transformadores vinculando as Barras reais (From/To)
        for trafo in topology_dto.get("transformers", []):
            from_bus = bus_models.get(trafo["from_bus_ext_id"])
            to_bus = bus_models.get(trafo["to_bus_ext_id"])
            
            if from_bus and to_bus:
                system_model.transformers.append(
                    TransformerModel(
                        id=uuid.uuid4(),
                        external_id=trafo["external_id"],
                        name=trafo["name"],
                        from_bus_id=from_bus.id,
                        to_bus_id=to_bus.id,
                        r_pu=trafo.get("r_pu", 0.0),
                        x_pu=trafo.get("x_pu", 0.0),
                        capacity_mva=trafo.get("capacity_mva", 0.0)
                    )
                )    
        # Retorna a raiz populada. O cascade="all" do SQLAlchemy fará o resto!
        return system_model
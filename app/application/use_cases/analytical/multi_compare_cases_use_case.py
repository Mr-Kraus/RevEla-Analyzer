from typing import List
from sqlalchemy.orm import Session
from app.infrastructure.database.models.reliability_result_model import ReliabilityResultModel
from app.infrastructure.database.models.region_model import RegionModel
from app.application.dto.analytical_dtos import (
    MultiCompareRequestDTO, MultiCompareResponseDTO, MultiCompareElementDataDTO
)
from app.infrastructure.database.models.simulation_model import SimulationRunModel

class MultiCompareCasesUseCase:
    def __init__(self, db_session: Session):
        self.session = db_session

    def execute(self, request: MultiCompareRequestDTO) -> MultiCompareResponseDTO:
        indicators = ["LOLP", "LOLE", "EPNS", "EENS", "LOLF", "LOLD", "LOLC"]
        units = {
            "LOLP": "%", "LOLE": "h/yr", "EPNS": "MW", 
            "EENS": "MWh/yr", "LOLF": "occ/yr", "LOLD": "h/occ", "LOLC": "$/yr"
        }

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
        # Agora desempacotamos a tupla (linha_do_banco, id_do_caso) que a Query retorna
        for row, case_id in db_results:
            cid_str = str(case_id)

            if granularity == "GLOBAL":
                el_name = "Global System"

            elif granularity == "REGION":
                el_name = str(row.region_name)

                
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

        # 3. Monta a lista de elementos final
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
            elements=elements_dto
        )
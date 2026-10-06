import uuid
import numpy as np
from typing import List
from app.infrastructure.database.repositories.postgres_time_series_repository import PostgresTimeSeriesRepository
from app.infrastructure.database.repositories.postgres_case_repository import PostgresCaseRepository
from app.api.schemas.time_series_schema import ENSAggregationResponse
from app.domain.enums.granularity_enum import TimeSeriesGranularity

class GetENSAggregationUseCase:
    def __init__(self, ts_repo: PostgresTimeSeriesRepository, case_repo: PostgresCaseRepository):
        self.ts_repo = ts_repo
        self.case_repo = case_repo

    def execute(self, case_id: uuid.UUID, simulation_id: uuid.UUID, granularity: TimeSeriesGranularity) -> ENSAggregationResponse:
        # 1. Pega o nome do caso
        case_entity = self.case_repo.get_by_id(case_id)
        case_name = case_entity.display_name if case_entity else "Desconhecido"

        # 2. Busca os dados brutos de ENS no banco
        raw_series = self.ts_repo.get_ens_series_by_simulation(simulation_id)
        
        # 3. Calcula as médias
        ens_g = self._aggregate(raw_series.get("Main System - G", {}).get("values", []), granularity)
        ens_t = self._aggregate(raw_series.get("Main System - T", {}).get("values", []), granularity)
        ens_gt = self._aggregate(raw_series.get("Main System - G+T", {}).get("values", []), granularity)

        # Retorna o DTO estrito
        return ENSAggregationResponse(
            case_name=case_name,
            granularity=granularity,
            unit="MW", # A unidade média padrão da série
            ens_generation=ens_g,
            ens_transmission=ens_t,
            ens_gen_trans=ens_gt
        )

    def _aggregate(self, values: List[float], granularity: TimeSeriesGranularity) -> List[float]:
        if not values:
            return []
            
        arr = np.array(values)
        
        if granularity == TimeSeriesGranularity.HOURLY:
            return [float(v) for v in arr]
            
        elif granularity == TimeSeriesGranularity.WEEKLY:
            chunks = np.array_split(arr, 52)
            
        elif granularity == TimeSeriesGranularity.MONTHLY:
            chunks = np.array_split(arr, 12)
            
        elif granularity == TimeSeriesGranularity.YEARLY:
            chunks = [arr]
            
        else:
            return []

        # Calcula a média (mean) de cada bloco
        return [float(np.mean(chunk)) for chunk in chunks]
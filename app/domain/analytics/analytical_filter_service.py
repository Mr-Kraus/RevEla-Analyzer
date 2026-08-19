from typing import List, Dict, Any, Optional
from app.application.dto.filter_dto import AnalyticalFilterDTO

class AnalyticalFilterService:
    """
    Serviço de Domínio para aplicar os filtros analíticos (M03-F07).
    Filtra coleções de dados brutos antes que eles entrem nos motores de cálculo.
    """

    @staticmethod
    def apply_filters(data: List[Dict[str, Any]], filters: Optional[AnalyticalFilterDTO]) -> List[Dict[str, Any]]:
        if not filters:
            return data

        filtered_data = data

        if filters.region_external_ids:
            filtered_data = [
                item for item in filtered_data 
                if item.get("region_external_id") in filters.region_external_ids
            ]

        if filters.bus_external_ids:
            filtered_data = [
                item for item in filtered_data 
                if item.get("bus_external_id", item.get("external_id")) in filters.bus_external_ids
            ]

        if filters.generator_external_ids:
            filtered_data = [
                item for item in filtered_data 
                if item.get("generator_id", item.get("external_id")) in filters.generator_external_ids
            ]

        return filtered_data
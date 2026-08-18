from typing import List, Dict, Any

class AggregationEngine:
    """
    Motor responsável por consolidar e agrupar resultados em diferentes granularidades.
    """

    @staticmethod
    def aggregate_by_region(bus_results: List[Dict[str, Any]], indicators: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Soma os indicadores de todas as barras pertencentes a uma mesma região.
        Retorna: { "Region_1": {"epns": 15.2, "lolp": 0.05}, ... }
        """
        region_aggregations: Dict[str, Dict[str, float]] = {}

        for bus in bus_results:
            region_id = bus.get("region_external_id", "UNKNOWN")
            if region_id not in region_aggregations:
                region_aggregations[region_id] = {ind: 0.0 for ind in indicators}

            for ind in indicators:
                val = float(bus.get(ind, 0.0))
                region_aggregations[region_id][ind] += val

        # Arredondando para evitar ruído de ponto flutuante
        for reg in region_aggregations.values():
            for ind in indicators:
                reg[ind] = round(reg[ind], 6)

        return region_aggregations

    @staticmethod
    def aggregate_by_generation_class(generators: List[Dict[str, Any]], metric_key: str = "capacity_mva") -> Dict[str, float]:
        """
        Agrupa capacidades ou outras métricas por classe de tecnologia (ex: HIDRO, TERMI, SOLAR).
        """
        tech_aggregations: Dict[str, float] = {}
        
        for gen in generators:
            tech = gen.get("technology_type", "OTHER")
            val = float(gen.get(metric_key, 0.0))
            tech_aggregations[tech] = round(tech_aggregations.get(tech, 0.0) + val, 4)
            
        return tech_aggregations
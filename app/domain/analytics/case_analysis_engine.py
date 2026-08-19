from typing import Dict, List, Any
import uuid

class CaseAnalysisEngine:
    """
    Engine responsável pela análise detalhada e isolada de um único caso de estudo.
    Permite visualizar a saúde e o risco da infraestrutura dividida por:
    - Regiões
    - Barras
    - Geradores
    - Linhas de Transmissão
    - Transformadores
    """

    @staticmethod
    def analyze_regions(bus_results: List[Dict[str, Any]], indicator: str = "epns") -> List[Dict[str, Any]]:
        """
        Agrupa os indicadores por região e calcula o risco acumulado de cada uma.
        """
        region_map: Dict[str, float] = {}
        
        for bus in bus_results:
            region_id = bus.get("region_external_id", "DESCONHECIDA")
            val = float(bus.get(indicator, 0.0))
            region_map[region_id] = region_map.get(region_id, 0.0) + val
            
        region_analysis = [
            {"region_external_id": r_id, indicator: round(val, 6)}
            for r_id, val in region_map.items()
        ]
        
        return sorted(region_analysis, key=lambda x: x[indicator], reverse=True)
    

    @staticmethod
    def analyze_buses(bus_results: List[Dict[str, Any]], indicator: str = "epns") -> List[Dict[str, Any]]:
        """
        Mapeia e ordena as barras com base no indicador de risco especificado.
        """
        analyzed_buses = []
        for bus in bus_results:
            val = float(bus.get(indicator, 0.0))
            analyzed_buses.append({
                "bus_external_id": bus.get("bus_external_id"),
                "bus_name": bus.get("bus_name", f"Bus_{bus.get('bus_external_id')}"),
                indicator: round(val, 6)
            })
            
        return sorted(analyzed_buses, key=lambda x: x[indicator], reverse=True)

    @staticmethod
    def analyze_equipment_contribution(
        equipments: List[Dict[str, Any]], 
        contribution_key: str = "failure_rate"
    ) -> List[Dict[str, Any]]:
        """
        Análise genérica de contribuição/impacto para equipamentos (Geradores, Linhas, Transformadores).
        """
        analyzed_eqs = []
        for eq in equipments:
            val = float(eq.get(contribution_key, 0.0))
            analyzed_eqs.append({
                "equipment_id": eq.get("external_id"),
                "name": eq.get("name"),
                "impact_metric": contribution_key,
                "value": val
            })
            
        return sorted(analyzed_eqs, key=lambda x: x["value"], reverse=True)
    
    @staticmethod
    def analyze_generators(generators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Avalia a frota de geração baseada na sua capacidade e taxa de falha (se houver)."""
        analyzed = []
        for gen in generators:
            cap = float(gen.get("capacity_mva", 0.0))
            analyzed.append({
                "generator_id": gen.get("external_id"),
                "name": gen.get("name"),
                "capacity_mva": cap,
                # Lógica futura: cruzar capacidade com failure_rate para achar o "Risco Geração"
            })
        return sorted(analyzed, key=lambda x: x["capacity_mva"], reverse=True)

    @staticmethod
    def analyze_lines(lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Avalia o impacto e criticidade das Linhas de Transmissão."""
        analyzed = []
        for line in lines:
            frate = float(line.get("failure_rate", 0.0))
            analyzed.append({
                "line_id": line.get("external_id"),
                "name": line.get("name"),
                "failure_rate": frate
            })
        return sorted(analyzed, key=lambda x: x["failure_rate"], reverse=True)

    @staticmethod
    def analyze_transformers(transformers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Avalia o impacto e criticidade dos Transformadores."""
        analyzed = []
        for trafo in transformers:
            frate = float(trafo.get("failure_rate", 0.0))
            analyzed.append({
                "transformer_id": trafo.get("external_id"),
                "name": trafo.get("name"),
                "failure_rate": frate
            })
        return sorted(analyzed, key=lambda x: x["failure_rate"], reverse=True)
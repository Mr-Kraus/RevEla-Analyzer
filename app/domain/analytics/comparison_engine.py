from typing import Dict, List, Any, Optional
import uuid

class ComparisonEngine:
    """
    Motor encarregado de efetuar comparações quantitativas entre Casos/Simulações.
    Trabalha com comparações Par-a-Par (A x B) e Multicenário (N Casos).
    """

    @staticmethod
    def calculate_delta(val_a: float, val_b: float) -> Dict[str, float]:
        """Calcula a variação absoluta e percentual entre o Valor A (base) e o Valor B (comparado)."""
        abs_diff = val_b - val_a
        
        if val_a == 0.0:
            pct_diff = 0.0 if val_b == 0.0 else (100.0 if val_b > 0 else -100.0)
        else:
            pct_diff = (abs_diff / abs(val_a)) * 100.0
            
        return {
            "val_a": val_a,
            "val_b": val_b,
            "absolute_difference": round(abs_diff, 6),
            "percentage_difference": round(pct_diff, 4)
        }

    @classmethod
    def compare_global_indicators(
        cls, 
        dict_results_a: Dict[str, float], 
        dict_results_b: Dict[str, float],
        indicators: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compara os indicadores globais entre o Caso A e o Caso B.
        Exemplo: Compare LOLE, LOLP, EPNS entre o Caso Base e uma Expansão.
        """
        if indicators is None:
            indicators = ["lolp", "lole", "epns", "eens", "lolf", "lold", "lolc"]

        comparison_matrix = {}
        for ind in indicators:
            val_a = float(dict_results_a.get(ind, 0.0))
            val_b = float(dict_results_b.get(ind, 0.0))
            comparison_matrix[ind] = cls.calculate_delta(val_a, val_b)

        return comparison_matrix

    @classmethod
    def compare_buses(
        cls, 
        bus_results_a: List[Dict[str, Any]], 
        bus_results_b: List[Dict[str, Any]], 
        indicator: str
    ) -> List[Dict[str, Any]]:
        """
        Compara o comportamento das Barras do sistema entre o Caso A e o Caso B
        para um indicador específico (ex: 'epns').
        """
        map_b: Dict[str, float] = {b["bus_external_id"]: float(b.get(indicator, 0.0)) for b in bus_results_b}
        
        comparison = []
        for bus_a in bus_results_a:
            bus_id = bus_a["bus_external_id"]
            val_a = float(bus_a.get(indicator, 0.0))
            val_b = map_b.get(bus_id, 0.0)
            
            delta = cls.calculate_delta(val_a, val_b)
            comparison.append({
                "bus_external_id": bus_id,
                "bus_name": bus_a.get("bus_name", f"Bus_{bus_id}"),
                **delta
            })
            
        return comparison
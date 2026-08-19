from typing import List, Dict, Any, Set

class AnalyticalValidator:
    """Garante a integridade analítica exigida pela Fase M03-F10."""

    @staticmethod
    def validate_reliability_result(result_dict: Dict[str, Any]) -> List[str]:
        errors = []
        for key in ["lolp", "lole", "epns", "eens", "lolf", "lold", "lolc"]:
            val = result_dict.get(key)
            if val is None:
                errors.append(f"O indicador '{key}' não pode ser nulo.")
            elif isinstance(val, (int, float)) and val < 0:
                errors.append(f"O indicador '{key}' possui valor negativo inválido ({val}).")
        return errors

    @classmethod
    def audit_batch_results(cls, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audita nulos e duplicidades nos resultados das barras."""
        total_records = len(results_list)
        all_errors = []
        seen_buses: Set[str] = set()

        for idx, rec in enumerate(results_list):
            errs = cls.validate_reliability_result(rec)
            
            # Checagem de duplicidade
            bus_id = rec.get("bus_external_id")
            if bus_id:
                if bus_id in seen_buses:
                    errs.append(f"Duplicidade detectada para a barra {bus_id}.")
                seen_buses.add(bus_id)

            if errs:
                all_errors.append({"index": idx, "bus": bus_id, "errors": errs})

        return {
            "total_audited": total_records,
            "corrupted_count": len(all_errors),
            "is_consistent": len(all_errors) == 0,
            "details": all_errors
        }

    @staticmethod
    def audit_topology_consistency(buses: List[Dict[str, Any]], lines: List[Dict[str, Any]]) -> List[str]:
        """Verifica referências órfãs e inconsistências topológicas."""
        bus_ids = {b.get("external_id") for b in buses}
        topological_errors = []

        for line in lines:
            if line.get("from_bus_id") not in bus_ids:
                topological_errors.append(f"Linha {line.get('external_id')} conectada a barra de origem inexistente.")
            if line.get("to_bus_id") not in bus_ids:
                topological_errors.append(f"Linha {line.get('external_id')} conectada a barra de destino inexistente.")
                
        return topological_errors
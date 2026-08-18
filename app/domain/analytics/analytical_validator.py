from typing import List, Dict, Any

class AnalyticalValidator:
    """
    Garante a integridade analítica exigida pela Fase M03.13.
    Verifica se os resultados carregados do banco possuem consistência matemática e estrutural.
    """

    @staticmethod
    def validate_reliability_result(result_dict: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Validação de valores nulos ou negativos proibidos para probabilidades/energias
        for key in ["lolp", "lole", "epns", "eens", "lolf", "lold", "lolc"]:
            val = result_dict.get(key)
            if val is None:
                errors.append(f"O indicador '{key}' não pode ser nulo.")
            elif isinstance(val, (int, float)) and val < 0:
                errors.append(f"O indicador '{key}' possui valor negativo inválido ({val}).")

        return errors

    @classmethod
    def audit_batch_results(cls, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_records = len(results_list)
        corrupted_records = 0
        all_errors = []

        for idx, rec in enumerate(results_list):
            errs = cls.validate_reliability_result(rec)
            if errs:
                corrupted_records += 1
                all_errors.append({"index": idx, "errors": errs})

        return {
            "total_audited": total_records,
            "corrupted_count": corrupted_records,
            "is_consistent": corrupted_records == 0,
            "details": all_errors
        }
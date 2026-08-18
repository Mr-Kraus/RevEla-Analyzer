from typing import List, Dict, Any

class RankingEngine:
    """
    Motor encarregado de classificar elementos por ordem de criticidade.
    Suporta ordenação por barras, regiões, equipamentos e classes de geração.
    """

    @staticmethod
    def rank_elements(
        elements: List[Dict[str, Any]], 
        metric_key: str, 
        top_n: int = 10, 
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Gera um ranking geral para qualquer lista de dicionários com base em uma chave numérica.
        
        :param elements: Lista de elementos contendo métricas (ex: [{'bus_id': '1', 'epns': 15.2}, ...])
        :param metric_key: Chave da métrica usada para ordenação (ex: 'epns', 'lole')
        :param top_n: Quantidade de itens a retornar no top N (padrão: 10)
        :param descending: Se True, do maior para o menor (mais crítico primeiro)
        """
        if not elements:
            return []

        # Ordena com segurança garantindo conversão para float
        sorted_elements = sorted(
            elements,
            key=lambda item: float(item.get(metric_key, 0.0)),
            reverse=descending
        )

        top_elements = sorted_elements[:top_n]

        # Adiciona a posição do ranking (1º, 2º, 3º...)
        ranked_output = []
        for index, item in enumerate(top_elements, start=1):
            ranked_item = dict(item)
            ranked_item["rank_position"] = index
            ranked_output.append(ranked_item)

        return ranked_output

    @classmethod
    def rank_critical_buses(
        cls, 
        bus_results: List[Dict[str, Any]], 
        indicator: str = "epns", 
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Rankeia as Barras mais críticas para o indicador selecionado."""
        return cls.rank_elements(bus_results, metric_key=indicator, top_n=top_n, descending=True)

    @classmethod
    def rank_critical_regions(
        cls, 
        region_aggregated_results: List[Dict[str, Any]], 
        indicator: str = "epns", 
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Rankeia as Regiões elétricas mais críticas."""
        return cls.rank_elements(region_aggregated_results, metric_key=indicator, top_n=top_n, descending=True)
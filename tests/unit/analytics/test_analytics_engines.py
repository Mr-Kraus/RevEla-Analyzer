from app.domain.analytics.comparison_engine import ComparisonEngine
from app.domain.analytics.ranking_engine import RankingEngine
from app.domain.analytics.analytical_validator import AnalyticalValidator

def test_comparison_engine_deltas():
    delta = ComparisonEngine.calculate_delta(100.0, 150.0)
    assert delta["absolute_difference"] == 50.0
    assert delta["percentage_difference"] == 50.0

def test_ranking_engine_ordering():
    data = [
        {"bus_external_id": "1", "bus_name": "Bus A", "epns": 5.0},
        {"bus_external_id": "2", "bus_name": "Bus B", "epns": 50.0},
        {"bus_external_id": "3", "bus_name": "Bus C", "epns": 12.0},
    ]
    ranked = RankingEngine.rank_critical_buses(data, indicator="epns", top_n=2)
    assert len(ranked) == 2
    assert ranked[0]["bus_external_id"] == "2"  # O maior (50.0) deve ser o 1º colocado
    assert ranked[0]["rank_position"] == 1

def test_analytical_validator_clean_data():
    valid_record = {"lolp": 0.01, "lole": 10.0, "epns": 1.5, "eens": 12.0, "lolf": 2.0, "lold": 1.2, "lolc": 0.0}
    errors = AnalyticalValidator.validate_reliability_result(valid_record)
    assert len(errors) == 0
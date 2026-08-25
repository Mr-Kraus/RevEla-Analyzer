import uuid
from typing import Dict, Any, List
from app.domain.entities.time_series import TimeSeriesMetadata, DataTimeSeries

class TimeSeriesDtoMapper:
    @staticmethod
    def to_domain_metadata(sim_run_id: uuid.UUID, dto: Dict[str, Any]) -> TimeSeriesMetadata:
        return TimeSeriesMetadata(
            id=uuid.uuid4(),
            simulation_run_id=sim_run_id,
            name=dto.get("name", "Generic Series"),
            series_type=dto.get("series_type", "Unknown"),
            data_position=dto.get("data_position", "Input"),
            unit_x=dto.get("unit_x", "h"),
            unit_y=dto.get("unit_y", "MW")
        )

    @staticmethod
    def to_domain_data(metadata_id: uuid.UUID, raw_values: List[float]) -> DataTimeSeries:
        return DataTimeSeries(
            id=uuid.uuid4(),
            metadata_id=metadata_id,
            values=raw_values
        )
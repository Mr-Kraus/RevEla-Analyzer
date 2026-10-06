from typing import Dict, Any, List
from app.ingestion.parsers.raw_dtos import RawTimeSeriesDTO

class TimeSeriesNormalizer:
    """Normaliza as séries temporais brutas em dicionários canônicos padronizados."""
    
    def normalize(self, raw_data: RawTimeSeriesDTO, position: str = "Output", unit_x: str = "h", unit_y: str = "MW") -> List[Dict[str, Any]]:
        canonical_series = []
        
        for block in raw_data.series:
            canonical_series.append({
                "name": block.name,
                "series_type": block.series_type,
                "data_position": position,
                "unit_x": unit_x,
                "unit_y": unit_y,
                "raw_values": block.raw_values
            })
            
        return canonical_series
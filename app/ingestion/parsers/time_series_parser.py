import re
from typing import List, Dict, Any

class TimeSeriesParser:
    """Lê arquivos baseados em blocos de tags e extrai arrays brutos."""
    
    @staticmethod
    def parse_file(filepath: str, series_type: str) -> List[Dict[str, Any]]:
        parsed_series = []
        
        # Tenta ler com UTF-8, se der erro de acentuação (comum no Windows), usa latin-1
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as file:
                lines = file.readlines()
            
        is_reading_values = False
        current_values = []
        
        for line in lines:
            line = line.strip()
            if not line or line == ";": 
                continue
            
            if line.startswith("<VAL>") or line.startswith("<VALOR>"):
                is_reading_values = True
                current_values = []
                continue
                
            if line.startswith("<\VALOR>") or line.startswith("<FIM>") or line.startswith("</RID>"):
                if is_reading_values and current_values:
                    parsed_series.append({
                        "name": f"{series_type} Series", 
                        "series_type": series_type,
                        "raw_values": current_values
                    })
                is_reading_values = False
                continue
                
            if is_reading_values:
                clean_val = line.replace(";", "").replace(",", ".")
                try:
                    current_values.append(float(clean_val))
                except ValueError:
                    pass 
                    
        return parsed_series
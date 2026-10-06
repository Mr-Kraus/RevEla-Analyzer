import logging
from typing import List
from app.ingestion.parsers.raw_dtos import RawTimeSeriesDTO, RawTimeSeriesBlockDTO

logger = logging.getLogger(__name__)

class TimeSeriesParser:
    """Lê arquivos baseados em blocos de tags e extrai arrays brutos para TimeSeries."""
    
    @staticmethod
    def parse_file(filepath: str, series_type: str) -> RawTimeSeriesDTO:
        parsed_blocks = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {filepath}: {e}")
            return RawTimeSeriesDTO(series=[])

        num_series = 1
        
        
        for i, line in enumerate(lines):
            if line.strip().startswith("<NSERI>"):
                for j in range(i+1, min(i+5, len(lines))):
                    val = lines[j].strip().split(';')[0]
                    if val.isdigit():
                        num_series = int(val)
                        break
                break


        series_names = []
        for i, line in enumerate(lines):
            if line.strip().startswith("<SERIE>"):
                for j in range(i-1, -1, -1):
                    prev = lines[j].strip()
                    
                    if prev and not prev.startswith(";") and not prev.startswith("<"):
                        names = [n.strip() for n in prev.split(";") if n.strip()]
                        if names and ("série" in names[0].lower() or "serie" in names[0].lower()):
                            continue
                            
                        if names:
                            series_names = names
                        break
                break

        # Ajusta o total de colunas caso encontre mais nomes do que o NSERI dizia
        num_series = max(num_series, len(series_names))
        
        # Preenche com nomes genéricos caso falte algum cabeçalho
        for k in range(len(series_names), num_series):
            series_names.append(f"{series_type} Series {k+1}")

        # 3. Lê os dados matriciais com base em num_series
        is_reading_values = False
        series_data = [[] for _ in range(num_series)]
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped == ";": 
                continue

            if line_stripped.startswith("<VAL>") or line_stripped.startswith("<VALOR>"):
                is_reading_values = True
                continue
                
            if line_stripped.startswith("<\\VALOR>") or line_stripped.startswith("</VALOR>") or line_stripped.startswith("<FIM>") or line_stripped.startswith("</RID>"):
                is_reading_values = False
                continue
                
            if is_reading_values:
                parts = line_stripped.split(";")
                # Varre exatamente o número de colunas descobertas
                for col_idx in range(num_series):
                    if col_idx < len(parts):
                        clean_val = parts[col_idx].strip().replace(",", ".")
                        if clean_val:
                            try:
                                series_data[col_idx].append(float(clean_val))
                            except ValueError:
                                series_data[col_idx].append(0.0)
                        else:
                            series_data[col_idx].append(0.0)
                    else:
                        series_data[col_idx].append(0.0)

        # 4. Empacota no DTO Bruto de Transporte
        for col_idx, data_array in enumerate(series_data):
            if data_array:
                parsed_blocks.append(RawTimeSeriesBlockDTO(
                    name=series_names[col_idx],
                    series_type=series_type,
                    raw_values=data_array
                ))

        return RawTimeSeriesDTO(series=parsed_blocks)
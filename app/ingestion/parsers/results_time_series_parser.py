import logging
from typing import List
from app.ingestion.parsers.raw_dtos import RawTimeSeriesDTO, RawTimeSeriesBlockDTO

logger = logging.getLogger(__name__)

class ResultsTimeSeriesParser:
    """
    Parser especializado para arquivos de saída (Results) do tipo CSV.
    Estrutura esperada:
    Linha 1: Contexto (ex: ;Main System;;;)
    Linha 2: Cabeçalhos (ex: Hour;G; T; G+T;)
    Linha 3+: Valores temporais
    """
    
    @staticmethod
    def parse_file(filepath: str, series_type: str) -> RawTimeSeriesDTO:
        logger.info(f"Lendo CSV de Resultados: {filepath}")
        parsed_blocks = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as file:
                lines = file.readlines()

        if len(lines) < 2:
            logger.warning(f"Arquivo {filepath} está vazio ou inválido.")
            return RawTimeSeriesDTO(series=[])

        context_name = lines[0].replace(";", "").strip()
        if not context_name:
            context_name = "System"

        
        raw_headers = lines[1].split(';')
        
        
        headers = [h.strip() for h in raw_headers[1:] if h.strip()]

       
        series_data = [[] for _ in headers]

        # 3. Extrair os dados da Linha 3 em diante
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue

            parts = line.split(';')
            
            # parts[0] é a Hora (ignoramos, pois a posição no array dita a hora)
            # Varremos do parts[1] em diante
            for col_idx, header in enumerate(headers):
                if col_idx + 1 < len(parts):
                    val_str = parts[col_idx + 1].strip().replace(',', '.')
                    if val_str:
                        try:
                            series_data[col_idx].append(float(val_str))
                        except ValueError:
                            series_data[col_idx].append(0.0)

        
        for col_idx, header in enumerate(headers):
            # O nome da série ficará, por exemplo: "Main System - G" ou "Main System - G+T"
            full_name = f"{context_name} - {header}"
            
            parsed_blocks.append(RawTimeSeriesBlockDTO(
                name=full_name,
                series_type=series_type,
                raw_values=series_data[col_idx]
            ))

        return RawTimeSeriesDTO(series=parsed_blocks)
import re
from typing import List, Dict, Any

class TimeSeriesParser:
    """Lê arquivos baseados em blocos de tags e extrai arrays brutos (múltiplas colunas suportadas)."""
    
    @staticmethod
    def parse_file(filepath: str, series_type: str) -> List[Dict[str, Any]]:
        parsed_series = []
        
        # Tenta ler com UTF-8, se der erro de acentuação usa latin-1
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as file:
                lines = file.readlines()
            
        is_reading_values = False
        series_names = []
        series_data = []  # Será uma lista de listas: [ [curva1], [curva2], ... ]
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or line_stripped == ";": 
                continue
            
            # 1. Identifica os nomes das séries (estão na linha antes da tag <SERIE>)
            if line_stripped.startswith("<SERIE>"):
                if i > 0:
                    header_line = lines[i-1].strip()
                    # Separa os nomes e remove colunas vazias
                    names = [n.strip() for n in header_line.split(";") if n.strip()]
                    if names:
                        series_names = names
                continue

            # 2. Inicializa as listas quando a matriz de dados começar
            if line_stripped.startswith("<VAL>") or line_stripped.startswith("<VALOR>"):
                is_reading_values = True
                # Cria um array vazio para cada série que descobrimos no cabeçalho
                num_series = len(series_names) if series_names else 1
                series_data = [[] for _ in range(num_series)]
                continue
                
            # 3. Finaliza a leitura e empacota os resultados
            if line_stripped.startswith("<\\VALOR>") or line_stripped.startswith("</VALOR>") or line_stripped.startswith("<FIM>") or line_stripped.startswith("</RID>"):
                if is_reading_values and series_data:
                    for col_idx, data_array in enumerate(series_data):
                        # Pega o nome real se existir, senão cria um genérico
                        s_name = series_names[col_idx] if col_idx < len(series_names) else f"{series_type} Series {col_idx+1}"
                        
                        parsed_series.append({
                            "name": s_name, 
                            "series_type": series_type,
                            "raw_values": data_array
                        })
                is_reading_values = False
                continue
                
            # 4. Lê os valores da matriz linha por linha, coluna por coluna
            if is_reading_values:
                parts = line_stripped.split(";")
                for col_idx, part in enumerate(parts):
                    # Garante que não vamos ler mais colunas do que mapeamos
                    if col_idx < len(series_data):
                        clean_val = part.strip().replace(",", ".")
                        if clean_val:
                            try:
                                series_data[col_idx].append(float(clean_val))
                            except ValueError:
                                series_data[col_idx].append(0.0) # Previne falhas com sujeiras
                                
        return parsed_series
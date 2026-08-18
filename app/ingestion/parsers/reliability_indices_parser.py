import logging
from pathlib import Path
from typing import List, Dict
from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawReliabilityIndicesDTO

logger = logging.getLogger(__name__)

class ReliabilityIndicesParser(BaseParser):
    """
    Parser para os resultados finais de confiabilidade.
    Regra contratual: Busca por Âncoras e limpeza de valores nulos nativos do C++ (-nan(ind)).
    """

    def parse(self, file_path: Path) -> RawReliabilityIndicesDTO:
        logger.info(f"Iniciando parsing de Índices de Confiabilidade: {file_path.name}")
        blocks: Dict[str, List[List[str]]] = {}
        
        current_anchor = None
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for raw_line in f:
                line = raw_line.strip('\n').strip()
                
                # Linha em branco encerra o bloco atual
                if not line:
                    current_anchor = None
                    continue
                    
                # 1. Identificação de Âncoras
                if "Total Global Indices:" in line:
                    current_anchor = "TOTAL_GLOBAL"
                    blocks[current_anchor] = []
                    continue
                elif "Global Indices by Failure Type:" in line:
                    current_anchor = "BY_FAILURE_TYPE"
                    blocks[current_anchor] = []
                    continue
                elif "Main System Indices by Region:" in line:
                    current_anchor = "BY_REGION"
                    blocks[current_anchor] = []
                    continue
                elif "Main System Indices by Bus:" in line:
                    current_anchor = "BY_BUS"
                    blocks[current_anchor] = []
                    continue
                    
                # 2. Leitura dos Dados (se estivermos dentro de uma âncora)
                if current_anchor:
                    parts = line.split(';')
                    # 3. Regra de Limpeza: Substitui a aberração matemática do C++
                    clean_parts = [p.strip() if p.strip() != "-nan(ind)" else "NaN" for p in parts]
                    blocks[current_anchor].append(clean_parts)
                    
        logger.info(f"Parsing concluído. {len(blocks)} matrizes de resultados extraídas.")
        return RawReliabilityIndicesDTO(blocks=blocks)
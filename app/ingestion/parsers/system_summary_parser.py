import logging
from typing import Dict, Any, List
from app.ingestion.parsers.raw_dtos import RawSystemSummaryDTO

logger = logging.getLogger(__name__)

class SystemSummaryParser:
    """Parser para o arquivo 'system summary.csv' (ou similar)."""
    
    @staticmethod
    def parse_file(filepath: str) -> RawSystemSummaryDTO:
        logger.info(f"Lendo System Summary: {filepath}")
        
        general_info = {}
        generators_info = []
        is_parsing_generators = False
        generator_headers = []

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as file:
                lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Verifica se entrou no bloco de geradores
            if line.startswith("Generators information:"):
                is_parsing_generators = True
                continue
                
            # Se a linha estiver vazia ou for quebra de bloco após os geradores
            if is_parsing_generators and line.startswith("Rated load/generation capacity ratio"):
                is_parsing_generators = False
            
            parts = [p.strip() for p in line.split(';')]
            
            if is_parsing_generators:
                if not generator_headers:
                    # Salva os cabeçalhos (Technology, Facilities, Units, etc)
                    generator_headers = [p for p in parts if p]
                else:
                    # Monta o dicionário para cada linha de gerador
                    gen_data = {}
                    for idx, header in enumerate(generator_headers):
                        if idx < len(parts) and parts[idx]:
                            gen_data[header] = parts[idx]
                    if gen_data:
                        generators_info.append(gen_data)
            else:
                # É uma linha de chave;valor comum
                if len(parts) >= 2:
                    key = parts[0].replace(":", "").strip()
                    value = parts[1].strip()
                    general_info[key] = value

        return RawSystemSummaryDTO(general_info=general_info, generators_info=generators_info)
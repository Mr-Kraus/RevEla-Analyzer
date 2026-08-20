import logging
from pathlib import Path
from typing import List
from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawSystemDTO, RawSystemBlockDTO

logger = logging.getLogger(__name__)

class TemplateSystemParser(BaseParser):
    """
    Máquina de Estados para ler o 'Template System.csv'.
    Extrai múltiplos blocos (<BARRAS>, <TRAFOS>, etc.) sequencialmente.
    """

    def parse(self, file_path: Path) -> RawSystemDTO:
        logger.info(f"Iniciando parsing de Sistema (Máquina de Estados): {file_path.name}")
        blocks = {}

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            state = 'SEARCHING'
            current_block = None
            buffer_lines = []
            headers = []
            records = []

            for raw_line in f:
                line = raw_line.strip()
                line_clean = line.strip(';')

                if state == 'SEARCHING':
                    if line.startswith('<') and line_clean.endswith('>'):
                        tag = line_clean[1:-1].strip()
                        # Ignora tags internas (Adicionado suporte ao /VAL por segurança)
                        if tag not in ['VAL', '\\VAL', '/VAL', 'MODEL']:
                            current_block = tag
                            state = 'WAITING_FOR_VAL'
                            buffer_lines = []
                            records = []

                elif state == 'WAITING_FOR_VAL':
                    if line.startswith('<VAL>'):
                        headers = self._extract_and_deduplicate_headers(buffer_lines)
                        state = 'READING_DATA'
                    else:
                        if line: 
                            buffer_lines.append(raw_line.strip('\n'))

                elif state == 'READING_DATA':
                    if line.startswith('<\\VAL>') or line.startswith('</VAL>'):
                        blocks[current_block] = RawSystemBlockDTO(
                            block_name=current_block,
                            headers=headers,
                            records=records
                        )
                        logger.debug(f"Bloco <{current_block}> capturado com {len(records)} registros.")
                        state = 'SEARCHING'
                    else:
                        if line_clean:
                            parts = [p.strip() for p in raw_line.strip('\n').split(';')]
                            record = {}
                            for i, h in enumerate(headers):
                                if h: 
                                    record[h] = parts[i] if i < len(parts) else ""
                            records.append(record)

        logger.info(f"Parsing de Sistema concluído. {len(blocks)} blocos extraídos.")
        return RawSystemDTO(blocks=blocks)

    def _extract_and_deduplicate_headers(self, buffer: List[str]) -> List[str]:
        """
        Varre o buffer para achar a linha de cabeçalho principal.
        Procura ativamente por 'ID' ou 'CLAS' na primeira coluna para não ser
        enganado por variáveis perdidas no arquivo (ex: 'SIT', 'PRP').
        """
        raw_headers = []
        for line in buffer:
            parts = line.split(';')
            first_col = parts[0].strip().upper()
            
            # Ancoragem forte: O cabeçalho real sempre começa com ID ou CLAS
            if first_col in ['ID', 'CLAS', 'NUM', 'NODE'] and not line.startswith('<'):
                raw_headers = [p.strip() for p in parts]
                break

        # Fallback de segurança (se não achar ID, pega a primeira linha com muitas colunas)
        if not raw_headers:
            for line in buffer:
                parts = line.split(';')
                if len([p for p in parts if p.strip()]) > 3 and not line.startswith('<'):
                    raw_headers = [p.strip() for p in parts]
                    break

        seen = {}
        deduped = []
        for h in raw_headers:
            if not h:
                deduped.append("")
                continue
            if h in seen:
                seen[h] += 1
                deduped.append(f"{h}_{seen[h]}")
            else:
                seen[h] = 1
                deduped.append(h)
        return deduped
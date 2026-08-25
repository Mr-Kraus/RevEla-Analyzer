import logging
from pathlib import Path
from typing import List, Dict

from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawSystemDTO, RawSystemBlockDTO

logger = logging.getLogger(__name__)

class TemplateSystemParser(BaseParser):
    """
    Máquina de Estados Genérica para ler o 'Template System.csv'.
    """
    def __init__(self, tag_mapping: Dict[str, str] = None):
        super().__init__()
        # Dicionário que traduz a Tag lida no arquivo para a Tag Canônica do REVELA
        self.tag_mapping = tag_mapping or {}

    def parse(self, file_path: Path) -> RawSystemDTO:
        logger.info(f"Iniciando parsing de Sistema: {file_path.name}")
        blocks = {}
        carga_nominal = 0.0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            # (Mantém a lógica da CARGAP idêntica ao que você já fez)
            for i, line in enumerate(lines):
                if line.startswith("<CARGAP>"):
                    if i + 1 < len(lines):
                        partes = lines[i+1].split(';')
                        if len(partes) > 1 and partes[1].strip():
                            carga_nominal = float(partes[1].replace(',', '.'))
                    break

        state = "SEARCHING"
        current_block = None
        buffer_lines = []
        headers = []
        records = []

        for raw_line in lines:
            line = raw_line.strip()
            line_clean = line.strip(";")

            if state == "SEARCHING":
                if line.startswith("<") and line_clean.endswith(">"):
                    original_tag = line_clean[1:-1].strip()

                    if original_tag not in ["VAL", "\\VAL", "/VAL", "MODEL"]:
                        # TRADUÇÃO MÁGICA: Pega o nome padrão, ou mantém o original se não tiver mapeamento
                        current_block = self.tag_mapping.get(original_tag, original_tag)
                        
                        state = "WAITING_FOR_VAL"
                        buffer_lines = []
                        records = []

            elif state == "WAITING_FOR_VAL":
                if line.startswith("<VAL>"):
                    headers = self._extract_and_deduplicate_headers(buffer_lines)
                    state = "READING_DATA"
                else:
                    if line:
                        buffer_lines.append(raw_line.strip("\n"))

            elif state == "READING_DATA":
                if line.startswith("<\\VAL>") or line.startswith("</VAL>"):
                    blocks[current_block] = RawSystemBlockDTO(
                        block_name=current_block,
                        headers=headers,
                        records=records,
                    )
                    state = "SEARCHING"
                else:
                    if line_clean:
                        parts = [p.strip() for p in raw_line.strip("\n").split(";")]
                        record = {}
                        for i, h in enumerate(headers):
                            if h:
                                record[h] = parts[i] if i < len(parts) else ""
                        records.append(record)

        return RawSystemDTO(blocks=blocks, carga_nominal=carga_nominal)

    def _extract_and_deduplicate_headers(
        self,
        buffer: List[str],
    ) -> List[str]:

        raw_headers = []

        for line in buffer:
            parts = line.split(";")
            first_col = parts[0].strip().upper()

            if (
                first_col in ["ID", "CLAS", "NUM", "NODE"]
                and not line.startswith("<")
            ):
                raw_headers = [p.strip() for p in parts]
                break

        if not raw_headers:
            for line in buffer:
                parts = line.split(";")

                if (
                    len([p for p in parts if p.strip()]) > 3
                    and not line.startswith("<")
                ):
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
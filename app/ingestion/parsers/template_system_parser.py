import logging
from pathlib import Path
from typing import List

from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawSystemDTO, RawSystemBlockDTO

logger = logging.getLogger(__name__)


class TemplateSystemParser(BaseParser):
    """
    Máquina de Estados para ler o 'Template System.csv'.

    Extrai:
    - blocos estruturados (<BARRAS>, <TRAFOS>, etc.)
    - carga nominal do sistema (<CARGAP>)
    """

    def parse(self, file_path: Path) -> RawSystemDTO:
        logger.info(
            f"Iniciando parsing de Sistema (Máquina de Estados): {file_path.name}"
        )

        blocks = {}
        
        # Capturando a carga dinamicamente
        carga_nominal = 0.0
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("<CARGAP>"):
                    logger.info(f"[RASTREADOR - PARSER] Tag <CARGAP> encontrada na linha {i}")
                    if i + 1 < len(lines):
                        partes = lines[i+1].split(';')
                        logger.info(f"[RASTREADOR - PARSER] Linha seguinte split: {partes}")
                        if len(partes) > 1 and partes[1].strip():
                            carga_nominal = float(partes[1].replace(',', '.'))
                            logger.info(f"[RASTREADOR - PARSER] CARGA EXTRAÍDA COM SUCESSO: {carga_nominal}")
                    break
        
        # =====================================================
        # MÁQUINA DE ESTADOS ORIGINAL
        # =====================================================

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
                    tag = line_clean[1:-1].strip()

                    if tag not in ["VAL", "\\VAL", "/VAL", "MODEL"]:
                        current_block = tag
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
                if (
                    line.startswith("<\\VAL>")
                    or line.startswith("</VAL>")
                ):
                    blocks[current_block] = RawSystemBlockDTO(
                        block_name=current_block,
                        headers=headers,
                        records=records,
                    )

                    logger.debug(
                        f"Bloco <{current_block}> capturado com "
                        f"{len(records)} registros."
                    )

                    state = "SEARCHING"

                else:
                    if line_clean:
                        parts = [
                            p.strip()
                            for p in raw_line.strip("\n").split(";")
                        ]

                        record = {}

                        for i, h in enumerate(headers):
                            if h:
                                record[h] = (
                                    parts[i]
                                    if i < len(parts)
                                    else ""
                                )

                        records.append(record)

        logger.info(
            f"Parsing concluído. "
            f"{len(blocks)} blocos extraídos. "
            f"Carga nominal = {carga_nominal}"
        )

        return RawSystemDTO(
            blocks=blocks,
            carga_nominal=carga_nominal, # A carga vai para o DTO aqui!
        )

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
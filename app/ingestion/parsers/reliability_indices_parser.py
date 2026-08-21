import logging
from pathlib import Path
from typing import List, Dict

from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawReliabilityIndicesDTO

logger = logging.getLogger(__name__)


class ReliabilityIndicesParser(BaseParser):
    """
    Parser para resultados finais de confiabilidade.
    Extrai blocos de índices, anos simulados e intervalos de confiança.
    """

    def parse(self, file_path: Path) -> RawReliabilityIndicesDTO:
        logger.info(f"Iniciando parsing de Índices de Confiabilidade: {file_path.name}")

        blocks: Dict[str, List[List[str]]] = {}
        current_anchor = None
        confidence_intervals = {}
        simulated_years = 0

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for raw_line in f:
                line = raw_line.strip()

                # --- EXTRAÇÕES RÁPIDAS (Variáveis Isoladas) ---
                if line.startswith("Simulated years;"):
                    try:
                        simulated_years = int(line.split(';')[1].strip())
                        logger.info(f"[RASTREADOR] Anos Simulados lidos: {simulated_years}")
                    except ValueError:
                        pass
                
                elif line.startswith("LOLP (prob.);="):
                    partes = line.split(';')
                    if len(partes) > 3 and partes[3].strip(): confidence_intervals["LOLP"] = partes[3].strip()
                elif line.startswith("LOLE (h/year);="):
                    partes = line.split(';')
                    if len(partes) > 3 and partes[3].strip(): confidence_intervals["LOLE"] = partes[3].strip()
                elif line.startswith("EPNS (MW);="):
                    partes = line.split(';')
                    if len(partes) > 3 and partes[3].strip(): confidence_intervals["EPNS"] = partes[3].strip()
                elif line.startswith("EENS (MWh/year);="):
                    partes = line.split(';')
                    if len(partes) > 3 and partes[3].strip(): confidence_intervals["EENS"] = partes[3].strip()
                elif line.startswith("LOLF (occ./year);="):
                    partes = line.split(';')
                    if len(partes) > 3 and partes[3].strip(): confidence_intervals["LOLF"] = partes[3].strip()

                # --- LÓGICA ORIGINAL DE BLOCOS MATRICIAIS ---
                if not line:
                    current_anchor = None
                    continue

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

                if current_anchor:
                    parts = line.split(";")
                    clean_parts = [
                        p.strip() if p.strip() != "-nan(ind)" else "NaN"
                        for p in parts
                    ]
                    blocks[current_anchor].append(clean_parts)

        logger.info(f"Parsing concluído. {len(blocks)} matrizes extraídas.")

        return RawReliabilityIndicesDTO(
            blocks=blocks,
            simulated_years=simulated_years,
            confidence_intervals=confidence_intervals
        )
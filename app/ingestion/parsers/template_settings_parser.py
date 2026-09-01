import logging
from pathlib import Path
from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawSettingsDTO

logger = logging.getLogger(__name__)

class TemplateSettingsParser(BaseParser):
    """
    Realiza o parse do arquivo Template Settings.csv.
    Extrai parâmetros Key/Value e destaca metadados essenciais.
    """

    def parse(self, file_path: Path) -> RawSettingsDTO:
        logger.info(f"Iniciando parsing de Settings: {file_path.name}")

        parameters = {}
        analysis_type = "N/A"
        syst_rep = "N/A"
        coef_beta = "N/A"

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f.readlines():
                line = line.strip()
                if not line or line.startswith(";"):
                    continue

                parts = line.split(";")
                if len(parts) >= 2:
                    key = parts[0].strip().upper()
                    raw_value = parts[1].strip()

                    # ==========================================
                    # EXTRAÇÕES EXPLÍCITAS DE ALTO VALOR
                    # ==========================================
                    if key == "ANALYSIS_TYPE":
                        analysis_type = raw_value
                    elif key == "SYST_REP":
                        syst_rep = raw_value
                    elif key == "COEF_BETA":
                        coef_beta = raw_value

                    # ==========================================
                    # PARSING GENÉRICO E TIPAGEM
                    # ==========================================
                    if raw_value.lower() == "true":
                        val = True
                    elif raw_value.lower() == "false":
                        val = False
                    else:
                        try:
                            val = float(raw_value) if "." in raw_value else int(raw_value)
                        except ValueError:
                            val = raw_value

                    parameters[key] = val

        logger.info(f"Parsing concluído. {len(parameters)} parâmetros extraídos.")

        return RawSettingsDTO(
            parameters=parameters,
            analysis_type=analysis_type,
            system_representation=syst_rep,
            convergence_beta=coef_beta
        )
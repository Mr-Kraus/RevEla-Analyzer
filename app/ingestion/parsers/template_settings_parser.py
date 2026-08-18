import logging
from pathlib import Path
from app.ingestion.parsers.base_parser import BaseParser
from app.ingestion.parsers.raw_dtos import RawSettingsDTO

logger = logging.getLogger(__name__)

class TemplateSettingsParser(BaseParser):
    """
    Realiza o parse do arquivo 'Template Settings.csv'.
    Regra contratual: Leitura em dicionário (Key-Value) delimitado por ';'.
    """

    def parse(self, file_path: Path) -> RawSettingsDTO:
        logger.info(f"Iniciando parsing de Settings: {file_path.name}")
        parameters = {}

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(';')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    raw_value = parts[1].strip()

                    # Conversão básica de tipos embutidos na string (Booleano/Numérico)
                    if raw_value.lower() == 'true':
                        val = True
                    elif raw_value.lower() == 'false':
                        val = False
                    else:
                        try:
                            # Tenta converter para número se possível, senão mantém string
                            val = float(raw_value) if '.' in raw_value else int(raw_value)
                        except ValueError:
                            val = raw_value

                    parameters[key] = val

        logger.info(f"Parsing concluído. {len(parameters)} parâmetros extraídos.")
        return RawSettingsDTO(parameters=parameters)
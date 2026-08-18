import logging
from pathlib import Path
from typing import List

from app.ingestion.discovery.case_candidate import CaseCandidate
from app.application.interfaces.ingestion_services import ICaseDiscoveryService

logger = logging.getLogger(__name__)


class CaseDiscovery(ICaseDiscoveryService):
    """
    Serviço de varredura do sistema de arquivos para identificar a estrutura do caso ReLeVa.
    Implementa ICaseDiscoveryService.
    """

    def discover(self, target_path: Path) -> CaseCandidate:
        logger.info(f"CASE_DISCOVERY_STARTED no caminho: {target_path}")

        candidate = CaseCandidate(root_path=target_path, case_name=target_path.name)

        if not target_path.exists() or not target_path.is_dir():
            error_msg = f"O caminho especificado não existe ou não é um diretório: {target_path}"
            logger.error(error_msg)
            candidate.errors.append(error_msg)
            return candidate

        # Varredura de Templates na raiz do caso
        for item in target_path.iterdir():
            if item.is_file() and item.name.lower().startswith("template") and item.name.lower().endswith(".csv"):
                candidate.detected_templates.append(item)

        # Varredura de Diretórios e Arquivos de Resultados (Results_*)
        for item in target_path.iterdir():
            if item.is_dir() and item.name.lower().startswith("results"):
                candidate.detected_result_directories.append(item)
                for res_file in item.rglob("*.csv"):
                    if res_file.is_file():
                        candidate.detected_result_files.append(res_file)

        logger.info(
            f"CASE_DISCOVERY_COMPLETED para {candidate.case_name}: "
            f"{len(candidate.detected_templates)} template(s), "
            f"{len(candidate.detected_result_files)} arquivo(s) de resultado."
        )

        return candidate
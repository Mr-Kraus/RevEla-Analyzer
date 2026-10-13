import logging
from pathlib import Path

from app.ingestion.discovery.case_candidate import CaseCandidate
from app.application.interfaces.ingestion_services import ICaseDiscoveryService

logger = logging.getLogger(__name__)

class CaseDiscovery(ICaseDiscoveryService):
    """
    Serviço de varredura do sistema de arquivos para identificar a estrutura do caso ReLeVa.
    Atualizado para destacar os Templates de Sistema e Diretórios de Resultados.
    """

    def discover(self, target_path: Path) -> CaseCandidate:
        logger.info(f"CASE_DISCOVERY_STARTED no caminho: {target_path}")

        candidate = CaseCandidate(root_path=target_path, case_name=target_path.name)

        if not target_path.exists() or not target_path.is_dir():
            error_msg = f"O caminho especificado não existe ou não é um diretório: {target_path}"
            logger.error(error_msg)
            candidate.errors.append(error_msg)
            return candidate

        # Varredura na raiz do caso
        for item in target_path.iterdir():
            
            # 1. Identifica e categoriza os Templates
            if item.is_file() and item.name.lower().startswith("template") and item.name.lower().endswith(".csv"):
                candidate.detected_templates.append(item)
                
                # Destaca os Template System para escolha do usuário
                if item.name.lower().startswith("template system"):
                    candidate.system_templates.append(item)

            # 2. Identifica as Pastas de Resultados
            elif item.is_dir() and item.name.lower().startswith("results"):
                candidate.result_directories.append(item)
                
                for res_file in item.rglob("*.csv"):
                    if res_file.is_file():
                        candidate.detected_result_files.append(res_file)

        # Avisos se estiver faltando opções base
        if not candidate.system_templates:
            candidate.warnings.append("Nenhum 'Template System' encontrado na raiz.")
        if not candidate.result_directories:
            candidate.warnings.append("Nenhuma pasta de resultados ('Results...') encontrada.")

        logger.info(
            f"CASE_DISCOVERY_COMPLETED para {candidate.case_name}: "
            f"{len(candidate.system_templates)} Template System(s), "
            f"{len(candidate.result_directories)} pasta(s) de resultados."
        )

        return candidate
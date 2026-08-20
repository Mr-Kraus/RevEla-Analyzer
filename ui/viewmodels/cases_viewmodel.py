from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient
import os

class CasesViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    case_deleted = pyqtSignal(str)

    # Sinais para o fluxo de importação
    import_started = pyqtSignal()
    import_success = pyqtSignal(str)
    import_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_case_id = None # Guarda o ID temporário durante a importação

    def load_cases(self):
        worker = self.api_client.make_request_async("GET", "/cases")
        worker.finished.connect(self._on_cases_loaded)
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        # É importante manter uma referência ao worker para ele não ser destruído pelo Garbage Collector
        self._load_worker = worker 

    def _on_cases_loaded(self, response):
        if response.status_code == 200:
            cases = response.json().get("data", [])
            self.cases_loaded.emit(cases)
        else:
            self.error_occurred.emit("Erro ao carregar a lista de casos.")

    # ==========================================
    # FLUXO DE IMPORTAÇÃO (Registro -> Ingestão)
    # ==========================================
    def import_case(self, folder_path: str):
        self.import_started.emit()
        folder_name = os.path.basename(folder_path)
        
        # 1º Passo: Registrar o caso no banco
        payload = {
            "external_name": folder_name[:10], # Pega o comecinho do nome como ID externo
            "display_name": f"Caso: {folder_name}",
            "source_path": folder_path
        }
        
        self._reg_worker = self.api_client.make_request_async("POST", "/cases", json=payload)
        self._reg_worker.finished.connect(self._on_case_registered)
        self._reg_worker.error.connect(self.import_failed.emit)
        self._reg_worker.start()

    def _on_case_registered(self, response):
        if response.status_code == 200:
            data = response.json().get("data", {})
            self.current_case_id = data.get("id")
            
            # 2º Passo: Mandar o servidor Ingerir os CSVs (Isso pode demorar lá no backend!)
            self._ingest_worker = self.api_client.make_request_async("POST", f"/cases/{self.current_case_id}/import")
            self._ingest_worker.finished.connect(self._on_case_ingested)
            self._ingest_worker.error.connect(self.import_failed.emit)
            self._ingest_worker.start()
        else:
            self.import_failed.emit("Falha ao registrar o caso no banco de dados.")

    def _on_case_ingested(self, response):
        if response.status_code == 200:
            self.import_success.emit("Caso importado e processado com sucesso!")
            self.load_cases() # Atualiza a tabela
        else:
            self.import_failed.emit("Erro durante o processamento dos CSVs no servidor.")

    # ==========================================
    # FLUXO DE EXCLUSÃO
    # ==========================================
    def delete_case(self, case_id: str):
        """Dispara a requisição DELETE para a API de forma assíncrona."""
        self._del_worker = self.api_client.make_request_async("DELETE", f"/cases/{case_id}")
        self._del_worker.finished.connect(lambda resp: self._on_case_deleted(resp, case_id))
        self._del_worker.start()

    def _on_case_deleted(self, response, case_id: str):
        if response.status_code == 200:
            self.case_deleted.emit(case_id)
            self.load_cases()  # Recarrega a lista atualizada automaticamente
        else:
            msg = f"Falha ao excluir o caso. Status: {response.status_code}"
            self.error_occurred.emit(msg)
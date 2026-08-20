from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient
import os

class CasesViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    case_deleted = pyqtSignal(str)
    case_updated = pyqtSignal()
    regions_loaded = pyqtSignal(list)
    regions_updated = pyqtSignal()

    import_started = pyqtSignal()
    import_success = pyqtSignal(str)
    import_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_case_id = None

    def load_cases(self):
        worker = self.api_client.make_request_async("GET", "/cases")
        worker.finished.connect(self._on_cases_loaded)
        worker.error.connect(self.error_occurred.emit)
        worker.start()
        self._load_worker = worker 

    def _on_cases_loaded(self, response):
        if response.status_code == 200:
            cases = response.json().get("data", [])
            self.cases_loaded.emit(cases)
        else:
            self.error_occurred.emit("Erro ao carregar a lista de casos.")

    def import_case(self, folder_path: str, display_name: str):
        self.import_started.emit()
        folder_name = os.path.basename(folder_path)
        
        payload = {
            "external_name": folder_name[:10],
            "display_name": display_name or f"Caso: {folder_name}",
            "source_path": folder_path
        }
        
        self._reg_worker = self.api_client.make_request_async("POST", "/cases", json=payload)
        self._reg_worker.finished.connect(self._on_case_registered)
        self._reg_worker.error.connect(self.import_failed.emit)
        self._reg_worker.start()

    def _on_case_registered(self, response):
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get("success"):
                data = resp_data.get("data", {})
                self.current_case_id = data.get("id")
                
                # Só manda ingerir se o registro no banco deu 100% certo
                self._ingest_worker = self.api_client.make_request_async("POST", f"/cases/{self.current_case_id}/import")
                self._ingest_worker.finished.connect(self._on_case_ingested)
                self._ingest_worker.error.connect(self.import_failed.emit)
                self._ingest_worker.start()
            else:
                self.import_failed.emit(f"Falha ao registrar: {resp_data.get('message')}")
        else:
            self.import_failed.emit(f"Falha de comunicação com o servidor (Status {response.status_code}).")

    def _on_case_ingested(self, response):
        if response.status_code == 200:
            resp_data = response.json()
            
            # Lê a flag de sucesso do backend ao invés de confiar só no HTTP 200
            if resp_data.get("success"):
                self.import_success.emit("Caso importado e processado com sucesso!")
            else:
                # O backend respondeu, mas avisou que a ingestão (leitura dos CSVs) quebrou
                error_msg = resp_data.get("message", "Erro interno no processamento dos CSVs.")
                self.import_failed.emit(f"O caso foi registrado, mas a ingestão falhou: {error_msg}")
                
            self.load_cases() # Atualiza a tabela (mostrará READY ou FAILED corretamente)
        else:
            self.import_failed.emit("Erro do servidor durante o processamento dos CSVs.")

    def update_case_name(self, case_id: str, new_display_name: str):
        payload = {"display_name": new_display_name}
        # Salva em self para não ser destruído pelo Garbage Collector!
        self._name_worker = self.api_client.make_request_async("PATCH", f"/cases/{case_id}", json=payload)
        self._name_worker.finished.connect(
            lambda resp: self.case_updated.emit() if resp.status_code == 200 else self.error_occurred.emit("Erro ao atualizar nome do caso.")
        )
        self._name_worker.start()

    def load_regions(self, case_id: str):
        # Salva em self para manter a thread viva!
        self._regions_worker = self.api_client.make_request_async("GET", f"/cases/{case_id}/regions")
        self._regions_worker.finished.connect(
            lambda resp: self.regions_loaded.emit(resp.json().get("data", [])) if resp.status_code == 200 else self.error_occurred.emit("Erro ao carregar regiões.")
        )
        self._regions_worker.start()

    def update_region_aliases(self, case_id: str, regions_payload: list):
        # Salva em self!
        self._aliases_worker = self.api_client.make_request_async("PUT", f"/cases/{case_id}/regions", json=regions_payload)
        self._aliases_worker.finished.connect(
            lambda resp: self.regions_updated.emit() if resp.status_code == 200 else self.error_occurred.emit("Erro ao atualizar apelidos.")
        )
        self._aliases_worker.start()
    def delete_case(self, case_id: str):
        self._del_worker = self.api_client.make_request_async("DELETE", f"/cases/{case_id}")
        self._del_worker.finished.connect(lambda resp: self._on_case_deleted(resp, case_id))
        self._del_worker.start()

    def _on_case_deleted(self, response, case_id: str):
        if response.status_code == 200:
            self.case_deleted.emit(case_id)
            self.load_cases()
        else:
            self.error_occurred.emit(f"Falha ao excluir o caso. Status: {response.status_code}")
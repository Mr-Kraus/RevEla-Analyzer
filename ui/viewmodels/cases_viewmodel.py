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
    
    # NOVO SINAL: Avisa a tela que a descoberta terminou e entrega as listas de arquivos
    discovery_completed = pyqtSignal(str, dict) 

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

    def discover_case(self, folder_path: str, display_name: str):
        """Etapa 1: Faz a varredura da pasta no backend"""
        self.import_started.emit()
        folder_name = os.path.basename(folder_path)
        
        payload = {
            "external_name": folder_name[:10],
            "display_name": display_name or f"Caso: {folder_name}",
            "source_path": folder_path
        }
        
        self._reg_worker = self.api_client.make_request_async("POST", "/cases", json=payload)
        self._reg_worker.finished.connect(self._on_case_discovered)
        self._reg_worker.error.connect(self.import_failed.emit)
        self._reg_worker.start()

    def _on_case_discovered(self, response):
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get("success"):
                data = resp_data.get("data", {})
                self.current_case_id = data.get("id")
                discovery_details = data.get("discovery_details", {})
                
                # Avisa a interface gráfica para abrir o pop-up com as opções!
                self.discovery_completed.emit(self.current_case_id, discovery_details)
            else:
                self.import_failed.emit(f"Falha na descoberta: {resp_data.get('message')}")
        else:
            self.import_failed.emit(f"Falha de comunicação com o servidor (Status {response.status_code}).")

    def run_import(self, case_id: str, template: str, results_dir: str, software_version: str):
        """Etapa 2: Executa a importação real após o usuário escolher no pop-up"""
        import_payload = {
            "software_version": software_version,
            "selected_template": template,
            "selected_results": results_dir
        }
        
        self._ingest_worker = self.api_client.make_request_async(
            "POST", 
            f"/cases/{case_id}/import",
            json=import_payload
        )
        self._ingest_worker.finished.connect(self._on_case_ingested)
        self._ingest_worker.error.connect(self.import_failed.emit)
        self._ingest_worker.start()

    def _on_case_ingested(self, response):
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get("success"):
                self.import_success.emit("Caso importado e processado com sucesso!")
            else:
                error_msg = resp_data.get("message", "Erro interno no processamento dos CSVs.")
                self.import_failed.emit(f"O caso foi registrado, mas a ingestão falhou: {error_msg}")
                
            self.load_cases() 
        else:
            self.import_failed.emit("Erro do servidor durante o processamento dos CSVs.")

    # ... (Os métodos update_case_name, load_regions, update_region_aliases e delete_case continuam iguais abaixo)
    def update_case_name(self, case_id: str, new_display_name: str):
        payload = {"display_name": new_display_name}
        self._name_worker = self.api_client.make_request_async("PATCH", f"/cases/{case_id}", json=payload)
        self._name_worker.finished.connect(
            lambda resp: self.case_updated.emit() if resp.status_code == 200 else self.error_occurred.emit("Erro ao atualizar nome do caso.")
        )
        self._name_worker.start()

    def load_regions(self, case_id: str):
        self._regions_worker = self.api_client.make_request_async("GET", f"/cases/{case_id}/regions")
        self._regions_worker.finished.connect(
            lambda resp: self.regions_loaded.emit(resp.json().get("data", [])) if resp.status_code == 200 else self.error_occurred.emit("Erro ao carregar regiões.")
        )
        self._regions_worker.start()

    def update_region_aliases(self, case_id: str, regions_payload: list):
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
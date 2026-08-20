from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class TabGlobalViewModel(QObject):
    cases_list_ready = pyqtSignal(list)
    global_data_ready = pyqtSignal(str, dict) # case_id, data
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self._workers = {} # Previne o crash do Garbage Collector para múltiplas chamadas

    def load_available_cases(self):
        worker = self.api_client.make_request_async("GET", "/cases")
        worker.finished.connect(self._on_cases_list_loaded)
        self._workers["cases_list"] = worker
        worker.start()

    def _on_cases_list_loaded(self, response):
        if response.status_code == 200:
            cases = [c for c in response.json().get("data", []) if c.get("status") == "READY"]
            self.cases_list_ready.emit(cases)
        else:
            self.error_occurred.emit("Falha ao carregar lista de casos.")

    def load_case_global_data(self, case_id: str):
        worker = self.api_client.make_request_async("GET", f"/analysis/case/{case_id}/global")
        worker.finished.connect(lambda r, cid=case_id: self._on_global_data_loaded(r, cid))
        self._workers[f"global_{case_id}"] = worker
        worker.start()

    def _on_global_data_loaded(self, response, case_id: str):
        if response.status_code == 200:
            data = response.json().get("data", {})
            self.global_data_ready.emit(case_id, data)
        else:
            self.error_occurred.emit(f"Falha ao carregar dados globais do caso {case_id}.")
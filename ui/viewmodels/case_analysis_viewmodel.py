from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class CaseAnalysisViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    case_selected = pyqtSignal(str) # Dispara o UUID do caso para as sub-abas
    error_occurred = pyqtSignal(str)
    is_loading = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def load_cases(self):
        self.is_loading.emit(True)
        self._worker = self.api_client.make_request_async("GET", "/cases")
        self._worker.finished.connect(self._on_cases_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_cases_loaded(self, response):
        self.is_loading.emit(False)
        if response.status_code == 200:
            # Filtra apenas os casos prontos para análise
            cases = [c for c in response.json().get("data", []) if c.get("status") == "READY"]
            self.cases_loaded.emit(cases)
        else:
            self.error_occurred.emit("Falha ao carregar lista de casos.")

    def select_case(self, case_id: str):
        """Avisa todas as abas que um novo caso foi selecionado."""
        if case_id:
            self.case_selected.emit(case_id)

    def _on_error(self, msg):
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
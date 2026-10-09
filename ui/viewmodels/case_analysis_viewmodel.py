from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class CaseAnalysisViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    case_selected = pyqtSignal(str) 
    analysis_data_ready = pyqtSignal(dict)  # Sinal para entregar os dados gerais
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
            cases = [c for c in response.json().get("data", []) if c.get("status") == "READY"]
            self.cases_loaded.emit(cases)
        else:
            self.error_occurred.emit("Falha ao carregar lista de casos.")

    def select_case(self, case_id: str):
        if case_id:
            self.case_selected.emit(case_id)

    def fetch_geral_data(self, case_id: str):
        """Busca os dados de indicadores e elementos do caso selecionado."""
        self.is_loading.emit(True)
        
        # Puxa dados granulares para permitir visualizar os vários elementos no gráfico
        payload = {
            "case_ids": [case_id],
            "granularity": "BUS", 
            "element_id": "ALL"
        }
        self._worker_analysis = self.api_client.make_request_async("POST", "/analysis/multi-compare", json=payload)
        self._worker_analysis.finished.connect(self._on_geral_data_loaded)
        self._worker_analysis.error.connect(self._on_error)
        self._worker_analysis.start()

    def _on_geral_data_loaded(self, response):
        self.is_loading.emit(False)
        if response.status_code == 200:
            self.analysis_data_ready.emit(response.json())
        else:
            self.error_occurred.emit("Falha ao carregar dados da análise.")

    def _on_error(self, msg):
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
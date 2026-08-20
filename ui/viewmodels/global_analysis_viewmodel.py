from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class GlobalAnalysisViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    analysis_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    is_loading = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def load_cases(self):
        """Busca os casos para popular o ComboBox (Dropdown)."""
        self.is_loading.emit(True)
        self._cases_worker = self.api_client.make_request_async("GET", "/cases")
        self._cases_worker.finished.connect(self._on_cases_loaded)
        self._cases_worker.error.connect(self._on_error)
        self._cases_worker.start()

    def _on_cases_loaded(self, response):
        self.is_loading.emit(False)
        if response.status_code == 200:
            cases = response.json().get("data", [])
            # Filtra apenas os casos que já foram importados com sucesso
            ready_cases = [c for c in cases if c.get("status") == "READY"]
            self.cases_loaded.emit(ready_cases)
        else:
            self.error_occurred.emit("Falha ao carregar lista de casos.")

    def load_analysis(self, case_id: str):
        """Passo 1: Descobre qual é o ID da Simulação deste caso."""
        self.is_loading.emit(True)
        self._sim_worker = self.api_client.make_request_async("GET", f"/cases/{case_id}/simulations")
        self._sim_worker.finished.connect(self._on_simulations_loaded)
        self._sim_worker.error.connect(self._on_error)
        self._sim_worker.start()

    def _on_simulations_loaded(self, response):
        if response.status_code == 200:
            sims = response.json().get("data", [])
            if sims:
                sim_id = sims[0].get("simulation_id") # Pega a simulação mais recente
                
                # Passo 2: Busca os indicadores globais matemáticos
                self._analysis_worker = self.api_client.make_request_async("GET", f"/analysis/global/{sim_id}")
                self._analysis_worker.finished.connect(self._on_analysis_loaded)
                self._analysis_worker.error.connect(self._on_error)
                self._analysis_worker.start()
            else:
                self.is_loading.emit(False)
                self.error_occurred.emit("Nenhuma simulação encontrada para este caso.")
        else:
            self.is_loading.emit(False)
            self.error_occurred.emit("Erro ao buscar a simulação do caso.")

    def _on_analysis_loaded(self, response):
        self.is_loading.emit(False)
        if response.status_code == 200:
            data = response.json().get("data", {})
            self.analysis_loaded.emit(data.get("indicators", {}))
        else:
            self.error_occurred.emit("Erro ao carregar análise global.")

    def _on_error(self, msg):
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
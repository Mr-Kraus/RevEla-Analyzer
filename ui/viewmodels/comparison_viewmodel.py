from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class ComparisonViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    comparison_ready = pyqtSignal(dict, dict) # Envia (Dados do Caso A, Dados do Caso B)
    error_occurred = pyqtSignal(str)
    is_loading = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.case_a_id = None
        self.case_b_id = None
        self.data_a = None
        self.data_b = None

    def load_cases(self):
        """Busca os casos disponíveis para preencher os seletores."""
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

    # ==========================================
    # CORRENTE DE REQUISIÇÕES (A -> B -> Tela)
    # ==========================================
    def compare_cases(self, case_a_id: str, case_b_id: str):
        self.is_loading.emit(True)
        self.case_b_id = case_b_id
        # Inicia a busca pelo Caso A
        self._worker_sim_a = self.api_client.make_request_async("GET", f"/cases/{case_a_id}/simulations")
        self._worker_sim_a.finished.connect(self._on_sim_a_loaded)
        self._worker_sim_a.error.connect(self._on_error)
        self._worker_sim_a.start()

    def _on_sim_a_loaded(self, response):
        sims = response.json().get("data", []) if response.status_code == 200 else []
        if not sims: return self._on_error("Simulação não encontrada para o Caso A.")
        
        sim_id = sims[0].get("simulation_id")
        self._worker_glob_a = self.api_client.make_request_async("GET", f"/analysis/global/{sim_id}")
        self._worker_glob_a.finished.connect(self._on_glob_a_loaded)
        self._worker_glob_a.start()

    def _on_glob_a_loaded(self, response):
        self.data_a = response.json().get("data", {}).get("indicators", {}) if response.status_code == 200 else {}
        
        # Agora busca a Simulação do Caso B
        self._worker_sim_b = self.api_client.make_request_async("GET", f"/cases/{self.case_b_id}/simulations")
        self._worker_sim_b.finished.connect(self._on_sim_b_loaded)
        self._worker_sim_b.start()

    def _on_sim_b_loaded(self, response):
        sims = response.json().get("data", []) if response.status_code == 200 else []
        if not sims: return self._on_error("Simulação não encontrada para o Caso B.")
        
        sim_id = sims[0].get("simulation_id")
        self._worker_glob_b = self.api_client.make_request_async("GET", f"/analysis/global/{sim_id}")
        self._worker_glob_b.finished.connect(self._on_glob_b_loaded)
        self._worker_glob_b.start()

    def _on_glob_b_loaded(self, response):
        self.is_loading.emit(False)
        self.data_b = response.json().get("data", {}).get("indicators", {}) if response.status_code == 200 else {}
        # Tudo pronto! Avisa a tela para desenhar.
        self.comparison_ready.emit(self.data_a, self.data_b)

    def _on_error(self, msg):
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
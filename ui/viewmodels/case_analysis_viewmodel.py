from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class CaseAnalysisViewModel(QObject):
    cases_loaded = pyqtSignal(list)
    case_selected = pyqtSignal(str) 
    analysis_data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    is_loading = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self._current_case_id = None
        
        self._aggregated_data = {}
        self._pending_requests = 0

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
        self._current_case_id = case_id
        self._aggregated_data = {}
        self._pending_requests = 3 # Esperamos 3 requisições
        self.is_loading.emit(True)
        
        # 1. Busca dados granulares (Elementos para o Gráfico)
        payload = {"case_ids": [case_id], "granularity": "BUS", "element_id": "ALL"}
        self._worker_elements = self.api_client.make_request_async("POST", "/analysis/multi-compare", json=payload)
        self._worker_elements.finished.connect(self._on_elements_loaded)
        self._worker_elements.error.connect(self._on_error)
        self._worker_elements.start()

        # 2. Busca o System Summary e Tecnologias de Geração
        self._worker_summary = self.api_client.make_request_async("GET", f"/analysis/case/{case_id}/system-summary")
        self._worker_summary.finished.connect(self._on_summary_loaded)
        self._worker_summary.error.connect(self._on_error)
        self._worker_summary.start()

        # 3. Busca os Indicadores Globais
        self._worker_global = self.api_client.make_request_async("GET", f"/analysis/case/{case_id}/global")
        self._worker_global.finished.connect(self._on_global_loaded)
        self._worker_global.error.connect(self._on_error)
        self._worker_global.start()

    def _on_elements_loaded(self, response):
        if response.status_code == 200:
            data = response.json()
            self._aggregated_data["elements"] = data.get("elements", data.get("data", {}).get("elements", []))
            self._aggregated_data["indicators"] = data.get("indicators", data.get("data", {}).get("indicators", []))
        self._check_all_requests_done()

    def _on_summary_loaded(self, response):
        if response.status_code == 200:
            data = response.json().get("data", {})
            self._aggregated_data["system_summary"] = data.get("system_summary", [])
            self._aggregated_data["generation_tech"] = data.get("generation_tech", {})
        self._check_all_requests_done()

    def _on_global_loaded(self, response):
        if response.status_code == 200:
            data = response.json().get("data", {})
            inds = data.get("indicators", {})
            gen_info = data.get("general_info", {})

            # Formata a lista para a tabela usando a convergência individual de cada indicador
            rel_list = []
            for ind_name, ind_data in inds.items():
                rel_list.append({
                    "nome": ind_name, 
                    "valor": ind_data.get("value", 0.0), 
                    # A view já sabe tratar strings formatadas (como "1.7415%" ou "N/A")
                    "beta": ind_data.get("conf", "N/A")
                })

            self._aggregated_data["global_reliability"] = rel_list
            self._aggregated_data["simulated_years"] = gen_info.get("Anos Simulados", "N/A")
            
        self._check_all_requests_done()

    def _check_all_requests_done(self):
        self._pending_requests -= 1
        if self._pending_requests <= 0:
            self.is_loading.emit(False)
            self.analysis_data_ready.emit(self._aggregated_data)

    def _on_error(self, msg):
        self._pending_requests = 0
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
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
        self.current_sim_info = {} # Cache das informações da Simulação

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
                # Guarda as informações da Simulação (Analysis Type, Years, etc)
                self.current_sim_info = sims[0] 
                sim_id = self.current_sim_info.get("simulation_id", self.current_sim_info.get("id"))
                
                # Passo 2: Busca os indicadores globais e metadados
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
            
            indicators = data.get("indicators", {})
            case_info = data.get("case_informations", data.get("metadata", {}))
            sim_info = getattr(self, "current_sim_info", {})
            
            # Busca as variáveis considerando a chave crua do CSV ou a chave do Normalizador
            analysis_type = sim_info.get("analysis_type", case_info.get("Analysis Type", case_info.get("ANALYSIS_TYPE", "N/A")))
            beta = case_info.get("Convergence Beta", case_info.get("COEF_BETA", "N/A"))
            sim_years = sim_info.get("simulated_years", case_info.get("Anos Simulados", case_info.get("simulated_years", "N/A")))
            
            enriched_data = {
                "indicators": indicators,
                "case_informations": case_info,
                "simulation_info": sim_info,
                "general_info": {
                    "Tipo de Análise": analysis_type,
                    "Convergência (Beta)": beta,
                    "Anos Simulados": sim_years
                }
            }
            
            self.analysis_loaded.emit(enriched_data)
        else:
            self.error_occurred.emit("Erro ao carregar análise global.")
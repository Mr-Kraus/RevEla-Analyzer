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
            
            indicators = data.get("indicators", {})
            raw_general_info = data.get("general_info", {})
            
            # Mapeia dinamicamente preservando o que a API mandar, 
            # e corrigindo a chave de convergência/beta se vier "Padrão"
            convergencia_val = raw_general_info.get("Convergência (Beta)", raw_general_info.get("Convergência", "N/A"))
            if convergencia_val == "Padrão":
                convergencia_val = raw_general_info.get("COEF_BETA", "N/A")

            general_info = {
                "Número de Barras": raw_general_info.get("Número de Barras", raw_general_info.get("BARRAS", "N/A")),
                "Convergência (Beta)": convergencia_val,
                "Tipo de Análise": raw_general_info.get("Tipo de Análise", raw_general_info.get("ANALYSIS_TYPE", "N/A")),
                "Representação do Sistema": raw_general_info.get("Representação do Sistema", raw_general_info.get("SYST_REP", "N/A"))
            }
            
            # Se houver outros campos extras no raw_general_info que não estão na lista fixa acima, 
            # podemos opcionalmente mantê-los ou garantir que os principais apareçam.
            for k, v in raw_general_info.items():
                if k not in general_info:
                    general_info[k] = v

            payload = {
                "case_name": data.get("case_name", "Desconhecido"),
                "indicators": indicators,
                "general_info": general_info
            }
            
            self.global_data_ready.emit(case_id, payload)
        else:
            self.error_occurred.emit(f"Falha ao carregar dados globais do caso {case_id}.")
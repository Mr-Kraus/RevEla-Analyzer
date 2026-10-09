from PyQt6.QtCore import QObject, pyqtSignal
import requests
from ui.services.api_client import APIClient
from app.infrastructure.database.session.database import SessionLocal
from app.application.use_cases.analytical.multi_compare_time_series_use_case import MultiCompareTimeSeriesUseCase

class ComparisonViewModel(QObject):
    # Sinais atualizados para fazer "match" exato com a View
    cases_list_ready = pyqtSignal(list)
    comparison_data_ready = pyqtSignal(dict) 
    error_occurred = pyqtSignal(str)
    is_loading = pyqtSignal(bool)
    time_series_data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.api_url = "http://127.0.0.1:8000"
        self.api_client = APIClient()

    def load_available_cases(self):
        """Busca os casos disponíveis para preencher os seletores da interface."""
        self.is_loading.emit(True)
        self._worker = self.api_client.make_request_async("GET", "/cases")
        self._worker.finished.connect(self._on_cases_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_cases_loaded(self, response):
        self.is_loading.emit(False)
        if response.status_code == 200:
            # Filtra apenas os casos prontos (READY)
            cases = [c for c in response.json().get("data", []) if c.get("status") == "READY"]
            self.cases_list_ready.emit(cases)
        else:
            self.error_occurred.emit("Falha ao carregar lista de casos.")

    def fetch_multi_case_data(self, case_ids: list, granularity: str, element_id: str = "ALL"):
        """Envia os IDs e a granularidade para a rota de BI do Backend."""
        payload = {
            "case_ids": case_ids,
            "granularity": granularity,
            "element_id": element_id
        }
        
        try:
            # Chama o endpoint no FastAPI para análise múltipla
            response = requests.post(f"{self.api_url}/analysis/multi-compare", json=payload)
            
            if response.status_code == 200:
                self.comparison_data_ready.emit(response.json())
            else:
                self.error_occurred.emit(f"Erro na análise: {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Erro de conexão: {str(e)}")

    def fetch_time_series_data(self, case_ids: list):
        """Busca os dados de séries temporais diretamente no banco via Use Case."""
        session = SessionLocal() 
        try:
            use_case = MultiCompareTimeSeriesUseCase(session)
            result_data = use_case.execute(case_ids, series_type="Load")
            self.time_series_data_ready.emit(result_data)
            
        except Exception as e:
            self.error_occurred.emit(f"Erro ao buscar Séries Temporais: {str(e)}")
        finally:
            session.close()

    def _on_error(self, msg):
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
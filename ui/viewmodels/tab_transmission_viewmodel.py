from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class TabTransmissionViewModel(QObject):
    transmission_data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def load_transmission(self, case_id: str):
        url = f"/analysis/case/{case_id}/transmission"
        self._worker = self.api_client.make_request_async("GET", url)
        self._worker.finished.connect(self._on_data_loaded)
        self._worker.start()

    def _on_data_loaded(self, response):
        if response.status_code == 200:
            data = response.json().get("data", {})
            self.transmission_data_ready.emit(data)
        else:
            self.error_occurred.emit(f"Falha ao carregar dados de transmissão ({response.status_code})")
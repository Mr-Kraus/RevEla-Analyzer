from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class TabTopologyViewModel(QObject):
    topology_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()

    def load_topology(self, case_id: str):
        url = f"/analysis/case/{case_id}/topology"
        print(f"DEBUG API: Iniciando GET para a URL -> {url}")
        
        self._worker = self.api_client.make_request_async("GET", url)
        self._worker.finished.connect(self._on_topology_loaded)
        self._worker.start()

    def _on_topology_loaded(self, response):
        print(f"DEBUG API: Resposta recebida. Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            self.topology_ready.emit(data)
        else:
            print(f"DEBUG API: Texto do erro retornado pelo backend -> {response.text}")
            print("Carregando rede de demonstracao (Fallback).")
            dummy_data = self._generate_dummy_topology()
            self.topology_ready.emit(dummy_data)

    def _generate_dummy_topology(self):
        """Gera um Grafo de Teste (5 Barras e 6 Linhas) para teste visual."""
        return {
            "nodes": [
                {"id": "B1", "label": "Barra 1 (Geração)", "group": "generation"},
                {"id": "B2", "label": "Barra 2 (Carga)", "group": "load"},
                {"id": "B3", "label": "Barra 3 (Carga)", "group": "load"},
                {"id": "B4", "label": "Barra 4 (Carga)", "group": "load"},
                {"id": "B5", "label": "Barra 5 (Geração)", "group": "generation"}
            ],
            "edges": [
                {"from": "B1", "to": "B2", "label": "L1-2"},
                {"from": "B2", "to": "B3", "label": "L2-3"},
                {"from": "B3", "to": "B4", "label": "L3-4"},
                {"from": "B4", "to": "B5", "label": "L4-5"},
                {"from": "B5", "to": "B1", "label": "L5-1"},
                {"from": "B2", "to": "B5", "label": "L2-5"}
            ]
        }
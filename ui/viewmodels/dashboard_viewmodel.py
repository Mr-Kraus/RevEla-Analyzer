from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class DashboardViewModel(QObject):
    # Sinais emitidos para atualizar a interface
    stats_updated = pyqtSignal(dict)
    recent_cases_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.cases_worker = None
        self.user_worker = None

    def load_dashboard_data(self):
        """Busca os dados necessários para popular a tela inicial."""
        # 1. Buscar dados do usuário (se a sua API tiver a rota /auth/me)
        # 2. Buscar a lista de casos
        self.cases_worker = self.api_client.make_request_async("GET", "/cases")
        self.cases_worker.finished.connect(self._on_cases_loaded)
        self.cases_worker.error.connect(self.error_occurred.emit)
        self.cases_worker.start()

    def _on_cases_loaded(self, response):
        if response.status_code == 200:
            cases = response.json().get("data", [])
            
            # Cálculo dos Status para os Cards
            total_cases = len(cases)
            ready_cases = len([c for c in cases if c.get("status") == "READY"])
            
            # Simulando data de última importação (pegando o primeiro da lista, se houver)
            last_import = "Nenhuma"
            if cases:
                last_import = "Hoje (Simulado)" # Aqui você pode pegar a data real do dict do caso
            
            stats = {
                "total_cases": total_cases,
                "ready_cases": ready_cases,
                "db_status": "Conectado",
                "last_import": last_import
            }
            
            self.stats_updated.emit(stats)
            
            # Pega apenas os 5 últimos casos para a tabela de casos recentes
            recent_cases = cases[:5] 
            self.recent_cases_loaded.emit(recent_cases)
        else:
            self.error_occurred.emit("Falha ao carregar dados do Dashboard.")
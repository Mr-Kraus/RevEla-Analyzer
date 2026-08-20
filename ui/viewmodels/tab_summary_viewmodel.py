from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class TabSummaryViewModel(QObject):
    # Sinais para atualizar a interface
    metadata_loaded = pyqtSignal(dict)       # Dados gerais e globais
    detailed_data_loaded = pyqtSignal(object)  # Dados para o gráfico e tabela inferior
    error_occurred = pyqtSignal(str)
    is_loading = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_sim_id = None

    def load_case_data(self, case_id: str):
        """Passo 1: Descobre a simulação associada ao caso e seus metadados."""
        self.is_loading.emit(True)
        self._worker_sim = self.api_client.make_request_async("GET", f"/cases/{case_id}/simulations")
        self._worker_sim.finished.connect(self._on_sim_loaded)
        self._worker_sim.error.connect(self._on_error)
        self._worker_sim.start()

    def _on_sim_loaded(self, response):
        if response.status_code == 200 and response.json().get("data"):
            sim_data = response.json().get("data")[0] # Pega a simulação mais recente
            self.current_sim_id = sim_data.get("simulation_id")
            
            # Aqui extraímos metadados como tempo, anos simulados, etc (se existirem no banco)
            # Para não travar, enviamos o que temos e logo em seguida buscamos os indicadores
            
            self._worker_global = self.api_client.make_request_async("GET", f"/analysis/global/{self.current_sim_id}")
            self._worker_global.finished.connect(lambda res, meta=sim_data: self._on_global_loaded(res, meta))
            self._worker_global.start()
        else:
            self._on_error("Nenhuma simulação pronta encontrada para este caso.")

    def _on_global_loaded(self, response, sim_metadata):
        if response.status_code == 200:
            data = response.json().get("data", {})
            indicators = data.get("indicators", {})
            
            # Junta os metadados da simulação com os indicadores globais e envia pra View
            combined_metadata = {**sim_metadata, **indicators}
            self.metadata_loaded.emit(combined_metadata)
            
            # Passo 3: Carrega os dados detalhados (padrão: EPNS) para desenhar o primeiro gráfico
            self.load_detailed_data("EPNS")
        else:
            self._on_error("Erro ao carregar indicadores globais.")

    def load_detailed_data(self, indicator: str):
        """Busca os detalhes de Barras/Regiões para o gráfico dinâmico."""
        if not self.current_sim_id: return
        
        self.is_loading.emit(True)
        
        # Transformando o indicador para minúsculo (ex: "EPNS" vira "epns")
        indicador_minusculo = indicator.lower()
        
        self._worker_det = self.api_client.make_request_async(
            "GET", 
            f"/analysis/case/{self.current_sim_id}?indicator={indicador_minusculo}"
        )
        self._worker_det.finished.connect(self._on_detailed_loaded)
        self._worker_det.start()

    def _on_detailed_loaded(self, response):
        self.is_loading.emit(False)
        if response.status_code == 200:
            data = response.json().get("data", [])
            self.detailed_data_loaded.emit(data)
        else:
            self._on_error("Erro ao carregar dados detalhados.")

    def _on_error(self, msg):
        self.is_loading.emit(False)
        self.error_occurred.emit(msg)
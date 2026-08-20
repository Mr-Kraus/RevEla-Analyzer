import requests
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Dict, Optional, Any

class APIWorker(QThread):
    """
    Worker assíncrono para requisições HTTP. 
    Roda em uma thread separada para não congelar a interface gráfica.
    """
    # Sinais emitidos quando a requisição termina ou falha
    finished = pyqtSignal(object)  # Retorna o objeto requests.Response
    error = pyqtSignal(str)        # Retorna a mensagem de erro

    def __init__(self, method: str, url: str, **kwargs):
        super().__init__()
        self.method = method
        self.url = url
        self.kwargs = kwargs

    def run(self):
        """Método executado automaticamente em segundo plano ao chamar start()."""
        try:
            response = requests.request(self.method, self.url, **self.kwargs)
            self.finished.emit(response)
        except requests.exceptions.ConnectionError:
            self.error.emit("Falha de conexão: Servidor API offline ou inacessível.")
        except requests.exceptions.Timeout:
            self.error.emit("Timeout: O servidor demorou muito para responder.")
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Erro de rede inesperado: {str(e)}")
        except Exception as e:
            self.error.emit(f"Erro interno: {str(e)}")


class APIClient:
    """
    Padrão Singleton: Mantém o estado da API (URL e Token) durante toda a sessão.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIClient, cls).__new__(cls)
            cls._instance.base_url = "http://127.0.0.1:8000"
            cls._instance.token = None
        return cls._instance

    def set_token(self, token: str):
        """Armazena o JWT após o login bem-sucedido."""
        self.token = token

    def clear_token(self):
        """Limpa o JWT no momento do logout."""
        self.token = None

    def _get_headers(self) -> Dict[str, str]:
        """Prepara os cabeçalhos padrão, injetando o JWT se existir."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def make_request_async(self, method: str, endpoint: str, **kwargs) -> APIWorker:
        """
        Gera um Worker pronto para ser executado.
        
        Uso típico no ViewModel:
            worker = api_client.make_request_async("GET", "/analysis")
            worker.finished.connect(self.on_success)
            worker.error.connect(self.on_error)
            worker.start()
        """
        url = f"{self.base_url}{endpoint}"
        
        # Mescla os cabeçalhos de autenticação com os que já vieram no kwargs (se houver)
        request_headers = self._get_headers()
        if "headers" in kwargs:
            request_headers.update(kwargs["headers"])
        kwargs["headers"] = request_headers

        return APIWorker(method, url, **kwargs)
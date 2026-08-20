from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.api_client import APIClient

class LoginViewModel(QObject):
    # Sinais para avisar a View sobre o que está acontecendo
    login_success = pyqtSignal()
    login_error = pyqtSignal(str)
    is_loading = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.worker = None

    def login(self, email: str, password: str):
        # Avisa a tela para ligar o "Loading"
        self.is_loading.emit(True)
        
        # O FastAPI exige envio via formulário (data) para a rota de OAuth2, com as chaves 'username' e 'password'
        payload = {"username": email, "password": password}
        
        # Dispara a requisição em background
        self.worker = self.api_client.make_request_async("POST", "/auth/login", data=payload)
        self.worker.finished.connect(self._on_request_finished)
        self.worker.error.connect(self._on_request_error)
        self.worker.start()

    def _on_request_finished(self, response):
        self.is_loading.emit(False)
        
        if response.status_code == 200:
            data = response.json()
            # Salva o Token JWT no Singleton
            self.api_client.set_token(data.get("access_token"))
            self.login_success.emit()
        else:
            self.login_error.emit("E-mail ou senha incorretos.")

    def _on_request_error(self, error_msg):
        self.is_loading.emit(False)
        self.login_error.emit(error_msg)
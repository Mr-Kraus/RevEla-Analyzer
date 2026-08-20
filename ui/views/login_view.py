from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from ui.viewmodels.login_viewmodel import LoginViewModel
from ui.views.main_window import MainWindow

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = LoginViewModel()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("REVela Analyzer - Login")
        self.setFixedSize(350, 450)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        # Título
        title = QLabel("REVela Analyzer")
        font = title.font()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Campos de entrada
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-mail (ex: admin@revela.com)")
        self.email_input.setFixedHeight(35)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(35)

        # Label de Erro (invisível por padrão)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()

        # Botão
        self.login_btn = QPushButton("Entrar")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:disabled { background-color: #BDBDBD; }
        """)

        # Adicionando tudo ao layout
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.error_label)
        layout.addWidget(self.login_btn)

    def setup_connections(self):
        # Quando clicar no botão, dispara a função
        self.login_btn.clicked.connect(self.handle_login)
        # Bônus: Quando apertar "Enter" na senha, tenta logar
        self.password_input.returnPressed.connect(self.handle_login)
        
        # Ouve os sinais do ViewModel
        self.viewmodel.login_success.connect(self.on_login_success)
        self.viewmodel.login_error.connect(self.on_login_error)
        self.viewmodel.is_loading.connect(self.update_loading_state)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            self.on_login_error("Preencha todos os campos.")
            return
            
        self.error_label.hide()
        self.viewmodel.login(email, password)

    def update_loading_state(self, is_loading):
        """Desativa a tela para o usuário não clicar várias vezes."""
        self.login_btn.setEnabled(not is_loading)
        self.login_btn.setText("Autenticando..." if is_loading else "Entrar")
        self.email_input.setEnabled(not is_loading)
        self.password_input.setEnabled(not is_loading)

    def on_login_success(self):
        # Instancia e mostra a tela principal
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Fecha a janelinha de login
        self.close()

        
    def on_login_error(self, msg):
        self.error_label.setText(msg)
        self.error_label.show()
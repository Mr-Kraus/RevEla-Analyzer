from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QButtonGroup
from PyQt6.QtCore import Qt
from ui.views.cases_view import CasesView
from ui.views.dashboard_view import DashboardView 
from ui.views.global_analysis_view import GlobalAnalysisView
from ui.views.settings_view import SettingsView
from ui.views.comparison_view import ComparisonView
from ui.views.case_analysis_view import CaseAnalysisView



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REVela Analyzer - Enterprise")
        self.resize(1280, 720)
        self.setup_ui()
        
        # Após montar a UI, forçamos o clique no botão de Dashboard para iniciar na primeira tela
        self.btn_dashboard.click()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================= SIDEBAR =================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QWidget { background-color: #2C3E50; }
            QPushButton {
                color: #ECF0F1; background-color: transparent; border: none;
                padding: 15px; text-align: left; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #34495E; border-left: 4px solid #3498DB; }
            QPushButton:checked { background-color: #2980B9; border-left: 4px solid #ECF0F1; }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo_label = QLabel("REVela\nAnalyzer")
        logo_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold; padding: 20px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(20)

        # Criação do grupo de botões para garantir que apenas um fique "ativo" (checked) por vez
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_dashboard = self.create_nav_button("📊 Dashboard", 0)
        self.btn_casos = self.create_nav_button("📁 Gestão de Casos", 1)
        self.btn_global = self.create_nav_button("🌍 Global Analysis", 2)
        self.btn_compare = self.create_nav_button("⚖️ Comparison", 3)
        self.btn_detailed = self.create_nav_button("🔍 Case Analysis", 4)
        self.btn_settings = self.create_nav_button("⚙️ Configurações", 5)

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_casos)
        sidebar_layout.addWidget(self.btn_global)
        sidebar_layout.addWidget(self.btn_compare)
        sidebar_layout.addWidget(self.btn_detailed)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_settings)

        # ================= STACKED WIDGET (ÁREA CENTRAL) =================
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #F5F6FA;")
        
        # Adicionando as telas ao StackedWidget (A Ordem importa e deve bater com os IDs do nav_group)
        self.view_dashboard = DashboardView()
        self.content_area.addWidget(self.view_dashboard) # Índice 0
        
        # Telas provisórias para as demais seções enquanto não as construímos
        self.view_cases = CasesView()
        self.content_area.addWidget(self.view_cases) # Índice 1
        self.view_global = GlobalAnalysisView()
        self.content_area.addWidget(self.view_global) # Índice 2
        self.view_compare = ComparisonView()
        self.content_area.addWidget(self.view_compare) # Índice 3
        self.view_detailed = CaseAnalysisView()
        self.content_area.addWidget(self.view_detailed) # Índice 4
        self.view_settings = SettingsView()
        self.content_area.addWidget(self.view_settings) # Índice 5

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        # Conectar a mudança de tela
        self.nav_group.buttonClicked.connect(self.switch_page)

    def create_nav_button(self, text: str, page_index: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Salva o índice da página dentro do botão para sabermos qual tela abrir
        btn.page_index = page_index 
        self.nav_group.addButton(btn)
        return btn

    def create_placeholder_page(self, text: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #7F8C8D;")
        layout.addWidget(label)
        return page

    def switch_page(self, button: QPushButton):
        """Muda a tela do StackedWidget com base no botão clicado"""
        self.content_area.setCurrentIndex(button.page_index)
        
        # Se mudou para o Dashboard, pede para ele carregar os dados atualizados da API
        if button.page_index == 0:
            self.view_dashboard.load_data()
        elif button.page_index == 1:
            self.view_cases.load_data()
        elif button.page_index == 2:
            self.view_global.load_data()
        elif button.page_index == 3:
            self.view_compare.load_data()
        elif button.page_index == 4:
            self.view_detailed.load_data()
        elif button.page_index == 5:
            self.view_settings.load_data()
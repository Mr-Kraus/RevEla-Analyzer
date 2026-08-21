from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QButtonGroup
from PyQt6.QtCore import Qt
from ui.views.cases_view import CasesView
from ui.views.dashboard_view import DashboardView 
from ui.views.tab_global_view import TabGlobalView
from ui.views.settings_view import SettingsView
from ui.views.comparison_view import ComparisonView # <-- ABA RESTABELECIDA
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

        # Criação do grupo de botões
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_dashboard = self.create_nav_button("📊 Dashboard", 0)
        self.btn_casos = self.create_nav_button("📁 Gestão de Casos", 1)
        self.btn_global = self.create_nav_button("🌍 Análise Global", 2)
        self.btn_compare = self.create_nav_button("⚖️ Comparações", 3) # <-- BOTÃO DE VOLTA
        self.btn_detailed = self.create_nav_button("🔍 Análise de Caso", 4)
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
        
        # Adicionando as telas ao StackedWidget (A ordem reflete os page_indexes 0 a 5)
        self.view_dashboard = DashboardView()
        self.content_area.addWidget(self.view_dashboard) # 0
        
        self.view_cases = CasesView()
        self.content_area.addWidget(self.view_cases) # 1
        
        self.view_global = TabGlobalView()
        self.content_area.addWidget(self.view_global) # 2
        
        self.view_compare = ComparisonView() # <-- ABA RESTABELECIDA
        self.content_area.addWidget(self.view_compare) # 3
        
        self.view_detailed = CaseAnalysisView()
        self.content_area.addWidget(self.view_detailed) # 4
        
        self.view_settings = SettingsView()
        self.content_area.addWidget(self.view_settings) # 5

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        # Conexões
        self.nav_group.buttonClicked.connect(self.switch_page)
        
        # Conecta o clique no botão "Analisar" da tabela de casos
        self.view_cases.analyze_requested.connect(self.open_analysis_screen)

    def create_nav_button(self, text: str, page_index: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.page_index = page_index 
        self.nav_group.addButton(btn)
        return btn

    def switch_page(self, button: QPushButton):
        """Muda a tela do StackedWidget com base no botão clicado"""
        self.content_area.setCurrentIndex(button.page_index)
        
        # Dispara o carregamento de dados da aba correspondente (se o método existir)
        if button.page_index == 0 and hasattr(self.view_dashboard, 'load_data'):
            self.view_dashboard.load_data()
        elif button.page_index == 1 and hasattr(self.view_cases, 'load_data'):
            self.view_cases.load_data()
        elif button.page_index == 2 and hasattr(self.view_global, 'load_data'):
            self.view_global.load_data()
        elif button.page_index == 3 and hasattr(self.view_compare, 'load_data'):
            self.view_compare.load_data()
        elif button.page_index == 5 and hasattr(self.view_settings, 'load_data'):
            self.view_settings.load_data()

    def open_analysis_screen(self, case_id: str, case_name: str):
        """Redireciona para a tela de Análise Detalhada de Caso quando solicitado."""
        self.view_detailed.load_case(case_id, case_name)
        self.btn_detailed.setChecked(True)
        self.content_area.setCurrentIndex(4) # O Índice da Análise Detalhada agora é 4!
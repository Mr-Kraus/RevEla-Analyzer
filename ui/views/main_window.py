from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QButtonGroup
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QIcon
import ui.resources_rc

from ui.views.cases_view import CasesView
from ui.views.dashboard_view import DashboardView 
from ui.views.tab_global_view import TabGlobalView
from ui.views.settings_view import SettingsView
from ui.views.comparison_view import ComparisonView 
from ui.views.case_analysis_view import CaseAnalysisView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RevEla Analyzer - LABPLAN")
        self.resize(1280, 720)
        
        # Ícone superior da janela puxando da pasta widgets conforme solicitado
        self.setWindowIcon(QIcon("ui/widgets/icone.ico"))
        
        self.is_sidebar_expanded = True
        
        self.setup_ui()
        # Forçamos o clique no botão de Dashboard para iniciar na primeira tela
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
        
        # O clique na área vazia da sidebar dispara a animação de expansão/recolhimento
        self.sidebar.mousePressEvent = self.toggle_sidebar

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.logo_label = QLabel("RevEla")
        self.logo_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold; padding: 20px;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # O clique na logo também dispara a animação
        self.logo_label.mousePressEvent = self.toggle_sidebar
        sidebar_layout.addWidget(self.logo_label)
        sidebar_layout.addSpacing(20)

        # Criação do grupo de botões de navegação
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        # Criando botões com caminhos específicos para você alocar os PNGs
        self.btn_dashboard = self.create_nav_button("HOME", 0, "ui/widgets/icon_home.png")
        self.btn_casos     = self.create_nav_button("LOAD CASES", 1, "ui/widgets/icon_cases.png")
        self.btn_global    = self.create_nav_button("GLOBAL ANALYSIS", 2, "ui/widgets/icon_global.png")
        self.btn_compare   = self.create_nav_button("COMPARISONS", 3, "ui/widgets/icon_compare.png") 
        self.btn_detailed  = self.create_nav_button("CASE ANALYSIS", 4, "ui/widgets/icon_detailed.png")
        self.btn_settings  = self.create_nav_button("SETTINGS", 5, "ui/widgets/icon_settings.png")

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
        
        self.view_dashboard = DashboardView()
        self.content_area.addWidget(self.view_dashboard) # 0
        
        self.view_cases = CasesView()
        self.content_area.addWidget(self.view_cases) # 1
        
        self.view_global = TabGlobalView()
        self.content_area.addWidget(self.view_global) # 2
        
        self.view_compare = ComparisonView() 
        self.content_area.addWidget(self.view_compare) # 3
        
        self.view_detailed = CaseAnalysisView()
        self.content_area.addWidget(self.view_detailed) # 4
        
        self.view_settings = SettingsView()
        self.content_area.addWidget(self.view_settings) # 5

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        # Conexões
        self.nav_group.buttonClicked.connect(self.switch_page)
        self.view_cases.analyze_requested.connect(self.open_analysis_screen)

    def create_nav_button(self, text: str, page_index: int, icon_path: str) -> QPushButton:
        btn = QPushButton("  " + text)
        btn.setProperty("original_text", text) # Guarda o texto original
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(22, 22))
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.page_index = page_index 
        self.nav_group.addButton(btn)
        return btn

    def toggle_sidebar(self, event):
        """Alterna a sidebar entre modo recolhido (70px) e expandido (250px)"""
        width = self.sidebar.width()
        target_width = 70 if self.is_sidebar_expanded else 250

        # Atualiza os textos instantaneamente antes da animação terminar
        if target_width == 70:
            self.logo_label.setText("")
            for btn in self.nav_group.buttons():
                btn.setText("") # Remove o texto, deixa só o ícone
                btn.setToolTip(btn.property("original_text")) # Adiciona um Tooltip
        else:
            self.logo_label.setText("RevEla")
            for btn in self.nav_group.buttons():
                btn.setText("  " + btn.property("original_text")) # Restaura o texto
                btn.setToolTip("")

        # Animação da Largura Mínima
        self.animation1 = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation1.setDuration(300)
        self.animation1.setStartValue(width)
        self.animation1.setEndValue(target_width)
        self.animation1.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # Animação da Largura Máxima
        self.animation2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.animation2.setDuration(300)
        self.animation2.setStartValue(width)
        self.animation2.setEndValue(target_width)
        self.animation2.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self.animation1.start()
        self.animation2.start()

        self.is_sidebar_expanded = not self.is_sidebar_expanded

    def switch_page(self, button: QPushButton):
        """Muda a tela do StackedWidget com base no botão clicado"""
        self.content_area.setCurrentIndex(button.page_index)
        
        if button.page_index == 0 and hasattr(self.view_dashboard, 'load_data'):
            self.view_dashboard.load_data()
        elif button.page_index == 1 and hasattr(self.view_cases, 'load_data'):
            self.view_cases.load_data()
        elif button.page_index == 2 and hasattr(self.view_global, 'load_data'):
            self.view_global.load_data()
        elif button.page_index == 3 and hasattr(self.view_compare, 'load_data'):
            self.view_compare.load_data()
        elif button.page_index == 4 and hasattr(self.view_detailed, 'load_data'):
            self.view_detailed.load_data()
        elif button.page_index == 5 and hasattr(self.view_settings, 'load_data'):
            self.view_settings.load_data()

    def open_analysis_screen(self, case_id: str, case_name: str):
        """Redireciona para a tela de Análise Detalhada de Caso quando solicitado."""
        self.view_detailed.load_case(case_id, case_name)
        self.btn_detailed.setChecked(True)
        self.content_area.setCurrentIndex(4)
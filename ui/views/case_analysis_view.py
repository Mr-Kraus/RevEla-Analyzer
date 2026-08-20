from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt
from ui.viewmodels.case_analysis_viewmodel import CaseAnalysisViewModel
from ui.views.tab_summary_view import TabSummaryView
from ui.views.tab_topology_view import TabTopologyView





class CaseAnalysisView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = CaseAnalysisViewModel()
        self.case_mapping = {}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ==========================================
        # TOP BAR: Título e Seletor de Casos
        # ==========================================
        top_bar = QHBoxLayout()
        title = QLabel("Análise Detalhada (Drill-down)")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        
        self.combo_cases = QComboBox()
        self.combo_cases.setFixedWidth(350)
        self.combo_cases.setFixedHeight(35)
        self.combo_cases.addItem("Selecione um caso para analisar...")
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Caso Base: "))
        top_bar.addWidget(self.combo_cases)
        
        layout.addLayout(top_bar)

        # ==========================================
        # SISTEMA DE ABAS (TABS)
        # ==========================================
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #BDC3C7; background-color: #F5F6FA; }
            QTabBar::tab { background: #ECF0F1; color: #2C3E50; padding: 10px 20px; font-weight: bold; border-top-left-radius: 4px; border-top-right-radius: 4px; border-right: 1px solid #BDC3C7; }
            QTabBar::tab:selected { background: #FFFFFF; border-bottom-color: #FFFFFF; color: #2980B9; border-top: 3px solid #2980B9; }
        """)

        # 1. Instanciamos a ABA REAL que acabamos de criar!
        self.tab_summary = TabSummaryView()
        
        # 2. Instanciamos os placeholders para as próximas abas
        self.tab_topology = TabTopologyView()
        self.tab_generation = QWidget()
        self.tab_transmission = QWidget()
        
        # Textos temporários para as abas vazias
        QVBoxLayout(self.tab_topology).addWidget(QLabel("Aba de Topologia (Grafo de Rede) - Em construção"))
        
        # 3. Adicionamos tudo no QTabWidget
        self.tabs.addTab(self.tab_summary, "📊 Resumo Executivo")
        self.tabs.addTab(self.tab_generation, "⚡ Geração")
        self.tabs.addTab(self.tab_transmission, "🔌 Transmissão")
        self.tabs.addTab(self.tab_topology, "🕸️ Topologia (Grafo)")

        layout.addWidget(self.tabs)

    def setup_connections(self):
        self.viewmodel.cases_loaded.connect(self.populate_cases)
        self.viewmodel.error_occurred.connect(self.show_error)
        
        # Quando o usuário escolhe um caso no Dropdown
        self.combo_cases.currentIndexChanged.connect(self.on_case_selected)

    def load_data(self):
        """Chamado pela MainWindow ao abrir esta seção"""
        self.viewmodel.load_cases()

    def populate_cases(self, cases: list):
        self.combo_cases.blockSignals(True)
        self.combo_cases.clear()
        self.combo_cases.addItem("Selecione um caso para analisar...")
        self.case_mapping.clear()
        
        for case in cases:
            display = f"{case.get('external_name')} - {case.get('display_name')}"
            self.combo_cases.addItem(display)
            self.case_mapping[display] = case.get("id")
            
        self.combo_cases.blockSignals(False)

    def on_case_selected(self, index):
        if index > 0:
            selected_text = self.combo_cases.currentText()
            case_id = self.case_mapping.get(selected_text)
            if case_id:
                # Avisa a Aba de Resumo para carregar os dados!
                self.tab_summary.load_case(case_id)
                self.tab_topology.load_case(case_id)

    def show_error(self, msg):
        QMessageBox.warning(self, "Erro", msg)
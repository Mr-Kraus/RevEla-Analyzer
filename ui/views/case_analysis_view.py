from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTabWidget, QMessageBox)
from PyQt6.QtCore import Qt
from ui.viewmodels.case_analysis_viewmodel import CaseAnalysisViewModel

from ui.views.tab_summary_view import TabSummaryView
from ui.views.tab_topology_view import TabTopologyView
from ui.views.tab_transmission_view import TabTransmissionView
from ui.views.tab_generation_view import TabGenerationView

class CaseAnalysisView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = CaseAnalysisViewModel()
        self.case_mapping = {}
        self.current_case_id = None
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
            QTabWidget::pane { border: 1px solid #BDC3C7; background-color: #F5F6FA; border-radius: 6px;}
            QTabBar::tab { background: #ECF0F1; color: #2C3E50; padding: 10px 20px; font-weight: bold; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px;}
            QTabBar::tab:selected { background: #FFFFFF; color: #2980B9; border-top: 3px solid #2980B9; }
            QTabBar::tab:hover:!selected { background: #D6DBDF; }
        """)

        # Instanciando as Abas
        self.tab_summary = TabSummaryView()
        self.tab_topology = TabTopologyView()
        self.tab_generation = TabGenerationView()
        self.tab_transmission = TabTransmissionView()
        
        # Adicionando tudo no QTabWidget
        self.tabs.addTab(self.tab_summary, "📊 Resumo Executivo")
        self.tabs.addTab(self.tab_generation, "🏭 Geração")
        self.tabs.addTab(self.tab_transmission, "⚡ Transmissão")
        self.tabs.addTab(self.tab_topology, "🕸️ Topologia (Grafo)")

        layout.addWidget(self.tabs)

    def setup_connections(self):
        self.viewmodel.cases_loaded.connect(self.populate_cases)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.combo_cases.currentIndexChanged.connect(self.on_case_selected)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def load_data(self):
        """Chamado pela MainWindow ao clicar no botão lateral."""
        self.viewmodel.load_cases()

    def load_case(self, case_id: str, case_name: str = ""):
        """Chamado pela MainWindow quando o usuário clica em 'Analisar' na tabela de Gestão."""
        self.current_case_id = case_id
        
        # Sincroniza a combobox com o caso selecionado sem causar duplo carregamento
        target_text = f"{case_name}"
        index_to_set = -1
        
        for i in range(self.combo_cases.count()):
            if case_id == self.case_mapping.get(self.combo_cases.itemText(i)):
                index_to_set = i
                break
                
        if index_to_set != -1:
            self.combo_cases.setCurrentIndex(index_to_set)

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

        # Se já houver um caso ativo (vindo da aba de Gestão), seleciona ele
        if self.current_case_id:
            self.load_case(self.current_case_id)

    def on_case_selected(self, index):
        if index > 0:
            selected_text = self.combo_cases.currentText()
            case_id = self.case_mapping.get(selected_text)
            if case_id:
                self.current_case_id = case_id 
                
                # Carrega o Resumo imediatamente (é leve)
                if hasattr(self.tab_summary, 'load_case'):
                    self.tab_summary.load_case(case_id)
                
                # Força o recarregamento da aba que estiver ativada no momento
                self.on_tab_changed(self.tabs.currentIndex())

    def show_error(self, msg):
        QMessageBox.warning(self, "Erro", msg)

    def on_tab_changed(self, index):
        """Lazy Loading: Só carrega os dados pesados se a aba for ativada."""
        if not self.current_case_id:
            return
            
        current_widget = self.tabs.widget(index)

        if current_widget == self.tab_topology:
            if getattr(self.tab_topology, 'loaded_case_id', None) != self.current_case_id:
                self.tab_topology.load_case(self.current_case_id)
                self.tab_topology.loaded_case_id = self.current_case_id

        elif current_widget == self.tab_transmission:
            if getattr(self.tab_transmission, 'loaded_case_id', None) != self.current_case_id:
                self.tab_transmission.load_case(self.current_case_id)
                self.tab_transmission.loaded_case_id = self.current_case_id

        elif current_widget == self.tab_generation:
            if getattr(self.tab_generation, 'loaded_case_id', None) != self.current_case_id:
                self.tab_generation.load_case(self.current_case_id)
                self.tab_generation.loaded_case_id = self.current_case_id
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QFrame, QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt
from ui.viewmodels.global_analysis_viewmodel import GlobalAnalysisViewModel
from ui.services.settings_service import SettingsService


class GlobalAnalysisView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = GlobalAnalysisViewModel()
        self.case_mapping = {} # Para associar o nome do caso ao seu UUID
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Cabeçalho e Seletor
        top_bar = QHBoxLayout()
        title = QLabel("Global Analysis")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        
        self.case_selector = QComboBox()
        self.case_selector.setFixedWidth(300)
        self.case_selector.setFixedHeight(35)
        self.case_selector.addItem("Select a case...")
        self.case_selector.setStyleSheet("padding: 5px; font-size: 14px;")
        
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Base Case: "))
        top_bar.addWidget(self.case_selector)
        
        layout.addLayout(top_bar)

        # ==========================================
        # CARDS DE INDICADORES (GRID)
        # ==========================================
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(20)
        
        # Variáveis de Referência dos Indicadores Matemáticos
        self.val_lole = self.create_indicator_card("LOLE (h/ano)", self.cards_grid, 0, 0)
        self.val_epns = self.create_indicator_card("EPNS (MW)", self.cards_grid, 0, 1)
        self.val_eens = self.create_indicator_card("EENS (MWh)", self.cards_grid, 0, 2)
        
        self.val_lolp = self.create_indicator_card("LOLP", self.cards_grid, 1, 0)
        self.val_lolf = self.create_indicator_card("LOLF (occ/ano)", self.cards_grid, 1, 1)
        self.val_lold = self.create_indicator_card("LOLD (h/occ)", self.cards_grid, 1, 2)

        # Variáveis de Referência dos Metadados (Configurações do Caso)
        self.val_analysis_type = self.create_indicator_card("Type of Analysis", self.cards_grid, 2, 0)
        self.val_beta = self.create_indicator_card("Convergence (Beta)", self.cards_grid, 2, 1)
        self.val_years = self.create_indicator_card("Simulated Years", self.cards_grid, 2, 2)

        layout.addLayout(self.cards_grid)
        layout.addStretch() # Empurra tudo para cima

    def create_indicator_card(self, title_text: str, grid: QGridLayout, row: int, col: int) -> QLabel:
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white; border-radius: 8px; border: 1px solid #BDC3C7; }")
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title_text)
        lbl_title.setStyleSheet("color: #7F8C8D; font-size: 14px; font-weight: bold; border: none;")
        
        lbl_value = QLabel("-") # Valor inicial vazio
        lbl_value.setStyleSheet("color: #2980B9; font-size: 26px; font-weight: bold; border: none;")
        
        frame_layout.addWidget(lbl_title)
        frame_layout.addWidget(lbl_value)
        
        grid.addWidget(frame, row, col)
        return lbl_value

    def setup_connections(self):
        self.viewmodel.cases_loaded.connect(self.populate_cases)
        self.viewmodel.analysis_loaded.connect(self.update_indicators)
        self.viewmodel.error_occurred.connect(self.show_error)
        
        # Quando o usuário escolhe um caso diferente no dropdown
        self.case_selector.currentIndexChanged.connect(self.on_case_selected)

    def load_data(self):
        """Chamado pela MainWindow toda vez que entra na aba"""
        self.viewmodel.load_cases()

    def populate_cases(self, cases: list):
        # Evita disparar o evento de "changed" enquanto popula
        self.case_selector.blockSignals(True)
        self.case_selector.clear()
        self.case_selector.addItem("Select a case...")
        self.case_mapping.clear()
        
        for case in cases:
            display = f"{case.get('external_name')} - {case.get('display_name')}"
            self.case_selector.addItem(display)
            self.case_mapping[display] = case.get("id")
            
        self.case_selector.blockSignals(False)

    def on_case_selected(self, index):
        if index > 0: # Ignora o "Selecione um caso..."
            selected_text = self.case_selector.currentText()
            case_id = self.case_mapping.get(selected_text)
            if case_id:
                # Reseta a tela
                self.val_lole.setText("Calculando...")
                self.val_epns.setText("Calculando...")
                self.val_eens.setText("Calculando...")
                self.val_lolp.setText("Calculando...")
                self.val_lolf.setText("Calculando...")
                self.val_lold.setText("Calculando...")
                
                self.val_analysis_type.setText("-")
                self.val_beta.setText("-")
                self.val_years.setText("-")
                
                # Aciona a API
                self.viewmodel.load_analysis(case_id)

    def update_indicators(self, data: dict):
        """Recebe o pacote completo do ViewModel e descasca as informações nas áreas corretas"""
        settings = SettingsService.get_instance()
        
        # Desempacota as gavetas mastigadas pelo ViewModel
        indicators = data.get("indicators", {})
        general_info = data.get("general_info", {})

        def extract_val(key: str) -> float:
            item = indicators.get(key, 0)
            if isinstance(item, dict):
                val = item.get("value", 0)
            else:
                val = item
            try:
                return float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                return 0.0

        # --- PREENCHE OS INDICADORES DE CONFIABILIDADE ---
        self.val_lole.setText(settings.format_number(extract_val('LOLE'), is_table=True))
        self.val_epns.setText(settings.format_number(extract_val('EPNS'), is_table=True))
        self.val_eens.setText(settings.format_number(extract_val('EENS'), is_table=True))
        self.val_lolp.setText(settings.format_number(extract_val('LOLP'), is_table=True, is_lolp=True))
        self.val_lolf.setText(settings.format_number(extract_val('LOLF'), is_table=True))
        self.val_lold.setText(settings.format_number(extract_val('LOLD'), is_table=True))

        # --- PREENCHE OS METADADOS DE SIMULAÇÃO ---
        self.val_analysis_type.setText(str(general_info.get("Tipo de Análise", "N/A")))
        self.val_beta.setText(str(general_info.get("Convergência (Beta)", "N/A")))
        self.val_years.setText(str(general_info.get("Anos Simulados", "N/A")))

    def show_error(self, msg):
        QMessageBox.warning(self, "Erro", msg)
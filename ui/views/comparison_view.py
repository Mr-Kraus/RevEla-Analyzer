from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from ui.viewmodels.comparison_viewmodel import ComparisonViewModel
from ui.services.settings_service import SettingsService

class ComparisonView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = ComparisonViewModel()
        self.case_mapping = {}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Comparação de Casos (A vs B)")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)

        # ==========================================
        # SELETORES SUPERIORES
        # ==========================================
        top_bar = QHBoxLayout()
        
        self.combo_a = QComboBox()
        self.combo_b = QComboBox()
        for combo in [self.combo_a, self.combo_b]:
            combo.setFixedWidth(250)
            combo.setFixedHeight(35)
            combo.addItem("Selecione um caso...")
            
        self.btn_compare = QPushButton("⚖️ Comparar Casos")
        self.btn_compare.setFixedHeight(35)
        self.btn_compare.setStyleSheet("""
            QPushButton { background-color: #E67E22; color: white; font-weight: bold; border-radius: 4px; padding: 0 15px; }
            QPushButton:hover { background-color: #D35400; }
            QPushButton:disabled { background-color: #BDC3C7; }
        """)

        top_bar.addWidget(QLabel("Caso Base (A):"))
        top_bar.addWidget(self.combo_a)
        top_bar.addSpacing(20)
        top_bar.addWidget(QLabel("Caso Alternativo (B):"))
        top_bar.addWidget(self.combo_b)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_compare)
        
        layout.addLayout(top_bar)

        # ==========================================
        # TABELA DE RESULTADOS
        # ==========================================
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Indicador", "Valor (Caso A)", "Valor (Caso B)", "Diferença Absoluta (B - A)", "Diferença %"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)

        # Rodapé de conclusão
        self.lbl_conclusion = QLabel("Selecione dois casos para comparar.")
        self.lbl_conclusion.setStyleSheet("font-size: 16px; font-weight: bold; color: #34495E; margin-top: 10px;")
        self.lbl_conclusion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_conclusion)

    def setup_connections(self):
        self.viewmodel.cases_loaded.connect(self.populate_combos)
        self.viewmodel.comparison_ready.connect(self.build_table)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.viewmodel.is_loading.connect(self.set_loading_state)
        self.btn_compare.clicked.connect(self.handle_compare)

    def load_data(self):
        """Chamado pela MainWindow ao abrir a aba."""
        self.viewmodel.load_cases()

    def populate_combos(self, cases: list):
        self.combo_a.clear()
        self.combo_b.clear()
        self.case_mapping.clear()
        
        self.combo_a.addItem("Selecione o Caso A...")
        self.combo_b.addItem("Selecione o Caso B...")
        
        for case in cases:
            display = f"{case.get('external_name')} - {case.get('display_name')}"
            self.combo_a.addItem(display)
            self.combo_b.addItem(display)
            self.case_mapping[display] = case.get("id")

    def handle_compare(self):
        case_a_name = self.combo_a.currentText()
        case_b_name = self.combo_b.currentText()
        
        id_a = self.case_mapping.get(case_a_name)
        id_b = self.case_mapping.get(case_b_name)
        
        if not id_a or not id_b:
            self.show_error("Por favor, selecione os dois casos para comparar.")
            return
            
        self.viewmodel.compare_cases(id_a, id_b)

    def set_loading_state(self, is_loading):
        self.btn_compare.setEnabled(not is_loading)
        self.btn_compare.setText("Calculando..." if is_loading else "⚖️ Comparar Casos")
        if is_loading:
            self.table.setRowCount(0)
            self.lbl_conclusion.setText("Analisando dados...")

    def build_table(self, data_a: dict, data_b: dict):
        settings = SettingsService.get_instance()
        indicators_list = ["LOLE", "EPNS", "EENS", "LOLP", "LOLF", "LOLD"]
        
        self.table.setRowCount(len(indicators_list))
        
        melhorias = 0
        pioras = 0

        for row, ind_name in enumerate(indicators_list):
            # Extração segura dos valores
            val_a = data_a.get(ind_name, {}).get("value", 0) if isinstance(data_a.get(ind_name), dict) else data_a.get(ind_name, 0)
            val_b = data_b.get(ind_name, {}).get("value", 0) if isinstance(data_b.get(ind_name), dict) else data_b.get(ind_name, 0)
            
            val_a = float(val_a) if val_a is not None else 0.0
            val_b = float(val_b) if val_b is not None else 0.0
            
            # Cálculos
            diff_abs = val_b - val_a
            diff_pct = ((val_b - val_a) / val_a * 100) if val_a != 0 else 0.0
            
            # Formatação baseada no SettingsService
            is_lolp = (ind_name == "LOLP")
            str_a = settings.format_number(val_a, is_table=True, is_lolp=is_lolp)
            str_b = settings.format_number(val_b, is_table=True, is_lolp=is_lolp)
            str_abs = settings.format_number(diff_abs, is_table=True, is_lolp=is_lolp)
            str_pct = f"{diff_pct:.2f} %"
            
            # Preenchendo colunas
            self.table.setItem(row, 0, QTableWidgetItem(ind_name))
            self.table.setItem(row, 1, QTableWidgetItem(str_a))
            self.table.setItem(row, 2, QTableWidgetItem(str_b))
            
            item_abs = QTableWidgetItem(f"{'+' if diff_abs > 0 else ''}{str_abs}")
            item_pct = QTableWidgetItem(f"{'+' if diff_pct > 0 else ''}{str_pct}")
            
            # Colorização de UX: Menos é Melhor!
            if diff_abs < 0:
                item_abs.setForeground(Qt.GlobalColor.darkGreen)
                item_pct.setForeground(Qt.GlobalColor.darkGreen)
                melhorias += 1
            elif diff_abs > 0:
                item_abs.setForeground(Qt.GlobalColor.darkRed)
                item_pct.setForeground(Qt.GlobalColor.darkRed)
                pioras += 1
                
            self.table.setItem(row, 3, item_abs)
            self.table.setItem(row, 4, item_pct)
            
        # Conclusão inteligente
        if melhorias > pioras:
            self.lbl_conclusion.setText("🏆 Conclusão: O Caso Alternativo (B) apresenta índices de confiabilidade superiores ao Caso Base (A).")
            self.lbl_conclusion.setStyleSheet("color: #27AE60; font-size: 16px; font-weight: bold;")
        elif pioras > melhorias:
            self.lbl_conclusion.setText("⚠️ Conclusão: O Caso Alternativo (B) piora a confiabilidade do sistema em relação ao Caso Base (A).")
            self.lbl_conclusion.setStyleSheet("color: #C0392B; font-size: 16px; font-weight: bold;")
        else:
            self.lbl_conclusion.setText("⚖️ Conclusão: Os casos são equivalentes ou não houve mudanças significativas.")
            self.lbl_conclusion.setStyleSheet("color: #34495E; font-size: 16px; font-weight: bold;")

    def show_error(self, msg):
        QMessageBox.warning(self, "Erro na Comparação", msg)
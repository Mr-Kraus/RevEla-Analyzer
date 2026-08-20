from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QScrollArea, QListWidget, QListWidgetItem, QComboBox, 
    QGroupBox, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.viewmodels.tab_global_viewmodel import TabGlobalViewModel

class TabGlobalView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabGlobalViewModel()
        self.cases_data = {} # Cache local dos dados já baixados {case_id: data_dict}
        self.selected_case_ids = []
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # ==========================================
        # PAINEL CENTRAL (Dados)
        # ==========================================
        self.content_stack = QStackedWidget()
        
        # Página Tipo 1: Scroll Area com Múltiplas Tabelas
        self.page_type1 = QScrollArea()
        self.page_type1.setWidgetResizable(True)
        self.page_type1.setStyleSheet("QScrollArea { border: none; background-color: #F5F6FA; }")
        self.scroll_content_type1 = QWidget()
        self.layout_type1 = QVBoxLayout(self.scroll_content_type1)
        self.layout_type1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.page_type1.setWidget(self.scroll_content_type1)
        self.content_stack.addWidget(self.page_type1)

        # Página Tipo 2: Tabela Única Lado a Lado
        self.page_type2 = QWidget()
        layout_type2 = QVBoxLayout(self.page_type2)
        layout_type2.setContentsMargins(0, 0, 0, 0)
        self.table_comparative = QTableWidget()
        self.table_comparative.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; border-radius: 6px; }
            QHeaderView::section { background-color: #ECF0F1; font-weight: bold; color: #2C3E50; padding: 6px; }
        """)
        layout_type2.addWidget(self.table_comparative)
        self.content_stack.addWidget(self.page_type2)

        layout.addWidget(self.content_stack, stretch=4)

        # ==========================================
        # PAINEL LATERAL DIREITO (Controles)
        # ==========================================
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("QFrame { background-color: white; border: 1px solid #D5D8DC; border-radius: 8px; }")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(15)

        lbl_config = QLabel("⚙️ Configuração de Visualização")
        lbl_config.setStyleSheet("font-weight: bold; color: #2C3E50; border: none; font-size: 14px;")
        
        self.combo_view_type = QComboBox()
        self.combo_view_type.addItems(["Tipo 1: Detalhado por Caso", "Tipo 2: Comparativo Lado a Lado"])
        self.combo_view_type.setStyleSheet("padding: 5px; border: 1px solid #BDC3C7; border-radius: 4px;")

        lbl_cases = QLabel("📂 Selecione os Casos:")
        lbl_cases.setStyleSheet("font-weight: bold; color: #2C3E50; border: none; margin-top: 10px;")

        self.list_cases = QListWidget()
        self.list_cases.setStyleSheet("border: 1px solid #BDC3C7; border-radius: 4px; padding: 5px;")

        sidebar_layout.addWidget(lbl_config)
        sidebar_layout.addWidget(self.combo_view_type)
        sidebar_layout.addWidget(lbl_cases)
        sidebar_layout.addWidget(self.list_cases)
        layout.addWidget(self.sidebar, stretch=1)

    def setup_connections(self):
        self.viewmodel.cases_list_ready.connect(self.populate_cases_list)
        self.viewmodel.global_data_ready.connect(self.on_data_received)
        self.viewmodel.error_occurred.connect(lambda e: QMessageBox.warning(self, "Erro", e))
        
        self.list_cases.itemChanged.connect(self.on_case_selection_changed)
        self.combo_view_type.currentIndexChanged.connect(self.render_view)

    def load_case(self, case_id: str):
        """Chamado quando a tela é aberta."""
        self.initial_case_id = case_id
        self.viewmodel.load_available_cases()

    def populate_cases_list(self, cases: list):
        self.list_cases.blockSignals(True)
        self.list_cases.clear()
        
        for case in cases:
            item = QListWidgetItem(case.get("display_name", ""))
            item.setData(Qt.ItemDataRole.UserRole, case.get("id"))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Marca automaticamente o caso que foi clicado lá na aba principal
            if case.get("id") == self.initial_case_id:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.list_cases.addItem(item)
            
        self.list_cases.blockSignals(False)
        self.on_case_selection_changed() # Força o primeiro carregamento

    def on_case_selection_changed(self):
        self.selected_case_ids = []
        for i in range(self.list_cases.count()):
            item = self.list_cases.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                cid = item.data(Qt.ItemDataRole.UserRole)
                self.selected_case_ids.append(cid)
                
                # Se não tem os dados no cache, pede pro backend!
                if cid not in self.cases_data:
                    self.viewmodel.load_case_global_data(cid)
                    
        self.render_view()

    def on_data_received(self, case_id: str, data: dict):
        self.cases_data[case_id] = data
        self.render_view()

    def render_view(self):
        view_type = self.combo_view_type.currentIndex()
        
        # Pega apenas os dados dos casos que estão marcados E já foram baixados da API
        active_data = [self.cases_data[cid] for cid in self.selected_case_ids if cid in self.cases_data]

        if view_type == 0:
            self.content_stack.setCurrentWidget(self.page_type1)
            self.render_type1(active_data)
        else:
            self.content_stack.setCurrentWidget(self.page_type2)
            self.render_type2(active_data)

    def render_type1(self, data_list: list):
        # Limpa layout atual
        while self.layout_type1.count():
            child = self.layout_type1.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for data in data_list:
            group = QGroupBox(f"📊 Caso: {data['case_name']}")
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #2C3E50; border: 2px solid #3498DB; border-radius: 6px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
            hbox = QHBoxLayout(group)
            hbox.setContentsMargins(15, 20, 15, 15)

            # Tabela Esquerda (Indicadores)
            t_ind = QTableWidget(7, 4)
            t_ind.setHorizontalHeaderLabels(["Indicador", "Unidade", "Valor", "Interv. Confiança (95%)"])
            t_ind.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            t_ind.verticalHeader().setVisible(False)
            t_ind.setStyleSheet("border: 1px solid #D5D8DC;")

            for row, (key, info) in enumerate(data["indicators"].items()):
                t_ind.setItem(row, 0, QTableWidgetItem(key))
                t_ind.setItem(row, 1, QTableWidgetItem(info["unit"]))
                t_ind.setItem(row, 2, QTableWidgetItem(str(info["value"])))
                t_ind.setItem(row, 3, QTableWidgetItem("± N/A")) # Placeholder de Confiança
            
            # Tabela Direita (Info Geral)
            t_info = QTableWidget(7, 2)
            t_info.setHorizontalHeaderLabels(["Informação Geral", "Valor"])
            t_info.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            t_info.verticalHeader().setVisible(False)
            t_info.setStyleSheet("border: 1px solid #D5D8DC; background-color: #FAFAFA;")

            for row, (key, val) in enumerate(data["general_info"].items()):
                t_info.setItem(row, 0, QTableWidgetItem(key))
                item_val = QTableWidgetItem(str(val))
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                t_info.setItem(row, 1, item_val)

            hbox.addWidget(t_ind, stretch=2)
            hbox.addWidget(t_info, stretch=1)
            self.layout_type1.addWidget(group)

    def render_type2(self, data_list: list):
        self.table_comparative.clear()
        
        if not data_list:
            self.table_comparative.setRowCount(0)
            self.table_comparative.setColumnCount(0)
            return

        headers = ["Indicador", "Unidade"] + [d["case_name"] for d in data_list]
        self.table_comparative.setColumnCount(len(headers))
        self.table_comparative.setHorizontalHeaderLabels(headers)
        self.table_comparative.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        indicators = list(data_list[0]["indicators"].keys())
        self.table_comparative.setRowCount(len(indicators))

        for row, ind in enumerate(indicators):
            unit = data_list[0]["indicators"][ind]["unit"]
            self.table_comparative.setItem(row, 0, QTableWidgetItem(ind))
            self.table_comparative.setItem(row, 1, QTableWidgetItem(unit))
            
            for col, data in enumerate(data_list):
                val = str(data["indicators"][ind]["value"])
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_comparative.setItem(row, 2 + col, item)
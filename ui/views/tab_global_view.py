from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QScrollArea, QListWidget, QListWidgetItem, QComboBox, 
    QGroupBox, QStackedWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from ui.viewmodels.tab_global_viewmodel import TabGlobalViewModel
from ui.services.settings_service import SettingsService


# =====================================================================
# WIDGETS CONCRETOS DE VISUALIZAÇÃO (OOP)
# =====================================================================

class CaseDetailCard(QGroupBox):
    """
    Componente Concreto para o Tipo 1: Card detalhado de um caso específico.
    Calcula a própria altura para evitar scroll interno nas tabelas.
    """
    def __init__(self, data: dict, settings: SettingsService):
        super().__init__()
        case_name = data.get("case_name", "Desconhecido")
        self.setTitle(f"📊 Caso: {case_name}")
        
        # Estilização do Card (Fundo branco, borda suave e sombra simulada)
        self.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px;
                color: #2C3E50; 
                background-color: #FFFFFF;
                border: 1px solid #D5D8DC; 
                border-radius: 8px; 
                margin-top: 15px; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 15px; 
                padding: 0 5px; 
                color: #2980B9;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(25)

        # 1. Tabela Principal (Indicadores)
        self.table_ind = QTableWidget(len(data["indicators"]), 4)
        self.table_ind.setHorizontalHeaderLabels([f"Indicadores ({case_name})", "Unidade", "Valor", "Interv. Confiança"])
        self._apply_modern_style(self.table_ind)

        for row, (key, info) in enumerate(data["indicators"].items()):
            self.table_ind.setItem(row, 0, QTableWidgetItem(key))
            
            item_unit = QTableWidgetItem(info["unit"])
            item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_ind.setItem(row, 1, item_unit)
            
            val_formatado = settings.format_number(info['value'], is_table=True, is_lolp=(key.upper() == "LOLP"))
            item_val = QTableWidgetItem(val_formatado)
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Destaque visual suave para o valor
            font = item_val.font()
            font.setBold(True)
            # ... (código existente da table_ind)
            item_val.setFont(font)
            self.table_ind.setItem(row, 2, item_val)
            
            # AGORA ELE LÊ A CONFIANÇA DO DICIONÁRIO!
            conf_str = info.get("conf", "N/A")
            texto_confianca = f"± {conf_str}" if conf_str != "N/A" else "N/A"
            
            item_conf = QTableWidgetItem(texto_confianca)
            item_conf.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if conf_str == "N/A":
                item_conf.setForeground(Qt.GlobalColor.darkGray)
            else:
                item_conf.setForeground(Qt.GlobalColor.darkGreen) # Verde para dar um charme nos acertos
                
            self.table_ind.setItem(row, 3, item_conf)

        # 2. Tabela Menor (Informações Gerais)
        self.table_info = QTableWidget(len(data["general_info"]), 2)
        self.table_info.setHorizontalHeaderLabels(["Informação Geral", "Valor"])
        self._apply_modern_style(self.table_info)

        for row, (key, val) in enumerate(data["general_info"].items()):
            self.table_info.setItem(row, 0, QTableWidgetItem(key))
            item_val = QTableWidgetItem(str(val))
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_info.setItem(row, 1, item_val)

        # MAGIA UX: Ajusta a altura exata para matar o scroll interno
        self._adjust_height_to_contents(self.table_ind)
        self._adjust_height_to_contents(self.table_info)

        layout.addWidget(self.table_ind, stretch=6)
        layout.addWidget(self.table_info, stretch=4)

    def _apply_modern_style(self, table: QTableWidget):
        """Aplica uma identidade visual corporativa e limpa."""
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Desabilita interação de clique para não ficar aquele quadrado azul feio
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Desliga os scrolls internos
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Zebrado para facilitar a leitura
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)

        table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #E0E6ED; 
                border-radius: 6px; 
                background-color: #FFFFFF; 
                alternate-background-color: #F8F9F9;
            }
            QTableWidget::item { 
                padding: 5px; 
                border-bottom: 1px solid #F2F4F4; 
                color: #34495E; 
            }
            QHeaderView::section { 
                background-color: #34495E; 
                color: #FFFFFF; 
                font-weight: bold; 
                padding: 10px; 
                border: none;
                border-bottom: 3px solid #3498DB;
            }
        """)

    def _adjust_height_to_contents(self, table: QTableWidget):
        """Calcula e trava a altura da tabela baseado no tamanho do cabeçalho e das linhas."""
        table.resizeRowsToContents()
        height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            height += table.rowHeight(row)
        # O +2 compensa os pixels das bordas externas
        table.setFixedHeight(height + 2)


class ComparativeTable(QTableWidget):
    """
    Componente Concreto para o Tipo 2: Tabela gigante comparando Múltiplos Casos Lado a Lado.
    """
    def __init__(self, data_list: list, settings: SettingsService):
        super().__init__()
        self.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; border-radius: 6px; alternate-background-color: #F8F9F9; }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #F2F4F4; color: #34495E; }
            QHeaderView::section { background-color: #34495E; color: white; font-weight: bold; padding: 10px; border: none; border-bottom: 3px solid #3498DB;}
        """)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)

        if not data_list:
            self.setRowCount(0)
            self.setColumnCount(0)
            return

        headers = ["Indicador", "Unidade"] + [d["case_name"] for d in data_list]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(2, len(headers)):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        indicators = list(data_list[0]["indicators"].keys())
        self.setRowCount(len(indicators))

        for row, ind in enumerate(indicators):
            unit = data_list[0]["indicators"][ind]["unit"]
            
            item_ind = QTableWidgetItem(ind)
            font = item_ind.font()
            font.setBold(True)
            item_ind.setFont(font)
            
            item_unit = QTableWidgetItem(unit)
            item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_unit.setForeground(Qt.GlobalColor.darkGray)

            self.setItem(row, 0, item_ind)
            self.setItem(row, 1, item_unit)
            
            for col, data in enumerate(data_list):
                raw_val = data["indicators"][ind]["value"]
                val_str = settings.format_number(raw_val, is_table=True, is_lolp=(ind.upper() == "LOLP"))
                
                item_val = QTableWidgetItem(val_str)
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                font_val = item_val.font()
                font_val.setBold(True)
                item_val.setFont(font_val)
                self.setItem(row, 2 + col, item_val)


# =====================================================================
# VIEW PRINCIPAL (Orquestrador)
# =====================================================================

class TabGlobalView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabGlobalViewModel()
        self.settings_service = SettingsService.get_instance()
        self.cases_data = {} 
        self.selected_case_ids = []
        self.initial_case_id = None
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 1. PAINEL CENTRAL (Stack de Visualização)
        self.content_stack = QStackedWidget()
        
        # Base Tipo 1 (Scroll Externo limpo e liso)
        self.page_type1 = QScrollArea()
        self.page_type1.setWidgetResizable(True)
        # Borda removida para não criar caixas desnecessárias
        self.page_type1.setStyleSheet("QScrollArea { border: none; background-color: transparent; }") 
        self.scroll_content_type1 = QWidget()
        self.scroll_content_type1.setStyleSheet("background-color: transparent;")
        
        self.layout_type1 = QVBoxLayout(self.scroll_content_type1)
        self.layout_type1.setAlignment(Qt.AlignmentFlag.AlignTop)
        # O espaçamento entre os cards
        self.layout_type1.setSpacing(25) 
        self.page_type1.setWidget(self.scroll_content_type1)
        self.content_stack.addWidget(self.page_type1)

        # Base Tipo 2 (Tabela Única)
        self.page_type2 = QWidget()
        self.layout_type2 = QVBoxLayout(self.page_type2)
        self.layout_type2.setContentsMargins(0, 0, 0, 0)
        self.content_stack.addWidget(self.page_type2)

        layout.addWidget(self.content_stack, stretch=4)

        # 2. PAINEL LATERAL (Controles)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet("QFrame { background-color: white; border: 1px solid #D5D8DC; border-radius: 8px; }")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(15)

        lbl_config = QLabel("⚙️ Visualização da Aba")
        lbl_config.setStyleSheet("font-weight: bold; color: #2C3E50; border: none; font-size: 14px;")
        
        self.combo_view_type = QComboBox()
        self.combo_view_type.addItems([
            "Tipo 1: Detalhado (Painéis Rolantes)", 
            "Tipo 2: Comparativo (Tabela Consolidada)"
        ])
        self.combo_view_type.setStyleSheet("padding: 8px; border: 1px solid #BDC3C7; border-radius: 4px;")

        lbl_cases = QLabel("📂 Casos Selecionados:")
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
        self.combo_view_type.currentIndexChanged.connect(self.save_user_preferences)
        self.settings_service.settings_changed.connect(self.render_view)

    def load_data(self):
        """Chamado pelo MainWindow ao clicar no botão lateral da Aba Global."""
        self.combo_view_type.blockSignals(True)
        self.combo_view_type.setCurrentIndex(self.settings_service.global_view_type)
        self.combo_view_type.blockSignals(False)
        self.viewmodel.load_available_cases()

    def save_user_preferences(self, index: int):
        self.settings_service.global_view_type = index

    def populate_cases_list(self, cases: list):
        self.list_cases.blockSignals(True)
        self.list_cases.clear()
        
        for case in cases:
            display_text = case.get("display_name", "")
            # Fallback caso não tenha display_name
            if not display_text:
                display_text = case.get("external_name", "Desconhecido")
                
            item = QListWidgetItem(display_text)
            cid = case.get("id")
            item.setData(Qt.ItemDataRole.UserRole, cid)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # MAGIA UX: Verifica a memória da classe para manter o estado dos checkboxes!
            if cid in self.selected_case_ids or cid == self.initial_case_id:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.list_cases.addItem(item)
            
        self.list_cases.blockSignals(False)
        # O método abaixo vai ler os itens que acabamos de marcar e remontar os gráficos/tabelas
        self.on_case_selection_changed()

    def on_case_selection_changed(self):
        self.selected_case_ids = []
        for i in range(self.list_cases.count()):
            item = self.list_cases.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                cid = item.data(Qt.ItemDataRole.UserRole)
                self.selected_case_ids.append(cid)
                
                if cid not in self.cases_data:
                    self.viewmodel.load_case_global_data(cid)
                    
        self.render_view()

    def on_data_received(self, case_id: str, data: dict):
        self.cases_data[case_id] = data
        self.render_view()

    def render_view(self):
        view_type = self.settings_service.global_view_type
        active_data = [self.cases_data[cid] for cid in self.selected_case_ids if cid in self.cases_data]

        if view_type == 0:
            self.content_stack.setCurrentWidget(self.page_type1)
            while self.layout_type1.count():
                child = self.layout_type1.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            
            for data in active_data:
                card = CaseDetailCard(data, self.settings_service)
                self.layout_type1.addWidget(card)
        else:
            self.content_stack.setCurrentWidget(self.page_type2)
            while self.layout_type2.count():
                child = self.layout_type2.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            
            comp_table = ComparativeTable(active_data, self.settings_service)
            self.layout_type2.addWidget(comp_table)
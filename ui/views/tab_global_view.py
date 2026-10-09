import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.viewmodels.settings_viewmodel import SettingsViewModel
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QScrollArea, QListWidget, QListWidgetItem, QComboBox, 
    QGroupBox, QStackedWidget, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from ui.viewmodels.tab_global_viewmodel import TabGlobalViewModel
from ui.services.settings_service import SettingsService

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

# =====================================================================
# FUNÇÃO GERADORA DE GRÁFICOS DUAL-AXIS
# =====================================================================
def create_dual_axis_chart(data_list: list, ind_left: str, ind_right: str) -> FigureCanvas:
    """Cria um gráfico combinando colunas (Eixo Esq) e Linhas (Eixo Dir)."""
    fig = Figure(figsize=(5, 3), dpi=100, facecolor='#FFFFFF')
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    
    x = np.arange(len(data_list))
    names = [d.get("case_name", "Desconhecido") for d in data_list]
    
    # Função segura para extrair os valores mesmo se a chave não existir
    def get_val(d, ind):
        return d.get("indicators", {}).get(ind, {}).get("value", 0.0)
        
    val_left = [get_val(d, ind_left) for d in data_list]
    val_right = [get_val(d, ind_right) for d in data_list]
    
    # Plota Barras (Eixo Esquerdo)
    ax1.bar(x, val_left, color='#38BDF8', width=0.4, label=ind_left, edgecolor='white')
    
    # Plota Marcadores/Linha (Eixo Direito)
    marker_style = '-o' if len(data_list) > 1 else 'o'
    ax2.plot(x, val_right, marker_style, color='#F59E0B', linewidth=2, markersize=8, label=ind_right)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=15 if len(data_list) > 1 else 0, ha='center' if len(data_list) == 1 else 'right', fontsize=9)
    
    ax1.set_ylabel(ind_left, color='#0284C7')
    ax2.set_ylabel(ind_right, color='#D97706')
    
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    fig.legend(h1+h2, l1+l2, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, frameon=False)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.85)
    
    return FigureCanvas(fig)


# =====================================================================
# WIDGETS CONCRETOS DE VISUALIZAÇÃO
# =====================================================================

class CaseDetailCard(QGroupBox):
    """Card detalhado de um caso específico para o modo 'Tabelas Separadas'."""
    def __init__(self, data: dict): # Removido o parâmetro settings
        super().__init__()
        case_name = data.get("case_name", "Desconhecido")
        self.setTitle(f"Caso: {case_name}")
        
        # Puxa configurações globais nativamente
        config = SettingsViewModel().load_settings()
        decimais = config.get("precisao_tabelas", 2)
        formato_lolp = config.get("formato_lolp", "decimal")
        
        self.setStyleSheet("""
            QGroupBox { 
                font-weight: normal; 
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
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(25)

        self.table_ind = QTableWidget(len(data["indicators"]), 4)
        self.table_ind.setHorizontalHeaderLabels(["Indicador", "Unidade", "Valor", "\u03B2"])
        self._apply_modern_style(self.table_ind)

        for row, (key, info) in enumerate(data["indicators"].items()):
            self.table_ind.setItem(row, 0, QTableWidgetItem(key))
            
            item_unit = QTableWidgetItem(info["unit"])
            item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_ind.setItem(row, 1, item_unit)
            
            raw_val = info.get("value", 0.0)
            
            # Aplica formatação científica para LOLP se habilitado nas configurações
            if key.upper() == "LOLP" and formato_lolp == "scientific":
                val_formatado = f"{raw_val:.{decimais}e}"
            else:
                val_formatado = f"{raw_val:.{decimais}f}"
                
            item_val = QTableWidgetItem(val_formatado)
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_ind.setItem(row, 2, item_val)
            
            conf_str = info.get("conf", "N/A")
            texto_confianca = f"± {conf_str}" if conf_str != "N/A" else "N/A"
            
            item_conf = QTableWidgetItem(texto_confianca)
            item_conf.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if conf_str == "N/A":
                item_conf.setForeground(Qt.GlobalColor.darkGray)
            else:
                item_conf.setForeground(Qt.GlobalColor.darkGreen) 
                
            self.table_ind.setItem(row, 3, item_conf)

        self._adjust_height_to_contents(self.table_ind)
        layout.addWidget(self.table_ind)

        charts_layout = QHBoxLayout()
        canvas_lole = create_dual_axis_chart([data], "LOLE", "EENS")
        canvas_lolf = create_dual_axis_chart([data], "LOLF", "LOLD")
        
        canvas_lole.setStyleSheet("border: none;")
        canvas_lolf.setStyleSheet("border: none;")
        
        charts_layout.addWidget(canvas_lole)
        charts_layout.addWidget(canvas_lolf)
        
        chart_container = QWidget()
        chart_container.setLayout(charts_layout)
        chart_container.setMinimumHeight(300)
        
        layout.addWidget(chart_container)

    def _apply_modern_style(self, table: QTableWidget):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)

        table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #E0E6ED; 
                border-radius: 6px; 
                background-color: #FFFFFF; 
                alternate-background-color: #F8F9F9;
                font-weight: normal;
            }
            QTableWidget::item { 
                padding: 5px; 
                border-bottom: 1px solid #F2F4F4; 
                color: #34495E; 
            }
            QHeaderView::section { 
                background-color: #34495E; 
                color: #FFFFFF; 
                font-weight: normal; 
                padding: 10px; 
                border: none;
                border-bottom: 3px solid #3498DB;
            }
        """)

    def _adjust_height_to_contents(self, table: QTableWidget):
        table.resizeRowsToContents()
        height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            height += table.rowHeight(row)
        table.setFixedHeight(height + 2)

class ComparativeTable(QTableWidget):
    """Tabela comparando Múltiplos Casos Lado a Lado para o modo 'Tabela Única'."""
    def __init__(self, data_list: list): # Removido o parâmetro settings
        super().__init__()
        
        config = SettingsViewModel().load_settings()
        decimais = config.get("precisao_tabelas", 2)
        formato_lolp = config.get("formato_lolp", "decimal")
        
        self.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; border-radius: 6px; alternate-background-color: #F8F9F9; font-weight: normal; }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #F2F4F4; color: #34495E; }
            QHeaderView::section { background-color: #34495E; color: white; font-weight: normal; padding: 10px; border: none; border-bottom: 3px solid #3498DB;}
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

        headers = ["Indicador", "Unidade"] + [d.get("case_name", "Desconhecido") for d in data_list]
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
            
            self.setItem(row, 0, QTableWidgetItem(ind))
            
            item_unit = QTableWidgetItem(unit)
            item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_unit.setForeground(Qt.GlobalColor.darkGray)
            self.setItem(row, 1, item_unit)
            
            for col, data in enumerate(data_list):
                raw_val = data["indicators"][ind].get("value", 0.0)
                
                if ind.upper() == "LOLP" and formato_lolp == "scientific":
                    val_str = f"{raw_val:.{decimais}e}"
                else:
                    val_str = f"{raw_val:.{decimais}f}"
                
                item_val = QTableWidgetItem(val_str)
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, 2 + col, item_val)

        self.resizeRowsToContents()
        height = self.horizontalHeader().height()
        for r in range(self.rowCount()): height += self.rowHeight(r)
        self.setFixedHeight(height + 2)

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
        self.current_view_type = 1
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 1. PAINEL CENTRAL (Stack de Visualização)
        self.content_stack = QStackedWidget()
        
        # Base Tipo 1 (Tabelas Separadas)
        self.page_type1 = QScrollArea()
        self.page_type1.setWidgetResizable(True)
        self.page_type1.setStyleSheet("QScrollArea { border: none; background-color: transparent; }") 
        self.scroll_content_type1 = QWidget()
        self.scroll_content_type1.setStyleSheet("background-color: transparent;")
        
        self.layout_type1 = QVBoxLayout(self.scroll_content_type1)
        self.layout_type1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_type1.setSpacing(25) 
        self.page_type1.setWidget(self.scroll_content_type1)
        self.content_stack.addWidget(self.page_type1)

        # Base Tipo 2 (Tabela Única com Gráficos no fundo)
        self.page_type2 = QScrollArea()
        self.page_type2.setWidgetResizable(True)
        self.page_type2.setStyleSheet("QScrollArea { border: none; background-color: transparent; }") 
        self.scroll_content_type2 = QWidget()
        self.scroll_content_type2.setStyleSheet("background-color: transparent;")
        
        self.layout_type2 = QVBoxLayout(self.scroll_content_type2)
        self.layout_type2.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_type2.setSpacing(20)
        self.page_type2.setWidget(self.scroll_content_type2)
        self.content_stack.addWidget(self.page_type2)

        layout.addWidget(self.content_stack, stretch=4)

        # 2. PAINEL LATERAL (Controles)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(300)
        self.sidebar.setStyleSheet("QFrame { background-color: white; border: 1px solid #D5D8DC; border-radius: 8px; }")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(15)

        lbl_config = QLabel("⚙️ Modo de Visualização")
        lbl_config.setStyleSheet("color: #2C3E50; border: none; font-size: 14px; font-weight: normal;")
        
        self.combo_view_type = QComboBox()
        self.combo_view_type.addItems([
            "Tabelas Separadas (Roláveis)", 
            "Tabela Única (Comparativo)"
        ])
        self.combo_view_type.setStyleSheet("padding: 8px; border: 1px solid #BDC3C7; border-radius: 4px; font-weight: normal;")

        lbl_cases = QLabel("📂 Casos Selecionados:")
        lbl_cases.setStyleSheet("color: #2C3E50; border: none; margin-top: 10px; font-weight: normal;")

        self.list_cases = QListWidget()
        self.list_cases.setStyleSheet("border: 1px solid #BDC3C7; border-radius: 4px; padding: 5px; font-weight: normal;")

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
        self.combo_view_type.blockSignals(True)
        # Substituído a chamada do settings_service pela variável local
        self.combo_view_type.setCurrentIndex(self.current_view_type)
        self.combo_view_type.blockSignals(False)
        self.viewmodel.load_available_cases()

    def save_user_preferences(self, index: int):
        # Agora ele salva na própria view
        self.current_view_type = index
        self.render_view()

    def populate_cases_list(self, cases: list):
        self.list_cases.blockSignals(True)
        self.list_cases.clear()
        
        for case in cases:
            display_text = case.get("display_name", "")
            if not display_text:
                display_text = case.get("external_name", "Desconhecido")
                
            item = QListWidgetItem(display_text)
            cid = case.get("id")
            item.setData(Qt.ItemDataRole.UserRole, cid)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if cid in self.selected_case_ids or cid == self.initial_case_id:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.list_cases.addItem(item)
            
        self.list_cases.blockSignals(False)
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

    def clear_layout_recursively(self, layout):
        """Método utilitário para deletar perfeitamente widgets aninhados."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout_recursively(item.layout())

    def render_view(self):
        view_type = self.current_view_type
        active_data = [self.cases_data[cid] for cid in self.selected_case_ids if cid in self.cases_data]

        if view_type == 0:
            # Tabelas Separadas (Roláveis)
            self.content_stack.setCurrentWidget(self.page_type1)
            self.clear_layout_recursively(self.layout_type1)
            
            if not active_data: return
            
            for data in active_data:
                card = CaseDetailCard(data)
                self.layout_type1.addWidget(card)
        else:
            # Tabela Única (Comparativo) + Gráficos Globais no fundo
            self.content_stack.setCurrentWidget(self.page_type2)
            self.clear_layout_recursively(self.layout_type2)
            
            if not active_data: return

            comp_table = ComparativeTable(active_data)
            self.layout_type2.addWidget(comp_table)
            
            # Gráficos de Comparação globais (todos os casos combinados)
            charts_layout = QHBoxLayout()
            canvas_lole = create_dual_axis_chart(active_data, "LOLE", "EENS")
            canvas_lolf = create_dual_axis_chart(active_data, "LOLF", "LOLD")
            
            canvas_lole.setStyleSheet("border: none;")
            canvas_lolf.setStyleSheet("border: none;")
            
            charts_layout.addWidget(canvas_lole)
            charts_layout.addWidget(canvas_lolf)
            
            chart_container = QWidget()
            chart_container.setLayout(charts_layout)
            chart_container.setMinimumHeight(350)
            
            self.layout_type2.addWidget(chart_container)
            self.layout_type2.addStretch()
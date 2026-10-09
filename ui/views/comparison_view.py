import uuid
import colorsys

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.viewmodels.settings_viewmodel import SettingsViewModel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QListWidget, QListWidgetItem, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGroupBox, QCheckBox, QScrollArea, QFrame,
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem, QToolBox, QRadioButton, QButtonGroup,
    QDialog, QLineEdit
)

from ui.services.settings_service import SettingsService
from ui.viewmodels.comparison_viewmodel import ComparisonViewModel

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

# =========================================================================
# VARIÁVEIS GLOBAIS DE TEMPO (Imutáveis)
# =========================================================================
HOURS_IN_YEAR = 8760
WEEKS_IN_YEAR = 52
MONTHS_IN_YEAR = 12


# =========================================================================
# DIÁLOGO DE FILTRO DE ELEMENTOS
# =========================================================================
class ElementFilterDialog(QDialog):
    def __init__(self, all_elements, active_elements, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtrar Elementos")
        self.resize(350, 450)
        self.all_elements = all_elements
        self.active_elements = set(active_elements)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Barra de Pesquisa
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar elemento (ex: Barra 1)...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.search_bar.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 4px;")
        layout.addWidget(self.search_bar)
        
        # Botões Rápidos
        btn_layout = QHBoxLayout()
        btn_all = QPushButton("Marcar Tudo")
        btn_none = QPushButton("Desmarcar Tudo")
        btn_all.clicked.connect(self.select_all)
        btn_none.clicked.connect(self.deselect_all)
        for btn in [btn_all, btn_none]:
            btn.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; padding: 5px; border-radius: 4px;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(btn_all)
        btn_layout.addWidget(btn_none)
        layout.addLayout(btn_layout)
        
        # Lista de Elementos
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 4px; padding: 5px;")
        for el in self.all_elements:
            item = QListWidgetItem(el)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if el in self.active_elements:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        # Botão Salvar
        self.btn_save = QPushButton("Aplicar Filtro")
        self.btn_save.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)
        layout.addWidget(self.btn_save)

    def filter_list(self, text):
        search_text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(search_text not in item.text().lower())

    def select_all(self):
        for i in range(self.list_widget.count()):
            if not self.list_widget.item(i).isHidden():
                self.list_widget.item(i).setCheckState(Qt.CheckState.Checked)

    def deselect_all(self):
        for i in range(self.list_widget.count()):
            if not self.list_widget.item(i).isHidden():
                self.list_widget.item(i).setCheckState(Qt.CheckState.Unchecked)

    def get_selected_elements(self):
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected


# =========================================================================
# CLASSE PRINCIPAL DA VIEW
# =========================================================================
class ComparisonView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = ComparisonViewModel()
        self.settings_vm = SettingsViewModel()
        self.cases_mapping = {}
        self.current_data = {}
        self.case_ids_cache = []
        self.case_names_cache = []
        
        # Filtros e Séries Temporais
        self.active_elements_filter = [] 
        self.current_ts_data = {} # Dados para a aba ENS
        
        self.chart_colors = ['#0EA5E9', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6']
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setStyleSheet("""
        QWidget { font-family: "Segoe UI", Arial, sans-serif; color: #0F172A; background-color: #F8FAFC; }
        QToolBox::tab { background-color: #F1F5F9; color: #0F172A; font-weight: bold; border-radius: 4px; padding: 5px; }
        QToolBox::tab:selected { background-color: #E0F2FE; color: #0369A1; }
        QGroupBox { font-weight: bold; border: 1px solid #CBD5E1; border-radius: 8px; margin-top: 15px; padding-top: 15px; background-color: #FFFFFF; }
        QComboBox, QSpinBox { border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px; background-color: #FFFFFF; }
        QComboBox:hover, QSpinBox:hover { border: 1px solid #0284C7; }
        QCheckBox, QRadioButton { spacing: 8px; font-size: 13px; color: #334155; }
        QScrollArea { border: none; background-color: transparent; }
        QTabWidget::pane { border: none; background-color: transparent; }
        QTabBar::tab { background: #E2E8F0; color: #64748B; padding: 10px 20px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
        QTabBar::tab:selected { background: #0284C7; color: #FFFFFF; }
        """)

        base_layout = QHBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)

        # 1. ÁREA PRINCIPAL
        self.main_content = QWidget()
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.btn_toggle_drawer = QPushButton("  Personalizar Gráfico")
        self.btn_toggle_drawer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_drawer.setStyleSheet("""
            QPushButton { background-color: #FFFFFF; color: #0F172A; font-weight: bold; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #F1F5F9; }
        """)
        
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.tabs, stretch=1)
        self.build_dynamic_tabs()
        base_layout.addWidget(self.main_content, stretch=1)

        # 2. BARRA LATERAL DIREITA
        self.right_sidebar = QFrame()
        self.right_sidebar.setFixedWidth(280)
        self.right_sidebar.setStyleSheet("QFrame { background-color: #FFFFFF; border-left: 1px solid #E2E8F0; }")
        rs_layout = QVBoxLayout(self.right_sidebar)
        rs_layout.setContentsMargins(15, 20, 15, 20)
        
        rs_title = QLabel("Configuração de Análise")
        rs_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; border: none;")
        rs_layout.addWidget(rs_title)

        self.toolbox = QToolBox()
        self.toolbox.setStyleSheet("border: none;")
        
        self.page_cases = QWidget()
        page_cases_layout = QVBoxLayout(self.page_cases)
        page_cases_layout.setContentsMargins(5, 10, 5, 10)
        
        self.scroll_cases = QScrollArea()
        self.scroll_cases.setWidgetResizable(True)
        self.cases_container = QWidget()
        self.cases_layout = QVBoxLayout(self.cases_container)
        self.cases_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_cases.setWidget(self.cases_container)
        page_cases_layout.addWidget(self.scroll_cases)
        self.toolbox.addItem(self.page_cases, "1. Casos em Funcionamento")

        self.page_granularity = QWidget()
        page_gran_layout = QVBoxLayout(self.page_granularity)
        page_gran_layout.setContentsMargins(5, 10, 5, 10)
        
        self.gran_group = QButtonGroup(self)
        self.rad_global = QRadioButton("Global")
        self.rad_region = QRadioButton("Por Região")
        self.rad_bus = QRadioButton("Por Barramento")
        self.rad_global.setChecked(True)
        
        self.gran_group.addButton(self.rad_global, 1)
        self.gran_group.addButton(self.rad_region, 2)
        self.gran_group.addButton(self.rad_bus, 3)
        
        page_gran_layout.addWidget(self.rad_global)
        page_gran_layout.addWidget(self.rad_region)
        page_gran_layout.addWidget(self.rad_bus)
        page_gran_layout.addStretch()
        self.toolbox.addItem(self.page_granularity, "2. Nível de Granularidade")

        rs_layout.addWidget(self.toolbox)
        base_layout.addWidget(self.right_sidebar)

        # 3. DRAWER (PERSONALIZAR GRÁFICO)
        self.setup_drawer()
        base_layout.addWidget(self.drawer)

    def build_dynamic_tabs(self):
        self.tabs.clear()
        config = self.settings_vm.load_settings()

        if config.get("analise_confiabilidade", True):
            self.tab_table = QWidget()
            self.setup_table_tab()
            self.tabs.addTab(self.tab_table, "Tabela de Dados")

            self.tab_bar = QWidget()
            self.setup_bar_tab()
            self.tabs.addTab(self.tab_bar, "Gráfico de Comparação")

            self.tab_simple_chart = QWidget()
            self.setup_simple_chart_tab()
            self.tabs.addTab(self.tab_simple_chart, "Gráfico Simples")
            
            self.tab_ens = QWidget()
            self.setup_ens_tab()
            self.tabs.addTab(self.tab_ens, "Análise ENS")

    def setup_drawer(self):
        self.drawer = QFrame()
        self.drawer.setFixedWidth(320)
        self.drawer.setStyleSheet("QFrame { background-color: #FFFFFF; border-left: 1px solid #E2E8F0; }")
        self.drawer.hide()

        drawer_layout = QVBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(20, 20, 20, 20)

        d_header = QHBoxLayout()
        d_title = QLabel("Personalizar Exibição")
        d_title.setStyleSheet("font-size: 16px; font-weight: 800; border: none;")
        self.btn_close_drawer = QPushButton("✕")
        self.btn_close_drawer.setFixedSize(24, 24)
        self.btn_close_drawer.clicked.connect(self.toggle_drawer)
        d_header.addWidget(d_title)
        d_header.addStretch()
        d_header.addWidget(self.btn_close_drawer)
        drawer_layout.addLayout(d_header)

        d_scroll = QScrollArea()
        d_scroll.setWidgetResizable(True)
        d_container = QWidget()
        d_inner = QVBoxLayout(d_container)
        
        self.chk_show_titles = QCheckBox("Exibir título de cada barra")
        self.chk_show_titles.setChecked(True)
        self.chk_show_units = QCheckBox("Exibir Unidades (MW, MWh, etc)")
        self.chk_show_units.setChecked(True)
        self.combo_grid = QComboBox()
        self.combo_grid.addItems(["Horizontais", "Nenhuma", "Horizontais e Verticais"])
        
        d_inner.addWidget(self.chk_show_titles)
        d_inner.addWidget(self.chk_show_units)
        d_inner.addWidget(QLabel("Linhas de Grade:"))
        d_inner.addWidget(self.combo_grid)
        d_inner.addStretch()

        d_scroll.setWidget(d_container)
        drawer_layout.addWidget(d_scroll)
        
        self.btn_apply = QPushButton("Aplicar Configurações")
        self.btn_apply.clicked.connect(self.plot_all_charts)
        drawer_layout.addWidget(self.btn_apply)

    def toggle_drawer(self):
        self.drawer.setVisible(not self.drawer.isVisible())

    def open_filter_dialog(self):
        if not self.current_data: return
        all_elements = [el.get("element_name") for el in self.current_data.get("elements", [])]
        dialog = ElementFilterDialog(all_elements, self.active_elements_filter, self)
        if dialog.exec():
            self.active_elements_filter = dialog.get_selected_elements()
            self.plot_all_charts()

    # =========================================================================
    # SETUP DE SUBJANELAS (TABS)
    # =========================================================================
    def setup_table_tab(self):
        layout = QVBoxLayout(self.tab_table)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("<b>Filtro de Indicador:</b>"))
        self.combo_table_filter = QComboBox()
        self.combo_table_filter.addItem("Todos os Indicadores")
        self.combo_table_filter.currentIndexChanged.connect(self.update_table_view)
        filter_layout.addWidget(self.combo_table_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; background-color: #FFFFFF; }")
        layout.addWidget(self.table)

    def setup_bar_tab(self):
        layout = QVBoxLayout(self.tab_bar)
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("<b>Barras:</b>"))
        self.combo_ind_bar = QComboBox()
        controls_layout.addWidget(self.combo_ind_bar)
        
        controls_layout.addWidget(QLabel("<b>Linhas:</b>"))
        self.combo_ind_line = QComboBox()
        controls_layout.addWidget(self.combo_ind_line)
        
        controls_layout.addWidget(QLabel("<b>Ordenar Por:</b>"))
        self.combo_sort_bar = QComboBox()
        self.combo_sort_bar.addItems(["Padrão", "Crescente (Barras)", "Decrescente (Barras)"])
        controls_layout.addWidget(self.combo_sort_bar)
        
        # Botão Filtro de Elementos
        self.btn_filter_compare = QPushButton()
        self.btn_filter_compare.setIcon(QIcon("ui/widgets/filter.png"))
        self.btn_filter_compare.setToolTip("Filtrar Elementos")
        self.btn_filter_compare.clicked.connect(self.open_filter_dialog)
        controls_layout.addWidget(self.btn_filter_compare)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.bar_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_ax = self.bar_figure.add_subplot(111)
        self.bar_ax2 = None 
        layout.addWidget(self.bar_canvas)

    def setup_simple_chart_tab(self):
        layout = QVBoxLayout(self.tab_simple_chart)
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("<b>Indicador Único:</b>"))
        self.combo_ind_simple = QComboBox()
        self.combo_ind_simple.currentIndexChanged.connect(self.plot_simple_chart)
        controls_layout.addWidget(self.combo_ind_simple)
        
        # Botão Filtro de Elementos
        self.btn_filter_simple = QPushButton()
        self.btn_filter_simple.setIcon(QIcon("ui/widgets/filter.png"))
        self.btn_filter_simple.setToolTip("Filtrar Elementos")
        self.btn_filter_simple.clicked.connect(self.open_filter_dialog)
        controls_layout.addWidget(self.btn_filter_simple)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.simple_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.simple_canvas = FigureCanvas(self.simple_figure)
        self.simple_ax = self.simple_figure.add_subplot(111)
        layout.addWidget(self.simple_canvas)

    def setup_ens_tab(self):
        layout = QVBoxLayout(self.tab_ens)
        
        controls_layout = QHBoxLayout()
        
        # Tipo de Gráfico
        self.ens_type_group = QButtonGroup(self)
        self.rad_ens_col = QRadioButton("Gráfico de Colunas")
        self.rad_ens_line = QRadioButton("Gráfico de Linhas")
        self.rad_ens_line.setChecked(True)
        self.ens_type_group.addButton(self.rad_ens_col)
        self.ens_type_group.addButton(self.rad_ens_line)
        self.ens_type_group.buttonClicked.connect(self.plot_ens_chart)
        
        controls_layout.addWidget(self.rad_ens_col)
        controls_layout.addWidget(self.rad_ens_line)
        controls_layout.addSpacing(15)
        
        # NOVO: Seleção da Série ENS
        controls_layout.addWidget(QLabel("<b>Série:</b>"))
        self.combo_ens_series = QComboBox()
        self.combo_ens_series.addItems(["Mista (G&T)", "Geração", "Transmissão"])
        self.combo_ens_series.currentIndexChanged.connect(self.plot_ens_chart)
        controls_layout.addWidget(self.combo_ens_series)
        controls_layout.addSpacing(15)
        
        # Granularidade Temporal
        controls_layout.addWidget(QLabel("<b>Granularidade:</b>"))
        self.combo_ens_granularity = QComboBox()
        self.combo_ens_granularity.addItems(["Horas", "Semanas", "Meses"])
        self.combo_ens_granularity.currentIndexChanged.connect(self.update_ens_spinboxes)
        controls_layout.addWidget(self.combo_ens_granularity)
        controls_layout.addSpacing(15)
        
        # Intervalos
        controls_layout.addWidget(QLabel("<b>Intervalo:</b>"))
        self.spin_ens_min = QSpinBox()
        self.spin_ens_min.setRange(0, HOURS_IN_YEAR)
        self.spin_ens_min.setValue(0)
        
        controls_layout.addWidget(QLabel("até"))
        
        self.spin_ens_max = QSpinBox()
        self.spin_ens_max.setRange(0, HOURS_IN_YEAR)
        self.spin_ens_max.setValue(24)
        
        self.spin_ens_min.valueChanged.connect(self.plot_ens_chart)
        self.spin_ens_max.valueChanged.connect(self.plot_ens_chart)
        
        controls_layout.addWidget(self.spin_ens_min)
        controls_layout.addWidget(self.spin_ens_max)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.ens_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.ens_canvas = FigureCanvas(self.ens_figure)
        self.ens_ax = self.ens_figure.add_subplot(111)
        layout.addWidget(self.ens_canvas)

    # =========================================================================
    # LÓGICA E CONEXÕES
    # =========================================================================
    def setup_connections(self):
        if hasattr(self.viewmodel, 'cases_list_ready'):
            self.viewmodel.cases_list_ready.connect(self.populate_cases_list)
        if hasattr(self.viewmodel, 'comparison_data_ready'):
            self.viewmodel.comparison_data_ready.connect(self.render_real_data)
        if hasattr(self.viewmodel, 'time_series_data_ready'):
            self.viewmodel.time_series_data_ready.connect(self.render_ens_data)
        
        self.gran_group.buttonClicked.connect(self.run_comparison)
        self.combo_ind_bar.currentIndexChanged.connect(self.plot_bar)
        self.combo_ind_line.currentIndexChanged.connect(self.plot_bar)
        self.combo_sort_bar.currentIndexChanged.connect(self.plot_bar)

    def load_data(self):
        if hasattr(self.viewmodel, 'load_available_cases'):
            self.viewmodel.load_available_cases()

    def populate_cases_list(self, cases: list):
        for i in reversed(range(self.cases_layout.count())): 
            self.cases_layout.itemAt(i).widget().setParent(None)

        for case in cases:
            if case.get("status", "") == "READY":
                cb = QCheckBox(f"{case.get('external_name', '')} - {case.get('display_name', '')}")
                cb.setProperty("case_id", case.get("id"))
                cb.stateChanged.connect(self.run_comparison)
                self.cases_layout.addWidget(cb)

    def get_selected_granularity(self):
        if self.rad_global.isChecked(): return "GLOBAL"
        if self.rad_region.isChecked(): return "REGION"
        return "BUS"

    def run_comparison(self):
        selected_ids = []
        selected_names = []
        
        for i in range(self.cases_layout.count()):
            cb = self.cases_layout.itemAt(i).widget()
            if isinstance(cb, QCheckBox) and cb.isChecked():
                selected_ids.append(cb.property("case_id"))
                selected_names.append(cb.text())

        if not selected_ids: return 

        self.case_ids_cache = selected_ids
        self.case_names_cache = selected_names
            
        gran_api = self.get_selected_granularity()
        self.viewmodel.fetch_multi_case_data(selected_ids, gran_api, "ALL")
        
        # Pede os dados de ENS temporal simultaneamente
        if hasattr(self.viewmodel, 'fetch_time_series_data'):
            self.viewmodel.fetch_time_series_data(selected_ids)

    def render_real_data(self, response_data: dict):
        self.current_data = response_data
        indicadores = response_data.get("indicators", [])
        elements = response_data.get("elements", [])
        
        # Inicializa todos os elementos como ativos no filtro padrão
        self.active_elements_filter = [el.get("element_name") for el in elements]
        
        if not indicadores: return

        for combo in [self.combo_table_filter, self.combo_ind_bar, self.combo_ind_line, self.combo_ind_simple]:
            combo.blockSignals(True)
            if combo == self.combo_table_filter:
                combo.clear()
                combo.addItem("Todos os Indicadores")
            else:
                combo.clear()
            combo.addItems(indicadores)
            combo.blockSignals(False)

        if len(indicadores) > 1:
            self.combo_ind_line.blockSignals(True)
            self.combo_ind_line.setCurrentIndex(1)
            self.combo_ind_line.blockSignals(False)

        self.update_table_view()
        self.plot_all_charts()

    def render_ens_data(self, ts_data: dict):
        # Callback para a chamada do ViewModel quando ele retornar os dados JSON de ENS
        self.current_ts_data = ts_data
        self.plot_ens_chart()

    def update_table_view(self):
        if not self.current_data: return
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_tabelas", 2)
        
        indicadores_completos = self.current_data.get("indicators", [])
        unidades = self.current_data.get("units", {})
        
        # Tabela respeita o filtro
        elements = [el for el in self.current_data.get("elements", []) if el.get("element_name") in self.active_elements_filter]
        
        selected_ind = self.combo_table_filter.currentText()
        indicadores = indicadores_completos if selected_ind == "Todos os Indicadores" else [selected_ind]

        self.table.clear()
        headers = ["Elemento", "Indicador", "Unidade"] + self.case_names_cache
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(elements) * len(indicadores))
        
        row_idx = 0
        for el in elements:
            vals_by_case = el.get("values_by_case", {})
            for ind in indicadores:
                self.table.setItem(row_idx, 0, QTableWidgetItem(el.get("element_name", "N/A")))
                self.table.setItem(row_idx, 1, QTableWidgetItem(ind))
                self.table.setItem(row_idx, 2, QTableWidgetItem(unidades.get(ind, "")))
                
                for col_idx, case_id in enumerate(self.case_ids_cache):
                    val = vals_by_case.get(case_id, {}).get(ind)
                    val_str = "-" if val is None else f"{val:.{decimais}f}"
                    self.table.setItem(row_idx, 3 + col_idx, QTableWidgetItem(val_str))
                row_idx += 1

    def plot_all_charts(self):
        self.plot_bar()
        self.plot_simple_chart()
        self.plot_ens_chart()

    def plot_bar(self):
        if not self.current_data: return
        
        self.bar_figure.clear()
        self.bar_ax = self.bar_figure.add_subplot(111)
        self.bar_ax2 = self.bar_ax.twinx() 
        
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_grafico", 2)
        mostrar_unidades = self.chk_show_units.isChecked()
        grid_style = self.combo_grid.currentText()
        
        ind_bar = self.combo_ind_bar.currentText()
        ind_line = self.combo_ind_line.currentText()
        if not ind_bar or not ind_line: return

        # Filtrar elementos baseados no popup
        elements = [el for el in self.current_data.get("elements", []) if el.get("element_name") in self.active_elements_filter]
        if not elements: 
            self.bar_canvas.draw()
            return
        
        sort_mode = self.combo_sort_bar.currentText()
        if "Crescente" in sort_mode: 
            elements.sort(key=lambda x: np.mean([x.get("values_by_case", {}).get(c, {}).get(ind_bar, 0.0) or 0.0 for c in self.case_ids_cache]))
        elif "Decrescente" in sort_mode: 
            elements.sort(key=lambda x: np.mean([x.get("values_by_case", {}).get(c, {}).get(ind_bar, 0.0) or 0.0 for c in self.case_ids_cache]), reverse=True)

        n_cases = len(self.case_ids_cache)
        element_names = [el.get("element_name", "") for el in elements]
        x = np.arange(len(element_names))
        width = 0.8 / n_cases if n_cases > 0 else 0.8
            
        for c, case_id in enumerate(self.case_ids_cache):
            color = self.chart_colors[c % len(self.chart_colors)]
            offset = (c - n_cases/2 + 0.5) * width
            
            vals_bar = [el.get("values_by_case", {}).get(case_id, {}).get(ind_bar) or 0.0 for el in elements]
            vals_bar = [round(v, decimais) for v in vals_bar]
            self.bar_ax.bar(x + offset, vals_bar, width, label=f"{self.case_names_cache[c]} (Barras)", color=color, alpha=0.7, edgecolor='white', linewidth=0.5)

            vals_line = [el.get("values_by_case", {}).get(case_id, {}).get(ind_line) or 0.0 for el in elements]
            vals_line = [round(v, decimais) for v in vals_line]
            self.bar_ax2.plot(x + offset, vals_line, marker='o', color=color, linewidth=2, label=f"{self.case_names_cache[c]} (Linhas)")

        if self.chk_show_titles.isChecked():
            self.bar_ax.set_xticks(x)
            self.bar_ax.set_xticklabels(element_names, rotation=45, ha='right')
        else:
            self.bar_ax.set_xticks([])
            
        unidade_bar = self.current_data.get("units", {}).get(ind_bar, "") if mostrar_unidades else ""
        unidade_line = self.current_data.get("units", {}).get(ind_line, "") if mostrar_unidades else ""
        
        self.bar_ax.set_ylabel(f"{ind_bar} {f'({unidade_bar})' if unidade_bar else ''}", fontweight='bold', color='#475569')
        self.bar_ax2.set_ylabel(f"{ind_line} {f'({unidade_line})' if unidade_line else ''}", fontweight='bold', color='#0F172A')
        self.bar_ax.set_title(f"{ind_bar} vs {ind_line}", pad=15, fontweight='bold')
        
        if grid_style == "Horizontais": self.bar_ax.grid(axis='y', linestyle='--', alpha=0.4)
        elif grid_style == "Horizontais e Verticais": self.bar_ax.grid(True, linestyle='--', alpha=0.4)
            
        self.bar_ax.spines['top'].set_visible(False)
        self.bar_ax2.spines['top'].set_visible(False)
        
        h1, l1 = self.bar_ax.get_legend_handles_labels()
        h2, l2 = self.bar_ax2.get_legend_handles_labels()
        self.bar_ax2.legend(h1+h2, l1+l2, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=9, edgecolor='#CBD5E1', framealpha=0.9)
        self.bar_figure.subplots_adjust(right=0.75, bottom=0.25)
        self.bar_canvas.draw()

    def plot_simple_chart(self):
        if not self.current_data: return
        self.simple_figure.clear()
        self.simple_ax = self.simple_figure.add_subplot(111)
        
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_grafico", 2)
        
        ind = self.combo_ind_simple.currentText()
        if not ind: return

        # Filtrar elementos
        elements = [el for el in self.current_data.get("elements", []) if el.get("element_name") in self.active_elements_filter]
        if not elements: 
            self.simple_canvas.draw()
            return
            
        n_cases = len(self.case_ids_cache)
        element_names = [el.get("element_name", "") for el in elements]
        x = np.arange(len(element_names))
        width = 0.8 / n_cases if n_cases > 0 else 0.8

        for c, case_id in enumerate(self.case_ids_cache):
            color = self.chart_colors[c % len(self.chart_colors)]
            offset = (c - n_cases/2 + 0.5) * width
            
            vals = [el.get("values_by_case", {}).get(case_id, {}).get(ind) or 0.0 for el in elements]
            vals = [round(v, decimais) for v in vals]
            self.simple_ax.bar(x + offset, vals, width, label=self.case_names_cache[c], color=color, edgecolor='white', linewidth=0.5)

        if self.chk_show_titles.isChecked():
            self.simple_ax.set_xticks(x)
            self.simple_ax.set_xticklabels(element_names, rotation=45, ha='right')
        else:
            self.simple_ax.set_xticks([])
            
        unidade = self.current_data.get("units", {}).get(ind, "")
        self.simple_ax.set_ylabel(f"{ind} {f'({unidade})' if unidade else ''}", fontweight='bold')
        self.simple_ax.set_title(f"Visualização de {ind}", pad=15, fontweight='bold')
        self.simple_ax.spines['top'].set_visible(False)
        self.simple_ax.spines['right'].set_visible(False)
        self.simple_ax.grid(axis='y', linestyle='--', alpha=0.4)
        
        self.simple_ax.legend(loc='upper right')
        self.simple_figure.subplots_adjust(bottom=0.25)
        self.simple_canvas.draw()

    def update_ens_spinboxes(self):
        gran = self.combo_ens_granularity.currentText()
        self.spin_ens_min.blockSignals(True)
        self.spin_ens_max.blockSignals(True)
        
        if gran == "Horas":
            self.spin_ens_min.setRange(0, HOURS_IN_YEAR)
            self.spin_ens_max.setRange(0, HOURS_IN_YEAR)
            self.spin_ens_max.setValue(24)
        elif gran == "Semanas":
            self.spin_ens_min.setRange(0, WEEKS_IN_YEAR)
            self.spin_ens_max.setRange(0, WEEKS_IN_YEAR)
            self.spin_ens_max.setValue(WEEKS_IN_YEAR)
        elif gran == "Meses":
            self.spin_ens_min.setRange(0, MONTHS_IN_YEAR)
            self.spin_ens_max.setRange(0, MONTHS_IN_YEAR)
            self.spin_ens_max.setValue(MONTHS_IN_YEAR)
            
        self.spin_ens_min.setValue(0)
        
        self.spin_ens_min.blockSignals(False)
        self.spin_ens_max.blockSignals(False)
        self.plot_ens_chart()

    def plot_ens_chart(self):
        """ Renderiza o gráfico de ENS adaptado ao intervalo, granularidade e tipo de série. """
        self.ens_figure.clear()
        self.ens_ax = self.ens_figure.add_subplot(111)
        
        if not self.current_ts_data: 
            self.ens_ax.text(0.5, 0.5, "Aguardando dados da simulação...", ha='center', va='center')
            self.ens_canvas.draw()
            return

        min_val = self.spin_ens_min.value()
        max_val = self.spin_ens_max.value()
        if min_val >= max_val: return
        
        gran = self.combo_ens_granularity.currentText()
        is_line = self.rad_ens_line.isChecked()
        
        # Mapeamento do número de agregamentos. O DB é sempre horario.
        bucket_size = 1
        if gran == "Semanas": bucket_size = HOURS_IN_YEAR // WEEKS_IN_YEAR
        elif gran == "Meses": bucket_size = HOURS_IN_YEAR // MONTHS_IN_YEAR
        
        # NOVO: Define qual chave de dados buscar no dicionário do ViewModel
        series_map = {
            "Mista (G&T)": "ens_array",
            "Geração": "geracao",
            "Transmissão": "transmissao"
        }
        selected_series = self.combo_ens_series.currentText()
        data_key = series_map.get(selected_series, "ens_array")
        
        n_cases = len(self.case_ids_cache)
        width = 0.8 / n_cases if n_cases > 0 else 0.8

        plotted = False
        for c, case_id in enumerate(self.case_ids_cache):
            color = self.chart_colors[c % len(self.chart_colors)]
            
            # Puxa a série dinamicamente baseada na escolha do usuário
            raw_data = self.current_ts_data.get(str(case_id), {}).get(data_key, [])
            
            if not raw_data:
                # Preenchimento temporário se o ViewModel não tiver carregado a série
                raw_data = np.random.uniform(0, 50, HOURS_IN_YEAR) 
                
            raw_data = np.array(raw_data)
            
            # Agregação de tempo (Soma)
            if bucket_size > 1:
                trunc_len = (len(raw_data) // bucket_size) * bucket_size
                agg_data = raw_data[:trunc_len].reshape(-1, bucket_size).sum(axis=1)
            else:
                agg_data = raw_data
                
            # Aplicar filtro de intervalo
            filtered_data = agg_data[min_val:max_val]
            x_vals = np.arange(min_val, min_val + len(filtered_data))
            
            if is_line:
                self.ens_ax.plot(x_vals, filtered_data, marker='o' if len(filtered_data) < 50 else None, color=color, linewidth=2, label=self.case_names_cache[c])
            else:
                offset = (c - n_cases/2 + 0.5) * width
                self.ens_ax.bar(x_vals + offset, filtered_data, width, color=color, label=self.case_names_cache[c])
            plotted = True

        if plotted:
            self.ens_ax.set_title(f"Energy Not Supplied (ENS) - {selected_series}", pad=15, fontweight='bold')
            self.ens_ax.set_xlabel(f"Tempo ({gran})", fontweight='bold')
            self.ens_ax.set_ylabel("MWh", fontweight='bold')
            self.ens_ax.spines['top'].set_visible(False)
            self.ens_ax.spines['right'].set_visible(False)
            self.ens_ax.grid(axis='y', linestyle='--', alpha=0.4)
            self.ens_ax.legend()

        self.ens_figure.tight_layout()
        self.ens_canvas.draw()
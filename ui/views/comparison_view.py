import uuid
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, 
    QListWidget, QListWidgetItem, QTabWidget, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt

# Integração do Matplotlib com PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.services.settings_service import SettingsService
from ui.viewmodels.comparison_viewmodel import ComparisonViewModel

class ComparisonView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = ComparisonViewModel()
        self.settings = SettingsService.get_instance()
        self.cases_mapping = {}
        self.current_data = {}
        self.case_ids_cache = []
        self.case_names_cache = []
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("Comparative Analysis Laboratory")
        title.setStyleSheet("font-family: Arial; font-size: 22px; font-weight: bold; color: #0F172A;")
        main_layout.addWidget(title)

        # ==========================================
        # PAINEL SUPERIOR: CONTROLES E FILTROS (25% Height)
        # ==========================================
        control_panel = QGroupBox("Analysis Configuration (Max 5 Cases)")
        control_panel.setStyleSheet("QGroupBox { font-family: Arial; font-weight: bold; color: #334155; border: 1px solid #E2E8F0; border-radius: 6px; padding-top: 15px; }")
        control_layout = QHBoxLayout(control_panel)

        # 1. Seletor de Casos
        cases_layout = QVBoxLayout()
        cases_layout.addWidget(QLabel("Select Base Cases:"))
        self.list_cases = QListWidget()
        self.list_cases.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 4px; background-color: #FFFFFF; font-family: Arial; font-weight: normal;")
        cases_layout.addWidget(self.list_cases)
        control_layout.addLayout(cases_layout, stretch=2)

        # 2. Seletor de Granularidade
        granularity_layout = QVBoxLayout()
        granularity_layout.addWidget(QLabel("Granularity Level:"))
        self.combo_granularity = QComboBox()
        self.combo_granularity.addItems(["Global", "By Region", "By Bus"])
        self.combo_granularity.setFixedHeight(30)
        granularity_layout.addWidget(self.combo_granularity)
        
        granularity_layout.addWidget(QLabel("Filter Element:"))
        self.combo_element = QComboBox()
        self.combo_element.addItem("System Wide (All)")
        self.combo_element.setFixedHeight(30)
        granularity_layout.addWidget(self.combo_element)
        control_layout.addLayout(granularity_layout, stretch=1)

        # 3. Botão de Ação
        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        self.btn_compare = QPushButton("Generate Comparison")
        self.btn_compare.setFixedHeight(45)
        self.btn_compare.setStyleSheet("""
            QPushButton { background-color: #2563EB; color: white; font-weight: bold; font-family: Arial; font-size: 14px; border-radius: 6px; }
            QPushButton:hover { background-color: #1D4ED8; }
            QPushButton:disabled { background-color: #94A3B8; }
        """)
        btn_layout.addWidget(self.btn_compare)
        control_layout.addLayout(btn_layout, stretch=1)

        # Define proporção de 20% / 80% na tela usando stretch
        main_layout.addWidget(control_panel, stretch=1)

        # ==========================================
        # PAINEL INFERIOR: ABAS DE RESULTADOS (75% Height)
        # ==========================================
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; background-color: #FFFFFF; border-radius: 6px;}
            QTabBar::tab { background: #F8FAFC; color: #334155; padding: 10px 20px; font-family: Arial; font-weight: bold; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px;}
            QTabBar::tab:selected { background: #FFFFFF; color: #2563EB; border-top: 3px solid #2563EB; }
        """)

        self.tab_table = QWidget()
        self.setup_table_tab()
        self.tabs.addTab(self.tab_table, "Data Table")

        self.tab_scatter = QWidget()
        self.setup_scatter_tab()
        self.tabs.addTab(self.tab_scatter, "Scatter Plot")

        self.tab_bar = QWidget()
        self.setup_bar_tab()
        self.tabs.addTab(self.tab_bar, "Grouped Bar Chart")

        main_layout.addWidget(self.tabs, stretch=4)

    # ---------------------------------------------------------
    # SETUP DAS ABAS INTERNAS
    # ---------------------------------------------------------
    def setup_table_tab(self):
        layout = QVBoxLayout(self.tab_table)
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setStyleSheet("""
            QTableWidget { border: none; background-color: #FFFFFF; alternate-background-color: #F8FAFC; font-family: Arial; color: #0F172A; }
            QHeaderView::section { background-color: #334155; color: white; font-weight: bold; padding: 8px; border: none; border-bottom: 2px solid #2563EB;}
            QTableWidget::item { border-bottom: 1px solid #E2E8F0; padding: 5px; }
        """)
        layout.addWidget(self.table)

    def setup_scatter_tab(self):
        layout = QVBoxLayout(self.tab_scatter)
        control_row = QHBoxLayout()
        control_row.addWidget(QLabel("X-Axis Indicator:"))
        self.combo_x = QComboBox()
        control_row.addWidget(self.combo_x)
        control_row.addSpacing(20)
        control_row.addWidget(QLabel("Y-Axis Indicator:"))
        self.combo_y = QComboBox()
        control_row.addWidget(self.combo_y)
        control_row.addStretch()
        layout.addLayout(control_row)

        self.scatter_figure = Figure(figsize=(5, 4), dpi=100)
        self.scatter_canvas = FigureCanvas(self.scatter_figure)
        self.scatter_ax = self.scatter_figure.add_subplot(111)
        layout.addWidget(self.scatter_canvas)

    def setup_bar_tab(self):
        layout = QVBoxLayout(self.tab_bar)
        control_row = QHBoxLayout()
        control_row.addWidget(QLabel("Indicator to Analyze:"))
        self.combo_bar_ind = QComboBox()
        control_row.addWidget(self.combo_bar_ind)
        control_row.addSpacing(20)
        
        # Checkbox para a Curva de Pareto
        self.chk_pareto = QCheckBox("Overlay Pareto Curve (85%)")
        self.chk_pareto.setChecked(False)
        control_row.addWidget(self.chk_pareto)
        
        control_row.addStretch()
        layout.addLayout(control_row)

        self.bar_figure = Figure(figsize=(5, 4), dpi=100)
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_ax = self.bar_figure.add_subplot(111)
        self.pareto_ax = None # Eixo secundário para o Pareto
        layout.addWidget(self.bar_canvas)

    # ---------------------------------------------------------
    # CONEXÕES E LÓGICA
    # ---------------------------------------------------------
    def setup_connections(self):
        if hasattr(self.viewmodel, 'cases_list_ready'):
            self.viewmodel.cases_list_ready.connect(self.populate_cases_list)
        elif hasattr(self.viewmodel, 'cases_loaded'):
            self.viewmodel.cases_loaded.connect(self.populate_cases_list)
            
        # === CORREÇÃO CRÍTICA AQUI: Conectando a resposta do ViewModel à View ===
        if hasattr(self.viewmodel, 'comparison_data_ready'):
            self.viewmodel.comparison_data_ready.connect(self.render_real_data)

        if hasattr(self.viewmodel, 'error_occurred'):
            self.viewmodel.error_occurred.connect(self.handle_error)

        self.list_cases.itemChanged.connect(self.enforce_max_cases)
        self.combo_granularity.currentTextChanged.connect(self.on_granularity_changed)
        self.btn_compare.clicked.connect(self.run_comparison)
        
        self.combo_x.currentIndexChanged.connect(self.plot_scatter)
        self.combo_y.currentIndexChanged.connect(self.plot_scatter)
        self.combo_bar_ind.currentIndexChanged.connect(self.plot_bar)
        self.chk_pareto.stateChanged.connect(self.plot_bar)

    def load_data(self):
        if hasattr(self.viewmodel, 'load_available_cases'):
            self.viewmodel.load_available_cases()
        elif hasattr(self.viewmodel, 'load_cases'):
            self.viewmodel.load_cases()

    def populate_cases_list(self, cases: list):
        self.list_cases.blockSignals(True)
        self.list_cases.clear()
        for case in cases:
            if case.get("status", "") == "READY":
                display_text = f"{case.get('external_name', '')} - {case.get('display_name', '')}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, case.get("id"))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.list_cases.addItem(item)
        self.list_cases.blockSignals(False)

    def enforce_max_cases(self, item):
        checked_items = [self.list_cases.item(i) for i in range(self.list_cases.count()) if self.list_cases.item(i).checkState() == Qt.CheckState.Checked]
        if len(checked_items) > 5:
            QMessageBox.warning(self, "Limit Exceeded", "You can compare a maximum of 5 cases simultaneously.")
            item.setCheckState(Qt.CheckState.Unchecked)

    def on_granularity_changed(self, text):
        self.combo_element.clear()
        if text == "Global":
            self.combo_element.addItem("System Wide (All)")
            self.combo_element.setEnabled(False)
        else:
            self.combo_element.setEnabled(True)
            self.combo_element.addItem("System Wide (All Elements Grouped)")
            # TODO: Add specific regions or buses here

    def run_comparison(self):
        selected_ids = []
        selected_names = []
        for i in range(self.list_cases.count()):
            item = self.list_cases.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_ids.append(item.data(Qt.ItemDataRole.UserRole))
                selected_names.append(item.text())

        if len(selected_ids) < 2:
            QMessageBox.warning(self, "Notice", "Please select at least 2 cases for comparison.")
            return

        # Guarda as seleções na memória
        self.case_ids_cache = selected_ids
        self.case_names_cache = selected_names

        # Mapeia a granularidade visual para o backend
        granularity = self.combo_granularity.currentText()
        gran_map = {"Global": "GLOBAL", "By Region": "REGION", "By Bus": "BUS"}
        gran_api = gran_map.get(granularity, "GLOBAL")
        
        element = "ALL" # Fica como ALL por padrão (traz todos os elementos)

        self.btn_compare.setText("Loading...")
        self.btn_compare.setEnabled(False)
        
        # Dispara a busca no banco!
        self.viewmodel.fetch_multi_case_data(selected_ids, gran_api, element)

    def render_real_data(self, response_data: dict):
        """Recebe o JSON DTO do Backend e desempacota na tabela."""
        self.btn_compare.setText("Generate Comparison")
        self.btn_compare.setEnabled(True)
        self.current_data = response_data
        
        indicadores = response_data.get("indicators", [])
        unidades = response_data.get("units", {})
        elements = response_data.get("elements", [])

        if not elements or not indicadores:
            QMessageBox.information(self, "No Data", "Não há dados para esta configuração.")
            return

        # --- PREENCHE A TABELA DINÂMICA ---
        self.table.clear()
        headers = ["Element", "Indicator", "Unit"] + self.case_names_cache
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(elements) * len(indicadores))
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        row_idx = 0
        for el in elements:
            # 1. Elemento e Mesclagem (setSpan)
            el_name = el.get("element_name", "N/A")
            item_el = QTableWidgetItem(el_name)
            item_el.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_el = item_el.font()
            font_el.setBold(True)
            item_el.setFont(font_el)
            
            self.table.setItem(row_idx, 0, item_el)
            self.table.setSpan(row_idx, 0, len(indicadores), 1)
            
            vals_by_case = el.get("values_by_case", {})

            # 2. Indicadores e Valores
            for ind in indicadores:
                item_ind = QTableWidgetItem(ind)
                item_ind.setFont(font_el) # Negrito
                self.table.setItem(row_idx, 1, item_ind)
                
                item_unit = QTableWidgetItem(unidades.get(ind, ""))
                item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_unit.setForeground(Qt.GlobalColor.darkGray)
                self.table.setItem(row_idx, 2, item_unit)
                
                for col_idx, case_id in enumerate(self.case_ids_cache):
                    val = vals_by_case.get(case_id, {}).get(ind)
                    
                    if val is None:
                        val_str = "-"
                    else:
                        val_str = self.settings.format_number(val, is_table=True)

                    item_val = QTableWidgetItem(val_str)
                    item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, 3 + col_idx, item_val)
                    
                row_idx += 1

        # --- ATUALIZA COMBOBOXES DE GRÁFICOS ---
        self.combo_x.blockSignals(True)
        self.combo_y.blockSignals(True)
        self.combo_bar_ind.blockSignals(True)
        
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_bar_ind.clear()
        
        self.combo_x.addItems(indicadores)
        self.combo_y.addItems(indicadores)
        self.combo_bar_ind.addItems(indicadores)
        if len(indicadores) > 1: self.combo_y.setCurrentIndex(1)
        
        self.combo_x.blockSignals(False)
        self.combo_y.blockSignals(False)
        self.combo_bar_ind.blockSignals(False)

        # Chama os gráficos
        self.plot_scatter()
        self.plot_bar()

    def handle_error(self, message: str):
        """Destrava a tela e exibe o erro retornado pelo Backend."""
        self.btn_compare.setText("Generate Comparison")
        self.btn_compare.setEnabled(True)
        QMessageBox.critical(self, "Erro na Análise", message)

        
    def plot_scatter(self):
        ind_x = self.combo_x.currentText()
        ind_y = self.combo_y.currentText()
        if not ind_x or not ind_y or not self.current_data: return

        self.scatter_ax.clear()
        colors = ['#2563EB', '#0B1220', '#22C55E', '#EF4444', '#8B5CF6'] 
        elements = self.current_data.get("elements", [])

        # Para cada caso, plotamos todos os elementos mapeados (Global=1 ponto, Bus=Vários pontos)
        for i, case_id in enumerate(self.case_ids_cache):
            case_name = self.case_names_cache[i]
            color = colors[i % len(colors)]
            
            x_vals, y_vals = [], []
            for el in elements:
                vals = el.get("values_by_case", {}).get(case_id, {})
                v_x, v_y = vals.get(ind_x), vals.get(ind_y)
                if v_x is not None and v_y is not None:
                    x_vals.append(v_x)
                    y_vals.append(v_y)
                    
            if x_vals and y_vals:
                self.scatter_ax.scatter(x_vals, y_vals, s=120, color=color, label=case_name, alpha=0.8, edgecolors='white', linewidth=1.0)

        self.scatter_ax.set_title(f"Correlation: {ind_y} vs {ind_x}", pad=15, fontweight='bold', color='#0F172A')
        self.scatter_ax.set_xlabel(f"{ind_x} Value") 
        self.scatter_ax.set_ylabel(f"{ind_y} Value")
        self.scatter_ax.grid(True, linestyle='--', alpha=0.5)
        self.scatter_ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
        self.scatter_figure.tight_layout()
        self.scatter_canvas.draw()

    def plot_bar(self):
        ind = self.combo_bar_ind.currentText()
        if not ind or not self.current_data: return

        self.bar_ax.clear()
        if self.pareto_ax:
            self.pareto_ax.remove()
            self.pareto_ax = None

        colors = ['#2563EB', '#0B1220', '#22C55E', '#EF4444', '#8B5CF6']
        n_cases = len(self.case_ids_cache)
        elements = self.current_data.get("elements", [])
        
        if not elements: return

        element_names = [el.get("element_name", "") for el in elements]
        x = np.arange(len(element_names))
        width = 0.8 / n_cases
        data_matrix = [] 

        for c, case_id in enumerate(self.case_ids_cache):
            case_vals = []
            for el in elements:
                val = el.get("values_by_case", {}).get(case_id, {}).get(ind)
                case_vals.append(val if val is not None else 0.0)
            
            data_matrix.append(case_vals)
            offset = (c - n_cases/2 + 0.5) * width
            
            bars = self.bar_ax.bar(x + offset, case_vals, width, label=self.case_names_cache[c], color=colors[c], edgecolor='white', linewidth=1.0)
            
            # Anotações limpas e responsivas
            if len(elements) <= 15: # Evita poluição se houver centenas de barras
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        self.bar_ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#334155', rotation=90)

        self.bar_ax.set_xticks(x)
        self.bar_ax.set_xticklabels(element_names, rotation=45, ha='right', fontsize=8)
        self.bar_ax.legend(loc='upper right', fontsize=8)

        # Lógica da Curva de Pareto 85%
        if self.chk_pareto.isChecked():
            avgs = np.mean(np.array(data_matrix), axis=0)
            total = np.sum(avgs)
            if total > 0:
                cum_perc = np.cumsum(avgs) / total * 100
                self.pareto_ax = self.bar_ax.twinx()
                self.pareto_ax.plot(x, cum_perc, color='#F59E0B', marker='D', linewidth=2, markersize=5, label="Cumulative %")
                self.pareto_ax.set_ylabel("Cumulative %", color='#F59E0B')
                self.pareto_ax.tick_params(axis='y', labelcolor='#F59E0B')
                self.pareto_ax.set_ylim(0, 110)
                
                pareto_threshold = getattr(self.settings, 'pareto_threshold', 85.0)
                idx_85 = np.abs(cum_perc - pareto_threshold).argmin()
                self.pareto_ax.plot(x[idx_85], cum_perc[idx_85], marker='o', markersize=10, color='#EF4444')
                self.pareto_ax.annotate(f'{pareto_threshold}% Threshold', (x[idx_85], cum_perc[idx_85]), textcoords="offset points", xytext=(-10, 15), ha='right', color='#EF4444', fontweight='bold', fontsize=8)

        self.bar_ax.set_title(f"{ind} Distribution", pad=15, fontweight='bold', color='#0F172A')
        self.bar_ax.set_ylabel(f"{ind} Value")
        self.bar_ax.grid(axis='y', linestyle='--', alpha=0.5)
        self.bar_ax.spines['top'].set_visible(False)
        self.bar_ax.spines['right'].set_visible(False)
        
        self.bar_figure.tight_layout() 
        self.bar_canvas.draw()
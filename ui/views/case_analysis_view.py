import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QMessageBox, QSplitter, QSpinBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from ui.viewmodels.case_analysis_viewmodel import CaseAnalysisViewModel
from ui.viewmodels.settings_viewmodel import SettingsViewModel

from ui.views.tab_topology_view import TabTopologyView
from ui.views.tab_transmission_view import TabTransmissionView
from ui.views.tab_generation_view import TabGenerationView

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']


class CaseAnalysisView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = CaseAnalysisViewModel()
        self.settings_vm = SettingsViewModel()
        
        self.case_mapping = {}
        self.current_case_id = None
        self.loaded_geral_case_id = None
        self.current_geral_data = {}
        
        # Cores para gráficos (Tailwind base)
        self.chart_colors = ['#0EA5E9', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6']
        self.donut_colors = ['#F97316', '#3B82F6', '#10B981', '#8B5CF6', '#EAB308']
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setStyleSheet("""
        QWidget { font-family: "Segoe UI", Arial, sans-serif; color: #0F172A; background-color: #F8FAFC; font-weight: normal; }
        QComboBox { border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px 10px; background-color: #FFFFFF; font-size: 14px; font-weight: normal; }
        QComboBox:hover, QComboBox:focus { border: 1px solid #0284C7; }
        QSpinBox { border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px; background-color: #FFFFFF; font-weight: normal; }
        QSpinBox:hover, QSpinBox:focus { border: 1px solid #0284C7; }
        QTableWidget { border: 1px solid #E2E8F0; background-color: #FFFFFF; alternate-background-color: #F8FAFC;}
        QHeaderView::section { background-color: #F1F5F9; color: #334155; padding: 8px; border: none; border-bottom: 1px solid #CBD5E1; font-weight: normal; }
        QTabWidget::pane { border: 1px solid #E2E8F0; background-color: #FFFFFF; border-radius: 8px; border-top-left-radius: 0px;}
        QTabBar::tab { background: #E2E8F0; color: #64748B; padding: 10px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-weight: normal; }
        QTabBar::tab:selected { background: #FFFFFF; color: #0284C7; border-bottom: 2px solid #FFFFFF; border-top: 2px solid #0284C7;}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ==========================================
        # TOP BAR
        # ==========================================
        top_bar = QHBoxLayout()
        
        lbl_case = QLabel("Caso em Análise:")
        lbl_case.setStyleSheet("font-size: 16px; color: #1E293B;")
        
        self.combo_cases = QComboBox()
        self.combo_cases.setFixedWidth(500)
        self.combo_cases.setFixedHeight(35)
        self.combo_cases.addItem("Selecione um caso para analisar...")
        
        top_bar.addWidget(lbl_case)
        top_bar.addWidget(self.combo_cases)
        top_bar.addStretch()
        
        layout.addLayout(top_bar)

        # ==========================================
        # SISTEMA DE ABAS
        # ==========================================
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.build_dynamic_tabs()

    def build_dynamic_tabs(self):
        self.tabs.clear()
        config = self.settings_vm.load_settings()

        if config.get("analise_confiabilidade", True):
            self.tab_geral = QWidget()
            self.setup_tab_geral(self.tab_geral)
            self.tabs.addTab(self.tab_geral, "Visão Geral")
            
            self.tab_generation = TabGenerationView()
            self.tabs.addTab(self.tab_generation, "Geração")
            
            self.tab_transmission = TabTransmissionView()
            self.tabs.addTab(self.tab_transmission, "Transmissão")
            
        if config.get("analise_rede", False):
            self.tab_topology = TabTopologyView()
            self.tabs.addTab(self.tab_topology, "Topologia (Grafo)")

        if config.get("indicador_custo", False):
            self.tab_costs = QWidget()
            self.tab_costs.setLayout(QVBoxLayout())
            self.tab_costs.layout().addWidget(QLabel("Módulo de Custos e Finanças em construção..."))
            self.tabs.addTab(self.tab_costs, "Custos e Finanças")

        if config.get("indicador_carga", False):
            self.tab_load = QWidget()
            self.tab_load.setLayout(QVBoxLayout())
            self.tab_load.layout().addWidget(QLabel("Módulo de Análise de Carga em construção..."))
            self.tabs.addTab(self.tab_load, "Análise de Carga")

    # =========================================================
    # SETUP DA ABA "VISÃO GERAL"
    # =========================================================
    def setup_tab_geral(self, parent_widget):
        layout = QHBoxLayout(parent_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        splitter_main = QSplitter(Qt.Orientation.Horizontal)
        
        # ---------------------------------------------------------
        # PAINEL ESQUERDO (Scroll Area para as Tabelas)
        # ---------------------------------------------------------
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(20)
        
        # 1. Anos Simulados
        self.lbl_sim_years = QLabel("Anos Simulados: -")
        self.lbl_sim_years.setStyleSheet("font-size: 16px; color: #0284C7; padding: 5px;")
        left_layout.addWidget(self.lbl_sim_years)
        
        # 2. Tabela de Indicadores Globais
        lbl_global = QLabel("Indicadores Globais de Confiabilidade")
        lbl_global.setStyleSheet("font-size: 14px; color: #475569;")
        left_layout.addWidget(lbl_global)
        
        self.table_global = QTableWidget()
        self.table_global.setColumnCount(3)
        self.table_global.setHorizontalHeaderLabels(["Indicador", "Valor", "β"])
        self.table_global.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_global.setAlternatingRowColors(True)
        self.table_global.verticalHeader().setVisible(False)
        self.table_global.setFixedHeight(180) # Altura fixa para não ocupar a tela toda
        left_layout.addWidget(self.table_global)

        # 3. Tabela System Summary
        lbl_summary = QLabel("System Summary")
        lbl_summary.setStyleSheet("font-size: 14px; color: #475569;")
        left_layout.addWidget(lbl_summary)
        
        self.table_summary = QTableWidget()
        self.table_summary.setColumnCount(3)
        self.table_summary.setHorizontalHeaderLabels(["Parâmetro", "Valor", "Unidade"])
        self.table_summary.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_summary.setAlternatingRowColors(True)
        self.table_summary.verticalHeader().setVisible(False)
        self.table_summary.setMinimumHeight(250)
        left_layout.addWidget(self.table_summary)
        
        left_scroll.setWidget(left_panel)
        splitter_main.addWidget(left_scroll)
        
        # ---------------------------------------------------------
        # PAINEL DIREITO (Divisão Vertical: Rosquinha + Gráfico Distribuição)
        # ---------------------------------------------------------
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # PARTE SUPERIOR: Gráfico de Rosquinha
        donut_panel = QWidget()
        donut_layout = QVBoxLayout(donut_panel)
        donut_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_donut = QLabel("Capacidade por Tecnologia (Generating Units)")
        lbl_donut.setStyleSheet("font-size: 14px; color: #475569; padding-bottom: 5px;")
        donut_layout.addWidget(lbl_donut)
        
        self.donut_figure = Figure(figsize=(4, 3), dpi=100, facecolor='#FFFFFF')
        self.donut_canvas = FigureCanvas(self.donut_figure)
        self.donut_ax = self.donut_figure.add_subplot(111)
        donut_layout.addWidget(self.donut_canvas)
        
        right_splitter.addWidget(donut_panel)
        
        # PARTE INFERIOR: Gráfico de Elementos
        dist_panel = QWidget()
        dist_layout = QVBoxLayout(dist_panel)
        dist_layout.setContentsMargins(0, 10, 0, 0)
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Indicador:"))
        
        self.combo_geral_ind = QComboBox()
        self.combo_geral_ind.currentIndexChanged.connect(self.plot_geral_chart)
        controls_layout.addWidget(self.combo_geral_ind)
        controls_layout.addSpacing(15)
        
        controls_layout.addWidget(QLabel("Máx Elementos:"))
        self.spin_max_elements = QSpinBox()
        self.spin_max_elements.setRange(5, 10000)
        self.spin_max_elements.setValue(50)
        self.spin_max_elements.valueChanged.connect(self.plot_geral_chart)
        controls_layout.addWidget(self.spin_max_elements)
        controls_layout.addSpacing(15)
        
        self.chk_pareto = QCheckBox("Exibir Curva de Pareto")
        self.chk_pareto.setStyleSheet("color: #0284C7;")
        self.chk_pareto.stateChanged.connect(self.plot_geral_chart)
        controls_layout.addWidget(self.chk_pareto)
        
        controls_layout.addStretch()
        dist_layout.addLayout(controls_layout)
        
        self.geral_figure = Figure(figsize=(6, 3), dpi=100, facecolor='#FFFFFF')
        self.geral_canvas = FigureCanvas(self.geral_figure)
        self.geral_ax = self.geral_figure.add_subplot(111)
        self.geral_ax2 = None 
        dist_layout.addWidget(self.geral_canvas)
        
        right_splitter.addWidget(dist_panel)
        right_splitter.setSizes([300, 500]) # Proporção vertical
        
        splitter_main.addWidget(right_splitter)
        splitter_main.setSizes([400, 600]) # Proporção horizontal
        layout.addWidget(splitter_main)

    # =========================================================
    # CONEXÕES E EVENTOS PRINCIPAIS
    # =========================================================
    def setup_connections(self):
        self.viewmodel.cases_loaded.connect(self.populate_cases)
        self.viewmodel.analysis_data_ready.connect(self.render_geral_data)
        self.viewmodel.error_occurred.connect(self.show_error)
        
        self.combo_cases.currentIndexChanged.connect(self.on_case_selected)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def load_data(self):
        self.viewmodel.load_cases()

    def load_case(self, case_id: str, case_name: str = ""):
        self.current_case_id = case_id
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

        if self.current_case_id:
            self.load_case(self.current_case_id)

    def on_case_selected(self, index):
        if index > 0:
            selected_text = self.combo_cases.currentText()
            case_id = self.case_mapping.get(selected_text)
            if case_id:
                self.current_case_id = case_id 
                
                self.loaded_geral_case_id = None
                if hasattr(self, 'tab_topology'): self.tab_topology.loaded_case_id = None
                if hasattr(self, 'tab_generation'): self.tab_generation.loaded_case_id = None
                if hasattr(self, 'tab_transmission'): self.tab_transmission.loaded_case_id = None
                
                self.on_tab_changed(self.tabs.currentIndex())

    def on_tab_changed(self, index):
        if not self.current_case_id: return
            
        current_widget = self.tabs.widget(index)

        if hasattr(self, 'tab_topology') and current_widget == self.tab_topology:
            if getattr(self.tab_topology, 'loaded_case_id', None) != self.current_case_id:
                self.tab_topology.load_case(self.current_case_id)
                self.tab_topology.loaded_case_id = self.current_case_id

        elif hasattr(self, 'tab_transmission') and current_widget == self.tab_transmission:
            if getattr(self.tab_transmission, 'loaded_case_id', None) != self.current_case_id:
                self.tab_transmission.load_case(self.current_case_id)
                self.tab_transmission.loaded_case_id = self.current_case_id

        elif hasattr(self, 'tab_generation') and current_widget == self.tab_generation:
            if getattr(self.tab_generation, 'loaded_case_id', None) != self.current_case_id:
                self.tab_generation.load_case(self.current_case_id)
                self.tab_generation.loaded_case_id = self.current_case_id

        elif hasattr(self, 'tab_geral') and current_widget == self.tab_geral:
            if self.loaded_geral_case_id != self.current_case_id:
                # O ViewModel precisa chamar a API ou passar o mock. 
                # (Estou injetando o mock localmente caso o ViewModel ainda não retorne esses novos dados)
                self.viewmodel.fetch_geral_data(self.current_case_id)
                self.loaded_geral_case_id = self.current_case_id

    def show_error(self, msg):
        QMessageBox.warning(self, "Erro", msg)

    # =========================================================
    # LÓGICA DE RENDERIZAÇÃO E GRÁFICOS
    # =========================================================
    def render_geral_data(self, data: dict):
        self.current_geral_data = data
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_tabelas", 2)
        
        # MOCK - Fallback caso a API ainda não envie essa nova estrutura
        simulated_years = data.get("simulated_years", 20)
        self.lbl_sim_years.setText(f"Anos Simulados: {simulated_years}")
        
        # 1. Tabela de Confiabilidade Global (LOLE, EENS, EPNS...)
        reliability_data = data.get("global_reliability")
        if not reliability_data:
            reliability_data = [
                {"nome": "LOLE", "valor": 12.5, "beta": 0.05},
                {"nome": "EENS", "valor": 340.2, "beta": 0.02},
                {"nome": "EPNS", "valor": 150.0, "beta": 0.08},
                {"nome": "LOLP", "valor": 0.0014, "beta": 0.04},
            ]
            
        self.table_global.setRowCount(len(reliability_data))
        for row, param in enumerate(reliability_data):
            item_nome = QTableWidgetItem(param["nome"])
            item_val = QTableWidgetItem(f"{param['valor']:.{decimais}f}")
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_beta = QTableWidgetItem(f"{(param['beta'] * 100):.1f}%")
            item_beta.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.table_global.setItem(row, 0, item_nome)
            self.table_global.setItem(row, 1, item_val)
            self.table_global.setItem(row, 2, item_beta)

        # 2. Tabela System Summary
        summary_data = data.get("system_summary")
        if not summary_data:
            summary_data = [
                {"nome": "Rated load", "valor": 230.00, "unidade": "MW"},
                {"nome": "Peak load", "valor": 230.00, "unidade": "MW"},
                {"nome": "Mean load", "valor": 141.34, "unidade": "MW"},
                {"nome": "Annual total demand", "valor": 1.24, "unidade": "TWh"},
                {"nome": "Rated load/gen capacity", "valor": 73.72, "unidade": "%"},
            ]
            
        self.table_summary.setRowCount(len(summary_data))
        for row, param in enumerate(summary_data):
            item_nome = QTableWidgetItem(param["nome"])
            item_val = QTableWidgetItem(f"{param['valor']:.{decimais}f}")
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_unit = QTableWidgetItem(param["unidade"])
            item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.table_summary.setItem(row, 0, item_nome)
            self.table_summary.setItem(row, 1, item_val)
            self.table_summary.setItem(row, 2, item_unit)

        # 3. Gráfico de Rosquinha
        tech_data = data.get("generation_tech")
        if not tech_data:
            tech_data = {"Thermal": 212.00, "Hydro": 100.00}
        self.plot_donut_chart(tech_data)

        # 4. Gráfico de Distribuição
        indicadores = data.get("indicators", [])
        self.combo_geral_ind.blockSignals(True)
        self.combo_geral_ind.clear()
        self.combo_geral_ind.addItems(indicadores)
        self.combo_geral_ind.blockSignals(False)
        self.plot_geral_chart()

    def plot_donut_chart(self, tech_data: dict):
        self.donut_ax.clear()
        
        labels = list(tech_data.keys())
        values = list(tech_data.values())
        
        if sum(values) == 0:
            self.donut_ax.text(0.5, 0.5, "Sem dados de geração", ha='center', va='center', color='#94A3B8')
        else:
            # Propriedades do Donut
            wedges, texts, autotexts = self.donut_ax.pie(
                values, labels=labels, autopct='%1.1f%%', 
                startangle=90, colors=self.donut_colors,
                wedgeprops=dict(width=0.4, edgecolor='white')
            )
            
            # Estilo dos textos
            for text in texts: text.set_color('#334155')
            for autotext in autotexts:
                autotext.set_color('white')
                # A fonte normal foi solicitada
        
        self.donut_figure.tight_layout()
        self.donut_canvas.draw()

    def plot_geral_chart(self):
        if not self.current_geral_data: return
        
        self.geral_figure.clear()
        self.geral_ax = self.geral_figure.add_subplot(111)
        if self.geral_ax2:
            self.geral_ax2 = None
            
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_grafico", 2)
        ind = self.combo_geral_ind.currentText()
        if not ind: return
        
        elements = self.current_geral_data.get("elements", [])
        if not elements: return
        
        case_id_str = str(self.current_case_id)
        
        def get_val(el):
            v = el.get("values_by_case", {}).get(case_id_str, {}).get(ind)
            if v is not None: return v
            return el.get("value", 0.0)
            
        elements.sort(key=get_val, reverse=True)
        
        limit = self.spin_max_elements.value()
        elements = elements[:limit]
        
        element_names = [el.get("element_name", "") for el in elements]
        y_vals = [round(get_val(el), decimais) for el in elements]
        x_indices = np.arange(len(element_names))
        
        total_elements = len(elements)
        color = self.chart_colors[0]

        if total_elements > 100:
            self.geral_ax.plot(x_indices, y_vals, color=color, linewidth=1.5)
            self.geral_ax.fill_between(x_indices, y_vals, alpha=0.3, color=color)
        else:
            self.geral_ax.bar(x_indices, y_vals, width=0.7, color=color, edgecolor='white', alpha=0.9)

        if total_elements > 25:
            self.geral_ax.set_xticks([])
            self.geral_ax.set_xlabel(f"Elementos do Sistema ({total_elements} elementos)", style='italic', color='#64748B')
        else:
            self.geral_ax.set_xticks(x_indices)
            self.geral_ax.set_xticklabels(element_names, rotation=45, ha='right', fontsize=9)

        self.geral_ax.set_ylabel(f"Valor ({ind})")
        self.geral_ax.set_title(f"Distribuição de {ind}")
        self.geral_ax.grid(axis='y', linestyle='--', alpha=0.4)
        self.geral_ax.spines['top'].set_visible(False)
        self.geral_ax.spines['right'].set_visible(False)

        if self.chk_pareto.isChecked() and sum(y_vals) > 0:
            self.geral_ax2 = self.geral_ax.twinx()
            cumulative_sum = np.cumsum(y_vals)
            pareto_percentages = 100 * cumulative_sum / cumulative_sum[-1]
            
            self.geral_ax2.plot(x_indices, pareto_percentages, color='#EF4444', linewidth=2.5, marker='' if total_elements > 50 else 'o', label='Pareto Acumulado (%)')
            self.geral_ax2.set_ylabel("Frequência Acumulada (%)", color='#EF4444')
            self.geral_ax2.set_ylim(0, 105)
            self.geral_ax2.spines['top'].set_visible(False)
            self.geral_ax2.axhline(80, color='#94A3B8', linestyle=':', linewidth=1.5)

        self.geral_figure.tight_layout()
        self.geral_canvas.draw()
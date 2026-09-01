import uuid
import colorsys

import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QGroupBox,
    QCheckBox,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
)

from ui.services.settings_service import SettingsService
from ui.viewmodels.comparison_viewmodel import ComparisonViewModel


# Força o Matplotlib a usar Arial globalmente
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']



class ComparisonView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = ComparisonViewModel()
        self.settings = SettingsService.get_instance()
        self.cases_mapping = {}
        self.current_data = {}
        self.case_ids_cache = []
        self.case_names_cache = []
        
        # Cache para lembrar quais caixinhas estavam marcadas em cada granularidade
        self.filter_state_cache = {}
        
        # Paleta de Cores Moderna e Vibrante (Tailwind Colors)
        self.chart_colors = ['#0EA5E9', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6']
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setStyleSheet("""
        /* =========================================================
           BASE
           ========================================================= */

        QWidget {
            font-family: "Segoe UI", Arial, sans-serif;
            color: #0F172A;
        }

        /* =========================================================
           GROUP BOX
           ========================================================= */

        QGroupBox {
            font-weight: bold;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
            background-color: #FFFFFF;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: #334155;
        }

        /* =========================================================
           COMBO BOX
           ========================================================= */

        QComboBox {
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px;
            background-color: #FFFFFF;
            color: #0F172A;
        }

        QComboBox:hover,
        QComboBox:focus {
            border: 1px solid #0284C7;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #CBD5E1;
            background-color: #FFFFFF;
            selection-background-color: #E0F2FE;
            selection-color: #0369A1;
        }

        /* =========================================================
           LIST WIDGET
           ========================================================= */

        QListWidget {
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px;
            background-color: #FFFFFF;
            color: #0F172A;
        }

        QListWidget::item {
            padding: 4px;
        }

        QListWidget::item:hover {
            background-color: #F1F5F9;
        }

        QListWidget::item:selected {
            background-color: #E0F2FE;
            color: #0369A1;
        }

        /* =========================================================
           CHECK BOX
           ========================================================= */

        QCheckBox {
            spacing: 8px;
            font-size: 12px;
            color: #334155;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #CBD5E1;
            background-color: #FFFFFF;
        }

        QCheckBox::indicator:hover {
            border: 1px solid #0284C7;
        }

        QCheckBox::indicator:checked {
            background-color: #0284C7;
            border: 1px solid #0284C7;
        }

        /* =========================================================
           SCROLL AREA
           ========================================================= */

        QScrollArea {
            border: none;
            background-color: #F8FAFC;
        }

        QScrollArea > QWidget > QWidget {
            background-color: #F8FAFC;
        }

        /* =========================================================
           SCROLL BAR - VERTICAL
           ========================================================= */

        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 8px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background: #CBD5E1;
            min-height: 30px;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical:hover {
            background: #94A3B8;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            background: none;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }

        /* =========================================================
           SCROLL BAR - HORIZONTAL
           ========================================================= */

        QScrollBar:horizontal {
            border: none;
            background: transparent;
            height: 8px;
            margin: 0;
        }

        QScrollBar::handle:horizontal {
            background: #CBD5E1;
            min-width: 30px;
            border-radius: 4px;
        }

        QScrollBar::handle:horizontal:hover {
            background: #94A3B8;
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0;
            background: none;
        }

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {
            background: transparent;
        }

        /* =========================================================
           TREE WIDGET
           ========================================================= */

        QTreeWidget {
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 5px;
            background-color: #FFFFFF;
            color: #0F172A;
        }

        QTreeWidget::item {
            padding: 4px;
            border-bottom: 1px solid #F8FAFC;
        }

        QTreeWidget::item:hover {
            background-color: #F1F5F9;
        }

        QTreeWidget::item:selected {
            background-color: #E0F2FE;
            color: #0369A1;
        }

        QTreeWidget::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #94A3B8;
            background-color: #FFFFFF;
        }

        QTreeWidget::indicator:hover {
            border: 1px solid #0284C7;
        }

        QTreeWidget::indicator:checked {
            background-color: #0284C7;
            border: 1px solid #0284C7;
        }

        /* =========================================================
           SPIN BOX
           ========================================================= */

        QSpinBox {
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 6px 12px;
            background-color: #FFFFFF;
            color: #0F172A;
            font-weight: 600;
        }

        QSpinBox:hover,
        QSpinBox:focus {
            border: 1px solid #0284C7;
        }

        QSpinBox::up-button,
        QSpinBox::down-button {
            background-color: #F1F5F9;
            border-left: 1px solid #CBD5E1;
            width: 18px;
        }

        QSpinBox::up-button:hover,
        QSpinBox::down-button:hover {
            background-color: #E2E8F0;
        }
    """)

        # LAYOUT BASE (Permite o painel lateral)
        base_layout = QHBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)

        # --- ÁREA PRINCIPAL ---
        self.main_content = QWidget()
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # CABEÇALHO
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Comparative Analysis")
        title.setStyleSheet("font-size: 26px; font-weight: 900; color: #0F172A; letter-spacing: -0.5px; margin: 0; padding: 0;")
        subtitle = QLabel("Compare indicators across multiple base cases")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B; margin: 0; padding: 0;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)

        self.btn_toggle_drawer = QPushButton("  Personalizar Gráfico")
        self.btn_toggle_drawer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_drawer.setStyleSheet("""
            QPushButton { background-color: #FFFFFF; color: #0F172A; font-weight: bold; font-size: 13px; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #F1F5F9; border-color: #94A3B8; }
        """)
        header_layout.addWidget(self.btn_toggle_drawer, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addLayout(header_layout)

        # CONFIG CARD
        control_panel = QGroupBox()
        control_panel.setStyleSheet("QGroupBox { border: 1px solid #E2E8F0; border-radius: 8px; background-color: #FFFFFF; }")
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)

        cases_layout = QVBoxLayout()
        cases_layout.addWidget(QLabel("<b>Select Base Cases (Max 5):</b>"))
        self.list_cases = QListWidget()
        self.list_cases.setFixedHeight(70)
        cases_layout.addWidget(self.list_cases)
        control_layout.addLayout(cases_layout, stretch=3)

        granularity_layout = QVBoxLayout()
        granularity_layout.addWidget(QLabel("<b>Granularity Level:</b>"))
        self.combo_granularity = QComboBox()
        self.combo_granularity.addItems(["Global", "By Region", "By Bus"])
        self.combo_granularity.setFixedHeight(35)
        granularity_layout.addWidget(self.combo_granularity)
        granularity_layout.addStretch() 
        control_layout.addLayout(granularity_layout, stretch=1)

        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        self.btn_compare = QPushButton("Generate Comparison")
        self.btn_compare.setFixedHeight(50)
        self.btn_compare.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_compare.setStyleSheet("""
            QPushButton { background-color: #0284C7; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; }
            QPushButton:hover { background-color: #0369A1; }
            QPushButton:disabled { background-color: #94A3B8; color: #E2E8F0; }
        """)
        btn_layout.addWidget(self.btn_compare)
        control_layout.addLayout(btn_layout, stretch=1)

        main_layout.addWidget(control_panel)

        # TABS DE ANÁLISE
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; background-color: #FFFFFF; border-radius: 8px; border-top-left-radius: 0px;}
            QTabBar::tab { background: #F8FAFC; color: #64748B; padding: 10px 20px; font-weight: bold; border: 1px solid transparent; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px;}
            QTabBar::tab:selected { background: #FFFFFF; color: #0284C7; border: 1px solid #E2E8F0; border-bottom: 2px solid #FFFFFF; border-top: 3px solid #0284C7; }
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

        main_layout.addWidget(self.tabs, stretch=1)
        base_layout.addWidget(self.main_content, stretch=1)

        self.tab_time_series = QWidget()
        self.setup_time_series_tab()
        self.tabs.addTab(self.tab_time_series, "Load Input Template")

        # --- PAINEL LATERAL (DRAWER) ---
        self.setup_drawer()
        base_layout.addWidget(self.drawer)

    def setup_drawer(self):
        self.drawer = QFrame()
        self.drawer.setFixedWidth(320)
        self.drawer.setStyleSheet("QFrame { background-color: #FFFFFF; border-left: 1px solid #E2E8F0; }")
        self.drawer.hide()

        drawer_layout = QVBoxLayout(self.drawer)
        drawer_layout.setContentsMargins(20, 20, 20, 20)
        drawer_layout.setSpacing(15)

        # Cabeçalho do Drawer
        d_header = QHBoxLayout()
        d_title = QLabel("Personalizar Gráfico")
        d_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #0F172A; border: none;")
        self.btn_close_drawer = QPushButton("✕")
        self.btn_close_drawer.setFixedSize(24, 24)
        self.btn_close_drawer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close_drawer.setStyleSheet("QPushButton { border: none; font-weight: bold; color: #64748B; background: transparent; } QPushButton:hover { color: #EF4444; }")
        self.btn_close_drawer.clicked.connect(self.toggle_drawer)
        d_header.addWidget(d_title)
        d_header.addStretch()
        d_header.addWidget(self.btn_close_drawer)
        drawer_layout.addLayout(d_header)

        # Scroll do Drawer
        d_scroll = QScrollArea()
        d_scroll.setStyleSheet("border: none;")
        d_scroll.setWidgetResizable(True)
        d_container = QWidget()
        d_inner = QVBoxLayout(d_container)
        d_inner.setContentsMargins(0, 10, 0, 10)
        d_inner.setSpacing(20)

        def add_section_title(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #94A3B8; text-transform: uppercase; border: none; margin-top: 10px;")
            d_inner.addWidget(lbl)

        # Seção 1: Exibição
        add_section_title("Exibição")
        self.chk_hide_nulls = QCheckBox("Não exibir valores nulos")
        self.chk_hide_nulls.setChecked(True)
        self.chk_show_titles = QCheckBox("Exibir título de cada barra")
        self.chk_show_titles.setChecked(True)
        d_inner.addWidget(self.chk_hide_nulls)
        d_inner.addWidget(self.chk_show_titles)

        # Seção 2: Aparência
        add_section_title("Aparência")
        d_inner.addWidget(QLabel("Esquema de Cores:"))
        self.combo_color = QComboBox()
        self.combo_color.addItems(["Padrão (Tailwind)", "Alto Contraste"])
        d_inner.addWidget(self.combo_color)
        
        d_inner.addWidget(QLabel("Estilo das Barras:"))
        self.combo_bar_style = QComboBox()
        self.combo_bar_style.addItems(["Agrupadas"])
        d_inner.addWidget(self.combo_bar_style)

        d_inner.addWidget(QLabel("Tamanho da Fonte:"))
        self.combo_font_size = QComboBox()
        self.combo_font_size.addItems(["Pequeno", "Médio", "Grande"])
        self.combo_font_size.setCurrentText("Médio")
        d_inner.addWidget(self.combo_font_size)

        # Seção 3: Eixos
        add_section_title("Eixos")
        self.chk_show_y1 = QCheckBox("Exibir eixo Y Principal")
        self.chk_show_y1.setChecked(True)
        self.chk_show_y2 = QCheckBox("Exibir eixo Y Secundário (%)")
        self.chk_show_y2.setChecked(True)
        self.chk_invert_x = QCheckBox("Inverter ordem do eixo X")
        d_inner.addWidget(self.chk_show_y1)
        d_inner.addWidget(self.chk_show_y2)
        d_inner.addWidget(self.chk_invert_x)

        # Seção 4: Outros
        add_section_title("Outros")
        d_inner.addWidget(QLabel("Linhas de Grade:"))
        self.combo_grid = QComboBox()
        self.combo_grid.addItems(["Horizontais", "Nenhuma", "Horizontais e Verticais"])
        d_inner.addWidget(self.combo_grid)

        d_inner.addWidget(QLabel("Densidade de Dados:"))
        self.combo_density = QComboBox()
        self.combo_density.addItems(["Normal", "Compacta", "Espaçada"])
        d_inner.addWidget(self.combo_density)

        d_inner.addStretch()
        d_scroll.setWidget(d_container)
        drawer_layout.addWidget(d_scroll)

        # Botões do Drawer
        d_btn_layout = QHBoxLayout()
        self.btn_restore = QPushButton("Restaurar")
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.setStyleSheet("QPushButton { background-color: #F1F5F9; color: #334155; border: 1px solid #CBD5E1; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        self.btn_apply = QPushButton("✓ Aplicar")
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setStyleSheet("QPushButton { background-color: #0284C7; color: white; border: none; padding: 8px; border-radius: 4px; font-weight: bold; }")
        
        d_btn_layout.addWidget(self.btn_restore)
        d_btn_layout.addWidget(self.btn_apply)
        drawer_layout.addLayout(d_btn_layout)

    def toggle_drawer(self):
        self.drawer.setVisible(not self.drawer.isVisible())

    # ---------------------------------------------------------
    # SETUP DAS ABAS INTERNAS
    # ---------------------------------------------------------
    def setup_table_tab(self):
        layout = QVBoxLayout(self.tab_table)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Novo Filtro da Tabela
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("<b>Reliability Indicator Filter:</b>"))
        self.combo_table_filter = QComboBox()
        self.combo_table_filter.addItem("All Indicators")
        self.combo_table_filter.currentIndexChanged.connect(self.update_table_view)
        self.combo_table_filter.setMinimumWidth(200)
        filter_layout.addWidget(self.combo_table_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { border: 1px solid #E2E8F0; background-color: #FFFFFF; alternate-background-color: #F8FAFC; color: #1E293B; }
            QHeaderView::section { background-color: #F1F5F9; color: #334155; font-weight: bold; padding: 10px; border: none; border-bottom: 2px solid #CBD5E1; }
            QTableWidget::item { border-bottom: 1px solid #E2E8F0; padding: 8px; }
        """)
        layout.addWidget(self.table)

    def setup_scatter_tab(self):
        layout = QVBoxLayout(self.tab_scatter)
        layout.setContentsMargins(15, 15, 15, 15)
        
        control_row = QHBoxLayout()
        control_row.addWidget(QLabel("<b>Plot Mode:</b>"))
        self.combo_scatter_type = QComboBox()
        self.combo_scatter_type.addItems(["Scatter Plot", "Bar (X) & Line (Y)"])
        self.combo_scatter_type.currentIndexChanged.connect(self.plot_scatter)
        control_row.addWidget(self.combo_scatter_type)
        control_row.addSpacing(20)

        control_row.addWidget(QLabel("<b>X-Axis Indicator:</b>"))
        self.combo_x = QComboBox()
        self.combo_x.setMinimumWidth(150)
        control_row.addWidget(self.combo_x)
        control_row.addSpacing(20)
        
        control_row.addWidget(QLabel("<b>Y-Axis Indicator:</b>"))
        self.combo_y = QComboBox()
        self.combo_y.setMinimumWidth(150)
        control_row.addWidget(self.combo_y)
        control_row.addStretch()
        layout.addLayout(control_row)

        self.scatter_figure = Figure(figsize=(6, 4), dpi=100, facecolor='#FFFFFF')
        self.scatter_canvas = FigureCanvas(self.scatter_figure)
        self.scatter_canvas.wheelEvent = lambda event: event.ignore() # Fix de Rolagem
        self.scatter_ax = self.scatter_figure.add_subplot(111)
        self.scatter_ax2 = None # Suporte para 2º Eixo
        layout.addWidget(self.scatter_canvas)

    def setup_bar_tab(self):
        main_layout = QVBoxLayout(self.tab_bar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        top_panel = QHBoxLayout()
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        
        row_ind = QHBoxLayout()
        row_ind.addWidget(QLabel("<b>Indicator:</b>"))
        self.combo_bar_ind = QComboBox()
        self.combo_bar_ind.setMinimumWidth(180)
        row_ind.addWidget(self.combo_bar_ind)
        
        # NOVO: Checkbox para visualização múltipla (Global)
        self.chk_show_all_indicators = QCheckBox("Comparar Todos Lado a Lado (Global)")
        self.chk_show_all_indicators.setStyleSheet("font-weight: bold; color: #0284C7; margin-left: 15px;")
        self.chk_show_all_indicators.stateChanged.connect(self.toggle_all_indicators_mode)
        self.chk_show_all_indicators.hide() # Fica escondido por padrão
        row_ind.addWidget(self.chk_show_all_indicators)
        row_ind.addStretch()
        
        controls_layout.addLayout(row_ind)
        
        row_sort = QHBoxLayout()
        row_sort.addWidget(QLabel("<b>Sort By:</b>"))
        self.combo_sort_bar = QComboBox()
        self.combo_sort_bar.addItems(["Default (Name/ID)", "Ascending (Value)", "Descending (Value)"])
        self.combo_sort_bar.setMinimumWidth(180)
        row_sort.addWidget(self.combo_sort_bar)
        row_sort.addStretch()
        controls_layout.addLayout(row_sort)
        
        top_panel.addLayout(controls_layout, stretch=1)
        
        filter_group = QGroupBox("Filter Elements to Plot")
        filter_group.setStyleSheet("QGroupBox { border: 1px solid #E2E8F0; border-radius: 6px; }")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setContentsMargins(10, 15, 10, 10)
        
        btn_row = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_deselect_all = QPushButton("Deselect All")
        for btn in [self.btn_select_all, self.btn_deselect_all]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background-color: #F1F5F9; color: #475569; padding: 4px 10px; border: 1px solid #CBD5E1; border-radius: 4px; font-size: 11px;")
        
        btn_row.addWidget(self.btn_select_all)
        btn_row.addWidget(self.btn_deselect_all)
        btn_row.addStretch()
        filter_layout.addLayout(btn_row)
        
        self.list_elements_filter = QListWidget()
        self.list_elements_filter.setFixedHeight(80) 
        self.list_elements_filter.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 4px;")
        filter_layout.addWidget(self.list_elements_filter)
        
        top_panel.addWidget(filter_group, stretch=2)
        layout.addLayout(top_panel)

        self.bar_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumHeight(500) 
        self.bar_canvas.wheelEvent = lambda event: event.ignore() 
        self.bar_ax = self.bar_figure.add_subplot(111)
        layout.addWidget(self.bar_canvas)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def setup_time_series_tab(self):
        layout = QVBoxLayout(self.tab_time_series)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        top_split = QHBoxLayout()
        self.ts_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.ts_canvas = FigureCanvas(self.ts_figure)
        self.ts_canvas.wheelEvent = lambda event: event.ignore() # Fix de Rolagem
        self.ts_ax = self.ts_figure.add_subplot(111)
        top_split.addWidget(self.ts_canvas, stretch=4)

        self.tree_series = QTreeWidget()
        self.tree_series.setHeaderHidden(True)
        self.tree_series.setFixedWidth(280)
        self.tree_series.itemChanged.connect(self.plot_time_series)
        top_split.addWidget(self.tree_series, stretch=1)
        layout.addLayout(top_split, stretch=1)

        bottom_controls = QGroupBox()
        bottom_controls.setStyleSheet("QGroupBox { border: 1px solid #E2E8F0; border-radius: 6px; background-color: #FFFFFF; }")
        control_layout = QHBoxLayout(bottom_controls)
        control_layout.setContentsMargins(15, 10, 15, 10)

        control_layout.addWidget(QLabel("<b>Y-Axis View:</b>"))
        self.combo_ts_unit = QComboBox()
        self.combo_ts_unit.addItems(["Power (MW)", "Energy (Per Hour)"])
        self.combo_ts_unit.currentIndexChanged.connect(self.plot_time_series)
        control_layout.addWidget(self.combo_ts_unit)
        control_layout.addSpacing(40)

        control_layout.addWidget(QLabel("<b>X-Axis Zoom (Hours):</b>"))
        self.spin_x_min = QSpinBox()
        self.spin_x_min.setRange(0, 8760)
        self.spin_x_min.setValue(0)
        self.spin_x_min.setFixedWidth(90)
        self.spin_x_min.valueChanged.connect(self.update_x_axis_limits)
        control_layout.addWidget(self.spin_x_min)
        control_layout.addWidget(QLabel("até"))

        self.spin_x_max = QSpinBox()
        self.spin_x_max.setRange(0, 8760)
        self.spin_x_max.setValue(240)
        self.spin_x_max.setFixedWidth(90)
        self.spin_x_max.valueChanged.connect(self.update_x_axis_limits)
        control_layout.addWidget(self.spin_x_max)
        control_layout.addStretch()
        layout.addWidget(bottom_controls)

    def setup_bar_tab(self):
        main_layout = QVBoxLayout(self.tab_bar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        top_panel = QHBoxLayout()
        
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(10)
        
        row_ind = QHBoxLayout()
        row_ind.addWidget(QLabel("<b>Indicator:</b>"))
        self.combo_bar_ind = QComboBox()
        self.combo_bar_ind.setMinimumWidth(180)
        row_ind.addWidget(self.combo_bar_ind)
        self.chk_show_all_indicators = QCheckBox("Comparar Todos Lado a Lado (Global)")
        self.chk_show_all_indicators.setStyleSheet("font-weight: bold; color: #0284C7; margin-left: 15px;")
        self.chk_show_all_indicators.stateChanged.connect(self.toggle_all_indicators_mode)
        self.chk_show_all_indicators.hide() 
        row_ind.addWidget(self.chk_show_all_indicators)
        row_ind.addStretch()
        controls_layout.addLayout(row_ind)
        
        row_sort = QHBoxLayout()
        row_sort.addWidget(QLabel("<b>Sort By:</b>"))
        self.combo_sort_bar = QComboBox()
        self.combo_sort_bar.addItems(["Default (Name/ID)", "Ascending (Value)", "Descending (Value)"])
        self.combo_sort_bar.setMinimumWidth(180)
        row_sort.addWidget(self.combo_sort_bar)
        row_sort.addStretch()
        controls_layout.addLayout(row_sort)
        
        self.chk_pareto = QCheckBox("Overlay Pareto Curves")
        self.chk_pareto.setChecked(True)
        self.chk_pareto.setStyleSheet("font-weight: bold; color: #475569; margin-top: 5px;")
        controls_layout.addWidget(self.chk_pareto)
        
        top_panel.addLayout(controls_layout, stretch=1)
        
        filter_group = QGroupBox("Filter Elements to Plot")
        filter_group.setStyleSheet("QGroupBox { border: 1px solid #E2E8F0; border-radius: 6px; }")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setContentsMargins(10, 15, 10, 10)
        
        btn_row = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_deselect_all = QPushButton("Deselect All")
        for btn in [self.btn_select_all, self.btn_deselect_all]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background-color: #F1F5F9; color: #475569; padding: 4px 10px; border: 1px solid #CBD5E1; border-radius: 4px; font-size: 11px;")
        
        btn_row.addWidget(self.btn_select_all)
        btn_row.addWidget(self.btn_deselect_all)
        btn_row.addStretch()
        filter_layout.addLayout(btn_row)
        
        self.list_elements_filter = QListWidget()
        self.list_elements_filter.setFixedHeight(80) 
        self.list_elements_filter.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 4px;")
        filter_layout.addWidget(self.list_elements_filter)
        
        top_panel.addWidget(filter_group, stretch=2)
        layout.addLayout(top_panel)

        self.bar_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumHeight(500) 
        self.bar_ax = self.bar_figure.add_subplot(111)
        self.pareto_ax = None
        layout.addWidget(self.bar_canvas)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    # ---------------------------------------------------------
    # CONEXÕES E LÓGICA
    # ---------------------------------------------------------
    def setup_connections(self):
        self.btn_toggle_drawer.clicked.connect(self.toggle_drawer)

        if hasattr(self.viewmodel, 'cases_list_ready'):
            self.viewmodel.cases_list_ready.connect(self.populate_cases_list)
        elif hasattr(self.viewmodel, 'cases_loaded'):
            self.viewmodel.cases_loaded.connect(self.populate_cases_list)
            
        if hasattr(self.viewmodel, 'comparison_data_ready'):
            self.viewmodel.comparison_data_ready.connect(self.render_real_data)

        if hasattr(self.viewmodel, 'error_occurred'):
            self.viewmodel.error_occurred.connect(self.handle_error)

        if hasattr(self.viewmodel, 'time_series_data_ready'):
            self.viewmodel.time_series_data_ready.connect(self.render_time_series_data)

        self.list_cases.itemChanged.connect(self.enforce_max_cases)
        self.btn_compare.clicked.connect(self.run_comparison)
        
        self.combo_x.currentIndexChanged.connect(self.plot_scatter)
        self.combo_y.currentIndexChanged.connect(self.plot_scatter)
        
        self.combo_bar_ind.currentIndexChanged.connect(self.plot_bar)
        self.combo_sort_bar.currentIndexChanged.connect(self.plot_bar)
        
        
        self.btn_select_all.clicked.connect(self.select_all_elements)
        self.btn_deselect_all.clicked.connect(self.deselect_all_elements)
        
        # Conecta a atualização do cache e do gráfico a qualquer clique na lista
        self.list_elements_filter.itemChanged.connect(self.save_filter_state)
        self.list_elements_filter.itemChanged.connect(self.plot_bar)

        self.btn_apply.clicked.connect(self.plot_bar)
        self.btn_restore.clicked.connect(self.restore_defaults)

    def save_filter_state(self, item=None):
        """Salva as escolhas atuais da list_elements_filter na granularidade ativa."""
        granularity = self.combo_granularity.currentText()
        checked_names = set()
        for i in range(self.list_elements_filter.count()):
            list_item = self.list_elements_filter.item(i)
            if list_item.checkState() == Qt.CheckState.Checked:
                checked_names.add(list_item.text())
        self.filter_state_cache[granularity] = checked_names

    def restore_defaults(self):
        self.chk_hide_nulls.setChecked(True)
        self.chk_show_titles.setChecked(True)
        self.combo_color.setCurrentIndex(0)
        self.combo_font_size.setCurrentText("Médio")
        self.chk_show_y1.setChecked(True)
        self.chk_show_y2.setChecked(True)
        self.chk_invert_x.setChecked(False)
        self.combo_grid.setCurrentText("Horizontais")
        self.combo_density.setCurrentText("Normal")
        self.plot_bar()

    def select_all_elements(self):
        self.list_elements_filter.blockSignals(True)
        for i in range(self.list_elements_filter.count()):
            self.list_elements_filter.item(i).setCheckState(Qt.CheckState.Checked)
        self.list_elements_filter.blockSignals(False)
        self.save_filter_state()
        self.plot_bar()

    def deselect_all_elements(self):
        self.list_elements_filter.blockSignals(True)
        for i in range(self.list_elements_filter.count()):
            self.list_elements_filter.item(i).setCheckState(Qt.CheckState.Unchecked)
        self.list_elements_filter.blockSignals(False)
        self.save_filter_state()
        self.plot_bar()

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

        self.case_ids_cache = selected_ids
        self.case_names_cache = selected_names

        granularity = self.combo_granularity.currentText()
        gran_map = {"Global": "GLOBAL", "By Region": "REGION", "By Bus": "BUS"}
        gran_api = gran_map.get(granularity, "GLOBAL")
        
        self.btn_compare.setText("Processing Data...")
        self.btn_compare.setEnabled(False)
        self.viewmodel.fetch_multi_case_data(selected_ids, gran_api, "ALL")

        if hasattr(self.viewmodel, 'fetch_time_series_data'):
            self.viewmodel.fetch_time_series_data(selected_ids)

    def render_real_data(self, response_data: dict):
        self.btn_compare.setText("Generate Comparison")
        self.btn_compare.setEnabled(True)
        self.current_data = response_data
        
        indicadores = response_data.get("indicators", [])
        elements = response_data.get("elements", [])
        
        if not elements or not indicadores:
            QMessageBox.information(self, "No Data", "Não há dados para esta configuração.")
            return
        
        granularity = self.combo_granularity.currentText()
        if hasattr(self, 'chk_show_all_indicators'):
            if granularity == "Global":
                self.chk_show_all_indicators.show()
            else:
                self.chk_show_all_indicators.hide()
                self.chk_show_all_indicators.setChecked(False)
        
        # Preenche o filtro da Tabela
        self.combo_table_filter.blockSignals(True)
        self.combo_table_filter.clear()
        self.combo_table_filter.addItem("All Indicators")
        self.combo_table_filter.addItems(indicadores)
        self.combo_table_filter.blockSignals(False)

        # Preenche o filtro de Elementos dos Gráficos com Memória
        granularity = self.combo_granularity.currentText()
        if granularity not in self.filter_state_cache:
            self.filter_state_cache[granularity] = {el.get("element_name", "N/A") for el in elements}
            
        saved_checked_names = self.filter_state_cache.get(granularity, set())

        self.list_elements_filter.blockSignals(True)
        self.list_elements_filter.clear()
        for el in elements:
            el_name = el.get("element_name", "N/A")
            item = QListWidgetItem(el_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if el_name in saved_checked_names:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.list_elements_filter.addItem(item)
        self.list_elements_filter.blockSignals(False)

        # Atualiza a tabela
        self.update_table_view()

        # Atualiza Comboboxes de Eixos 
        for combo in [self.combo_x, self.combo_y, self.combo_bar_ind]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(indicadores)
            
        if len(indicadores) > 1: self.combo_y.setCurrentIndex(1)
        for combo in [self.combo_x, self.combo_y, self.combo_bar_ind]:
            combo.blockSignals(False)

        self.plot_scatter()
        self.plot_bar()

    def update_table_view(self):
        """Renderiza a tabela respeitando o filtro de indicadores."""
        if not self.current_data: return
        
        response_data = self.current_data
        indicadores_completos = response_data.get("indicators", [])
        unidades = response_data.get("units", {})
        elements = response_data.get("elements", [])
        case_info = response_data.get("case_informations", {})
        sys_summary = response_data.get("system_summaries", {})
        
        selected_ind = self.combo_table_filter.currentText()
        if selected_ind == "All Indicators" or not selected_ind:
            indicadores = indicadores_completos
        else:
            indicadores = [selected_ind]

        info_keys = ["Analysis Type", "System Representation", "Convergence Beta", "Import Date", "Last Update"]
        summary_keys = ["Total Buses", "Total Generators", "Total Transformers", "Total Lines", "Radial Buses", "Interconnected Buses"]

        total_rows = (1 + len(info_keys) + 1 + len(summary_keys) + 1 + (len(elements) * len(indicadores)))
        self.table.clear()
        headers = ["Element", "Indicator", "Unit"] + self.case_names_cache
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(total_rows)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        row_idx = 0
        def add_section_header(title):
            nonlocal row_idx
            item = QTableWidgetItem(title)
            item.setBackground(Qt.GlobalColor.lightGray)
            item.setForeground(Qt.GlobalColor.black)
            font = item.font()
            font.setBold(True)
            font.setPointSize(10)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item)
            self.table.setSpan(row_idx, 0, 1, len(headers))
            row_idx += 1

        add_section_header("CASE INFORMATIONS")
        for key in info_keys:
            self.table.setItem(row_idx, 0, QTableWidgetItem("Metadata"))
            self.table.setItem(row_idx, 1, QTableWidgetItem(key))
            self.table.setItem(row_idx, 2, QTableWidgetItem("-"))
            for col_idx, case_id in enumerate(self.case_ids_cache):
                item_val = QTableWidgetItem(str(case_info.get(case_id, {}).get(key, "N/A")))
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, 3 + col_idx, item_val)
            row_idx += 1

        add_section_header("SYSTEM SUMMARY (TOPOLOGY)")
        for key in summary_keys:
            self.table.setItem(row_idx, 0, QTableWidgetItem("Topology"))
            self.table.setItem(row_idx, 1, QTableWidgetItem(key))
            self.table.setItem(row_idx, 2, QTableWidgetItem("Count"))
            for col_idx, case_id in enumerate(self.case_ids_cache):
                item_val = QTableWidgetItem(str(sys_summary.get(case_id, {}).get(key, 0)))
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, 3 + col_idx, item_val)
            row_idx += 1

        add_section_header("RELIABILITY INDICATORS")
        for el in elements:
            item_el = QTableWidgetItem(el.get("element_name", "N/A"))
            item_el.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_el = item_el.font()
            font_el.setBold(True)
            item_el.setFont(font_el)
            
            self.table.setItem(row_idx, 0, item_el)
            self.table.setSpan(row_idx, 0, len(indicadores), 1)
            
            vals_by_case = el.get("values_by_case", {})
            for ind in indicadores:
                item_ind = QTableWidgetItem(ind)
                item_ind.setFont(font_el)
                self.table.setItem(row_idx, 1, item_ind)
                
                item_unit = QTableWidgetItem(unidades.get(ind, ""))
                item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_unit.setForeground(Qt.GlobalColor.darkGray)
                self.table.setItem(row_idx, 2, item_unit)
                
                for col_idx, case_id in enumerate(self.case_ids_cache):
                    val = vals_by_case.get(case_id, {}).get(ind)
                    val_str = "-" if val is None else self.settings.format_number(val, is_table=True)
                    item_val = QTableWidgetItem(val_str)
                    item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, 3 + col_idx, item_val)
                row_idx += 1
        
        def add_section_header(title):
            nonlocal row_idx
            item = QTableWidgetItem(title)
            item.setBackground(Qt.GlobalColor.lightGray)
            item.setForeground(Qt.GlobalColor.black)
            font = item.font()
            font.setBold(True)
            font.setPointSize(10)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row_idx, 0, item)
            self.table.setSpan(row_idx, 0, 1, len(headers))
            row_idx += 1

        # 1. BLOCO CASE INFORMATIONS
        add_section_header("CASE INFORMATIONS")
        for key in info_keys:
            self.table.setItem(row_idx, 0, QTableWidgetItem("Metadata"))
            self.table.setItem(row_idx, 1, QTableWidgetItem(key))
            self.table.setItem(row_idx, 2, QTableWidgetItem("-"))
            for col_idx, case_id in enumerate(self.case_ids_cache):
                val = case_info.get(case_id, {}).get(key, "N/A")
                item_val = QTableWidgetItem(str(val))
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, 3 + col_idx, item_val)
            row_idx += 1

        # 2. BLOCO SYSTEM SUMMARY
        add_section_header("SYSTEM SUMMARY (TOPOLOGY)")
        for key in summary_keys:
            self.table.setItem(row_idx, 0, QTableWidgetItem("Topology"))
            self.table.setItem(row_idx, 1, QTableWidgetItem(key))
            self.table.setItem(row_idx, 2, QTableWidgetItem("Count"))
            for col_idx, case_id in enumerate(self.case_ids_cache):
                val = sys_summary.get(case_id, {}).get(key, 0)
                item_val = QTableWidgetItem(str(val))
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, 3 + col_idx, item_val)
            row_idx += 1

        # 3. BLOCO INDICADORES
        add_section_header("RELIABILITY INDICATORS")
        for el in elements:
            el_name = el.get("element_name", "N/A")
            item_el = QTableWidgetItem(el_name)
            item_el.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_el = item_el.font()
            font_el.setBold(True)
            item_el.setFont(font_el)
            
            self.table.setItem(row_idx, 0, item_el)
            self.table.setSpan(row_idx, 0, len(indicadores), 1)
            
            vals_by_case = el.get("values_by_case", {})

            for ind in indicadores:
                item_ind = QTableWidgetItem(ind)
                item_ind.setFont(font_el)
                self.table.setItem(row_idx, 1, item_ind)
                
                item_unit = QTableWidgetItem(unidades.get(ind, ""))
                item_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_unit.setForeground(Qt.GlobalColor.darkGray)
                self.table.setItem(row_idx, 2, item_unit)
                
                for col_idx, case_id in enumerate(self.case_ids_cache):
                    val = vals_by_case.get(case_id, {}).get(ind)
                    val_str = "-" if val is None else self.settings.format_number(val, is_table=True)
                    item_val = QTableWidgetItem(val_str)
                    item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, 3 + col_idx, item_val)
                row_idx += 1

        # --- ATUALIZA COMBOBOXES DOS GRÁFICOS ---
        for combo in [self.combo_x, self.combo_y, self.combo_bar_ind]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(indicadores)
            
        if len(indicadores) > 1: self.combo_y.setCurrentIndex(1)
        
        for combo in [self.combo_x, self.combo_y, self.combo_bar_ind]:
            combo.blockSignals(False)

        self.plot_scatter()
        self.plot_bar()

    def handle_error(self, message: str):
        self.btn_compare.setText("Generate Comparison")
        self.btn_compare.setEnabled(True)
        QMessageBox.critical(self, "Erro na Análise", message)

    def plot_scatter(self):
        ind_x = self.combo_x.currentText()
        ind_y = self.combo_y.currentText()
        plot_type = getattr(self, 'combo_scatter_type', None)
        ptype = plot_type.currentText() if plot_type else "Scatter Plot"
        
        self.scatter_ax.clear()
        if hasattr(self, 'scatter_ax2') and self.scatter_ax2:
            self.scatter_ax2.remove()
            self.scatter_ax2 = None

        if not ind_x or not ind_y or not self.current_data: return
        elements = self.current_data.get("elements", [])
        colors = self.chart_colors if self.combo_color.currentText() == "Padrão (Tailwind)" else ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442']

        if ptype == "Scatter Plot":
            for i, case_id in enumerate(self.case_ids_cache):
                case_name = self.case_names_cache[i]
                color = colors[i % len(colors)]
                
                x_vals, y_vals, labels = [], [], []
                for el in elements:
                    vals = el.get("values_by_case", {}).get(case_id, {})
                    v_x, v_y = vals.get(ind_x), vals.get(ind_y)
                    if v_x is not None and v_y is not None:
                        x_vals.append(v_x)
                        y_vals.append(v_y)
                        labels.append(el.get("element_name", ""))
                        
                if x_vals and y_vals:
                    self.scatter_ax.scatter(x_vals, y_vals, s=120, color=color, label=case_name, alpha=0.75, edgecolors='white', linewidth=1.0)
                    for vx, vy, lbl in zip(x_vals, y_vals, labels):
                        self.scatter_ax.annotate(lbl, (vx, vy), xytext=(6, 6), textcoords='offset points', fontsize=8, color='#475569', alpha=0.85)

            self.scatter_ax.set_title(f"Correlation: {ind_y} vs {ind_x}", pad=15, fontweight='bold', color='#1E293B')
            self.scatter_ax.set_xlabel(f"{ind_x} Value", fontweight='bold') 
            self.scatter_ax.set_ylabel(f"{ind_y} Value", fontweight='bold')
            self.scatter_ax.grid(True, linestyle='--', alpha=0.3)
            self.scatter_ax.spines['top'].set_visible(False)
            self.scatter_ax.spines['right'].set_visible(False)
            # Legenda Externa (Descolada do Quadro)
            self.scatter_ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9, framealpha=0.9, edgecolor='#CBD5E1')
            self.scatter_figure.subplots_adjust(right=0.70) 

        else:
            # Gráfico Híbrido: Bar (Ind X) & Line (Ind Y)
            self.scatter_ax2 = self.scatter_ax.twinx()
            n_cases = len(self.case_ids_cache)
            element_names = [el.get("element_name", "") for el in elements]
            x = np.arange(len(element_names))
            
            density = self.combo_density.currentText()
            width = 0.8 / n_cases if density == "Normal" else (0.95 / n_cases if density == "Compacta" else 0.6 / n_cases)
            if len(element_names) == 1: width = min(width, 0.15)
            
            for c, case_id in enumerate(self.case_ids_cache):
                case_name = self.case_names_cache[c]
                color = colors[c % len(colors)]
                
                x_vals, y_vals = [], []
                for el in elements:
                    vals = el.get("values_by_case", {}).get(case_id, {})
                    x_vals.append(vals.get(ind_x, 0.0) or 0.0)
                    y_vals.append(vals.get(ind_y, 0.0) or 0.0)
                    
                offset = (c - n_cases/2 + 0.5) * width
                self.scatter_ax.bar(x + offset, x_vals, width, color=color, alpha=0.7, label=f"{case_name} (Bar)")
                self.scatter_ax2.plot(x + offset, y_vals, marker='o', color=color, linewidth=2, label=f"{case_name} (Line)")
            
            font_size = 7 if self.combo_font_size.currentText() == "Pequeno" else (9 if self.combo_font_size.currentText() == "Médio" else 11)
            self.scatter_ax.set_xticks(x)
            self.scatter_ax.set_xticklabels(element_names, rotation=90 if len(element_names)>5 else 0, ha='center', fontsize=font_size)
            self.scatter_ax.set_ylabel(f"{ind_x} (Bars)", fontweight='bold', color='#475569')
            self.scatter_ax2.set_ylabel(f"{ind_y} (Lines)", fontweight='bold', color='#0F172A')
            self.scatter_ax.set_title(f"{ind_x} vs {ind_y} across Elements", pad=15, fontweight='bold', color='#1E293B')
            
            if len(element_names) == 1:
                self.scatter_ax.set_xlim(-2.5, 2.5)
            elif len(element_names) > 1:
                self.scatter_ax.set_xlim(-0.5, len(element_names) - 0.5)

            self.scatter_ax.spines['top'].set_visible(False)
            self.scatter_ax2.spines['top'].set_visible(False)
            
            h1, l1 = self.scatter_ax.get_legend_handles_labels()
            h2, l2 = self.scatter_ax2.get_legend_handles_labels()
            self.scatter_ax.legend(h1+h2, l1+l2, loc='center left', bbox_to_anchor=(1.10, 0.5), fontsize=8, edgecolor='#CBD5E1')
            self.scatter_figure.subplots_adjust(right=0.65, bottom=0.2)
            
        self.scatter_canvas.draw()

    def plot_bar(self):
        if not self.current_data: return
        
        # Limpa toda a figura para reconfigurar os subplots de forma dinâmica
        self.bar_figure.clear()
        
        is_global = self.combo_granularity.currentText() == "Global"
        show_all_global = getattr(self, 'chk_show_all_indicators', None) and self.chk_show_all_indicators.isChecked() and is_global
        colors = self.chart_colors if self.combo_color.currentText() == "Padrão (Tailwind)" else ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442']
        
        if show_all_global:
            indicadores = self.current_data.get("indicators", [])
            if not indicadores: return
            
            n_inds = len(indicadores)
            axs = self.bar_figure.subplots(1, n_inds)
            if n_inds == 1: axs = [axs] # Garante que seja iterável
            
            elements = self.current_data.get("elements", [])
            if not elements: return
            global_el = elements[0] # No global sempre haverá 1 elemento
            
            n_cases = len(self.case_ids_cache)
            width = 0.8 / n_cases
            x = np.arange(1)
            
            for idx, ind in enumerate(indicadores):
                ax = axs[idx]
                for c, case_id in enumerate(self.case_ids_cache):
                    val = global_el.get("values_by_case", {}).get(case_id, {}).get(ind, 0.0)
                    if val is None: val = 0.0
                    offset = (c - n_cases/2 + 0.5) * width
                    
                    ax.bar(
                        x + offset, [val], width, 
                        label=self.case_names_cache[c] if idx == 0 else "", 
                        color=colors[c % len(colors)], edgecolor='white', linewidth=0.5, alpha=0.95
                    )
                
                # Estilização minimalista para os gráficos pequenos
                font_size_title = 8 if n_inds > 4 else 10
                ax.set_title(ind, pad=10, fontweight='bold', color='#1E293B', fontsize=font_size_title)
                ax.set_xticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#CBD5E1')
                ax.spines['bottom'].set_color('#CBD5E1')
                ax.grid(axis='y', linestyle='-', alpha=0.15, color='#94A3B8')

            # Legenda Global para a figura inteira (fora do último gráfico)
            self.bar_figure.legend(loc='center left', bbox_to_anchor=(0.85, 0.5), fontsize=9, edgecolor='#CBD5E1', framealpha=0.9)
            self.bar_figure.subplots_adjust(left=0.05, right=0.80, bottom=0.1, top=0.85, wspace=0.4)
            self.bar_figure.suptitle("Comparativo Geral de Indicadores", fontweight='bold', color='#0F172A', fontsize=14, y=0.95)
            self.bar_canvas.draw()
            return
            

        # Recria o eixo singular
        self.bar_ax = self.bar_figure.add_subplot(111)
        
        ind = self.combo_bar_ind.currentText()
        if not ind: return

        hide_nulls = self.chk_hide_nulls.isChecked()
        show_titles = self.chk_show_titles.isChecked()
        
        checked_names = set()
        for i in range(self.list_elements_filter.count()):
            item = self.list_elements_filter.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_names.add(item.text())

        all_elements = self.current_data.get("elements", [])
        elements = []
        for el in all_elements:
            if el.get("element_name") not in checked_names:
                continue
            if hide_nulls:
                has_value = any(el.get("values_by_case", {}).get(c, {}).get(ind, 0.0) > 0 for c in self.case_ids_cache)
                if not has_value: continue
            elements.append(el)
        
        if not elements: 
            self.bar_figure.tight_layout()
            self.bar_canvas.draw()
            return

        sort_mode = self.combo_sort_bar.currentText()
        def get_avg_val(el):
            vals = [el.get("values_by_case", {}).get(c, {}).get(ind, 0.0) for c in self.case_ids_cache]
            clean_vals = [v if v is not None else 0.0 for v in vals]
            return np.mean(clean_vals) if clean_vals else 0.0

        if "Ascending" in sort_mode: elements.sort(key=get_avg_val)
        elif "Descending" in sort_mode: elements.sort(key=get_avg_val, reverse=True)
        else: elements.sort(key=lambda x: x.get("element_name", ""))
            
        if getattr(self, 'chk_invert_x', None) and self.chk_invert_x.isChecked(): elements.reverse()

        n_cases = len(self.case_ids_cache)
        element_names = [el.get("element_name", "") for el in elements]
        x = np.arange(len(element_names))
        
        density = getattr(self, 'combo_density', None)
        den_text = density.currentText() if density else "Normal"
        width = 0.8 / n_cases if den_text == "Normal" else (0.95 / n_cases if den_text == "Compacta" else 0.6 / n_cases)
        
        if len(element_names) == 1:
            width = min(width, 0.15)
            
        for c, case_id in enumerate(self.case_ids_cache):
            case_vals = []
            for el in elements:
                val = el.get("values_by_case", {}).get(case_id, {}).get(ind)
                case_vals.append(val if val is not None else 0.0)
            
            offset = (c - n_cases/2 + 0.5) * width
            
            self.bar_ax.bar(
                x + offset, case_vals, width, 
                label=self.case_names_cache[c], color=colors[c % len(colors)], edgecolor='white', linewidth=0.5, alpha=0.95
            )

        if show_titles:
            font_size = 7 if self.combo_font_size.currentText() == "Pequeno" else (9 if self.combo_font_size.currentText() == "Médio" else 11)
            self.bar_ax.set_xticks(x)
            self.bar_ax.set_xticklabels(element_names, rotation=90 if len(element_names) > 5 else 0, ha='center', fontsize=font_size, color='#334155')
        else:
            self.bar_ax.set_xticks([])
            self.bar_ax.set_xlabel("Elements (Titles Hidden)", style='italic', color='#64748B')

        self.bar_ax.set_title(f"{ind} Distribution", pad=15, fontweight='bold', color='#1E293B', fontsize=14)
        
        if len(element_names) == 1:
            self.bar_ax.set_xlim(-2.5, 2.5)
        elif len(element_names) > 1:
            self.bar_ax.set_xlim(-0.5, len(element_names) - 0.5)

        if self.chk_show_y1.isChecked():
            self.bar_ax.set_ylabel(f"{ind} Value", fontweight='bold', color='#475569')
        else:
            self.bar_ax.get_yaxis().set_visible(False)
            
        grid_style = self.combo_grid.currentText()
        if grid_style == "Horizontais":
            self.bar_ax.grid(axis='y', linestyle='-', alpha=0.15, color='#94A3B8')
        elif grid_style == "Horizontais e Verticais":
            self.bar_ax.grid(True, linestyle='-', alpha=0.15, color='#94A3B8')

        self.bar_ax.spines['top'].set_visible(False)
        self.bar_ax.spines['right'].set_visible(False)
        self.bar_ax.spines['left'].set_color('#CBD5E1')
        self.bar_ax.spines['bottom'].set_color('#CBD5E1')
        
        self.bar_ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9, edgecolor='#CBD5E1', framealpha=0.9)
        self.bar_figure.subplots_adjust(left=0.08, right=0.75, bottom=0.2, top=0.90) 
        
        self.bar_canvas.draw()

    def setup_time_series_tab(self):
        layout = QVBoxLayout(self.tab_time_series)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Parte Superior: Gráfico (Esquerda) + Árvore (Direita)
        top_split = QHBoxLayout()
        
        # Gráfico
        self.ts_figure = Figure(figsize=(8, 5), dpi=100, facecolor='#FFFFFF')
        self.ts_canvas = FigureCanvas(self.ts_figure)
        self.ts_ax = self.ts_figure.add_subplot(111)
        top_split.addWidget(self.ts_canvas, stretch=4)

        # Árvore de Seleção
        self.tree_series = QTreeWidget()
        self.tree_series.setHeaderHidden(True)
        self.tree_series.setFixedWidth(280)
        self.tree_series.itemChanged.connect(self.plot_time_series)
        top_split.addWidget(self.tree_series, stretch=1)

        layout.addLayout(top_split, stretch=1)

        # Rodapé: Controles de Eixo e Visualização
        bottom_controls = QGroupBox()
        bottom_controls.setStyleSheet("QGroupBox { border: 1px solid #E2E8F0; border-radius: 6px; background-color: #FFFFFF; }")
        control_layout = QHBoxLayout(bottom_controls)
        control_layout.setContentsMargins(15, 10, 15, 10)

        control_layout.addWidget(QLabel("<b>Y-Axis View:</b>"))
        self.combo_ts_unit = QComboBox()
        self.combo_ts_unit.addItems(["Power (MW)", "Energy (Per Hour)"])
        self.combo_ts_unit.currentIndexChanged.connect(self.plot_time_series)
        control_layout.addWidget(self.combo_ts_unit)
        
        control_layout.addSpacing(40)

        control_layout.addWidget(QLabel("<b>X-Axis Zoom (Hours):</b>"))
        self.spin_x_min = QSpinBox()
        self.spin_x_min.setRange(0, 8760)
        self.spin_x_min.setValue(0)
        self.spin_x_min.setFixedWidth(90)
        self.spin_x_min.valueChanged.connect(self.update_x_axis_limits)
        control_layout.addWidget(self.spin_x_min)

        control_layout.addWidget(QLabel("até"))

        self.spin_x_max = QSpinBox()
        self.spin_x_max.setRange(0, 8760)
        self.spin_x_max.setValue(240)
        self.spin_x_max.setFixedWidth(90)
        self.spin_x_max.valueChanged.connect(self.update_x_axis_limits)
        control_layout.addWidget(self.spin_x_max)

        control_layout.addStretch()
        layout.addWidget(bottom_controls)

    def render_time_series_data(self, ts_data: dict):
        self.current_ts_data = ts_data.get("time_series", {})
        
        self.tree_series.blockSignals(True)
        self.tree_series.clear()

        for i, case_id in enumerate(self.case_ids_cache):
            case_name = self.case_names_cache[i]
            series_list = self.current_ts_data.get(str(case_id), [])
            
            if not series_list: continue

            case_node = QTreeWidgetItem(self.tree_series, [case_name])
            case_node.setFlags(case_node.flags() | Qt.ItemFlag.ItemIsAutoTristate | Qt.ItemFlag.ItemIsUserCheckable)
            case_node.setCheckState(0, Qt.CheckState.Unchecked)
            case_node.setExpanded(True)
            
            for idx, series in enumerate(series_list):
                real_name = series.get("series_name", f"Série {idx + 1}")
                child_name = f"{real_name} ({series.get('unit_y', 'MW')})"
                
                child_node = QTreeWidgetItem(case_node, [child_name])
                child_node.setFlags(child_node.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child_node.setCheckState(0, Qt.CheckState.Unchecked)
                child_node.setData(0, Qt.ItemDataRole.UserRole, series["values"])

        self.tree_series.blockSignals(False)
        self.plot_time_series()

    def plot_time_series(self, *args):
        self.ts_ax.clear()
        
        mode = self.combo_ts_unit.currentText()
        is_energy = "Energy" in mode
        
        plotted_any = False
        colors = self.chart_colors if self.combo_color.currentText() == "Padrão (Tailwind)" else ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442']

        def get_distinct_colors(base_hex, count):
            """Gera sub-cores rotacionando o Matiz (Hue) da cor base"""
            if count == 1: return [base_hex]
            rgb = mcolors.hex2color(base_hex)
            h, l, s = colorsys.rgb_to_hls(*rgb)
            return [mcolors.rgb2hex(colorsys.hls_to_rgb((h + (i * 0.85 / count)) % 1.0, l, s)) for i in range(count)]

        for i in range(self.tree_series.topLevelItemCount()):
            case_node = self.tree_series.topLevelItem(i)
            base_color = colors[i % len(colors)]
            
            num_children = case_node.childCount()
            sub_colors = get_distinct_colors(base_color, num_children)
            
            for j in range(num_children):
                child_node = case_node.child(j)
                child_node.setForeground(0, QColor(sub_colors[j]))
                
                if child_node.checkState(0) == Qt.CheckState.Checked:
                    raw_values = child_node.data(0, Qt.ItemDataRole.UserRole)
                    if not raw_values: continue
                    
                    y_vals = np.array(raw_values)
                    if is_energy:
                        y_vals = y_vals * 3600
                        
                    x_vals = np.arange(len(y_vals))
                    label = f"[{case_node.text(0)[:8]}...] {child_node.text(0)}"
                    
                    self.ts_ax.plot(x_vals, y_vals, color=sub_colors[j], linewidth=1.5, label=label)
                    plotted_any = True

        if plotted_any:
            self.ts_ax.set_title("Load Profile Comparison", pad=15, fontweight='bold', color='#1E293B', fontsize=14)
            self.ts_ax.set_xlabel("Time (Hours)", fontweight='bold')
            self.ts_ax.set_ylabel("Energy (Joules)" if is_energy else "Power (MW)", fontweight='bold')
            self.ts_ax.grid(True, linestyle='--', alpha=0.3)
            self.ts_ax.spines['top'].set_visible(False)
            self.ts_ax.spines['right'].set_visible(False)
            self.ts_ax.set_xlim(self.spin_x_min.value(), self.spin_x_max.value())
            
            self.ts_ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9, edgecolor='#CBD5E1', framealpha=0.9)
            self.ts_figure.subplots_adjust(right=0.7)
        else:
            self.ts_figure.subplots_adjust(right=0.95)

        self.ts_canvas.draw()

    def update_x_axis_limits(self):
        x_min = self.spin_x_min.value()
        x_max = self.spin_x_max.value()
        
        if x_min >= x_max:
            return

        self.ts_ax.set_xlim(x_min, x_max)
        self.ts_canvas.draw()

    def toggle_all_indicators_mode(self):
        """Desativa a seleção única de indicadores caso o usuário queira ver todos."""
        show_all = self.chk_show_all_indicators.isChecked()
        self.combo_bar_ind.setEnabled(not show_all)
        self.combo_sort_bar.setEnabled(not show_all)
        self.plot_bar()
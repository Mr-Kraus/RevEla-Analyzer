import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSplitter, QSpinBox, QMessageBox, QFrame, 
                             QAbstractItemView, QToolTip)
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

from ui.viewmodels.tab_summary_viewmodel import TabSummaryViewModel
from ui.services.settings_service import SettingsService

class NumericTableWidgetItem(QTableWidgetItem):
    """
    Subclasse para permitir a ordenação numérica real nas colunas da QTableWidget,
    ignorando a ordenação alfabética padrão (ex: evitar que '9' seja maior que '10').
    """
    def __lt__(self, other):
        try:
            return float(self.data(Qt.ItemDataRole.UserRole)) < float(other.data(Qt.ItemDataRole.UserRole))
        except (ValueError, TypeError):
            return super().__lt__(other)


class TabSummaryView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabSummaryViewModel()
        self.full_detailed_data = {} 
        
        # Variáveis de cache para o Tooltip do mouse
        self._current_x_positions = []
        self._current_names = []
        self._current_values = []
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # Estilo Flat, Moderno e Responsivo (Sem sombras)
        self.setStyleSheet("""
            QWidget {
                background-color: #F8FAFC;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #0F172A;
            }
            QComboBox, QSpinBox {
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 6px;
                background-color: #FFFFFF;
                min-width: 120px;
            }
            QComboBox::drop-down, QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background-color: #F1F5F9;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #CBD5E1;
                background-color: #FFFFFF;
                selection-background-color: #E0F2FE;
                selection-color: #0369A1;
                outline: 0px; 
            }
            QCheckBox {
                spacing: 8px;
                font-weight: bold;
                color: #334155;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #CBD5E1;
                background: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background: #0284C7;
                border: 1px solid #0284C7;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                alternate-background-color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #E2E8F0;
                color: #334155;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #CBD5E1;
                border-bottom: 2px solid #CBD5E1;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(8)
        
        # ==========================================
        # PAINEL ESQUERDO (Informações Gerais)
        # ==========================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        lbl_meta = QLabel("Informações Gerais")
        lbl_meta.setStyleSheet("font-weight: 900; font-size: 18px; color: #1E293B;")
        left_layout.addWidget(lbl_meta)
        
        self.table_meta = QTableWidget(0, 2)
        self.table_meta.setHorizontalHeaderLabels(["Parâmetro", "Valor"])
        self.table_meta.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_meta.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_meta.verticalHeader().setVisible(False)
        self.table_meta.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_meta.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(self.table_meta)
        
        # ==========================================
        # PAINEL DIREITO (Gráfico e Tabela Detalhada)
        # ==========================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # --- Controles Superiores do Gráfico ---
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px;")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(15, 10, 15, 10)
        
        self.combo_var = QComboBox()
        self.combo_var.addItems(["EPNS", "LOLE", "EENS", "LOLP"])
        
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Por Barra", "Por Região"])
        
        self.combo_chart_style = QComboBox()
        self.combo_chart_style.addItems(["Barras", "Linhas"])
        
        self.spin_top = QSpinBox()
        self.spin_top.setRange(5, 10000)
        self.spin_top.setValue(10000)
        self.spin_top.setPrefix("Máx Elem: ")
        
        self.check_pareto = QCheckBox("Curva de Pareto")
        self.check_pareto.setChecked(True)
        
        controls_layout.addWidget(QLabel("<b>Variável:</b>"))
        controls_layout.addWidget(self.combo_var)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(QLabel("<b>Visão:</b>"))
        controls_layout.addWidget(self.combo_type)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(QLabel("<b>Estilo:</b>"))
        controls_layout.addWidget(self.combo_chart_style)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(self.spin_top)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(self.check_pareto)
        controls_layout.addStretch()
        
        right_layout.addWidget(controls_frame)
        
        # --- Gráfico (PyQtGraph) ---
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', '#334155')
        pg.setConfigOptions(antialias=True)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMinimumHeight(350)
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
        right_layout.addWidget(self.plot_widget, stretch=3)
        
        # --- Tabela Inferior ---
        self.table_details = QTableWidget(0, 3)
        self.table_details.setHorizontalHeaderLabels(["Elemento", "Valor", "Contribuição %"])
        self.table_details.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_details.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_details.setAlternatingRowColors(True)
        self.table_details.verticalHeader().setVisible(False)
        self.table_details.setSortingEnabled(True)
        right_layout.addWidget(self.table_details, stretch=2)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([350, 850])
        layout.addWidget(main_splitter)

    def setup_connections(self):
        self.viewmodel.metadata_loaded.connect(self.populate_metadata)
        self.viewmodel.detailed_data_loaded.connect(self.process_detailed_data)
        self.viewmodel.error_occurred.connect(self.show_error)
        
        self.combo_var.currentTextChanged.connect(self.viewmodel.load_detailed_data)
        self.combo_type.currentIndexChanged.connect(self.update_chart_and_table)
        self.combo_chart_style.currentIndexChanged.connect(self.update_chart_and_table)
        self.spin_top.valueChanged.connect(self.update_chart_and_table)
        self.check_pareto.stateChanged.connect(self.update_chart_and_table)
        
        # Habilita o rastreamento do mouse para o Tooltip dinâmico
        self.plot_widget.scene().sigMouseMoved.connect(self.on_mouse_moved)

    def load_case(self, case_id: str):
        # Limpa caches e interface para não herdar dados do caso anterior
        self.full_detailed_data = {} 
        self.table_meta.setRowCount(0)
        self.table_details.setRowCount(0)
        self.plot_widget.clear()
        self.viewmodel.load_case_data(case_id)

    def populate_metadata(self, data: dict):
        settings = SettingsService.get_instance()
        self.table_meta.setRowCount(0)
        
        display_map = {
            "simulated_years": "Anos Simulados", "simulation_time": "Tempo de Simulação",
            "LOLE": "LOLE (h/ano)", "EPNS": "EPNS (MW)", "EENS": "EENS (MWh/ano)",
            "LOLP": "LOLP", "LOLF": "LOLF (occ/ano)", "LOLD": "LOLD (h/occ)"
        }
        
        for key, display_name in display_map.items():
            if key in data:
                val = data[key]
                if isinstance(val, dict): val = val.get("value", 0)
                
                if isinstance(val, (int, float)):
                    is_lolp = (key == "LOLP")
                    str_val = settings.format_number(val, is_table=True, is_lolp=is_lolp)
                else:
                    str_val = str(val)
                    
                row = self.table_meta.rowCount()
                self.table_meta.insertRow(row)
                
                item_title = QTableWidgetItem(display_name)
                item_title.setFont(self.table_meta.font())
                self.table_meta.setItem(row, 0, item_title)
                
                item_val = QTableWidgetItem(str_val)
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_meta.setItem(row, 1, item_val)

    def process_detailed_data(self, data):
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            self.full_detailed_data = data[0]
        elif isinstance(data, dict):
            self.full_detailed_data = data
        else:
            self.full_detailed_data = {}
            
        self.update_chart_and_table()

    def update_chart_and_table(self):
        if not hasattr(self, 'full_detailed_data') or not self.full_detailed_data:
            return
            
        settings = SettingsService.get_instance()
        top_n = self.spin_top.value()
        group_mode = self.combo_type.currentText()
        ind_key = self.combo_var.currentText()
        ind_key_lower = ind_key.lower()
        
        raw_list = []
        is_manual_grouping = False
        
        if group_mode == "Por Região":
            reg_data = self.full_detailed_data.get("region_aggregations", {})
            if isinstance(reg_data, dict) and reg_data:
                raw_list = reg_data.get("top_elements", [])
                if not raw_list:
                    # RETIRADO A TRAVA DOS FLOATS - Aceita os dicionários aninhados agora
                    raw_list = [{"element_name": k, "value": v} for k, v in reg_data.items()]
            elif isinstance(reg_data, list):
                raw_list = reg_data
            
            if not raw_list:
                is_manual_grouping = True
                buses_data = self.full_detailed_data.get("top_critical_buses", {})
                if isinstance(buses_data, dict):
                    raw_list = buses_data.get("top_elements", [])
                elif isinstance(buses_data, list):
                    raw_list = buses_data
        else:
            buses_data = self.full_detailed_data.get("top_critical_buses", {})
            if isinstance(buses_data, dict):
                raw_list = buses_data.get("top_elements", [])
            elif isinstance(buses_data, list):
                raw_list = buses_data
                
        processed_data = []
        for item in raw_list:
            if not isinstance(item, dict): continue
            
            if is_manual_grouping:
                name = item.get("region", item.get("region_name", "Região Desconhecida"))
            else:
                name = item.get("element_name", item.get("element_id", "Desconhecido"))
            
            val = item.get("value", item.get(ind_key_lower, item.get(ind_key, 0.0)))
            
            # Se for o dicionário aninhado (Ex: {"epns": 10.5}), extrai a chave certa!
            if isinstance(val, dict): 
                val = val.get(ind_key_lower, val.get(ind_key, 0.0))
                
            try: val = float(val)
            except: val = 0.0
                
            processed_data.append({"name": str(name), "value": val})

        if is_manual_grouping:
            grouped = {}
            for item in processed_data:
                grouped[item["name"]] = grouped.get(item["name"], 0.0) + item["value"]
            processed_data = [{"name": k, "value": v} for k, v in grouped.items()]

        # ORDENAÇÃO
        sorted_data = sorted(processed_data, key=lambda x: x["value"], reverse=True)
        top_data = sorted_data[:top_n]
        total_value = sum(item["value"] for item in sorted_data)
        
        # Atualiza variáveis para o Tooltip dinâmico
        self._current_names = [item["name"] for item in top_data]
        self._current_values = [item["value"] for item in top_data]
        self._current_x_positions = list(range(len(top_data)))
        
        # PREENCHE A TABELA
        self.table_details.setSortingEnabled(False)
        self.table_details.setRowCount(0)
        
        for row, item in enumerate(top_data):
            self.table_details.insertRow(row)
            val = item["value"]
            pct = (val / total_value * 100) if total_value > 0 else 0
            
            item_name = QTableWidgetItem(item["name"])
            self.table_details.setItem(row, 0, item_name)
            
            item_val = NumericTableWidgetItem(settings.format_number(val, is_table=True, is_lolp=(ind_key=="LOLP")))
            item_val.setData(Qt.ItemDataRole.UserRole, val)
            item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_details.setItem(row, 1, item_val)
            
            item_pct = NumericTableWidgetItem(f"{pct:.2f}%")
            item_pct.setData(Qt.ItemDataRole.UserRole, pct)
            item_pct.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_details.setItem(row, 2, item_pct)
            
        self.table_details.setSortingEnabled(True)

        # ==========================================
        # ATUALIZAÇÃO DO GRÁFICO E EIXO X SEGURO
        # ==========================================
        self.plot_widget.clear()
        
        if not top_data or total_value == 0: 
            self.plot_widget.setTitle(f"Nenhum valor numérico para {ind_key} ({group_mode})", color='#475569')
            return
        
        chart_style = self.combo_chart_style.currentText()
        
        if chart_style == "Barras":
            chart = pg.BarGraphItem(x=self._current_x_positions, height=self._current_values, width=0.6, brush='#3498DB', pen='#2980B9')
            self.plot_widget.addItem(chart)
        elif chart_style == "Linhas":
            chart = pg.PlotDataItem(x=self._current_x_positions, y=self._current_values, pen=pg.mkPen(color='#3498DB', width=3), symbol='o', symbolBrush='#FFFFFF', symbolPen='#2980B9')
            self.plot_widget.addItem(chart)
        
        x_axis = self.plot_widget.getAxis('bottom')
        
        # Trava de Segurança e Fallback para versões antigas do pyqtgraph
        if len(top_data) > 50:
            ticks = [list(zip(self._current_x_positions, [""] * len(self._current_names)))]
            self.plot_widget.setLabel('bottom', f"Textos ocultos ({len(top_data)} elementos). Consulte a tabela abaixo.")
            x_axis.setHeight(30)
        else:
            self.plot_widget.setLabel('bottom', "")
            if len(top_data) > 8:
                x_axis.setHeight(100)
                try:
                    # Rotação vertical: Necessita pyqtgraph >= 0.13.0
                    x_axis.setStyle(tickTextAngle=-90)
                    ticks = [list(zip(self._current_x_positions, self._current_names))]
                except Exception:
                    # PLANO B: Encurta o nome para caber na horizontal (Versões Antigas)
                    short_names = [n[:6] + ".." if len(n) > 6 else n for n in self._current_names]
                    ticks = [list(zip(self._current_x_positions, short_names))]
            else:
                x_axis.setHeight(30)
                ticks = [list(zip(self._current_x_positions, self._current_names))]
                try:
                    x_axis.setStyle(tickTextAngle=0)
                except Exception:
                    pass
                    
        x_axis.setTicks(ticks)
        self.plot_widget.setTitle(f"Distribuição: {ind_key} ({group_mode})", size='12pt', color='#1E293B', bold=True)
        
        # ==========================================
        # PARETO INTELIGENTE
        # ==========================================
        if self.check_pareto.isChecked() and total_value > 0:
            max_y = max(self._current_values) if self._current_values else 1
            pareto_threshold = getattr(settings, 'pareto_threshold', 85.0)
            
            acumulado = 0
            pareto_y = []
            
            found_threshold = False
            threshold_x = -1
            threshold_y = -1
            
            for i, val in enumerate(self._current_values):
                acumulado += val
                pct_real = (acumulado / total_value) * 100
                pct_scaled = (acumulado / total_value) * max_y
                pareto_y.append(pct_scaled)
                
                if not found_threshold and pct_real >= pareto_threshold:
                    found_threshold = True
                    threshold_x = i
                    threshold_y = pct_scaled
                    
            pareto_line = pg.PlotDataItem(x=self._current_x_positions, y=pareto_y, pen=pg.mkPen(color='#E74C3C', width=1.5, style=Qt.PenStyle.SolidLine))
            self.plot_widget.addItem(pareto_line)
            
            if found_threshold:
                target_point = pg.ScatterPlotItem(x=[threshold_x], y=[threshold_y], size=10, pen=pg.mkPen(color='#FFFFFF', width=2), brush='#C0392B')
                self.plot_widget.addItem(target_point)
                text_item = pg.TextItem(f"{pareto_threshold}% Threshold", color='#C0392B', anchor=(0, 1.5))
                text_item.setPos(threshold_x, threshold_y)
                self.plot_widget.addItem(text_item)

    def on_mouse_moved(self, evt):
        """
        Evento disparado quando o mouse se move sobre o gráfico.
        Mapeia a posição do mouse e verifica se está sobre uma barra/linha para exibir o tooltip.
        """
        if not hasattr(self, '_current_x_positions') or not self._current_x_positions:
            return

        pos = evt
        # Verifica se o cursor está dentro da área de desenho do gráfico
        if self.plot_widget.sceneBoundingRect().contains(pos):
            # Mapeia as coordenadas de pixel para as coordenadas matemáticas (x, y) do gráfico
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            x_val = mouse_point.x()
            y_val = mouse_point.y()

            # Descobre o índice da barra mais próxima no eixo X
            closest_idx = int(round(x_val))

            if 0 <= closest_idx < len(self._current_x_positions):
                bar_x = self._current_x_positions[closest_idx]
                bar_y = self._current_values[closest_idx]
                name = self._current_names[closest_idx]
                chart_style = self.combo_chart_style.currentText()

                is_hovering = False
                
                # Tolerância no eixo X (a largura da barra é 0.6, então consideramos +/- 0.3)
                if abs(x_val - bar_x) <= 0.3:
                    if chart_style == "Barras":
                        # Na barra, o Y do mouse deve estar entre 0 e a altura máxima da barra
                        if 0 <= y_val <= bar_y:
                            is_hovering = True
                    else: # Gráfico de Linhas
                        # Tolerância dinâmica no eixo Y para facilitar acertar o ponto da linha
                        y_range = self.plot_widget.plotItem.vb.viewRange()[1]
                        y_tolerance = (y_range[1] - y_range[0]) * 0.1 
                        if abs(y_val - bar_y) <= y_tolerance:
                            is_hovering = True

                if is_hovering:
                    settings = SettingsService.get_instance()
                    is_lolp = (self.combo_var.currentText() == "LOLP")
                    val_str = settings.format_number(bar_y, is_lolp=is_lolp)
                    
                    # Exibe o Tooltip nativo no cursor do mouse
                    QToolTip.showText(QCursor.pos(), f"Elemento: {name}\nValor: {val_str}", self.plot_widget)
                    return

        # Se sair das barras ou da área, oculta o balãozinho
        QToolTip.hideText()

    def show_error(self, msg):
        QMessageBox.warning(self, "Aviso da API", msg)
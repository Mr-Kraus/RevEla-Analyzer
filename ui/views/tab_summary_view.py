from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QSplitter, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from ui.viewmodels.tab_summary_viewmodel import TabSummaryViewModel
from ui.services.settings_service import SettingsService

class TabSummaryView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabSummaryViewModel()
        self.raw_detailed_data = [] # Guarda os dados puros vindos da API
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ==========================================
        # PAINEL ESQUERDO (Metadados e Globais)
        # ==========================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        lbl_meta = QLabel("Resumo do Caso")
        lbl_meta.setStyleSheet("font-weight: bold; font-size: 16px; color: #2C3E50;")
        left_layout.addWidget(lbl_meta)
        
        self.table_meta = QTableWidget(0, 2)
        self.table_meta.setHorizontalHeaderLabels(["Parâmetro", "Valor"])
        self.table_meta.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_meta.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table_meta)
        
        # ==========================================
        # PAINEL DIREITO (Gráfico e Tabela Detalhada)
        # ==========================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # --- Controles Superiores do Gráfico ---
        controls_layout = QHBoxLayout()
        
        self.combo_var = QComboBox()
        self.combo_var.addItems(["EPNS", "LOLE", "EENS", "LOLP"])
        
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Por Barra", "Por Região"])
        
        # NOVO: Controle de estilo visual do gráfico
        self.combo_chart_style = QComboBox()
        self.combo_chart_style.addItems(["Barras", "Linhas"])
        
        self.spin_top = QSpinBox()
        self.spin_top.setRange(5, 500)
        self.spin_top.setValue(20)
        self.spin_top.setPrefix("Top: ")
        
        self.check_pareto = QCheckBox("Mostrar Pareto")
        
        controls_layout.addWidget(QLabel("Variável:"))
        controls_layout.addWidget(self.combo_var)
        controls_layout.addWidget(self.combo_type)
        controls_layout.addWidget(self.combo_chart_style)
        controls_layout.addWidget(self.spin_top)
        controls_layout.addWidget(self.check_pareto)
        controls_layout.addStretch()
        right_layout.addLayout(controls_layout)
        
        # --- Gráfico (PyQtGraph) ---
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', '#2C3E50')
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setFixedHeight(300)
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
        right_layout.addWidget(self.plot_widget)
        
        # --- Tabela Inferior ---
        self.table_details = QTableWidget(0, 3)
        self.table_details.setHorizontalHeaderLabels(["Elemento", "Valor", "Contribuição %"])
        self.table_details.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_details.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        right_layout.addWidget(self.table_details)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 700])
        layout.addWidget(main_splitter)

    def setup_connections(self):
        self.viewmodel.metadata_loaded.connect(self.populate_metadata)
        self.viewmodel.detailed_data_loaded.connect(self.process_detailed_data)
        self.viewmodel.error_occurred.connect(self.show_error)
        # O único que vai na API buscar dados novos é a troca de Variável (EPNS -> LOLE)
        self.combo_var.currentTextChanged.connect(self.viewmodel.load_detailed_data)
        
        # Todos os outros botões apenas recarregam a memória instantaneamente
        self.combo_type.currentIndexChanged.connect(self.update_chart_and_table)
        self.combo_chart_style.currentIndexChanged.connect(self.update_chart_and_table)
        self.spin_top.valueChanged.connect(self.update_chart_and_table)
        self.check_pareto.stateChanged.connect(self.update_chart_and_table)

    def load_case(self, case_id: str):
        self.table_meta.setRowCount(0)
        self.table_details.setRowCount(0)
        self.plot_widget.clear()
        self.viewmodel.load_case_data(case_id)

    def populate_metadata(self, data: dict):
        settings = SettingsService.get_instance()
        self.table_meta.setRowCount(0)
        
        display_map = {
            "simulated_years": "Anos Simulados", "simulation_time": "Tempo de Simulação (s)",
            "LOLE": "LOLE (h/ano)", "EPNS": "EPNS (MW)", "EENS": "EENS (MWh)",
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
                self.table_meta.setItem(row, 0, QTableWidgetItem(display_name))
                self.table_meta.setItem(row, 1, QTableWidgetItem(str_val))

    def process_detailed_data(self, data):
        """Salva o pacote completo de dados para alternarmos rapidamente na tela."""
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
        
        # ==========================================
        # 1. ABRINDO AS GAVETAS (Com Plano B)
        # ==========================================
        raw_list = []
        is_manual_grouping = False
        
        if group_mode == "Por Região":
            reg_data = self.full_detailed_data.get("region_aggregations", {})
            if isinstance(reg_data, dict) and reg_data:
                raw_list = reg_data.get("top_elements", [])
                if not raw_list:
                    raw_list = [{"element_name": k, "value": v} for k, v in reg_data.items() if isinstance(v, (int, float))]
            elif isinstance(reg_data, list):
                raw_list = reg_data
            
            # PLANO B: Se a gaveta de regiões veio vazia, pegamos as barras para somar!
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
                
        # ==========================================
        # 2. EXTRAÇÃO DOS VALORES
        # ==========================================
        processed_data = []
        for item in raw_list:
            if not isinstance(item, dict): continue
            
            # Se for agrupamento manual, o nome tem que ser a região
            if is_manual_grouping:
                name = item.get("region", item.get("region_name", "Região Desconhecida"))
            else:
                name = item.get("element_name", item.get("element_id", "Desconhecido"))
            
            val = item.get("value", item.get(ind_key_lower, item.get(ind_key, 0.0)))
            if isinstance(val, dict):
                val = val.get("value", 0.0)
                
            try:
                val = float(val)
            except:
                val = 0.0
                
            processed_data.append({"name": str(name), "value": val})

        # ==========================================
        # 2.5 SOMA MATEMÁTICA (AGRUPAMENTO)
        # ==========================================
        if is_manual_grouping:
            grouped = {}
            for item in processed_data:
                grouped[item["name"]] = grouped.get(item["name"], 0.0) + item["value"]
            processed_data = [{"name": k, "value": v} for k, v in grouped.items()]

        # ==========================================
        # 3. ORDENAÇÃO E TABELA
        # ==========================================
        sorted_data = sorted(processed_data, key=lambda x: x["value"], reverse=True)
        top_data = sorted_data[:top_n]
        total_value = sum(item["value"] for item in sorted_data)
        
        self.table_details.setRowCount(0)
        for row, item in enumerate(top_data):
            self.table_details.insertRow(row)
            val = item["value"]
            pct = (val / total_value * 100) if total_value > 0 else 0
            
            self.table_details.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.table_details.setItem(row, 1, QTableWidgetItem(settings.format_number(val, is_table=True)))
            self.table_details.setItem(row, 2, QTableWidgetItem(f"{pct:.2f}%"))

        # ==========================================
        # 4. ATUALIZAÇÃO DO GRÁFICO (PyQtGraph)
        # ==========================================
        self.plot_widget.clear()
        
        if not top_data or total_value == 0: 
            self.plot_widget.setTitle(f"Nenhum valor numérico encontrado para {ind_key} ({group_mode})")
            return
        
        x_positions = list(range(len(top_data)))
        y_values = [item["value"] for item in top_data]
        names = [item["name"] for item in top_data]
        
        chart_style = self.combo_chart_style.currentText()
        
        if chart_style == "Barras":
            chart = pg.BarGraphItem(x=x_positions, height=y_values, width=0.6, brush='#3498DB')
            self.plot_widget.addItem(chart)
        elif chart_style == "Linhas":
            chart = pg.PlotDataItem(x=x_positions, y=y_values, pen=pg.mkPen(color='#3498DB', width=3), symbol='o', symbolBrush='#2980B9')
            self.plot_widget.addItem(chart)
        
        ticks = [list(zip(x_positions, names))]
        x_axis = self.plot_widget.getAxis('bottom')
        x_axis.setTicks(ticks)
        self.plot_widget.setTitle(f"Top {len(top_data)} contribuições para {ind_key} ({group_mode})")
        
        if self.check_pareto.isChecked() and total_value > 0:
            max_y = max(y_values) if y_values else 1
            acumulado = 0
            pareto_y = []
            for val in y_values:
                acumulado += val
                pct_acumulado = (acumulado / total_value) * max_y
                pareto_y.append(pct_acumulado)
                
            pareto_line = pg.PlotDataItem(x=x_positions, y=pareto_y, pen=pg.mkPen(color='#E74C3C', width=3), symbol='t', symbolBrush='#C0392B')
            self.plot_widget.addItem(pareto_line)
    def show_error(self, msg):
        QMessageBox.warning(self, "Aviso da API", msg)
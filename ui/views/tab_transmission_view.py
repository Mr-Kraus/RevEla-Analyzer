from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLineEdit, QTabWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.viewmodels.tab_transmission_viewmodel import TabTransmissionViewModel

class TabTransmissionView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabTransmissionViewModel()
        self.raw_data = {}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. CARDS DE KPI (Resumo de Transmissão)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_lines = self._create_kpi_card("Linhas de Transmissão", "0", "#2980B9")
        self.card_trafos = self._create_kpi_card("Transformadores", "0", "#8E44AD")
        self.card_capacity = self._create_kpi_card("Capacidade Total (MVA)", "0.0", "#27AE60")
        self.card_fail_rate = self._create_kpi_card("Taxa Média Falhas (f/ano)", "0.0", "#E67E22")

        kpi_layout.addWidget(self.card_lines)
        kpi_layout.addWidget(self.card_trafos)
        kpi_layout.addWidget(self.card_capacity)
        kpi_layout.addWidget(self.card_fail_rate)
        main_layout.addLayout(kpi_layout)

        # 2. BARRA DE BUSCA
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filtrar por nome do equipamento ou barra...")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px 12px; border: 1px solid #BDC3C7; 
                border-radius: 6px; background-color: white; font-size: 13px;
            }
        """)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # 3. ABAS SECUNDÁRIAS (Linhas vs Transformadores)
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #D5D8DC; background: white; border-radius: 6px; }
            QTabBar::tab { background: #EBEDEF; padding: 8px 20px; font-weight: bold; color: #2C3E50; }
            QTabBar::tab:selected { background: white; color: #2980B9; border-top: 3px solid #2980B9; }
        """)

        # Tabela de Linhas
        self.table_lines = self._create_table(["ID Ext.", "Nome", "Barra Origem", "Barra Destino", "R (pu)", "X (pu)", "Cap. (MVA)", "Taxa Falha (f/ano)", "T. Reparo (h)"])
        # Tabela de Transformadores
        self.table_trafos = self._create_table(["ID Ext.", "Nome", "Barra Origem", "Barra Destino", "R (pu)", "X (pu)", "Cap. (MVA)", "Taxa Falha (f/ano)", "T. Reparo (h)"])

        self.sub_tabs.addTab(self.table_lines, "⚡ Linhas de Transmissão")
        self.sub_tabs.addTab(self.table_trafos, "🔄 Transformadores")

        main_layout.addWidget(self.sub_tabs)

    def _create_kpi_card(self, title: str, initial_val: str, color_hex: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white; border-left: 5px solid {color_hex};
                border-radius: 6px; border-top: 1px solid #E5E7EB;
                border-right: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB;
            }}
        """)
        card.setFixedHeight(75)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 8, 15, 8)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7F8C8D; font-size: 11px; font-weight: bold;")
        
        lbl_value = QLabel(initial_val)
        lbl_value.setStyleSheet("color: #2C3E50; font-size: 20px; font-weight: bold;")
        card.lbl_value = lbl_value # Atribui para fácil atualização posterior

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return card

    def _create_table(self, headers: list) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)
        table.setStyleSheet("""
            QTableWidget { background-color: white; border: none; }
            QHeaderView::section { background-color: #F4F6F7; font-weight: bold; color: #34495E; padding: 6px; border: none; }
        """)
        return table

    def setup_connections(self):
        self.viewmodel.transmission_data_ready.connect(self.on_data_received)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.search_input.textChanged.connect(self.apply_filter)

    def load_case(self, case_id: str):
        self.viewmodel.load_transmission(case_id)

    def on_data_received(self, data: dict):
        self.raw_data = data
        summary = data.get("summary", {})

        # Atualiza KPIs
        self.card_lines.lbl_value.setText(str(summary.get("total_lines", 0)))
        self.card_trafos.lbl_value.setText(str(summary.get("total_transformers", 0)))
        self.card_capacity.lbl_value.setText(f"{summary.get('total_capacity_mva', 0.0):,.1f}")
        self.card_fail_rate.lbl_value.setText(f"{summary.get('avg_failure_rate', 0.0):.4f}")

        # Popula Tabelas
        self.populate_lines(data.get("lines", []))
        self.populate_trafos(data.get("transformers", []))

    def populate_lines(self, lines: list):
        self.table_lines.setSortingEnabled(False)
        self.table_lines.setRowCount(0)
        for row, item in enumerate(lines):
            self.table_lines.insertRow(row)
            self.table_lines.setItem(row, 0, QTableWidgetItem(item.get("external_id")))
            self.table_lines.setItem(row, 1, QTableWidgetItem(item.get("name")))
            self.table_lines.setItem(row, 2, QTableWidgetItem(item.get("from_bus")))
            self.table_lines.setItem(row, 3, QTableWidgetItem(item.get("to_bus")))
            self.table_lines.setItem(row, 4, QTableWidgetItem(f"{item.get('r_pu'):.5f}"))
            self.table_lines.setItem(row, 5, QTableWidgetItem(f"{item.get('x_pu'):.5f}"))
            self.table_lines.setItem(row, 6, QTableWidgetItem(f"{item.get('capacity_mva'):.1f}"))
            self.table_lines.setItem(row, 7, QTableWidgetItem(f"{item.get('failure_rate'):.4f}"))
            self.table_lines.setItem(row, 8, QTableWidgetItem(f"{item.get('repair_time'):.2f}"))
        self.table_lines.setSortingEnabled(True)

    def populate_trafos(self, trafos: list):
        self.table_trafos.setSortingEnabled(False)
        self.table_trafos.setRowCount(0)
        for row, item in enumerate(trafos):
            self.table_trafos.insertRow(row)
            self.table_trafos.setItem(row, 0, QTableWidgetItem(item.get("external_id")))
            self.table_trafos.setItem(row, 1, QTableWidgetItem(item.get("name")))
            self.table_trafos.setItem(row, 2, QTableWidgetItem(item.get("from_bus")))
            self.table_trafos.setItem(row, 3, QTableWidgetItem(item.get("to_bus")))
            self.table_trafos.setItem(row, 4, QTableWidgetItem(f"{item.get('r_pu'):.5f}"))
            self.table_trafos.setItem(row, 5, QTableWidgetItem(f"{item.get('x_pu'):.5f}"))
            self.table_trafos.setItem(row, 6, QTableWidgetItem(f"{item.get('capacity_mva'):.1f}"))
            self.table_trafos.setItem(row, 7, QTableWidgetItem(f"{item.get('failure_rate'):.4f}"))
            self.table_trafos.setItem(row, 8, QTableWidgetItem(f"{item.get('repair_time'):.2f}"))
        self.table_trafos.setSortingEnabled(True)

    def apply_filter(self, text: str):
        text = text.lower()
        
        filtered_lines = [
            l for l in self.raw_data.get("lines", [])
            if text in l["name"].lower() or text in l["from_bus"].lower() or text in l["to_bus"].lower()
        ]
        filtered_trafos = [
            t for t in self.raw_data.get("transformers", [])
            if text in t["name"].lower() or text in t["from_bus"].lower() or text in t["to_bus"].lower()
        ]

        self.populate_lines(filtered_lines)
        self.populate_trafos(filtered_trafos)

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Aviso de Transmissão", msg)
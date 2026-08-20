from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLineEdit, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.viewmodels.tab_generation_viewmodel import TabGenerationViewModel

class TabGenerationView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = TabGenerationViewModel()
        self.raw_data = []
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. CARDS DE KPI (Resumo de Geração)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_total = self._create_kpi_card("Total de Unidades", "0", "#2980B9")
        self.card_capacity = self._create_kpi_card("Capacidade Instalada (MW)", "0.0", "#27AE60")
        self.card_fail_rate = self._create_kpi_card("Taxa Média Falhas (%)", "0.0", "#E74C3C")

        kpi_layout.addWidget(self.card_total)
        kpi_layout.addWidget(self.card_capacity)
        kpi_layout.addWidget(self.card_fail_rate)
        main_layout.addLayout(kpi_layout)

        # 2. BARRA DE BUSCA
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filtrar por nome do gerador, tecnologia ou barra...")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px 12px; border: 1px solid #BDC3C7; 
                border-radius: 6px; background-color: white; font-size: 13px;
            }
        """)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # 3. TABELA DE GERADORES
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID Ext.", "Nome", "Tecnologia", "Barra de Conexão", "Cap. (MW)", "Taxa Falha (%)", "T. Reparo (h)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; border-radius: 6px; }
            QHeaderView::section { background-color: #F4F6F7; font-weight: bold; color: #34495E; padding: 6px; border: none; }
        """)
        main_layout.addWidget(self.table)

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
        card.lbl_value = lbl_value 

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return card

    def setup_connections(self):
        self.viewmodel.generation_data_ready.connect(self.on_data_received)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.search_input.textChanged.connect(self.apply_filter)

    def load_case(self, case_id: str):
        self.viewmodel.load_generation(case_id)

    def on_data_received(self, data: dict):
        self.raw_data = data.get("generators", [])
        summary = data.get("summary", {})

        # Atualiza KPIs
        self.card_total.lbl_value.setText(str(summary.get("total_generators", 0)))
        self.card_capacity.lbl_value.setText(f"{summary.get('total_capacity_mw', 0.0):,.2f}")
        self.card_fail_rate.lbl_value.setText(f"{summary.get('avg_failure_rate', 0.0):.4f}")

        # Popula Tabela
        self.populate_table(self.raw_data)

    def populate_table(self, generators: list):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        for row, item in enumerate(generators):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item.get("external_id")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("name")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("technology")))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("bus")))
            
            # Formatação numérica
            cap_item = QTableWidgetItem()
            cap_item.setData(Qt.ItemDataRole.DisplayRole, item.get("capacity_mw"))
            self.table.setItem(row, 4, cap_item)
            
            fail_item = QTableWidgetItem()
            fail_item.setData(Qt.ItemDataRole.DisplayRole, item.get("failure_rate"))
            self.table.setItem(row, 5, fail_item)
            
            rep_item = QTableWidgetItem()
            rep_item.setData(Qt.ItemDataRole.DisplayRole, item.get("repair_time"))
            self.table.setItem(row, 6, rep_item)
            
        self.table.setSortingEnabled(True)

    def apply_filter(self, text: str):
        text = text.lower()
        filtered = [
            g for g in self.raw_data
            if text in g["name"].lower() or text in g["bus"].lower() or text in g["technology"].lower()
        ]
        self.populate_table(filtered)

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Aviso de Geração", msg)
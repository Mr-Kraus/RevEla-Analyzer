from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from ui.viewmodels.dashboard_viewmodel import DashboardViewModel

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = DashboardViewModel()
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)

        # ==========================================
        # LINHA DE CARDS DE RESUMO
        # ==========================================
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.card_total = self.create_stat_card("Casos Cadastrados", "-")
        self.card_ready = self.create_stat_card("Casos Prontos", "-")
        self.card_date = self.create_stat_card("Última Importação", "-")
        self.card_db = self.create_stat_card("Status do Banco", "Verificando...")

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_ready)
        cards_layout.addWidget(self.card_date)
        cards_layout.addWidget(self.card_db)
        
        layout.addLayout(cards_layout)

        # ==========================================
        # TABELA DE CASOS RECENTES
        # ==========================================
        subtitle = QLabel("Casos Recentes")
        subtitle.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495E; margin-top: 20px;")
        layout.addWidget(subtitle)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nome", "Descrição", "Status", "ID"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border-radius: 5px; border: 1px solid #D5D8DC; }
            QHeaderView::section { background-color: #ECF0F1; font-weight: bold; padding: 5px; border: none; }
        """)
        layout.addWidget(self.table)

    def create_stat_card(self, title_text: str, value_text: str) -> QFrame:
        """Cria um Card visual elegante para os indicadores rápidos."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 8px; border: 1px solid #E5E7EB; }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title_text)
        lbl_title.setStyleSheet("color: #7F8C8D; font-size: 14px; font-weight: bold; border: none;")
        
        lbl_value = QLabel(value_text)
        lbl_value.setStyleSheet("color: #2C3E50; font-size: 24px; font-weight: bold; border: none;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        # Guardamos a referência do valor para podermos atualizar depois
        frame.value_label = lbl_value 
        return frame

    def setup_connections(self):
        self.viewmodel.stats_updated.connect(self.update_stats)
        self.viewmodel.recent_cases_loaded.connect(self.update_table)
    
    def load_data(self):
        """Método chamado pela MainWindow quando esta aba é aberta."""
        self.viewmodel.load_dashboard_data()

    def update_stats(self, stats: dict):
        self.card_total.value_label.setText(str(stats.get("total_cases", 0)))
        self.card_ready.value_label.setText(str(stats.get("ready_cases", 0)))
        self.card_date.value_label.setText(stats.get("last_import", "-"))
        self.card_db.value_label.setText(stats.get("db_status", "Offline"))
        self.card_db.value_label.setStyleSheet("color: #27AE60; font-size: 24px; font-weight: bold; border: none;")

    def update_table(self, cases: list):
        self.table.setRowCount(len(cases))
        for row, case in enumerate(cases):
            self.table.setItem(row, 0, QTableWidgetItem(case.get("external_name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(case.get("display_name", "")))
            
            status_item = QTableWidgetItem(case.get("status", ""))
            # Pinta o status de verde se estiver pronto
            if case.get("status") == "READY":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
                
            self.table.setItem(row, 2, status_item)
            self.table.setItem(row, 3, QTableWidgetItem(case.get("id", "")))
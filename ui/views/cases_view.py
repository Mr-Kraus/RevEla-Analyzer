from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLineEdit, QFileDialog, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt
from ui.viewmodels.cases_viewmodel import CasesViewModel

class CasesView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = CasesViewModel()
        self.progress_dialog = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Cabeçalho da Tela
        title = QLabel("Gestão de Casos")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        
        # Barra Superior (Busca e Botão Importar)
        top_bar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar caso por nome...")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("padding: 5px; border: 1px solid #BDC3C7; border-radius: 4px;")
        
        self.btn_import = QPushButton("➕ Importar Novo Caso")
        self.btn_import.setFixedHeight(35)
        self.btn_import.setStyleSheet("""
            QPushButton { background-color: #27AE60; color: white; font-weight: bold; border-radius: 4px; padding: 0 15px; }
            QPushButton:hover { background-color: #2ECC71; }
        """)
        
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_import)

        # Tabela de Casos
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nome", "Caminho (Source)", "Status", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; }
            QHeaderView::section { background-color: #ECF0F1; font-weight: bold; padding: 5px; border: none; }
        """)

        # Montando o layout
        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.table)

    def setup_connections(self):
        # Botões
        self.btn_import.clicked.connect(self.handle_import_click)
        
        # Sinais do ViewModel
        self.viewmodel.cases_loaded.connect(self.populate_table)
        self.viewmodel.error_occurred.connect(self.show_error)
        
        # Sinais de Importação
        self.viewmodel.import_started.connect(self.show_loading)
        self.viewmodel.import_success.connect(self.hide_loading_success)
        self.viewmodel.import_failed.connect(self.hide_loading_error)

    def load_data(self):
        """Chamado pela MainWindow quando entra nesta aba"""
        self.viewmodel.load_cases()

    def populate_table(self, cases: list):
        self.table.setRowCount(0) # Limpa a tabela
        for row, case in enumerate(cases):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(case.get("display_name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(case.get("source_path", "")))
            
            status = case.get("status", "")
            item_status = QTableWidgetItem(status)
            if status == "READY":
                item_status.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 2, item_status)
            
            # Botão de Ação Placeholder (Excluir/Analisar)
            btn_action = QPushButton("Analisar")
            btn_action.setStyleSheet("background-color: #3498DB; color: white;")
            self.table.setCellWidget(row, 3, btn_action)

    def handle_import_click(self):
        # Abre o seletor nativo de diretórios (File Picker)
        folder_path = QFileDialog.getExistingDirectory(self, "Selecione a pasta do Caso")
        if folder_path:
            # Substitui barras invertidas para não quebrar o JSON no servidor Windows
            folder_path = folder_path.replace("\\", "/")
            self.viewmodel.import_case(folder_path)

    def show_loading(self):
        # Trava a tela enquanto importa (Seção 25 - Feedback Visual)
        self.progress_dialog = QProgressDialog("Processando caso no servidor. Isso pode levar alguns segundos...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Importando...")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setCancelButton(None) # Impede o usuário de cancelar a request
        self.progress_dialog.show()

    def hide_loading_success(self, msg):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.information(self, "Sucesso", msg)

    def hide_loading_error(self, msg):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.warning(self, "Erro na Importação", msg)

    def show_error(self, msg):
        QMessageBox.critical(self, "Erro", msg)
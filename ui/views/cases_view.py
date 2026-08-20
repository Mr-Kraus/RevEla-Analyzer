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
        
        # Barra Superior (Busca e Botões)
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

        # NOVO: Criação visual do Botão de Excluir que estava faltando
        self.btn_delete_case = QPushButton("🗑️ Excluir Caso")
        self.btn_delete_case.setFixedHeight(35)
        self.btn_delete_case.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; font-weight: bold; border-radius: 4px; padding: 0 15px; }
            QPushButton:hover { background-color: #C0392B; }
        """)
        
        top_bar.addWidget(self.search_input)
        top_bar.addWidget(self.btn_import)
        top_bar.addWidget(self.btn_delete_case)

        # Tabela de Casos
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nome", "Caminho (Source)", "Status", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Seleciona a linha inteira ao clicar
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; }
            QHeaderView::section { background-color: #ECF0F1; font-weight: bold; padding: 5px; border: none; }
        """)

        # Montando o layout
        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.table)

    def setup_connections(self):
        # Conexões de Botões
        self.btn_import.clicked.connect(self.handle_import_click)
        self.btn_delete_case.clicked.connect(self.confirm_and_delete_case)
        
        # Sinais do ViewModel (Listagem e Erros)
        self.viewmodel.cases_loaded.connect(self.populate_table)
        self.viewmodel.error_occurred.connect(self.show_error)
        
        # Sinais de Importação
        self.viewmodel.import_started.connect(self.show_loading)
        self.viewmodel.import_success.connect(self.hide_loading_success)
        self.viewmodel.import_failed.connect(self.hide_loading_error)

        # Sinais de Exclusão
        self.viewmodel.case_deleted.connect(self.on_case_deleted_success)

    def load_data(self):
        """Chamado pela MainWindow quando entra nesta aba"""
        self.viewmodel.load_cases()

    def populate_table(self, cases: list):
        self.table.setRowCount(0) # Limpa a tabela
        for row, case in enumerate(cases):
            self.table.insertRow(row)
            
            # Criamos o item do nome e salvamos o ID do banco de dados dentro dele (escondido)
            item_name = QTableWidgetItem(case.get("display_name", ""))
            item_name.setData(Qt.ItemDataRole.UserRole, case.get("id")) 
            self.table.setItem(row, 0, item_name)
            
            self.table.setItem(row, 1, QTableWidgetItem(case.get("source_path", "")))
            
            status = case.get("status", "")
            item_status = QTableWidgetItem(status)
            if status == "READY":
                item_status.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 2, item_status)
            
            # Botão de Ação Placeholder
            btn_action = QPushButton("Analisar")
            btn_action.setStyleSheet("background-color: #3498DB; color: white;")
            self.table.setCellWidget(row, 3, btn_action)

    def get_selected_case_id(self):
        """Descobre qual linha está selecionada e resgata o ID escondido."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        
        # Pega a linha do primeiro item selecionado
        row = selected_items[0].row()
        item = self.table.item(row, 0)
        
        # Retorna o ID que guardamos no Qt.UserRole
        return item.data(Qt.ItemDataRole.UserRole)

    def handle_import_click(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Selecione a pasta do Caso")
        if folder_path:
            folder_path = folder_path.replace("\\", "/")
            self.viewmodel.import_case(folder_path)

    def show_loading(self):
        self.progress_dialog = QProgressDialog("Processando caso no servidor. Isso pode levar alguns segundos...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Importando...")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setCancelButton(None) 
        self.progress_dialog.show()

    def hide_loading_success(self, msg):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.information(self, "Sucesso", msg)

    def hide_loading_error(self, msg):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.warning(self, "Erro na Importação", msg)

    def confirm_and_delete_case(self):
        selected_case_id = self.get_selected_case_id() 
        
        if not selected_case_id:
            QMessageBox.warning(self, "Aviso", "Selecione um caso na lista clicando nele para excluir.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este caso?\nTodas as simulações, topologia e resultados associados serão removidos permanentemente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.viewmodel.delete_case(selected_case_id)

    def on_case_deleted_success(self, case_id: str):
        QMessageBox.information(self, "Sucesso", "Caso excluído com sucesso do registro.")

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erro", msg)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLineEdit, QFileDialog, QMessageBox, 
    QProgressDialog, QMenu, QDialog, QDialogButtonBox, QInputDialog
)
from PyQt6.QtCore import Qt
from ui.viewmodels.cases_viewmodel import CasesViewModel
import os


class CaseConfigDialog(QDialog):
    """Modal de Configurações do Caso: Renomear e Definir Apelidos das Regiões"""
    def __init__(self, parent, case_id: str, current_name: str, viewmodel: CasesViewModel):
        super().__init__(parent)
        self.case_id = case_id
        self.viewmodel = viewmodel
        self.setWindowTitle("Configurações do Caso e Regiões")
        self.resize(550, 450)
        self.setup_ui(current_name)
        self.setup_connections()
        self.viewmodel.load_regions(self.case_id)

    def setup_ui(self, current_name: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 1. Nome Fictício do Caso
        lbl_name = QLabel("Nome Fictício / Exibição do Caso:")
        lbl_name.setStyleSheet("font-weight: bold; color: #2C3E50;")
        self.txt_case_name = QLineEdit(current_name)
        self.txt_case_name.setFixedHeight(35)
        self.txt_case_name.setStyleSheet("padding: 5px; border: 1px solid #BDC3C7; border-radius: 4px;")
        
        layout.addWidget(lbl_name)
        layout.addWidget(self.txt_case_name)

        # 2. Tabela de Apelidos de Região
        lbl_regions = QLabel("Apelidos das Regiões (Exibidos em Gráficos e Tabelas):")
        lbl_regions.setStyleSheet("font-weight: bold; color: #2C3E50;")
        
        self.table_regions = QTableWidget(0, 3)
        self.table_regions.setHorizontalHeaderLabels(["Cód. Ext.", "Nome Original", "Apelido (Custom)"])
        self.table_regions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_regions.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; }
            QHeaderView::section { background-color: #ECF0F1; font-weight: bold; padding: 5px; }
        """)

        layout.addWidget(lbl_regions)
        layout.addWidget(self.table_regions)

        # Botões do Diálogo
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.save_changes)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def setup_connections(self):
        self.viewmodel.regions_loaded.connect(self.populate_regions)

    def populate_regions(self, regions: list):
        self.table_regions.setRowCount(0)
        for row, reg in enumerate(regions):
            self.table_regions.insertRow(row)
            
            # ID oculto no Item
            item_ext = QTableWidgetItem(str(reg.get("external_id", "")))
            item_ext.setData(Qt.ItemDataRole.UserRole, reg.get("id"))
            item_ext.setFlags(item_ext.flags() ^ Qt.ItemFlag.ItemIsEditable) # Leitura
            
            item_orig = QTableWidgetItem(str(reg.get("name", "")))
            item_orig.setFlags(item_orig.flags() ^ Qt.ItemFlag.ItemIsEditable) # Leitura
            
            item_alias = QTableWidgetItem(str(reg.get("alias", ""))) # Editável
            
            self.table_regions.setItem(row, 0, item_ext)
            self.table_regions.setItem(row, 1, item_orig)
            self.table_regions.setItem(row, 2, item_alias)

    def save_changes(self):
        new_case_name = self.txt_case_name.text().strip()
        if new_case_name:
            self.viewmodel.update_case_name(self.case_id, new_case_name)

        regions_payload = []
        for r in range(self.table_regions.rowCount()):
            reg_id = self.table_regions.item(r, 0).data(Qt.ItemDataRole.UserRole)
            alias_val = self.table_regions.item(r, 2).text().strip()
            regions_payload.append({"id": reg_id, "alias": alias_val})

        if regions_payload:
            self.viewmodel.update_region_aliases(self.case_id, regions_payload)

        self.accept()


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

        title = QLabel("Gestão de Casos")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        
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

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nome de Exibição", "Caminho (Source)", "Status", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D5D8DC; }
            QHeaderView::section { background-color: #ECF0F1; font-weight: bold; padding: 5px; }
        """)

        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.table)

    def setup_connections(self):
        self.btn_import.clicked.connect(self.handle_import_click)
        self.viewmodel.cases_loaded.connect(self.populate_table)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.viewmodel.import_started.connect(self.show_loading)
        self.viewmodel.import_success.connect(self.hide_loading_success)
        self.viewmodel.import_failed.connect(self.hide_loading_error)
        self.viewmodel.case_deleted.connect(lambda: QMessageBox.information(self, "Sucesso", "Caso excluído."))
        self.viewmodel.case_updated.connect(self.viewmodel.load_cases)
        self.viewmodel.regions_updated.connect(lambda: QMessageBox.information(self, "Sucesso", "Configurações salvas."))

    def load_data(self):
        self.viewmodel.load_cases()

    def populate_table(self, cases: list):
        self.table.setRowCount(0)
        for row, case in enumerate(cases):
            self.table.insertRow(row)
            
            case_id = case.get("id")
            display_name = case.get("display_name", "")
            
            item_name = QTableWidgetItem(display_name)
            item_name.setData(Qt.ItemDataRole.UserRole, case_id) 
            self.table.setItem(row, 0, item_name)
            
            self.table.setItem(row, 1, QTableWidgetItem(case.get("source_path", "")))
            
            status = case.get("status", "")
            item_status = QTableWidgetItem(status)
            if status == "READY":
                item_status.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 2, item_status)
            
            # Botão "⋮" de Três Pontinhos (Menu de Ações)
            btn_menu = QPushButton("⋮")
            btn_menu.setFixedWidth(40)
            btn_menu.setStyleSheet("font-weight: bold; font-size: 16px; background-color: #ECF0F1; border-radius: 4px;")
            btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Anexa o menu de contexto no botão
            btn_menu.setMenu(self.create_action_menu(case_id, display_name))
            self.table.setCellWidget(row, 3, btn_menu)

    def create_action_menu(self, case_id: str, current_name: str) -> QMenu:
        menu = QMenu(self)
        
        act_config = menu.addAction("⚙️ Configurar Nome / Apelidos")
        act_config.triggered.connect(lambda: self.open_config_dialog(case_id, current_name))
        
        menu.addSeparator()
        
        act_delete = menu.addAction("🗑️ Excluir Caso")
        act_delete.triggered.connect(lambda: self.confirm_and_delete(case_id))
        
        return menu

    def open_config_dialog(self, case_id: str, current_name: str):
        dialog = CaseConfigDialog(self, case_id, current_name, self.viewmodel)
        dialog.exec()

    def handle_import_click(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Selecione a pasta do Caso")
        if folder_path:
            folder_path = folder_path.replace("\\", "/")
            default_name = os.path.basename(folder_path)
            
            # Pergunta o Nome Fictício no momento da importação
            custom_name, ok = QInputDialog.getText(
                self, 
                "Nome do Caso", 
                "Digite um nome fictício / customizado para este estudo:", 
                QLineEdit.EchoMode.Normal, 
                f"Estudo: {default_name}"
            )
            if ok and custom_name.strip():
                self.viewmodel.import_case(folder_path, custom_name.strip())

    def confirm_and_delete(self, case_id: str):
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este caso e todas as suas configurações/regiões?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.viewmodel.delete_case(case_id)

    def show_loading(self):
        self.progress_dialog = QProgressDialog("Processando caso no servidor...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Importando...")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.show()

    def hide_loading_success(self, msg):
        if self.progress_dialog: self.progress_dialog.close()
        QMessageBox.information(self, "Sucesso", msg)

    def hide_loading_error(self, msg):
        if self.progress_dialog: self.progress_dialog.close()
        QMessageBox.warning(self, "Erro na Importação", msg)

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erro", msg)
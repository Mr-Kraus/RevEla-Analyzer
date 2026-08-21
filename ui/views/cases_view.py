from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLineEdit, QFileDialog, QMessageBox, 
    QProgressDialog, QMenu, QDialog, QDialogButtonBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import Qt
from ui.viewmodels.cases_viewmodel import CasesViewModel
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLineEdit, QFileDialog, QMessageBox, 
    QMenu, QAbstractItemView
)
from PyQt6.QtGui import QFont, QCursor



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
    analyze_requested = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.viewmodel = CasesViewModel()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- Cabeçalho Superior ---
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Gestão de Casos")
        lbl_title.setStyleSheet("font-family: Arial; font-size: 20px; font-weight: bold; color: #0F172A;")
        
        self.btn_import = QPushButton("➕ Importar Novo Caso")
        self.btn_import.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_import.setStyleSheet("""
            QPushButton {
                background-color: #2563EB; color: white; font-family: Arial; 
                font-size: 12px; font-weight: bold; padding: 10px 20px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_import)
        layout.addLayout(header_layout)

        # --- Tabela de Casos ---
        self.table = QTableWidget(0, 4)
        # O último cabeçalho fica propositalmente vazio
        self.table.setHorizontalHeaderLabels(["Nome do Caso", "Data de Importação", "Status", ""])
        
        # Ajuste de larguras
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 50) # Coluna fininha para os 3 pontinhos

        # Estilização baseada no Guia de Identidade Visual
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E2E8F0;
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                font-family: Arial; font-size: 12px; color: #0F172A;
                border-radius: 8px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E2E8F0;
                padding-left: 10px;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                color: #334155;
                font-weight: bold;
                font-family: Arial; font-size: 12px;
                padding: 12px 10px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
            }
        """)
        
        layout.addWidget(self.table)

    def setup_connections(self):
        self.viewmodel.cases_loaded.connect(self.populate_table)
        self.viewmodel.error_occurred.connect(lambda e: QMessageBox.warning(self, "Erro", e))
        self.btn_import.clicked.connect(self.import_case)

    def load_data(self):
        self.viewmodel.load_cases()

    def import_case(self):
        # 1. Seleciona a pasta
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta do Caso")
        if folder:
            # 2. Pede ao usuário o nome do caso (o parâmetro que estava faltando)
            display_name, ok = QInputDialog.getText(self, "Nome do Caso", "Digite um nome de exibição para este caso:")
            if ok and display_name.strip():
                # 3. Chama o viewmodel com ambos os parâmetros
                self.viewmodel.import_case(folder, display_name.strip())

    def populate_table(self, cases: list):
        self.table.setRowCount(0)
        for row, case in enumerate(cases):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 45) # Linhas mais altas para respiro
            
            # Coluna 0: Nome
            item_name = QTableWidgetItem(f"{case.get('external_name', '')} - {case.get('display_name', '')}")
            item_name.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            # Coluna 1: Data
            item_date = QTableWidgetItem(case.get("created_at", "N/A")[:10]) # Simplifica data se for ISO
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_date)
            
            # Coluna 2: Widget Customizado de Status (Bolinha + Texto)
            status_widget = self._create_status_widget(case.get("status", "UNKNOWN"))
            self.table.setCellWidget(row, 2, status_widget)
            
            # Coluna 3: Widget Customizado de Ações (3 pontinhos)
            action_btn = self._create_action_button(case.get("id"), case.get("display_name", ""))
            self.table.setCellWidget(row, 3, action_btn)

    def _create_status_widget(self, status: str) -> QWidget:
        """Cria um widget centralizado com uma bolinha semântica e o texto do status."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dot = QLabel("●")
        text = QLabel(status.upper())
        text.setStyleSheet("font-family: Arial; font-size: 12px; font-weight: bold; color: #334155;")

        # Cores mapeadas do Guia de Identidade Visual
        if status.upper() == "READY":
            dot.setStyleSheet("color: #22C55E; font-size: 14px;") # Verde Sucesso
        elif status.upper() == "FAILED":
            dot.setStyleSheet("color: #EF4444; font-size: 14px;") # Vermelho Alerta
        else:
            dot.setStyleSheet("color: #F59E0B; font-size: 14px;") # Amarelo (Ingesting/Importing)

        layout.addWidget(dot)
        layout.addWidget(text)
        return widget

    def _create_action_button(self, case_id: str, case_name: str) -> QWidget:
        """Cria o botão minimalista de 3 pontos para as ações."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("⋮")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 18px; font-weight: bold; color: #0F172A;
                border-radius: 15px;
            }
            QPushButton:hover { background-color: #E2E8F0; color: #2563EB; }
        """)
        
        # Conecta o clique ao menu de contexto passando o botão como âncora
        btn.clicked.connect(lambda: self.show_action_menu(btn, case_id, case_name))
        
        layout.addWidget(btn)
        return widget

    def show_action_menu(self, button: QPushButton, case_id: str, case_name: str):
        """Exibe o menu suspenso de ações logo abaixo dos 3 pontinhos."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #E2E8F0; border-radius: 4px; font-family: Arial; padding: 5px; }
            QMenu::item { padding: 8px 25px; border-radius: 4px; color: #0F172A; }
            QMenu::item:selected { background-color: #F8FAFC; color: #2563EB; font-weight: bold; }
        """)

        action_analyze = menu.addAction("📊 Analisar Caso")
        action_edit = menu.addAction("⚙️ Editar Configurações")
        action_delete = menu.addAction("🗑️ Excluir")

        # Posição do menu colado abaixo do botão
        pos = button.mapToGlobal(button.rect().bottomLeft())
        selected_action = menu.exec(pos)

        # Direcionamento de Ações
        if selected_action == action_analyze:
            self.analyze_requested.emit(case_id, case_name)
            
        elif selected_action == action_edit:
            # AGORA PASSAMOS O NOME DO CASO AQUI TAMBÉM!
            self.edit_case(case_id, case_name) 
            
        elif selected_action == action_delete:
            confirm = QMessageBox.question(self, "Confirmar Exclusão", f"Tem certeza que deseja excluir o caso '{case_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.viewmodel.delete_case(case_id)
                self.load_data()

    def edit_case(self, case_id: str, case_name: str):
        """Chama a tela de configuração de caso."""
        try:
            # Passando o current_name para o Dialog
            dialog = CaseConfigDialog(parent=self, case_id=case_id, current_name=case_name, viewmodel=self.viewmodel)
        except TypeError:
            # Fallback (caso a ordem dos parâmetros na sua classe seja diferente)
            dialog = CaseConfigDialog(case_id, case_name, self.viewmodel, self)
            
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data() # Atualiza a lista se o nome do caso foi alterado
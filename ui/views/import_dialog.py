from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

class ImportSelectionDialog(QDialog):
    def __init__(self, discovery_details: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Importação do Caso")
        self.setMinimumWidth(450)
        
        self.discovery_details = discovery_details
        self.selected_template = None
        self.selected_results = None
        self.selected_software = "RELEVA"
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Avisos (Warnings) do Backend
        warnings = self.discovery_details.get("warnings", [])
        if warnings:
            lbl_warning = QLabel("\n".join(warnings))
            lbl_warning.setStyleSheet("color: #D97706; font-weight: bold;") # Laranja alerta
            lbl_warning.setWordWrap(True)
            layout.addWidget(lbl_warning)

        # 1. ComboBox: Template System
        layout.addWidget(QLabel("Selecione o Template System:"))
        self.combo_template = QComboBox()
        templates = self.discovery_details.get("system_templates", [])
        if not templates:
            self.combo_template.addItem("Nenhum template encontrado")
            self.combo_template.setEnabled(False)
        else:
            self.combo_template.addItems(templates)
        layout.addWidget(self.combo_template)

        # 2. ComboBox: Pasta de Resultados
        layout.addWidget(QLabel("Selecione a pasta de Resultados:"))
        self.combo_results = QComboBox()
        results = self.discovery_details.get("result_directories", [])
        if not results:
            self.combo_results.addItem("Nenhuma pasta de resultados encontrada")
            self.combo_results.setEnabled(False)
        else:
            self.combo_results.addItems(results)
        layout.addWidget(self.combo_results)
        
        # 3. ComboBox: Versão do Software
        layout.addWidget(QLabel("Versão do Software (Parser):"))
        self.combo_software = QComboBox()
        self.combo_software.addItems(["RELEVA", "PSMora"])
        layout.addWidget(self.combo_software)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_import = QPushButton("Iniciar Importação")
        self.btn_import.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        
        # Desabilita o botão se faltar arquivo base
        if not templates or not results:
            self.btn_import.setEnabled(False)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_import)
        layout.addLayout(btn_layout)

        # Conexões
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_import.clicked.connect(self.accept_selection)

    def accept_selection(self):
        self.selected_template = self.combo_template.currentText()
        self.selected_results = self.combo_results.currentText()
        self.selected_software = self.combo_software.currentText()
        self.accept()
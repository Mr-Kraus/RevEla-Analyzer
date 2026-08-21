from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, 
    QLineEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from ui.viewmodels.settings_viewmodel import SettingsViewModel

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = SettingsViewModel()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("⚙️ Configurações Gerais do Sistema")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")
        main_layout.addWidget(title)

        # 1. Grupo de Formatação de Números
        group_format = QGroupBox("Formatação e Precisão")
        group_format.setStyleSheet("QGroupBox { font-weight: bold; color: #2C3E50; border: 1px solid #D5D8DC; border-radius: 8px; margin-top: 10px; padding: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_format = QVBoxLayout(group_format)

        self.spin_table_dec = self._create_spinbox(layout_format, "Casas Decimais em Tabelas:", 0, 8)
        self.spin_chart_dec = self._create_spinbox(layout_format, "Casas Decimais em Gráficos:", 0, 8)
        
        self.combo_lolp = QComboBox()
        self.combo_lolp.addItems(["decimal", "scientific"])
        self._add_row(layout_format, "Formato do Indicador LOLP:", self.combo_lolp)
        main_layout.addWidget(group_format)

        # 2. Grupo de Preferências Visuais
        group_visual = QGroupBox("Preferências de Telas")
        group_visual.setStyleSheet(group_format.styleSheet())
        layout_visual = QVBoxLayout(group_visual)

        self.combo_chart = QComboBox()
        self.combo_chart.addItems(["Pareto", "Barras", "Linha"])
        self._add_row(layout_visual, "Tipo de Gráfico Padrão:", self.combo_chart)

        self.combo_global = QComboBox()
        self.combo_global.addItems(["Tipo 1: Detalhado por Caso", "Tipo 2: Comparativo Lado a Lado"])
        self._add_row(layout_visual, "Aba Global Padrão:", self.combo_global)
        main_layout.addWidget(group_visual)

        # 3. Grupo Conectividade
        group_net = QGroupBox("Servidor & API")
        group_net.setStyleSheet(group_format.styleSheet())
        layout_net = QVBoxLayout(group_net)
        
        self.txt_api = QLineEdit()
        self.txt_api.setStyleSheet("padding: 5px; border: 1px solid #BDC3C7; border-radius: 4px;")
        self._add_row(layout_net, "Endereço da API Backend:", self.txt_api)
        main_layout.addWidget(group_net)

        # Botão Salvar
        self.btn_save = QPushButton("💾 Salvar Configurações")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setFixedWidth(200)
        self.btn_save.setStyleSheet("QPushButton { background-color: #27AE60; color: white; font-weight: bold; border-radius: 6px; } QPushButton:hover { background-color: #2ECC71; }")
        
        row_btn = QHBoxLayout()
        row_btn.addStretch()
        row_btn.addWidget(self.btn_save)
        main_layout.addLayout(row_btn)
        main_layout.addStretch()

    def _create_spinbox(self, parent_layout, label_text, min_val, max_val):
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setFixedWidth(100)
        spin.setStyleSheet("padding: 5px; border: 1px solid #BDC3C7; border-radius: 4px;")
        self._add_row(parent_layout, label_text, spin)
        return spin

    def _add_row(self, layout, label_text, widget):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 14px; color: #34495E;")
        widget.setFixedHeight(35)
        row.addWidget(lbl)
        row.addWidget(widget)
        row.addStretch()
        layout.addLayout(row)

    def setup_connections(self):
        self.btn_save.clicked.connect(self.save_settings)
        self.viewmodel.settings_saved.connect(lambda: QMessageBox.information(self, "Sucesso", "Configurações salvas e aplicadas a todo o sistema!"))

    def load_data(self):
        """Chamado pelo MainWindow ao abrir a tela."""
        config = self.viewmodel.load_settings()
        self.spin_table_dec.setValue(config["table_decimals"])
        self.spin_chart_dec.setValue(config["chart_decimals"])
        self.combo_lolp.setCurrentText(config["lolp_format"])
        self.combo_chart.setCurrentText(config["default_chart_type"])
        self.combo_global.setCurrentIndex(config["global_view_type"])
        self.txt_api.setText(config["api_url"])

    def save_settings(self):
        config = {
            "table_decimals": self.spin_table_dec.value(),
            "chart_decimals": self.spin_chart_dec.value(),
            "lolp_format": self.combo_lolp.currentText(),
            "default_chart_type": self.combo_chart.currentText(),
            "global_view_type": self.combo_global.currentIndex(),
            "api_url": self.txt_api.text().strip()
        }
        self.viewmodel.save_settings(config)
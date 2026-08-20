from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QComboBox, QRadioButton, QButtonGroup, 
                             QPushButton, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from ui.viewmodels.settings_viewmodel import SettingsViewModel

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = SettingsViewModel()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Configurações Pessoais de Visualização")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(title)

        # ==========================================
        # GRUPO 1: FORMATAÇÃO NUMÉRICA E DECIMAIS
        # ==========================================
        group_decimals = QGroupBox("Formatação Numérica")
        group_decimals.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #34495E; }")
        dec_layout = QVBoxLayout(group_decimals)
        dec_layout.setSpacing(15)

        # Decimais em Tabelas
        row_table = QHBoxLayout()
        row_table.addWidget(QLabel("Casos Decimais em Tabelas:"))
        self.spin_table_dec = QSpinBox()
        self.spin_table_dec.setRange(0, 8)
        self.spin_table_dec.setFixedWidth(80)
        row_table.addWidget(self.spin_table_dec)
        row_table.addStretch()
        dec_layout.addLayout(row_table)

        # Decimais em Gráficos
        row_chart = QHBoxLayout()
        row_chart.addWidget(QLabel("Casos Decimais em Gráficos:"))
        self.spin_chart_dec = QSpinBox()
        self.spin_chart_dec.setRange(0, 8)
        self.spin_chart_dec.setFixedWidth(80)
        row_chart.addWidget(self.spin_chart_dec)
        row_chart.addStretch()
        dec_layout.addLayout(row_chart)

        # Formato do LOLP
        row_lolp = QHBoxLayout()
        row_lolp.addWidget(QLabel("Exibição do Indicador LOLP:"))
        self.radio_decimal = QRadioButton("Decimal Padrão (ex: 0.00032)")
        self.radio_scientific = QRadioButton("Potência de 10 / Notação Científica (ex: 3.20e-04)")
        
        self.lolp_group = QButtonGroup(self)
        self.lolp_group.addButton(self.radio_decimal, 1)
        self.lolp_group.addButton(self.radio_scientific, 2)

        row_lolp.addWidget(self.radio_decimal)
        row_lolp.addWidget(self.radio_scientific)
        row_lolp.addStretch()
        dec_layout.addLayout(row_lolp)

        layout.addWidget(group_decimals)

        # ==========================================
        # GRUPO 2: PREFERÊNCIAS DE GRÁFICOS
        # ==========================================
        group_charts = QGroupBox("Padrões de Gráficos e Exibição")
        group_charts.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: #34495E; }")
        chart_layout = QVBoxLayout(group_charts)
        chart_layout.setSpacing(15)

        row_chart_type = QHBoxLayout()
        row_chart_type.addWidget(QLabel("Tipo de Gráfico Padrão de Início:"))
        self.combo_chart_type = QComboBox()
        self.combo_chart_type.addItems(["Pareto", "Barras", "Linhas", "Radar", "Donut"])
        self.combo_chart_type.setFixedWidth(150)
        row_chart_type.addWidget(self.combo_chart_type)
        row_chart_type.addStretch()
        chart_layout.addLayout(row_chart_type)

        layout.addWidget(group_charts)

        # ==========================================
        # BOTÃO SALVAR
        # ==========================================
        self.btn_save = QPushButton("💾 Salvar Configurações")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setFixedWidth(200)
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #2980B9; color: white; font-weight: bold; border-radius: 5px; }
            QPushButton:hover { background-color: #3498DB; }
        """)
        layout.addWidget(self.btn_save)
        layout.addStretch()

    def setup_connections(self):
        self.btn_save.clicked.connect(self.handle_save)
        self.viewmodel.settings_saved.connect(self.on_settings_saved)

    def load_data(self):
        """Carrega as configurações salvas atualmente ao abrir esta aba."""
        curr = self.viewmodel.get_current_settings()
        self.spin_table_dec.setValue(curr["table_decimals"])
        self.spin_chart_dec.setValue(curr["chart_decimals"])
        
        if curr["lolp_format"] == "scientific":
            self.radio_scientific.setChecked(True)
        else:
            self.radio_decimal.setChecked(True)

        self.combo_chart_type.setCurrentText(curr["default_chart_type"])

    def handle_save(self):
        lolp_fmt = "scientific" if self.radio_scientific.isChecked() else "decimal"
        self.viewmodel.save_settings(
            table_dec=self.spin_table_dec.value(),
            chart_dec=self.spin_chart_dec.value(),
            lolp_fmt=lolp_fmt,
            chart_type=self.combo_chart_type.currentText()
        )

    def on_settings_saved(self, msg):
        QMessageBox.information(self, "Configurações", msg)
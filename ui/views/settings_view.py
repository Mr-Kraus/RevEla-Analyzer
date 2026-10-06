import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox,
    QLineEdit, QPushButton, QGroupBox, QMessageBox, QScrollArea,
    QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from ui.viewmodels.settings_viewmodel import SettingsViewModel

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = SettingsViewModel()
        self.setup_ui()
        self.setup_connections()

    def _create_color_icon(self, hex_color: str) -> QIcon:
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(hex_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 16, 16, 4, 4)
        painter.end()
        return QIcon(pixmap)

    def _create_palette_icon(self, cmap_name: str) -> QIcon:
        try:
            cmap = plt.get_cmap(cmap_name)
            colors = cmap.colors if hasattr(cmap, "colors") else cmap(np.linspace(0, 1, 5))
        except ValueError:
            return QIcon()

        pixmap = QPixmap(80, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        num_colors = min(len(colors), 5)
        block_w = 80 / num_colors
        for i in range(num_colors):
            c = mcolors.to_hex(colors[i])
            painter.fillRect(int(i * block_w), 0, int(block_w + 1), 16, QColor(c))
        painter.end()
        return QIcon(pixmap)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 22, 24, 22)
        main_layout.setSpacing(16)

        # =====================================================================
        # TODO O CSS GIGANTE FOI REMOVIDO DAQUI! 
        # O aplicativo agora puxa os estilos automaticamente do main.py
        # =====================================================================

        title = QLabel("Configurações Globais do Sistema")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px; background-color: transparent;")
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout_content = QVBoxLayout(scroll_content)
        layout_content.setSpacing(16)
        layout_content.setContentsMargins(0, 0, 12, 0)

        # ==========================================
        # 1. Grupo de Formatação de Números
        # ==========================================
        group_format = QGroupBox("Precisão e Formatação Matemática")
        layout_format = QVBoxLayout(group_format)
        layout_format.setSpacing(10)

        self.spin_table_dec = QSpinBox()
        self.spin_table_dec.setRange(0, 6)
        self.spin_chart_dec = QSpinBox()
        self.spin_chart_dec.setRange(0, 6)
        self.combo_lolp = QComboBox()
        self.combo_lolp.addItems(["decimal", "scientific"])

        layout_format.addLayout(self._create_labeled_widget("Tabelas (Casas Decimais):", self.spin_table_dec))
        layout_format.addLayout(self._create_labeled_widget("Gráficos (Casas Decimais):", self.spin_chart_dec))
        layout_format.addLayout(self._create_labeled_widget("Formato de Exibição LOLP:", self.combo_lolp))
        layout_content.addWidget(group_format)

        # ==========================================
        # 2. Grupo de Relatórios e Estética Visual
        # ==========================================
        group_report = QGroupBox("Estética de Gráficos e Exportação")
        layout_report = QVBoxLayout(group_report)
        layout_report.setSpacing(10)

        self.combo_img_type = QComboBox()
        self.combo_img_type.addItems(["PNG", "SVG", "JPEG"])
        
        self.combo_font = QComboBox()
        self.combo_font.addItems(["Arial", "Segoe UI", "Helvetica", "Times New Roman"])
        
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(8, 32)

        self.combo_font_color = QComboBox()
        self.combo_font_color.setIconSize(QSize(16, 16))
        font_colors = {
            "Chumbo Profundo": "#0F172A",
            "Cinza Metálico": "#475569",
            "Preto Absoluto": "#000000",
            "Azul Primário": "#0284C7",
            "Vermelho Atenção": "#DC2626"
        }
        for name, hex_code in font_colors.items():
            self.combo_font_color.addItem(self._create_color_icon(hex_code), name, hex_code)

        self.combo_chart_style = QComboBox()
        self.combo_chart_style.setIconSize(QSize(80, 16))
        palettes = ["tab10", "Set1", "Set2", "Paired", "viridis", "plasma", "inferno", "magma", "cividis", "Pastel1"]
        for palette in palettes:
            self.combo_chart_style.addItem(self._create_palette_icon(palette), palette, palette)

        layout_report.addLayout(self._create_labeled_widget("Formato de Imagem:", self.combo_img_type))
        layout_report.addLayout(self._create_labeled_widget("Família da Fonte:", self.combo_font))
        layout_report.addLayout(self._create_labeled_widget("Tamanho da Fonte Base:", self.spin_font_size))
        layout_report.addLayout(self._create_labeled_widget("Cor Principal da Fonte:", self.combo_font_color))
        layout_report.addLayout(self._create_labeled_widget("Paleta de Cores Padrão:", self.combo_chart_style))
        layout_content.addWidget(group_report)

        # ==========================================
        # 3. Módulos de Interesse
        # ==========================================
        group_modules = QGroupBox("Módulos e Abas Ativas")
        layout_modules = QVBoxLayout(group_modules)
        layout_modules.setSpacing(6)
        
        self.chk_confiabilidade = QCheckBox("Análise de Confiabilidade")
        self.chk_rede = QCheckBox("Análise de Rede")
        self.chk_geracao = QCheckBox("Análise de Geração")
        self.chk_veiculos = QCheckBox("Modelo de Veículos Elétricos")
        self.chk_gest_proc = QCheckBox("Modelo de Gestão de Processos")

        for chk in (self.chk_confiabilidade, self.chk_rede, self.chk_geracao, self.chk_veiculos, self.chk_gest_proc):
            layout_modules.addLayout(self._create_aligned_checkbox(chk))
        layout_content.addWidget(group_modules)

        # ==========================================
        # 4. Filtro de Indicadores
        # ==========================================
        group_indicators = QGroupBox("Indicadores de Monitoramento")
        layout_indicators = QVBoxLayout(group_indicators)
        layout_indicators.setSpacing(6)

        self.chk_ind_custo = QCheckBox("Indicadores Financeiros")
        self.chk_ind_carga = QCheckBox("Indicadores de Demanda")
        self.chk_ind_gerais = QCheckBox("Indicadores Sistêmicos")
        self.chk_ind_transicao = QCheckBox("Monitoramento de Transição Energética")
        self.chk_ind_funcionalidade = QCheckBox("Índices de Saúde do Equipamento")

        for chk in (self.chk_ind_custo, self.chk_ind_carga, self.chk_ind_gerais, self.chk_ind_transicao, self.chk_ind_funcionalidade):
            layout_indicators.addLayout(self._create_aligned_checkbox(chk))
        layout_content.addWidget(group_indicators)

        # ==========================================
        # 5. Infraestrutura API
        # ==========================================
        group_net = QGroupBox("Configuração de Infraestrutura")
        layout_net = QVBoxLayout(group_net)
        self.txt_api = QLineEdit()
        layout_net.addLayout(self._create_labeled_widget("Endereço do Backend:", self.txt_api))
        layout_content.addWidget(group_net)

        layout_content.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # ==========================================
        # Botão Salvar
        # ==========================================
        self.btn_save = QPushButton("Salvar Configurações Globais")
        self.btn_save.setFixedHeight(45)
        self.btn_save.setFixedWidth(280)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)

        row_btn = QHBoxLayout()
        row_btn.addStretch()
        row_btn.addWidget(self.btn_save)
        main_layout.addLayout(row_btn)

    def _create_labeled_widget(self, label_text, widget):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(18)

        lbl = QLabel(label_text)
        lbl.setFixedWidth(310)
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        lbl.setStyleSheet("font-size: 14px; color: #475569; font-weight: 600; background-color: transparent;")
        
        # Define a largura fixa de 220px via Python (antes estava no CSS)
        widget.setFixedWidth(220)

        layout.addWidget(lbl)
        layout.addWidget(widget)
        layout.addStretch()
        return layout

    def _create_aligned_checkbox(self, checkbox):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(18)
        
        spacer = QLabel("")
        spacer.setFixedWidth(310)
        
        layout.addWidget(spacer)
        layout.addWidget(checkbox)
        layout.addStretch()
        return layout

    def setup_connections(self):
        self.btn_save.clicked.connect(self.save_settings)

        self.viewmodel.settings_saved.connect(
            lambda: QMessageBox.information(
                self,
                "Preferências Salvas",
                "As configurações globais foram aplicadas. "
                "Os gráficos e tabelas responderão à nova parametrização."
            )
        )

    def load_data(self):
        config = self.viewmodel.load_settings()

        self.spin_table_dec.setValue(
            config["precisao_tabelas"]
        )
        self.spin_chart_dec.setValue(
            config["precisao_grafico"]
        )
        self.combo_lolp.setCurrentText(
            config["formato_lolp"]
        )

        self.combo_img_type.setCurrentText(
            config["tipo_imagem_relatorio"]
        )
        self.combo_font.setCurrentText(
            config["tipo_fonte_relatorio"]
        )
        self.spin_font_size.setValue(
            config["tamanho_fonte_relatorio"]
        )

        idx_color = self.combo_font_color.findData(
            config["cor_fonte_relatorio"]
        )
        if idx_color >= 0:
            self.combo_font_color.setCurrentIndex(idx_color)

        idx_pal = self.combo_chart_style.findData(
            config["estilo_grafico_relatorio"]
        )
        if idx_pal >= 0:
            self.combo_chart_style.setCurrentIndex(idx_pal)

        self.chk_confiabilidade.setChecked(
            config["analise_confiabilidade"]
        )
        self.chk_rede.setChecked(
            config["analise_rede"]
        )
        self.chk_geracao.setChecked(
            config["analise_geracao"]
        )
        self.chk_veiculos.setChecked(
            config["modelo_veiculos_eletricos"]
        )
        self.chk_gest_proc.setChecked(
            config["modelo_gest_proc"]
        )

        self.chk_ind_custo.setChecked(
            config["indicador_custo"]
        )
        self.chk_ind_carga.setChecked(
            config["indicador_carga"]
        )
        self.chk_ind_gerais.setChecked(
            config["indicador_gerais"]
        )
        self.chk_ind_transicao.setChecked(
            config["indicador_transicao"]
        )
        self.chk_ind_funcionalidade.setChecked(
            config["indicador_funcionalidade"]
        )

        self.txt_api.setText(config["api_url"])

    def save_settings(self):
        config = {
            "precisao_tabelas": self.spin_table_dec.value(),
            "precisao_grafico": self.spin_chart_dec.value(),
            "formato_lolp": self.combo_lolp.currentText(),
            "tipo_imagem_relatorio": self.combo_img_type.currentText(),
            "tipo_fonte_relatorio": self.combo_font.currentText(),
            "tamanho_fonte_relatorio": self.spin_font_size.value(),
            "cor_fonte_relatorio": self.combo_font_color.currentData(),
            "estilo_grafico_relatorio": self.combo_chart_style.currentData(),
            "analise_confiabilidade": self.chk_confiabilidade.isChecked(),
            "analise_rede": self.chk_rede.isChecked(),
            "analise_geracao": self.chk_geracao.isChecked(),
            "modelo_veiculos_eletricos": self.chk_veiculos.isChecked(),
            "modelo_gest_proc": self.chk_gest_proc.isChecked(),
            "indicador_custo": self.chk_ind_custo.isChecked(),
            "indicador_carga": self.chk_ind_carga.isChecked(),
            "indicador_gerais": self.chk_ind_gerais.isChecked(),
            "indicador_transicao": self.chk_ind_transicao.isChecked(),
            "indicador_funcionalidade": self.chk_ind_funcionalidade.isChecked(),
            "api_url": self.txt_api.text().strip()
        }

        self.viewmodel.save_settings(config)

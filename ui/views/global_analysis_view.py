import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt

# Assumindo que você possui um TabGlobalViewModel; caso contrário, adapte para o seu ViewModel
from ui.viewmodels.settings_viewmodel import SettingsViewModel

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']


class TabGlobalView(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_vm = SettingsViewModel()
        
        # Dados de exemplo / Cache
        self.current_cases = []
        self.current_indicators = ["LOLE", "EENS", "LOLF", "LOLD", "EPNS", "LOLP"]
        self.current_data = {} 
        
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
        QWidget { font-family: "Segoe UI", Arial, sans-serif; color: #0F172A; font-weight: normal; background-color: #F8FAFC; }
        QRadioButton { font-size: 14px; color: #334155; }
        QTableWidget { border: 1px solid #CBD5E1; background-color: #FFFFFF; alternate-background-color: #F8FAFC; }
        QHeaderView::section { background-color: #F1F5F9; color: #334155; padding: 8px; border: none; border-bottom: 1px solid #CBD5E1; font-weight: normal; }
        QScrollArea { border: none; background-color: transparent; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ==========================================
        # CONTROLES SUPERIORES (Modo de Exibição)
        # ==========================================
        top_layout = QHBoxLayout()
        
        lbl_view = QLabel("Modo de Exibição:")
        lbl_view.setStyleSheet("font-size: 15px; color: #1E293B;")
        top_layout.addWidget(lbl_view)
        
        self.view_group = QButtonGroup(self)
        self.rad_single = QRadioButton("Tabela Única (Comparativo)")
        self.rad_separated = QRadioButton("Tabelas Separadas (Roláveis)")
        self.rad_single.setChecked(True)
        
        self.view_group.addButton(self.rad_single)
        self.view_group.addButton(self.rad_separated)
        
        # Recarrega o layout quando o usuário troca a opção
        self.rad_single.toggled.connect(self.render_layout)
        
        top_layout.addWidget(self.rad_single)
        top_layout.addWidget(self.rad_separated)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)

        # ==========================================
        # ÁREA DE CONTEÚDO (Scrollável)
        # ==========================================
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(30)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def load_data(self):
        """
        Método chamado pela MainWindow ou ViewModel para injetar os dados reais.
        Substitua este mock pela integração real com sua API/ViewModel.
        """
        # --- MOCK DE DADOS PARA DEMONSTRAÇÃO ---
        self.current_cases = [
            {"id": "c1", "name": "Caso Base 2025"},
            {"id": "c2", "name": "Expansão Eólica"},
            {"id": "c3", "name": "Seca Severa"}
        ]
        
        self.current_data = {
            "c1": {"LOLE": 12.5, "EENS": 340.2, "LOLF": 2.1, "LOLD": 5.9, "EPNS": 150.0, "LOLP": 0.0014},
            "c2": {"LOLE": 8.2, "EENS": 210.5, "LOLF": 1.5, "LOLD": 5.4, "EPNS": 90.0, "LOLP": 0.0009},
            "c3": {"LOLE": 45.0, "EENS": 1250.0, "LOLF": 5.8, "LOLD": 7.7, "EPNS": 450.0, "LOLP": 0.0051},
        }
        # ---------------------------------------
        
        self.render_layout()

    def render_layout(self):
        """Limpa o layout e constrói a exibição baseada no RadioButton selecionado."""
        # Limpa todos os widgets anteriores
        for i in reversed(range(self.content_layout.count())): 
            widget_to_remove = self.content_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)
            else:
                layout_to_remove = self.content_layout.itemAt(i).layout()
                if layout_to_remove:
                    self.clear_layout_recursively(layout_to_remove)

        if not self.current_cases:
            lbl_empty = QLabel("Nenhum caso carregado para análise global.")
            self.content_layout.addWidget(lbl_empty)
            return

        if self.rad_single.isChecked():
            self.build_single_table_mode()
        else:
            self.build_separated_tables_mode()

    def clear_layout_recursively(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.clear_layout_recursively(item.layout())

    # =========================================================
    # CONSTRUTORES DE MODOS DE EXIBIÇÃO
    # =========================================================
    def build_single_table_mode(self):
        """Constrói uma única tabela com todos os casos, e os gráficos no final."""
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_tabelas", 2)
        
        # 1. Tabela Única
        table = QTableWidget()
        headers = ["Indicador"] + [c["name"] for c in self.current_cases]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(self.current_indicators))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        
        for row, ind in enumerate(self.current_indicators):
            table.setItem(row, 0, QTableWidgetItem(ind))
            for col, case in enumerate(self.current_cases):
                val = self.current_data.get(case["id"], {}).get(ind, 0.0)
                item_val = QTableWidgetItem(f"{val:.{decimais}f}")
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col + 1, item_val)
                
        # Ajusta a altura da tabela baseada no conteúdo
        table.setFixedHeight(40 + (len(self.current_indicators) * 30))
        self.content_layout.addWidget(table)
        
        # 2. Espaço vazio flexível (opcional, para empurrar pro fundo se a tela for muito grande)
        self.content_layout.addSpacing(20)
        
        # 3. Gráficos Comparativos Lado a Lado (Com todos os casos)
        charts_layout = QHBoxLayout()
        
        canvas_lole_eens = self.create_dual_axis_chart(self.current_cases, "LOLE", "EENS")
        canvas_lolf_lold = self.create_dual_axis_chart(self.current_cases, "LOLF", "LOLD")
        
        charts_layout.addWidget(canvas_lole_eens)
        charts_layout.addWidget(canvas_lolf_lold)
        
        chart_container = QWidget()
        chart_container.setLayout(charts_layout)
        chart_container.setMinimumHeight(350)
        
        self.content_layout.addWidget(chart_container)
        self.content_layout.addStretch()

    def build_separated_tables_mode(self):
        """Constrói blocos contendo Tabela + Gráficos exclusivos para CADA caso."""
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_tabelas", 2)
        
        for case in self.current_cases:
            # Container do Caso (Cartão)
            case_frame = QFrame()
            case_frame.setStyleSheet("QFrame { border: 1px solid #E2E8F0; border-radius: 8px; background-color: #FFFFFF; }")
            case_layout = QVBoxLayout(case_frame)
            case_layout.setContentsMargins(15, 15, 15, 15)
            case_layout.setSpacing(15)
            
            # Título do Caso
            lbl_title = QLabel(f"Análise: {case['name']}")
            lbl_title.setStyleSheet("font-size: 16px; color: #0284C7; border: none;")
            case_layout.addWidget(lbl_title)
            
            # 1. Tabela Individual do Caso
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Indicador", "Valor"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("border: 1px solid #CBD5E1;")
            table.setRowCount(len(self.current_indicators))
            
            for row, ind in enumerate(self.current_indicators):
                val = self.current_data.get(case["id"], {}).get(ind, 0.0)
                item_ind = QTableWidgetItem(ind)
                item_val = QTableWidgetItem(f"{val:.{decimais}f}")
                item_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                table.setItem(row, 0, item_ind)
                table.setItem(row, 1, item_val)
                
            table.setFixedHeight(40 + (len(self.current_indicators) * 30))
            case_layout.addWidget(table)
            
            # 2. Gráficos Comparativos Lado a Lado (Apenas com dados deste caso)
            charts_layout = QHBoxLayout()
            
            # Enviamos uma lista com apenas o caso atual para o construtor do gráfico
            canvas_lole_eens = self.create_dual_axis_chart([case], "LOLE", "EENS")
            canvas_lolf_lold = self.create_dual_axis_chart([case], "LOLF", "LOLD")
            
            # Removemos a borda nativa do canvas para ficar limpo dentro do frame
            canvas_lole_eens.setStyleSheet("border: none;")
            canvas_lolf_lold.setStyleSheet("border: none;")
            
            charts_layout.addWidget(canvas_lole_eens)
            charts_layout.addWidget(canvas_lolf_lold)
            
            chart_container = QWidget()
            chart_container.setStyleSheet("border: none;")
            chart_container.setLayout(charts_layout)
            chart_container.setMinimumHeight(300)
            
            case_layout.addWidget(chart_container)
            self.content_layout.addWidget(case_frame)
            
        self.content_layout.addStretch()

    # =========================================================
    # GERADOR DE GRÁFICOS (DUAL-AXIS)
    # =========================================================
    def create_dual_axis_chart(self, target_cases: list, ind_left: str, ind_right: str) -> FigureCanvas:
        """
        Cria um gráfico comparativo combinando colunas (Eixo Esq) e Linhas/Marcadores (Eixo Dir).
        :param target_cases: Lista de dicionários de casos a serem plotados.
        :param ind_left: Nome do indicador plotado em barras (ex: LOLE).
        :param ind_right: Nome do indicador plotado em linhas (ex: EENS).
        """
        fig = Figure(figsize=(5, 3), dpi=100, facecolor='#FFFFFF')
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        
        config = self.settings_vm.load_settings()
        decimais = config.get("precisao_grafico", 2)
        
        x = np.arange(len(target_cases))
        names = [c["name"] for c in target_cases]
        
        # Extrai e arredonda os valores
        val_left = [round(self.current_data.get(c["id"], {}).get(ind_left, 0.0), decimais) for c in target_cases]
        val_right = [round(self.current_data.get(c["id"], {}).get(ind_right, 0.0), decimais) for c in target_cases]
        
        # Plota Barras no eixo 1 (Azul Claro)
        ax1.bar(x, val_left, color='#38BDF8', width=0.4, label=ind_left, edgecolor='white')
        
        # Plota Marcadores no eixo 2 (Laranja)
        # Usa linha se houver mais de 1 caso, ou apenas o ponto se for 1 caso isolado.
        marker_style = '-o' if len(target_cases) > 1 else 'o'
        ax2.plot(x, val_right, marker_style, color='#F59E0B', linewidth=2, markersize=8, label=ind_right)
        
        # Formatação
        ax1.set_xticks(x)
        # Se for um único caso, o nome fica reto. Se for múltiplo, rotaciona levemente.
        ax1.set_xticklabels(names, rotation=15 if len(target_cases) > 1 else 0, ha='center' if len(target_cases) == 1 else 'right')
        
        ax1.set_ylabel(ind_left, color='#0284C7')
        ax2.set_ylabel(ind_right, color='#D97706')
        
        # Limpando o visual
        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax1.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Legenda limpa no topo central
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        fig.legend(h1+h2, l1+l2, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, frameon=False)
        
        fig.tight_layout()
        
        # Dá um pequeno respiro no topo para acomodar a legenda externa
        fig.subplots_adjust(top=0.85)
        
        return FigureCanvas(fig)
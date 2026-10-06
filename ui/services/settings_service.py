from PyQt6.QtCore import QObject, pyqtSignal

class SettingsService(QObject):
    _instance = None
    
    # Sinal global que avisa todas as abas quando o usuário salvar uma nova configuração
    settings_changed = pyqtSignal()

    # Constantes Globais Imutáveis
    HORAS_ANO = 8760
    SEMANAS_ANO = 52
    MESES_ANO = 12

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__() # <--- A correção exata do seu erro está aqui!
        
        # Precisão e Formatação
        self.precisao_tabelas = 3
        self.precisao_grafico = 3
        self.formato_lolp = "decimal"  # "decimal" ou "scientific"
        
        # Relatórios e Estética
        self.tipo_imagem_relatorio = "PNG"
        self.tipo_fonte_relatorio = "Arial"
        self.tamanho_fonte_relatorio = 12
        self.cor_fonte_relatorio = "#2C3E50"
        self.estilo_grafico_relatorio = "Padrão"
        
        # Módulos de Análise
        self.analise_confiabilidade = True
        self.analise_rede = True
        self.analise_geracao = True
        self.modelo_veiculos_eletricos = False
        self.modelo_gest_proc = False
        
        # Indicadores
        self.indicador_custo = True
        self.indicador_carga = True
        self.indicador_gerais = True
        self.indicador_transicao = False
        self.indicador_funcionalidade = False
        
        # API
        self.api_url = "http://127.0.0.1:8000"

    def apply_and_notify(self):
        """Dispara o gatilho para redesenhar gráficos e tabelas com as novas configurações"""
        self.settings_changed.emit()
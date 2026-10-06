from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.settings_service import SettingsService

class SettingsViewModel(QObject):
    settings_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.service = SettingsService.get_instance()

    def load_settings(self) -> dict:
        return {
            "precisao_tabelas": self.service.precisao_tabelas,
            "precisao_grafico": self.service.precisao_grafico,
            "formato_lolp": self.service.formato_lolp,
            "tipo_imagem_relatorio": self.service.tipo_imagem_relatorio,
            "tipo_fonte_relatorio": self.service.tipo_fonte_relatorio,
            "tamanho_fonte_relatorio": self.service.tamanho_fonte_relatorio,
            "cor_fonte_relatorio": self.service.cor_fonte_relatorio,
            "estilo_grafico_relatorio": self.service.estilo_grafico_relatorio,
            "analise_confiabilidade": self.service.analise_confiabilidade,
            "analise_rede": self.service.analise_rede,
            "analise_geracao": self.service.analise_geracao,
            "modelo_veiculos_eletricos": self.service.modelo_veiculos_eletricos,
            "modelo_gest_proc": self.service.modelo_gest_proc,
            "indicador_custo": self.service.indicador_custo,
            "indicador_carga": self.service.indicador_carga,
            "indicador_gerais": self.service.indicador_gerais,
            "indicador_transicao": self.service.indicador_transicao,
            "indicador_funcionalidade": self.service.indicador_funcionalidade,
            "api_url": self.service.api_url
        }

    def save_settings(self, config: dict):
        self.service.precisao_tabelas = config.get("precisao_tabelas", 3)
        self.service.precisao_grafico = config.get("precisao_grafico", 3)
        self.service.formato_lolp = config.get("formato_lolp", "decimal")
        
        self.service.tipo_imagem_relatorio = config.get("tipo_imagem_relatorio", "PNG")
        self.service.tipo_fonte_relatorio = config.get("tipo_fonte_relatorio", "Arial")
        self.service.tamanho_fonte_relatorio = config.get("tamanho_fonte_relatorio", 12)
        self.service.cor_fonte_relatorio = config.get("cor_fonte_relatorio", "#2C3E50")
        self.service.estilo_grafico_relatorio = config.get("estilo_grafico_relatorio", "Padrão")
        
        self.service.analise_confiabilidade = config.get("analise_confiabilidade", True)
        self.service.analise_rede = config.get("analise_rede", True)
        self.service.analise_geracao = config.get("analise_geracao", True)
        self.service.modelo_veiculos_eletricos = config.get("modelo_veiculos_eletricos", False)
        self.service.modelo_gest_proc = config.get("modelo_gest_proc", False)
        
        self.service.indicador_custo = config.get("indicador_custo", True)
        self.service.indicador_carga = config.get("indicador_carga", True)
        self.service.indicador_gerais = config.get("indicador_gerais", True)
        self.service.indicador_transicao = config.get("indicador_transicao", False)
        self.service.indicador_funcionalidade = config.get("indicador_funcionalidade", False)
        
        self.service.api_url = config.get("api_url", "http://127.0.0.1:8000")
        
        # 1. Avisa os gráficos e as tabelas globais:
        self.service.apply_and_notify()
        
        # 2. Avisa a tela de Settings que deu tudo certo:
        self.settings_saved.emit()
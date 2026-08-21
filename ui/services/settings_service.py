from PyQt6.QtCore import QSettings, QObject, pyqtSignal

class SettingsService(QObject):
    """
    Gerenciador Singleton Seguro de Preferências do Usuário.
    """
    settings_changed = pyqtSignal()
    _instance = None

    @classmethod
    def get_instance(cls):
        """Método seguro para recuperar a instância única sem bugar o PyQt."""
        if cls._instance is None:
            cls._instance = SettingsService()
        return cls._instance

    def __init__(self):
        super().__init__()
        # Inicializa o registro apenas na primeira vez
        self.settings = QSettings("REVela", "REVelaAnalyzer")

    # --- CASAS DECIMAIS EM TABELAS ---
    @property
    def table_decimals(self) -> int:
        return int(self.settings.value("table_decimals", 3)) # Default: 3

    @table_decimals.setter
    def table_decimals(self, val: int):
        self.settings.setValue("table_decimals", val)
        self.settings_changed.emit()

    # --- CASAS DECIMAIS EM GRÁFICOS ---
    @property
    def chart_decimals(self) -> int:
        return int(self.settings.value("chart_decimals", 3)) # Default: 3

    @chart_decimals.setter
    def chart_decimals(self, val: int):
        self.settings.setValue("chart_decimals", val)
        self.settings_changed.emit()

    # --- FORMATO DO LOLP ('decimal' ou 'scientific') ---
    @property
    def lolp_format(self) -> str:
        return str(self.settings.value("lolp_format", "decimal")) # Default: decimal

    @lolp_format.setter
    def lolp_format(self, val: str):
        self.settings.setValue("lolp_format", val)
        self.settings_changed.emit()

    # --- PREFERÊNCIAS DE GRÁFICO PADRÃO ---
    @property
    def default_chart_type(self) -> str:
        return str(self.settings.value("default_chart_type", "Pareto")) # Default: Pareto

    @default_chart_type.setter
    def default_chart_type(self, val: str):
        self.settings.setValue("default_chart_type", val)
        self.settings_changed.emit()

    # --- VISUALIZAÇÃO DA ABA GLOBAL (Tipo 1 ou Tipo 2) ---
    @property
    def global_view_type(self) -> int:
        """
        0: Tipo 1 (Detalhado por Caso - Scroll com Cards)
        1: Tipo 2 (Comparativo Lado a Lado - Tabela Única)
        """
        return int(self.settings.value("global_view_type", 0)) # Default: 0

    @global_view_type.setter
    def global_view_type(self, val: int):
        self.settings.setValue("global_view_type", val)
        self.settings_changed.emit()

    # --- ENDEREÇO DA API ---
    @property
    def api_url(self) -> str:
        return str(self.settings.value("api_url", "http://127.0.0.1:8000")) # Default local

    @api_url.setter
    def api_url(self, val: str):
        self.settings.setValue("api_url", val)
        self.settings_changed.emit()

    # --- MÉTODOS UTILITÁRIOS DE FORMATAÇÃO ---
    def format_number(self, value: float, is_table: bool = True, is_lolp: bool = False) -> str:
        """Formata qualquer número de acordo com as preferências atuais do usuário."""
        if value is None:
            return "-"
            
        try:
            val = float(value)
        except (ValueError, TypeError):
            return "-"

        decimals = self.table_decimals if is_table else self.chart_decimals

        # Regra especial para o LOLP
        if is_lolp and self.lolp_format == "scientific":
            return f"{val:.{decimals}e}" # Ex: 3.200e-05

        return f"{val:.{decimals}f}" # Ex: 0.00032 ou 2877.416
from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.settings_service import SettingsService

class SettingsViewModel(QObject):
    settings_saved = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.service = SettingsService.get_instance()

    def get_current_settings(self) -> dict: # O erro do parênteses duplo foi corrigido aqui!
        return {
            "table_decimals": self.service.table_decimals,
            "chart_decimals": self.service.chart_decimals,
            "lolp_format": self.service.lolp_format,
            "default_chart_type": self.service.default_chart_type,
        }

    def save_settings(self, table_dec: int, chart_dec: int, lolp_fmt: str, chart_type: str):
        self.service.table_decimals = table_dec
        self.service.chart_decimals = chart_dec
        self.service.lolp_format = lolp_fmt
        self.service.default_chart_type = chart_type
        self.settings_saved.emit("Configurações pessoais salvas com sucesso!")
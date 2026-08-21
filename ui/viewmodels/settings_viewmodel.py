from PyQt6.QtCore import QObject, pyqtSignal
from ui.services.settings_service import SettingsService

class SettingsViewModel(QObject):
    settings_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.service = SettingsService.get_instance()

    def load_settings(self) -> dict:
        return {
            "table_decimals": self.service.table_decimals,
            "chart_decimals": self.service.chart_decimals,
            "lolp_format": self.service.lolp_format,
            "default_chart_type": self.service.default_chart_type,
            "global_view_type": self.service.global_view_type,
            "api_url": self.service.api_url
        }

    def save_settings(self, config: dict):
        self.service.table_decimals = config.get("table_decimals", 3)
        self.service.chart_decimals = config.get("chart_decimals", 3)
        self.service.lolp_format = config.get("lolp_format", "decimal")
        self.service.default_chart_type = config.get("default_chart_type", "Pareto")
        self.service.global_view_type = config.get("global_view_type", 0)
        self.service.api_url = config.get("api_url", "http://127.0.0.1:8000")
        self.settings_saved.emit()
# ui/styles.py
"""
Sistema central de estilos do RevEla Analyzer.

Objetivo
--------
Centralizar cores, tipografia, dimensões e aparência dos widgets Qt em um
único arquivo. As janelas e widgets devem consumir este estilo sempre que
possível, evitando QSS espalhado pelos arquivos da interface.

IMPORTANTE
----------
Os ícones usados pelo stylesheet são arquivos PNG registrados no Qt Resource
System (.qrc). Para trocar um ícone, substitua o arquivo indicado na seção
ICONS ou altere somente o caminho correspondente nesta classe.

Estrutura esperada dos recursos:
    :/img/revela_analyzer/ui/widgets/
"""

from PyQt6.QtWidgets import QApplication


class GlobalStyles:
    """Estilo visual global do RevEla Analyzer."""

    # =========================================================================
    # PALETA DE CORES
    # =========================================================================

    PALETTE = {
        "bg_app": "#F8FAFC",
        "bg_surface": "#FFFFFF",
        "bg_hover": "#F1F5F9",

        "border_default": "#CBD5E1",
        "border_active": "#0078D4",

        "text_primary": "#0F172A",
        "text_secondary": "#334155",
        "text_disabled": "#94A3B8",

        "primary": "#0078D4",
        "primary_hover": "#005A9E",
        "primary_pressed": "#004578",

        "disabled_bg": "#E2E8F0",
    }

    # =========================================================================
    # DIMENSÕES PADRONIZADAS
    # =========================================================================

    METRICS = {
        "input_height": 34,
        "input_radius": 9,
        "button_radius": 9,
        "table_radius": 6,
        "scrollbar_width": 10,
        "combo_arrow_width": 28,
        "spin_button_width": 22,
    }

    # =========================================================================
    # ÍCONES PNG
    # =========================================================================

    ICONS = {
        "combo_arrow": ":/img/revela_analyzer/widgets/arrow_down.png",
        "spin_up": ":/img/revela_analyzer/widgets/triangle_up.png",
        "spin_down": ":/img/revela_analyzer/widgets/triangle_down.png",
        "radio_off": ":/img/revela_analyzer/widgets/point_off.png",
        "radio_hover": ":/img/revela_analyzer/widgets/point.png",
        "radio_checked": ":/img/revela_analyzer/widgets/point_solid.png",
    }

    # =========================================================================
    # ESTILO BASE
    # =========================================================================

    @classmethod
    def create_style(cls):
        """
        Retorna o estilo nativo do Qt.

        O RevEla utiliza QSS para a personalização visual. Portanto, não é
        necessário criar uma classe QProxyStyle apenas para aplicar o
        stylesheet.

        Uso:
            app.setStyle(GlobalStyles.create_style())
            app.setStyleSheet(GlobalStyles.get_app_stylesheet())
        """
        return QApplication.style()

    # =========================================================================
    # STYLESHEET GLOBAL
    # =========================================================================

    @classmethod
    def get_app_stylesheet(cls):
        """Retorna o stylesheet completo do RevEla."""

        p = cls.PALETTE
        i = cls.ICONS
        m = cls.METRICS

        stylesheet = f"""
        /* =================================================================
           APLICAÇÃO
           ================================================================= */

        QWidget {{
            background-color: {p["bg_app"]};
            color: {p["text_primary"]};
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 13px;
        }}


        /* =================================================================
           SCROLL AREA
           ================================================================= */

        QScrollArea {{
            border: none;
            background-color: transparent;
        }}


        /* =================================================================
           BARRAS DE ROLAGEM
           ================================================================= */

        QScrollBar:vertical {{
            border: none;
            background-color: {p["bg_app"]};
            width: {m["scrollbar_width"]}px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {p["border_default"]};
            border-radius: 5px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {p["text_disabled"]};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
            border: none;
            background: transparent;
        }}


        /* =================================================================
           CAMPOS DE ENTRADA — BASE
           ================================================================= */

        QLineEdit,
        QComboBox,
        QSpinBox,
        QDoubleSpinBox {{
            min-height: {m["input_height"]}px;
            max-height: {m["input_height"]}px;

            border: 1px solid {p["border_default"]};
            border-radius: {m["input_radius"]}px;

            padding: 4px 12px;

            background-color: {p["bg_surface"]};
            color: {p["text_primary"]};

            font-size: 13px;
            font-weight: 500;
        }}

        QLineEdit:hover,
        QComboBox:hover,
        QSpinBox:hover,
        QDoubleSpinBox:hover {{
            border-color: {p["border_active"]};
        }}

        QLineEdit:focus,
        QComboBox:focus,
        QSpinBox:focus,
        QDoubleSpinBox:focus {{
            border: 1px solid {p["border_active"]};
        }}

        QLineEdit:disabled,
        QComboBox:disabled,
        QSpinBox:disabled,
        QDoubleSpinBox:disabled {{
            background-color: {p["disabled_bg"]};
            color: {p["text_disabled"]};
            border-color: {p["border_default"]};
        }}


        /* =================================================================
           COMBOBOX
           ================================================================= */

        QComboBox {{
            padding-right: 34px;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: border;
            subcontrol-position: top right;

            width: {m["combo_arrow_width"]}px;

            border: none;
            background-color: transparent;
        }}

        /*
           [PNG - ÍCONE SUBSTITUÍVEL]
           Arquivo atual:
               widgets/arrow_down.png
        */
        QComboBox::down-arrow {{
            image: url({i["combo_arrow"]});
            width: 10px;
            height: 10px;
        }}

        QComboBox QAbstractItemView {{
            border: 1px solid {p["border_default"]};
            border-radius: 6px;

            background-color: {p["bg_surface"]};

            selection-background-color: {p["bg_hover"]};
            selection-color: {p["primary"]};

            outline: none;
            padding: 4px;
        }}

        QComboBox QAbstractItemView::item {{
            min-height: 28px;
            padding: 4px 8px;
        }}

        QComboBox QAbstractItemView::item:hover {{
            background-color: {p["bg_hover"]};
        }}


        /* =================================================================
           SPINBOX / DOUBLESPINBOX
           ================================================================= */

        QSpinBox,
        QDoubleSpinBox {{
            padding-right: 30px;
        }}

        QSpinBox::up-button,
        QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;

            width: {m["spin_button_width"]}px;

            border: none;
            background-color: transparent;
        }}

        QSpinBox::down-button,
        QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;

            width: {m["spin_button_width"]}px;

            border: none;
            background-color: transparent;
        }}

        /*
           [PNG - ÍCONE SUBSTITUÍVEL]
           Arquivo atual:
               widgets/triangle_up.png
        */
        QSpinBox::up-arrow,
        QDoubleSpinBox::up-arrow {{
            image: url({i["spin_up"]});
            width: 10px;
            height: 10px;
        }}

        /*
           [PNG - ÍCONE SUBSTITUÍVEL]
           Arquivo atual:
               widgets/triangle_down.png
        */
        QSpinBox::down-arrow,
        QDoubleSpinBox::down-arrow {{
            image: url({i["spin_down"]});
            width: 10px;
            height: 10px;
        }}

        QSpinBox::up-button:pressed,
        QDoubleSpinBox::up-button:pressed,
        QSpinBox::down-button:pressed,
        QDoubleSpinBox::down-button:pressed {{
            background-color: rgba(0, 0, 0, 0.05);
        }}


        /* =================================================================
           RADIO BUTTON
           ================================================================= */

        QRadioButton {{
            spacing: 8px;
        }}

        /*
           [PNG - ÍCONE SUBSTITUÍVEL]
           Estado normal:
               widgets/point_off.png
        */
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            image: url({i["radio_off"]});
        }}

        /*
           [PNG - ÍCONE SUBSTITUÍVEL]
           Estado hover:
               widgets/point.png
        */
        QRadioButton::indicator:hover {{
            image: url({i["radio_hover"]});
        }}

        /*
           [PNG - ÍCONE SUBSTITUÍVEL]
           Estado marcado:
               widgets/point_solid.png
        */
        QRadioButton::indicator:checked {{
            image: url({i["radio_checked"]});
        }}


        /* =================================================================
           BOTÕES
           ================================================================= */

        QPushButton {{
            min-height: 20px;

            padding: 8px 22px;

            background-color: {p["primary"]};
            color: white;

            border: none;
            border-radius: {m["button_radius"]}px;

            font-size: 14px;
            font-weight: 700;
        }}

        QPushButton:hover {{
            background-color: {p["primary_hover"]};
        }}

        QPushButton:pressed {{
            background-color: {p["primary_pressed"]};
        }}

        QPushButton:disabled {{
            background-color: {p["disabled_bg"]};
            color: {p["text_disabled"]};
        }}


        /* =================================================================
           TABELAS
           ================================================================= */

        QTableWidget {{
            background-color: {p["bg_surface"]};
            color: {p["text_primary"]};

            border: 1px solid {p["border_default"]};
            border-radius: {m["table_radius"]}px;

            gridline-color: {p["disabled_bg"]};

            selection-background-color: {p["bg_hover"]};
            selection-color: {p["primary"]};

            outline: none;
        }}

        QHeaderView::section {{
            background-color: {p["bg_app"]};
            color: {p["text_secondary"]};

            padding: 6px 4px;

            border: none;
            border-bottom: 2px solid {p["border_default"]};

            font-weight: 700;
        }}

        QHeaderView::section:hover {{
            background-color: {p["disabled_bg"]};
        }}
        """

        return stylesheet

    # =========================================================================
    # APLICAÇÃO DO ESTILO
    # =========================================================================

    @classmethod
    def apply(cls, app):
        """
        Aplica o estilo completo do RevEla à QApplication.

        Uso:
            app = QApplication(sys.argv)
            GlobalStyles.apply(app)
        """

        # O stylesheet é responsável pela identidade visual.
        app.setStyleSheet(cls.get_app_stylesheet())

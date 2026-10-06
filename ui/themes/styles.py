# ui/styles.py

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QProxyStyle, QStyle


class RevElaStyle(QProxyStyle):
    """
    Estilo personalizado do RevEla.

    Mantém o desenho nativo dos controles do Qt e substitui
    somente as setas dos ComboBox e SpinBox por setas desenhadas
    diretamente com QPainter.
    """

    def drawPrimitive(self, element, option, painter, widget=None):
        # =============================================================
        # SETAS DO COMBOBOX E SPINBOX
        # =============================================================

        if element == QStyle.PrimitiveElement.PE_IndicatorArrowDown:
            self._draw_arrow(
                painter,
                option.rect,
                direction="down",
                color=QColor("#0F172A")
            )
            return

        if element == QStyle.PrimitiveElement.PE_IndicatorArrowUp:
            self._draw_arrow(
                painter,
                option.rect,
                direction="up",
                color=QColor("#0F172A")
            )
            return

        super().drawPrimitive(element, option, painter, widget)

    @staticmethod
    def _draw_arrow(painter, rect, direction, color):
        """
        Desenha uma pequena seta usando QPainter.

        A seta não utiliza SVG nem imagem externa.
        """

        painter.save()

        # Antialiasing deixa a seta mais suave.
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True
        )

        pen = QPen(color)
        pen.setWidthF(1.7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Centro da região destinada à seta.
        cx = rect.center().x()
        cy = rect.center().y()

        # Dimensões da seta.
        width = 7
        height = 4

        if direction == "down":
            painter.drawLine(
                cx - width / 2,
                cy - height / 2,
                cx,
                cy + height / 2
            )

            painter.drawLine(
                cx,
                cy + height / 2,
                cx + width / 2,
                cy - height / 2
            )

        else:
            painter.drawLine(
                cx - width / 2,
                cy + height / 2,
                cx,
                cy - height / 2
            )

            painter.drawLine(
                cx,
                cy - height / 2,
                cx + width / 2,
                cy + height / 2
            )

        painter.restore()


class GlobalStyles:

    # =============================================================
    # PALETA DE CORES
    # =============================================================

    PALETTE = {
        "bg_app": "#F8FAFC",
        "bg_surface": "#FFFFFF",
        "bg_hover": "#F1F5F9",
        "border_default": "#CBD5E1",
        "border_active": "#0078d4",
        "text_primary": "#0F172A",
        "text_secondary": "#334155",
        "text_disabled": "#94A3B8",
        "primary": "#0078d4",
        "primary_hover": "#005A9E",
        "primary_pressed": "#004578",
        "disabled_bg": "#E2E8F0",
    }

    # =============================================================
    # ESTILO DO QT
    # =============================================================

    @classmethod
    def create_style(cls):
        """
        Cria o estilo personalizado do RevEla.

        Deve ser aplicado à QApplication:
            app.setStyle(GlobalStyles.create_style())
        """

        return RevElaStyle()

    # =============================================================
    # STYLE SHEET GLOBAL
    # =============================================================

    @classmethod
    def get_app_stylesheet(cls):

        stylesheet = """

        /* =========================================================
           ESTILO GLOBAL DA APLICAÇÃO
           ========================================================= */

        QWidget {
            background-color: @bg_app;
            font-family: 'Segoe UI', Arial, sans-serif;
            color: @text_primary;
        }


        /* =========================================================
           SCROLL AREA
           ========================================================= */

        QScrollArea {
            border: none;
            background-color: transparent;
        }


        /* =========================================================
           BARRAS DE ROLAGEM
           ========================================================= */

        QScrollBar:vertical {
            border: none;
            background-color: @bg_app;
            width: 10px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical {
            background-color: @border_default;
            border-radius: 5px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: @text_disabled;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }


        /* =========================================================
           INPUTS
           ========================================================= */

        QComboBox,
        QSpinBox,
        QLineEdit {
            min-height: 34px;
            max-height: 34px;

            border: 1px solid @border_default;
            border-radius: 9px;

            padding: 4px 12px;

            background-color: @bg_surface;
            color: @text_primary;

            font-size: 13px;
            font-weight: 500;
        }


        /* =========================================================
           COMBOBOX
           ========================================================= */

        QComboBox {
            padding-right: 32px;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;

            width: 30px;

            border: none;
            border-left: 1px solid @border_default;

            border-top-right-radius: 9px;
            border-bottom-right-radius: 9px;

            background-color: @bg_surface;
        }

        QComboBox::drop-down:hover {
            background-color: @bg_hover;
        }


        /* =========================================================
           LISTA DO COMBOBOX
           ========================================================= */

        QComboBox QAbstractItemView {
            border: 1px solid @border_default;
            border-radius: 6px;

            background-color: @bg_surface;

            selection-background-color: @bg_hover;
            selection-color: @primary;

            outline: none;
            padding: 4px;
        }


        /* =========================================================
           SPINBOX
           ========================================================= */

        QSpinBox {
            padding-right: 34px;
        }

        /*
           Não definimos ::up-button, ::down-button,
           ::up-arrow ou ::down-arrow.

           O Qt controla esses elementos nativamente.
           Somente o desenho das setas é substituído
           pelo RevElaStyle.
        */


        /* =========================================================
           CHECKBOXES E RADIO BUTTONS
           ========================================================= */

        QCheckBox,
        QRadioButton {
            spacing: 8px;

            font-size: 14px;
            color: @text_secondary;
            font-weight: 500;
        }

        QCheckBox:disabled,
        QRadioButton:disabled {
            color: @text_disabled;
        }


        QCheckBox::indicator,
        QRadioButton::indicator {
            width: 18px;
            height: 18px;

            border-radius: 4px;

            border: 2px solid @border_default;
            background-color: @bg_surface;
        }


        QRadioButton::indicator {
            border-radius: 11px;
        }


        QCheckBox::indicator:hover,
        QRadioButton::indicator:hover {
            border-color: @primary;
        }


        QCheckBox::indicator:checked,
        QRadioButton::indicator:checked {
            background-color: @primary;
            border-color: @primary;
        }


        QCheckBox::indicator:disabled,
        QRadioButton::indicator:disabled {
            background-color: @disabled_bg;
            border-color: @border_default;
        }


        /* =========================================================
           BOTÕES
           ========================================================= */

        QPushButton {
            background-color: @primary;

            color: white;

            font-size: 14px;
            font-weight: 700;

            border: none;
            border-radius: 9px;

            padding: 8px 22px;

            min-height: 20px;
        }


        QPushButton:hover {
            background-color: @primary_hover;
        }


        QPushButton:pressed {
            background-color: @primary_pressed;
        }


        QPushButton:disabled {
            background-color: @disabled_bg;
            color: @text_disabled;
        }


        /* =========================================================
           TABELAS
           ========================================================= */

        QTableWidget {
            background-color: @bg_surface;

            color: @text_primary;

            border: 1px solid @border_default;
            border-radius: 6px;

            gridline-color: @disabled_bg;

            selection-background-color: @bg_hover;
            selection-color: @primary;

            outline: none;
        }


        QHeaderView::section {
            background-color: @bg_app;

            color: @text_secondary;

            font-weight: 700;

            border: none;
            border-bottom: 2px solid @border_default;

            padding: 6px 4px;
        }


        QHeaderView::section:hover {
            background-color: @disabled_bg;
        }

        """

        # =============================================================
        # SUBSTITUIÇÃO DOS TOKENS DE CORES
        # =============================================================

        for token, color in sorted(
            cls.PALETTE.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            stylesheet = stylesheet.replace(
                f"@{token}",
                color
            )

        return stylesheet

    # =============================================================
    # APLICAÇÃO COMPLETA DO ESTILO
    # =============================================================

    @classmethod
    def apply(cls, app):
        """
        Aplica o estilo completo do RevEla à QApplication.

        Uso:

            app = QApplication(sys.argv)
            GlobalStyles.apply(app)
        """

        app.setStyle(cls.create_style())
        app.setStyleSheet(cls.get_app_stylesheet())
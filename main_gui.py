import sys
from PyQt6.QtWidgets import QApplication
from ui.views.login_view import LoginView


def main():
    app = QApplication(sys.argv)

    # Aplica um estilo base limpo
    app.setStyle("Fusion")

    # ==========================================
    # FOLHA DE ESTILOS GLOBAL
    # ==========================================
    app.setStyleSheet("""
        /* Garante que o texto padrão de tudo seja escuro */
        QWidget {
            color: #2C3E50;
        }

        /* Inputs e caixas de seleção */
        QLineEdit, QSpinBox, QComboBox {
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #BDC3C7;
            padding: 2px;
        }

        /* Tabelas */
        QTableWidget {
            color: #000000;
            background-color: #FFFFFF;
        }

        QHeaderView::section {
            color: #000000;
        }

        /* Menus drop-down */
        QComboBox QAbstractItemView {
            color: #000000;
            background-color: #FFFFFF;
        }
    """)

    window = LoginView()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
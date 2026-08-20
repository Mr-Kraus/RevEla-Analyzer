import sys
from PyQt6.QtWidgets import QApplication
from ui.views.login_view import LoginView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplica um estilo base limpo
    app.setStyle("Fusion") 
    
    # ==========================================
    # FOLHA DE ESTILOS GLOBAL (Garante a legibilidade)
    # ==========================================
    app.setStyleSheet("""
        /* Garante que o texto padrão de tudo seja escuro (Cinza Escuro / Preto) */
        QWidget {
            color: #2C3E50; 
        }
        
        /* Garante que inputs e caixas de seleção tenham fundo branco e letra preta */
        QLineEdit, QSpinBox, QComboBox {
            color: #000000;
            background-color: #FFFFFF;
            border: 1px solid #BDC3C7;
            padding: 2px;
        }
        
        /* Garante que as tabelas tenham letras pretas legíveis */
        QTableWidget {
            color: #000000;
            background-color: #FFFFFF;
        }
        
        QHeaderView::section {
            color: #000000;
        }
        
        /* Menus drop-down legíveis */
        QComboBox QAbstractItemView {
            color: #000000;
            background-color: #FFFFFF;
        }
    """)
    
    window = LoginView()
    window.show()
    
    sys.exit(app.exec())
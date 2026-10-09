import sys
from PyQt6.QtWidgets import QApplication
from ui.views.login_view import LoginView
from ui.themes.styles import GlobalStyles
from ui.themes.styles import GlobalStyles
import ui.resources_rc

from ui.themes.styles import GlobalStyles

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    GlobalStyles.apply(app)
    window = LoginView()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
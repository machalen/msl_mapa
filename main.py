import sys

# QWebEngineView s'ha d'importar ABANS de crear QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from database.db import DatabaseManager
from ui.main_window import MainWindow
from utils.paths import db_path


def main():
    # Necessari per a QWebEngineView en alguns sistemes
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setApplicationName("MSL Mapa")
    app.setOrganizationName("Gori & Co")

    db = DatabaseManager(str(db_path()))
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

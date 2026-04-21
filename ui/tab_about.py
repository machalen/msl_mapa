from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("MSL Mapa")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2563d4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        company = QLabel("Gori & Co SCMMDLG")
        company.setStyleSheet("font-size: 16px; color: #64748b; margin-top: 8px;")
        company.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company)

        desc = QLabel(
            "Gestió de la xarxa d'hospitals, doctors i projectes\n"
            "a la Península Ibèrica"
        )
        desc.setStyleSheet("font-size: 13px; color: #94a3b8; margin-top: 16px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

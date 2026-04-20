from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
)

from database.db import DatabaseManager
from utils.export import ExcelExporter


class DoctorsTab(QWidget):
    hospital_selected = pyqtSignal(int)   # doble clic → navegar a l'hospital al mapa

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self._data: list[dict] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        top = QHBoxLayout()
        self._search = QLineEdit(placeholderText="Cercar per nom, especialitat, institució, hospital…")
        self._search.textChanged.connect(self._on_search)
        top.addWidget(self._search)

        btn_export = QPushButton("Exportar Excel")
        btn_export.setFixedWidth(120)
        btn_export.clicked.connect(self._export)
        top.addWidget(btn_export)
        layout.addLayout(top)

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Nom", "Especialitat", "Email", "Telèfon", "Institució", "Hospital"]
        )
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table)

    def refresh(self):
        self._on_search(self._search.text())

    def _on_search(self, text: str):
        self._data = self.db.search_doctors(text.strip())
        self._table.setRowCount(len(self._data))
        for row, d in enumerate(self._data):
            self._table.setItem(row, 0, QTableWidgetItem(d["nom"]))
            self._table.setItem(row, 1, QTableWidgetItem(d.get("especialitat", "")))
            self._table.setItem(row, 2, QTableWidgetItem(d.get("email", "")))
            self._table.setItem(row, 3, QTableWidgetItem(d.get("telefon", "")))
            self._table.setItem(row, 4, QTableWidgetItem(d.get("institucio", "")))
            self._table.setItem(row, 5, QTableWidgetItem(d.get("hospital_nom", "")))

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar doctors", "doctors.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        ExcelExporter().export_doctors(self._data, path)
        QMessageBox.information(self, "Exportació", f"Fitxer guardat:\n{path}")

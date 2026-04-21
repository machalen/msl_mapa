from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
)

from database.db import DatabaseManager
from utils.export import ExcelExporter


class HospitalsTab(QWidget):
    hospital_selected = pyqtSignal(int)   # doble clic → pan mapa

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self._data: list[dict] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        top = QHBoxLayout()
        self._search = QLineEdit(placeholderText="Cercar hospitals, doctors o projectes…")
        self._search.textChanged.connect(self._on_search)
        top.addWidget(self._search)

        btn_export = QPushButton("Exportar Excel")
        btn_export.setFixedWidth(120)
        btn_export.clicked.connect(self._export)
        top.addWidget(btn_export)
        layout.addLayout(top)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Nom", "Status", "Ciutat", "Comunitat autònoma"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

    def refresh(self):
        self._on_search(self._search.text())

    def _on_search(self, text: str):
        self._data = self.db.search_hospitals(text.strip())
        self._table.setRowCount(len(self._data))
        for row, d in enumerate(self._data):
            self._table.setItem(row, 0, QTableWidgetItem(d["nom"]))
            self._table.setItem(row, 1, QTableWidgetItem(d["status"]))
            self._table.setItem(row, 2, QTableWidgetItem(d.get("ciutat", "")))
            self._table.setItem(row, 3, QTableWidgetItem(d.get("comunitat", "")))
            for col in range(4):
                item = self._table.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, d["id"])

    def _on_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self._data):
            self.hospital_selected.emit(self._data[row]["id"])

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar hospitals", "hospitals.xlsx",
            "Excel (*.xlsx)"
        )
        if not path:
            return
        ExcelExporter().export_hospitals(self._data, path)
        QMessageBox.information(self, "Exportació", f"Fitxer guardat:\n{path}")

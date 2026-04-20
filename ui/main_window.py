from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QWidget,
)
from PyQt6.QtCore import Qt

from database.db import DatabaseManager
from ui.map_widget import MapWidget
from ui.hospital_dialog import HospitalDialog
from ui.tab_hospitals import HospitalsTab
from ui.tab_doctors import DoctorsTab
from ui.tab_projectes import ProjectesTab
from ui.tab_about import AboutTab


class MainWindow(QMainWindow):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.setWindowTitle("MSL Mapa — Gori & Co")
        self.resize(1100, 720)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        # Pestanya 0: Mapa
        self._map_widget = MapWidget(self.db)
        self._tabs.addTab(self._map_widget, "Mapa")

        # Pestanyes de llistes
        self._tab_hospitals = HospitalsTab(self.db)
        self._tabs.addTab(self._tab_hospitals, "Hospitals")

        self._tab_doctors = DoctorsTab(self.db)
        self._tabs.addTab(self._tab_doctors, "Doctors")

        self._tab_projectes = ProjectesTab(self.db)
        self._tabs.addTab(self._tab_projectes, "Projectes")

        self._tab_about = AboutTab()
        self._tabs.addTab(self._tab_about, "Quant a")

        self.setCentralWidget(self._tabs)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        # Carregar dades inicials a les pestanyes de llista
        self._tab_hospitals.refresh()
        self._tab_doctors.refresh()
        self._tab_projectes.refresh()
        self._refresh_status()

    def _connect_signals(self):
        self._map_widget.hospital_clicked.connect(self._on_hospital_selected)
        self._map_widget.map_clicked_empty.connect(self._on_map_clicked_empty)
        self._tab_hospitals.hospital_selected.connect(self._on_hospital_tab_selected)

    # ── Interaccions del mapa ──────────────────────────────────────────────

    def _on_hospital_selected(self, hospital_id: int):
        hospital = self.db.get_hospital(hospital_id)
        if not hospital:
            return
        dlg = HospitalDialog(self.db, hospital, parent=self)
        result = dlg.exec()
        self.refresh_all()

    def _on_map_clicked_empty(self, lat: float, lng: float):
        dlg = HospitalDialog(self.db, None, lat=lat, lng=lng, parent=self)
        if dlg.exec() == 1:  # Accepted
            self.refresh_all()

    def _on_hospital_tab_selected(self, hospital_id: int):
        # Canvia a la pestanya del mapa i centra en l'hospital
        self._tabs.setCurrentIndex(0)
        self._map_widget.highlight_hospital(hospital_id)

    # ── Actualització global ───────────────────────────────────────────────

    def refresh_all(self):
        self._map_widget.refresh_pins()
        self._tab_hospitals.refresh()
        self._tab_doctors.refresh()
        self._tab_projectes.refresh()
        self._refresh_status()

    def _refresh_status(self):
        n_hospitals = len(self.db.get_all_hospitals())
        n_doctors = len(self.db.search_doctors(""))
        n_projectes = len(self.db.search_projectes(""))
        self._status.showMessage(
            f"{n_hospitals} hospitals  ·  {n_doctors} doctors  ·  {n_projectes} projectes"
        )

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)

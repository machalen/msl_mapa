import json
from pathlib import Path

from PyQt6.QtCore import QUrl, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from database.db import DatabaseManager
from utils.paths import resource_path

_MAP_HTML = resource_path("assets/map_template.html")


class _Bridge(QObject):
    """Objecte registrat a QWebChannel. JavaScript l'usa com a pyBridge."""

    hospital_clicked = pyqtSignal(int)
    map_clicked_empty = pyqtSignal(float, float)
    add_hospital_requested = pyqtSignal()

    @pyqtSlot(str)
    def on_js_message(self, message: str):
        try:
            data = json.loads(message)
            if data.get("type") == "pin_click":
                self.hospital_clicked.emit(int(data["hospital_id"]))
            elif data.get("type") == "map_click":
                self.map_clicked_empty.emit(float(data["lat"]), float(data["lng"]))
            elif data.get("type") == "add_hospital_click":
                self.add_hospital_requested.emit()
        except (KeyError, ValueError, json.JSONDecodeError):
            pass


class MapWidget(QWidget):
    hospital_clicked = pyqtSignal(int)
    map_clicked_empty = pyqtSignal(float, float)
    add_hospital_requested = pyqtSignal()

    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db

        self._view = QWebEngineView()

        # Habilitar accés a fitxers locals i JavaScript
        settings = self._view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        self._bridge = _Bridge()
        self._channel = QWebChannel()
        self._channel.registerObject("bridge", self._bridge)
        self._view.page().setWebChannel(self._channel)

        # Reencaminar senyals del bridge cap a l'exterior
        self._bridge.hospital_clicked.connect(self.hospital_clicked)
        self._bridge.map_clicked_empty.connect(self.map_clicked_empty)
        self._bridge.add_hospital_requested.connect(self.add_hospital_requested)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)

        # Connectar el senyal ABANS de carregar (evita perdre l'event)
        self._view.loadFinished.connect(self._on_load_finished)
        self._view.load(QUrl.fromLocalFile(str(_MAP_HTML.resolve())))

    def _on_load_finished(self, ok: bool):
        if ok:
            self.refresh_pins()

    def refresh_pins(self):
        hospitals = self.db.get_all_hospitals()
        data = [
            {"id": h.id, "nom": h.nom, "lat": h.lat, "lng": h.lng, "color": h.color}
            for h in hospitals
        ]
        js = f"setHospitals({json.dumps(data, ensure_ascii=False)})"
        self._view.page().runJavaScript(js)

    def pan_to_hospital(self, hospital_id: int):
        self._view.page().runJavaScript(f"panToHospital({hospital_id})")

    def highlight_hospital(self, hospital_id: int):
        self._view.page().runJavaScript(f"highlightHospital({hospital_id})")

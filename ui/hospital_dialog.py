from __future__ import annotations
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QTextEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QColorDialog,
    QMessageBox, QDialogButtonBox, QWidget, QSizePolicy,
)

from database.db import DatabaseManager
from models.hospital import Hospital
from models.doctor import Doctor
from models.projecte import Projecte


# ─── Diàleg per editar un doctor ──────────────────────────────────────────────

class DoctorDialog(QDialog):
    def __init__(self, db: DatabaseManager, doctor: Optional[Doctor],
                 hospital_id: int, parent=None):
        super().__init__(parent)
        self.db = db
        self.doctor = doctor or Doctor(nom="", hospital_id=hospital_id)
        self.hospital_id = hospital_id
        self.setWindowTitle("Doctor" if doctor else "Nou doctor")
        self.setMinimumWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._nom = QLineEdit(self.doctor.nom)
        self._especialitat = QLineEdit(self.doctor.especialitat)
        self._email = QLineEdit(self.doctor.email)
        self._telefon = QLineEdit(self.doctor.telefon)
        self._institucio = QLineEdit(self.doctor.institucio)
        self._linkedin = QLineEdit(self.doctor.linkedin)
        self._obs = QTextEdit(self.doctor.observacions)
        self._obs.setFixedHeight(80)

        form.addRow("Nom *", self._nom)
        form.addRow("Especialitat", self._especialitat)
        form.addRow("Email", self._email)
        form.addRow("Telèfon", self._telefon)
        form.addRow("Institució", self._institucio)
        form.addRow("LinkedIn", self._linkedin)

        layout.addLayout(form)

        # Projectes: llista de vinculats + desplegable per afegir-ne
        all_projectes = self.db.get_projectes_for_hospital(self.hospital_id)
        linked_ids = set(self.db.get_projecte_ids_for_doctor(self.doctor.id))
        # Diccionari id → nom per a tots els projectes de l'hospital
        self._all_proj_map: dict[int, str] = {p.id: p.nom for p in all_projectes}
        # Conjunt d'ids vinculats (mutable, es modifica amb add/remove)
        self._linked_ids: set[int] = set(linked_ids)

        grp = QGroupBox("Projectes associats")
        grp_layout = QVBoxLayout(grp)

        # Taula dels projectes ja vinculats
        self._proj_table = QTableWidget(0, 1)
        self._proj_table.setHorizontalHeaderLabels(["Projecte"])
        self._proj_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._proj_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._proj_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._proj_table.setMaximumHeight(120)
        grp_layout.addWidget(self._proj_table)
        self._refresh_proj_table()

        # Fila: desplegable + botó afegir + botó eliminar
        add_row = QHBoxLayout()
        self._proj_combo = QComboBox()
        self._proj_combo.setMinimumWidth(200)
        add_row.addWidget(self._proj_combo)
        btn_add_proj = QPushButton("+ Afegir")
        btn_add_proj.clicked.connect(self._add_proj_link)
        add_row.addWidget(btn_add_proj)
        btn_del_proj = QPushButton("Eliminar")
        btn_del_proj.clicked.connect(self._remove_proj_link)
        add_row.addWidget(btn_del_proj)
        add_row.addStretch()
        grp_layout.addLayout(add_row)

        self._update_proj_combo()
        layout.addWidget(grp)

        form2 = QFormLayout()
        form2.addRow("Observacions", self._obs)
        layout.addLayout(form2)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh_proj_table(self):
        linked = sorted(self._linked_ids,
                        key=lambda pid: self._all_proj_map.get(pid, ""))
        self._proj_table.setRowCount(len(linked))
        for row, pid in enumerate(linked):
            item = QTableWidgetItem(self._all_proj_map.get(pid, "?"))
            item.setData(Qt.ItemDataRole.UserRole, pid)
            self._proj_table.setItem(row, 0, item)

    def _update_proj_combo(self):
        """Omple el desplegable amb els projectes de l'hospital que encara no estan vinculats."""
        self._proj_combo.clear()
        for pid, nom in sorted(self._all_proj_map.items(), key=lambda x: x[1]):
            if pid not in self._linked_ids:
                self._proj_combo.addItem(nom, pid)  # userData = pid

    def _add_proj_link(self):
        pid = self._proj_combo.currentData()
        if pid is not None and pid not in self._linked_ids:
            self._linked_ids.add(pid)
            self._refresh_proj_table()
            self._update_proj_combo()

    def _remove_proj_link(self):
        selected = self._proj_table.selectedItems()
        if not selected:
            return
        pid = selected[0].data(Qt.ItemDataRole.UserRole)
        self._linked_ids.discard(pid)
        self._refresh_proj_table()
        self._update_proj_combo()

    def _save(self):
        nom = self._nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Camp obligatori", "El nom del doctor és obligatori.")
            return
        self.doctor.nom = nom
        self.doctor.especialitat = self._especialitat.text().strip()
        self.doctor.email = self._email.text().strip()
        self.doctor.telefon = self._telefon.text().strip()
        self.doctor.institucio = self._institucio.text().strip()
        self.doctor.linkedin = self._linkedin.text().strip()
        self.doctor.observacions = self._obs.toPlainText().strip()

        doc_id = self.db.save_doctor(self.doctor)
        self.doctor.id = doc_id
        self.db.set_doctor_projectes(doc_id, list(self._linked_ids))
        self.accept()


# ─── Diàleg per editar un projecte ────────────────────────────────────────────

class ProjecteDialog(QDialog):
    def __init__(self, db: DatabaseManager, projecte: Optional[Projecte],
                 hospital_id: int, parent=None):
        super().__init__(parent)
        self.db = db
        self.projecte = projecte or Projecte(nom="", hospital_id=hospital_id)
        self.setWindowTitle("Projecte" if projecte else "Nou projecte")
        self.setMinimumWidth(380)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._nom = QLineEdit(self.projecte.nom)
        self._tema = QLineEdit(self.projecte.tema)
        self._status = QComboBox()
        self._status.addItems(["actiu", "inactiu", "completat"])
        self._status.setCurrentText(self.projecte.status)
        self._obs = QTextEdit(self.projecte.observacions)
        self._obs.setFixedHeight(80)

        form.addRow("Nom *", self._nom)
        form.addRow("Tema", self._tema)
        form.addRow("Status", self._status)
        form.addRow("Observacions", self._obs)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        nom = self._nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Camp obligatori", "El nom del projecte és obligatori.")
            return
        self.projecte.nom = nom
        self.projecte.tema = self._tema.text().strip()
        self.projecte.status = self._status.currentText()
        self.projecte.observacions = self._obs.toPlainText().strip()
        self.db.save_projecte(self.projecte)
        self.accept()


# ─── Diàleg principal de l'hospital ───────────────────────────────────────────

class HospitalDialog(QDialog):
    def __init__(self, db: DatabaseManager, hospital: Optional[Hospital],
                 lat: float = 40.2, lng: float = -4.2, parent=None):
        super().__init__(parent)
        self.db = db
        self.hospital = hospital or Hospital(nom="", lat=lat, lng=lng)
        self._is_new = (hospital is None)
        self.setWindowTitle("Nou hospital" if self._is_new else f"Hospital: {self.hospital.nom}")
        self.setMinimumWidth(560)
        self.setMinimumHeight(600)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # ── Dades bàsiques de l'hospital ──────────────────────────────────
        grp_hosp = QGroupBox("Dades de l'hospital")
        form = QFormLayout(grp_hosp)

        self._nom = QLineEdit(self.hospital.nom)
        self._nom.setMinimumWidth(380)
        form.addRow("Nom *", self._nom)

        self._status = QComboBox()
        self._status.addItems(["actiu", "inactiu", "potencial"])
        self._status.setCurrentText(self.hospital.status)
        form.addRow("Status", self._status)

        color_row = QHBoxLayout()
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(32, 32)
        self._color = self.hospital.color
        self._update_color_btn()
        self._color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self._color_btn)
        color_row.addWidget(QLabel("Color del pin al mapa"))
        color_row.addStretch()
        form.addRow("Color", color_row)

        self._contacte = QTextEdit(self.hospital.contacte)
        self._contacte.setFixedHeight(60)
        form.addRow("Contacte", self._contacte)

        self._obs = QTextEdit(self.hospital.observacions)
        self._obs.setFixedHeight(60)
        form.addRow("Observacions", self._obs)

        # Coordenades guardades internament, no visibles a la UI
        self._lat_val = self.hospital.lat
        self._lng_val = self.hospital.lng

        layout.addWidget(grp_hosp)

        # ── Doctors ───────────────────────────────────────────────────────
        if not self._is_new:
            layout.addWidget(self._build_doctors_section())
            layout.addWidget(self._build_projectes_section())

        # ── Botons ────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()

        if not self._is_new:
            btn_delete = QPushButton("Eliminar hospital")
            btn_delete.setStyleSheet("color: #ef4444; border: 1px solid #ef4444; border-radius:4px; padding: 6px 12px;")
            btn_delete.clicked.connect(self._delete_hospital)
            btn_row.addWidget(btn_delete)

        btn_row.addStretch()
        btn_cancel = QPushButton("Cancel·lar")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("Guardar")
        btn_save.setDefault(True)
        btn_save.setStyleSheet("background: #2563d4; color: white; border-radius:4px; padding: 6px 16px; font-weight: bold;")
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _build_doctors_section(self) -> QGroupBox:
        grp = QGroupBox("Doctors")
        layout = QVBoxLayout(grp)

        self._doctors_table = QTableWidget(0, 4)
        self._doctors_table.setHorizontalHeaderLabels(["Nom", "Especialitat", "Email", "Telèfon"])
        self._doctors_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._doctors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._doctors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._doctors_table.setMaximumHeight(180)
        self._doctors_table.doubleClicked.connect(self._edit_doctor)
        layout.addWidget(self._doctors_table)

        btns = QHBoxLayout()
        btn_add = QPushButton("+ Afegir doctor")
        btn_add.clicked.connect(self._add_doctor)
        btn_del = QPushButton("Eliminar seleccionat")
        btn_del.clicked.connect(self._delete_doctor)
        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        layout.addLayout(btns)

        self._refresh_doctors()
        return grp

    def _build_projectes_section(self) -> QGroupBox:
        grp = QGroupBox("Projectes")
        layout = QVBoxLayout(grp)

        self._projectes_table = QTableWidget(0, 3)
        self._projectes_table.setHorizontalHeaderLabels(["Nom", "Tema", "Status"])
        self._projectes_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._projectes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._projectes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._projectes_table.setMaximumHeight(150)
        self._projectes_table.doubleClicked.connect(self._edit_projecte)
        layout.addWidget(self._projectes_table)

        btns = QHBoxLayout()
        btn_add = QPushButton("+ Afegir projecte")
        btn_add.clicked.connect(self._add_projecte)
        btn_del = QPushButton("Eliminar seleccionat")
        btn_del.clicked.connect(self._delete_projecte)
        btns.addWidget(btn_add)
        btns.addWidget(btn_del)
        btns.addStretch()
        layout.addLayout(btns)

        self._refresh_projectes()
        return grp

    # ── Color del pin ──────────────────────────────────────────────────────

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._color), self, "Selecciona el color del pin")
        if color.isValid():
            self._color = color.name()
            self._update_color_btn()

    def _update_color_btn(self):
        self._color_btn.setStyleSheet(
            f"background-color: {self._color}; border: 2px solid #94a3b8; border-radius: 4px;"
        )

    # ── Guardar hospital ───────────────────────────────────────────────────

    def _save(self):
        nom = self._nom.text().strip()
        if not nom:
            QMessageBox.warning(self, "Camp obligatori", "El nom de l'hospital és obligatori.")
            return
        self.hospital.nom = nom
        self.hospital.status = self._status.currentText()
        self.hospital.color = self._color
        self.hospital.contacte = self._contacte.toPlainText().strip()
        self.hospital.observacions = self._obs.toPlainText().strip()
        self.hospital.lat = self._lat_val
        self.hospital.lng = self._lng_val

        saved_id = self.db.save_hospital(self.hospital)
        self.hospital.id = saved_id
        self.accept()

    # ── Eliminar hospital ──────────────────────────────────────────────────

    def _delete_hospital(self):
        resp = QMessageBox.question(
            self, "Confirmar eliminació",
            f"Segur que vols eliminar «{self.hospital.nom}»?\n"
            "Això eliminarà també tots els doctors i projectes associats.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.db.delete_hospital(self.hospital.id)
            self.hospital = None
            self.done(2)  # codi 2 = eliminat

    # ── Doctors ────────────────────────────────────────────────────────────

    def _refresh_doctors(self):
        doctors = self.db.get_doctors_for_hospital(self.hospital.id)
        self._doctors_table.setRowCount(len(doctors))
        for row, d in enumerate(doctors):
            self._doctors_table.setItem(row, 0, QTableWidgetItem(d.nom))
            self._doctors_table.setItem(row, 1, QTableWidgetItem(d.especialitat))
            self._doctors_table.setItem(row, 2, QTableWidgetItem(d.email))
            self._doctors_table.setItem(row, 3, QTableWidgetItem(d.telefon))
            for col in range(4):
                item = self._doctors_table.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, d.id)

    def _add_doctor(self):
        dlg = DoctorDialog(self.db, None, self.hospital.id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._refresh_doctors()

    def _edit_doctor(self, index):
        row = index.row()
        doc_id = self._doctors_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        doctor = self.db.get_doctor(doc_id)
        dlg = DoctorDialog(self.db, doctor, self.hospital.id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._refresh_doctors()

    def _delete_doctor(self):
        rows = self._doctors_table.selectedItems()
        if not rows:
            return
        doc_id = rows[0].data(Qt.ItemDataRole.UserRole)
        nom = self._doctors_table.item(self._doctors_table.currentRow(), 0).text()
        resp = QMessageBox.question(
            self, "Confirmar eliminació",
            f"Eliminar el doctor «{nom}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.db.delete_doctor(doc_id)
            self._refresh_doctors()

    # ── Projectes ──────────────────────────────────────────────────────────

    def _refresh_projectes(self):
        projectes = self.db.get_projectes_for_hospital(self.hospital.id)
        self._projectes_table.setRowCount(len(projectes))
        for row, p in enumerate(projectes):
            self._projectes_table.setItem(row, 0, QTableWidgetItem(p.nom))
            self._projectes_table.setItem(row, 1, QTableWidgetItem(p.tema))
            self._projectes_table.setItem(row, 2, QTableWidgetItem(p.status))
            for col in range(3):
                item = self._projectes_table.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, p.id)

    def _add_projecte(self):
        dlg = ProjecteDialog(self.db, None, self.hospital.id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._refresh_projectes()

    def _edit_projecte(self, index):
        row = index.row()
        proj_id = self._projectes_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        projecte = self.db.get_projecte(proj_id)
        dlg = ProjecteDialog(self.db, projecte, self.hospital.id, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._refresh_projectes()

    def _delete_projecte(self):
        rows = self._projectes_table.selectedItems()
        if not rows:
            return
        proj_id = rows[0].data(Qt.ItemDataRole.UserRole)
        nom = self._projectes_table.item(self._projectes_table.currentRow(), 0).text()
        resp = QMessageBox.question(
            self, "Confirmar eliminació",
            f"Eliminar el projecte «{nom}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.db.delete_projecte(proj_id)
            self._refresh_projectes()

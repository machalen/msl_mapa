import sqlite3
from pathlib import Path
from typing import Optional

from models.hospital import Hospital
from models.doctor import Doctor
from models.projecte import Projecte
from utils.paths import resource_path

_SCHEMA = resource_path("database/schema.sql")


class DatabaseManager:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._apply_schema()

    def _apply_schema(self):
        sql = _SCHEMA.read_text(encoding="utf-8")
        self._conn.executescript(sql)
        self._conn.commit()

    def close(self):
        self._conn.close()

    # ── Hospitals ──────────────────────────────────────────────────────────

    def get_all_hospitals(self) -> list[Hospital]:
        rows = self._conn.execute(
            "SELECT * FROM hospitals ORDER BY nom"
        ).fetchall()
        return [self._row_to_hospital(r) for r in rows]

    def get_hospital(self, hospital_id: int) -> Optional[Hospital]:
        row = self._conn.execute(
            "SELECT * FROM hospitals WHERE id = ?", (hospital_id,)
        ).fetchone()
        return self._row_to_hospital(row) if row else None

    def save_hospital(self, h: Hospital) -> int:
        if h.id == 0:
            cur = self._conn.execute(
                """INSERT INTO hospitals (nom, status, color, contacte, observacions, lat, lng)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (h.nom, h.status, h.color, h.contacte, h.observacions, h.lat, h.lng),
            )
            self._conn.commit()
            return cur.lastrowid
        else:
            self._conn.execute(
                """UPDATE hospitals
                   SET nom=?, status=?, color=?, contacte=?, observacions=?, lat=?, lng=?,
                       actualitzat_el=datetime('now')
                   WHERE id=?""",
                (h.nom, h.status, h.color, h.contacte, h.observacions, h.lat, h.lng, h.id),
            )
            self._conn.commit()
            return h.id

    def delete_hospital(self, hospital_id: int):
        self._conn.execute("DELETE FROM hospitals WHERE id = ?", (hospital_id,))
        self._conn.commit()

    def _row_to_hospital(self, row) -> Hospital:
        return Hospital(
            id=row["id"],
            nom=row["nom"],
            status=row["status"],
            color=row["color"],
            contacte=row["contacte"],
            observacions=row["observacions"],
            lat=row["lat"],
            lng=row["lng"],
        )

    # ── Doctors ────────────────────────────────────────────────────────────

    def get_doctors_for_hospital(self, hospital_id: int) -> list[Doctor]:
        rows = self._conn.execute(
            "SELECT * FROM doctors WHERE hospital_id = ? ORDER BY nom",
            (hospital_id,),
        ).fetchall()
        return [self._row_to_doctor(r) for r in rows]

    def get_doctor(self, doctor_id: int) -> Optional[Doctor]:
        row = self._conn.execute(
            "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        return self._row_to_doctor(row) if row else None

    def save_doctor(self, d: Doctor) -> int:
        if d.id == 0:
            cur = self._conn.execute(
                """INSERT INTO doctors
                   (nom, especialitat, email, telefon, institucio, linkedin, observacions, hospital_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (d.nom, d.especialitat, d.email, d.telefon,
                 d.institucio, d.linkedin, d.observacions, d.hospital_id),
            )
            self._conn.commit()
            return cur.lastrowid
        else:
            self._conn.execute(
                """UPDATE doctors
                   SET nom=?, especialitat=?, email=?, telefon=?, institucio=?, linkedin=?,
                       observacions=?, actualitzat_el=datetime('now')
                   WHERE id=?""",
                (d.nom, d.especialitat, d.email, d.telefon,
                 d.institucio, d.linkedin, d.observacions, d.id),
            )
            self._conn.commit()
            return d.id

    def delete_doctor(self, doctor_id: int):
        self._conn.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        self._conn.commit()

    def _row_to_doctor(self, row) -> Doctor:
        return Doctor(
            id=row["id"],
            nom=row["nom"],
            especialitat=row["especialitat"],
            email=row["email"],
            telefon=row["telefon"],
            institucio=row["institucio"],
            linkedin=row["linkedin"],
            observacions=row["observacions"],
            hospital_id=row["hospital_id"],
        )

    # ── Projectes ──────────────────────────────────────────────────────────

    def get_projectes_for_hospital(self, hospital_id: int) -> list[Projecte]:
        rows = self._conn.execute(
            "SELECT * FROM projectes WHERE hospital_id = ? ORDER BY nom",
            (hospital_id,),
        ).fetchall()
        return [self._row_to_projecte(r) for r in rows]

    def get_projecte(self, projecte_id: int) -> Optional[Projecte]:
        row = self._conn.execute(
            "SELECT * FROM projectes WHERE id = ?", (projecte_id,)
        ).fetchone()
        return self._row_to_projecte(row) if row else None

    def save_projecte(self, p: Projecte) -> int:
        if p.id == 0:
            cur = self._conn.execute(
                """INSERT INTO projectes (nom, tema, status, observacions, hospital_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (p.nom, p.tema, p.status, p.observacions, p.hospital_id),
            )
            self._conn.commit()
            return cur.lastrowid
        else:
            self._conn.execute(
                """UPDATE projectes
                   SET nom=?, tema=?, status=?, observacions=?, actualitzat_el=datetime('now')
                   WHERE id=?""",
                (p.nom, p.tema, p.status, p.observacions, p.id),
            )
            self._conn.commit()
            return p.id

    def delete_projecte(self, projecte_id: int):
        self._conn.execute("DELETE FROM projectes WHERE id = ?", (projecte_id,))
        self._conn.commit()

    def _row_to_projecte(self, row) -> Projecte:
        return Projecte(
            id=row["id"],
            nom=row["nom"],
            tema=row["tema"],
            status=row["status"],
            observacions=row["observacions"],
            hospital_id=row["hospital_id"],
        )

    # ── Relacions doctor ↔ projecte ────────────────────────────────────────

    def get_projecte_ids_for_doctor(self, doctor_id: int) -> list[int]:
        rows = self._conn.execute(
            "SELECT projecte_id FROM doctor_projecte WHERE doctor_id = ?", (doctor_id,)
        ).fetchall()
        return [r["projecte_id"] for r in rows]

    def set_doctor_projectes(self, doctor_id: int, projecte_ids: list[int]):
        self._conn.execute(
            "DELETE FROM doctor_projecte WHERE doctor_id = ?", (doctor_id,)
        )
        for pid in projecte_ids:
            self._conn.execute(
                "INSERT OR IGNORE INTO doctor_projecte (doctor_id, projecte_id) VALUES (?, ?)",
                (doctor_id, pid),
            )
        self._conn.commit()

    # ── Cerca creuada (per als tabs de llista) ─────────────────────────────

    def search_hospitals(self, query: str) -> list[dict]:
        q = f"%{query}%"
        rows = self._conn.execute(
            """SELECT DISTINCT h.id, h.nom, h.status, h.color, h.contacte, h.observacions,
                               h.lat, h.lng
               FROM hospitals h
               LEFT JOIN doctors d  ON d.hospital_id = h.id
               LEFT JOIN projectes p ON p.hospital_id = h.id
               WHERE h.nom        LIKE ? OR h.contacte   LIKE ? OR h.observacions LIKE ?
                  OR d.nom        LIKE ? OR d.especialitat LIKE ?
                  OR p.nom        LIKE ? OR p.tema        LIKE ?
               ORDER BY h.nom""",
            (q, q, q, q, q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_doctors(self, query: str) -> list[dict]:
        q = f"%{query}%"
        rows = self._conn.execute(
            """SELECT d.id, d.nom, d.especialitat, d.email, d.telefon,
                      d.institucio, d.linkedin, d.observacions,
                      h.nom AS hospital_nom
               FROM doctors d
               JOIN hospitals h ON h.id = d.hospital_id
               WHERE d.nom LIKE ? OR d.especialitat LIKE ? OR d.email LIKE ?
                  OR d.institucio LIKE ? OR d.observacions LIKE ? OR h.nom LIKE ?
               ORDER BY d.nom""",
            (q, q, q, q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_projectes(self, query: str) -> list[dict]:
        q = f"%{query}%"
        rows = self._conn.execute(
            """SELECT p.id, p.nom, p.tema, p.status, p.observacions,
                      h.nom AS hospital_nom
               FROM projectes p
               JOIN hospitals h ON h.id = p.hospital_id
               WHERE p.nom LIKE ? OR p.tema LIKE ? OR p.observacions LIKE ? OR h.nom LIKE ?
               ORDER BY p.nom""",
            (q, q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Export complet (per a Excel) ───────────────────────────────────────

    def get_all_hospitals_export(self) -> list[dict]:
        return self.search_hospitals("")

    def get_all_doctors_export(self) -> list[dict]:
        return self.search_doctors("")

    def get_all_projectes_export(self) -> list[dict]:
        return self.search_projectes("")

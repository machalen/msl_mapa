"""Migració única des del JSON original de l'HTML a la base de dades SQLite."""

import json
import sys
from pathlib import Path

# Permet executar com a script directe des de msl_mapa/
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import DatabaseManager
from models.hospital import Hospital
from models.doctor import Doctor
from models.projecte import Projecte

# Colors predeterminats de l'HTML original
_COLOR_MAP = {
    "blue": "#3b82f6",
    "green": "#22c55e",
    "red": "#ef4444",
    "purple": "#a855f7",
    "orange": "#f97316",
}


def migrate(json_path: str, db_path: str):
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"ERROR: No es troba el fitxer JSON: {json_path}")
        sys.exit(1)

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    db = DatabaseManager(db_path)

    migrats = 0
    saltats = 0

    for entry in data:
        # Comprovació: si ja existeix un hospital amb el mateix nom i coordenades, salta'l
        existents = db.search_hospitals(entry.get("name", ""))
        ja_existeix = any(
            abs(e["lat"] - entry.get("lat", 0)) < 0.001
            and abs(e["lng"] - entry.get("lng", 0)) < 0.001
            for e in existents
        )
        if ja_existeix:
            print(f"  [saltat] {entry.get('name', '?')} (ja existeix)")
            saltats += 1
            continue

        color_raw = entry.get("pinColor", "blue") or "blue"
        color_hex = _COLOR_MAP.get(color_raw, color_raw if color_raw.startswith("#") else "#3b82f6")

        hosp = Hospital(
            nom=entry.get("name", "Sense nom"),
            lat=entry.get("lat", 40.0),
            lng=entry.get("lng", -4.0),
            status="actiu",
            color=color_hex,
            contacte="",
            observacions="",
        )
        hosp_id = db.save_hospital(hosp)

        # Migrar projectes (crea un mapa id_antic → id_nou)
        proj_id_map: dict[str, int] = {}
        for p in entry.get("projects", []):
            proj = Projecte(
                nom=p.get("name", "Sense nom"),
                hospital_id=hosp_id,
            )
            new_pid = db.save_projecte(proj)
            if "id" in p:
                proj_id_map[p["id"]] = new_pid

        # Migrar doctors
        for d in entry.get("doctors", []):
            doc = Doctor(
                nom=d.get("name", "Sense nom"),
                especialitat=d.get("role", ""),
                email=d.get("email", ""),
                telefon=d.get("phone", ""),
                institucio=d.get("institution", ""),
                linkedin=d.get("linkedin", ""),
                observacions=d.get("comments", ""),
                hospital_id=hosp_id,
            )
            doc_id = db.save_doctor(doc)

            # Vincular doctor amb projectes
            new_proj_ids = [
                proj_id_map[old_pid]
                for old_pid in d.get("projectIds", [])
                if old_pid in proj_id_map
            ]
            if new_proj_ids:
                db.set_doctor_projectes(doc_id, new_proj_ids)

        print(f"  [ok] {hosp.nom} → id={hosp_id} "
              f"({len(entry.get('doctors', []))} doctors, "
              f"{len(entry.get('projects', []))} projectes)")
        migrats += 1

    db.close()
    print(f"\nMigració completada: {migrats} hospitals migrats, {saltats} saltats.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migra dades del JSON original a SQLite")
    parser.add_argument(
        "--json",
        default=str(Path(__file__).parent.parent.parent / "design" / "msl-hospitals-2026-04-20.json"),
        help="Ruta al fitxer JSON d'origen",
    )
    parser.add_argument(
        "--db",
        default=str(Path(__file__).parent.parent / "msl_data.db"),
        help="Ruta a la base de dades SQLite destí",
    )
    args = parser.parse_args()

    print(f"JSON:  {args.json}")
    print(f"DB:    {args.db}\n")
    migrate(args.json, args.db)

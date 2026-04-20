"""Resolució de paths compatible amb execució des de font i des de bundle PyInstaller."""

import os
import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """Retorna el path correcte per a fitxers bundlejats (assets, schema.sql).
    - Quan corre des de font: relatiu a la carpeta arrel del projecte (msl_mapa/)
    - Quan corre com a bundle PyInstaller: des de sys._MEIPASS
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative
    return Path(__file__).parent.parent / relative


def db_path() -> Path:
    """Retorna el path de la base de dades.
    - Des de font: msl_mapa/msl_data.db (al costat del codi)
    - Bundle Windows: %APPDATA%/MSLMapa/msl_data.db
    - Bundle macOS/Linux: ~/.msl_mapa/msl_data.db
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            data_dir = Path(os.environ.get("APPDATA", Path.home())) / "MSLMapa"
        else:
            data_dir = Path.home() / ".msl_mapa"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "msl_data.db"
    return Path(__file__).parent.parent / "msl_data.db"

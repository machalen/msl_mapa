from dataclasses import dataclass, field


@dataclass
class Hospital:
    nom: str
    lat: float
    lng: float
    status: str = "actiu"
    color: str = "#2563d4"
    contacte: str = ""
    observacions: str = ""
    ciutat: str = ""
    comunitat: str = ""
    id: int = 0  # 0 = nou (no guardat)

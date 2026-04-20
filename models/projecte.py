from dataclasses import dataclass


@dataclass
class Projecte:
    nom: str
    hospital_id: int
    tema: str = ""
    status: str = "actiu"
    observacions: str = ""
    id: int = 0

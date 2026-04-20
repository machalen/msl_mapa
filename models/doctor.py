from dataclasses import dataclass


@dataclass
class Doctor:
    nom: str
    hospital_id: int
    especialitat: str = ""
    email: str = ""
    telefon: str = ""
    institucio: str = ""
    linkedin: str = ""
    observacions: str = ""
    id: int = 0

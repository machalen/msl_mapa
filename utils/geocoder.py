"""Cerca d'adreces via Nominatim (OpenStreetMap). Sense autenticació."""

import requests

_URL = "https://nominatim.openstreetmap.org/search"
_HEADERS = {"User-Agent": "MSLMapa/1.0 (msl@goriandco.com)"}


def search(query: str, limit: int = 5) -> list[dict]:
    """Retorna una llista de {display_name, lat, lng}. Pot llançar requests.RequestException."""
    resp = requests.get(
        _URL,
        params={"q": query, "format": "json", "limit": limit, "countrycodes": "es,pt"},
        headers=_HEADERS,
        timeout=8,
    )
    resp.raise_for_status()
    results = []
    for item in resp.json():
        results.append({
            "display_name": item["display_name"],
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
        })
    return results

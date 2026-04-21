"""Cerca d'adreces via Nominatim (OpenStreetMap). Sense autenticació."""

import requests

_URL = "https://nominatim.openstreetmap.org/search"
_HEADERS = {"User-Agent": "MSLMapa/1.0 (github.com/machalen/msl_mapa)"}


def search(query: str, limit: int = 5) -> list[dict]:
    """Retorna una llista de {display_name, lat, lng, ciutat, comunitat}. Pot llançar requests.RequestException."""
    resp = requests.get(
        _URL,
        params={"q": query, "format": "json", "limit": limit,
                "countrycodes": "es,pt", "addressdetails": 1},
        headers=_HEADERS,
        timeout=8,
    )
    resp.raise_for_status()
    results = []
    for item in resp.json():
        addr = item.get("address", {})
        ciutat = (addr.get("city") or addr.get("town") or
                  addr.get("village") or addr.get("municipality") or "")
        comunitat = addr.get("state") or ""
        results.append({
            "display_name": item["display_name"],
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
            "ciutat": ciutat,
            "comunitat": comunitat,
        })
    return results

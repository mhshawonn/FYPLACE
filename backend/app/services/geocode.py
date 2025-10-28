"""
Geocoding helpers backed by OpenStreetMap's Nominatim service.
"""

from __future__ import annotations

from typing import Optional, Tuple

import requests

from app.core.config import get_settings


class GeocodingError(RuntimeError):
    """Raised when the geocoder cannot find a location."""


def geocode_location(query: str) -> Tuple[float, float, str]:
    """
    Resolve a human-friendly location into coordinates.
    """
    settings = get_settings()
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": settings.user_agent}
    resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=settings.http_timeout)
    resp.raise_for_status()
    payload = resp.json()
    if not payload:
        raise GeocodingError(f"Could not geocode location: {query}")
    item = payload[0]
    lat = float(item["lat"])
    lon = float(item["lon"])
    display_name: Optional[str] = item.get("display_name")
    return lat, lon, display_name or query

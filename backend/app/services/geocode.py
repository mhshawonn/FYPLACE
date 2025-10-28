"""
Geocoding helpers backed by OpenStreetMap's Nominatim service.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import requests

from app.core.config import get_settings


class GeocodingError(RuntimeError):
    """Raised when the geocoder cannot find a location."""


_GEOCODE_CACHE: Dict[str, Tuple[float, float, str]] = {}


def geocode_location(query: str) -> Tuple[float, float, str]:
    """
    Resolve a human-friendly location into coordinates.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        raise GeocodingError("Location cannot be empty.")

    cache_key = cleaned_query.lower()
    cached = _GEOCODE_CACHE.get(cache_key)
    if cached:
        return cached

    settings = get_settings()
    params = {"q": cleaned_query, "format": "json", "limit": 1}
    headers = {"User-Agent": settings.user_agent}
    resp = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=settings.http_timeout)
    resp.raise_for_status()
    payload = resp.json()
    if not payload:
        raise GeocodingError(f"Could not geocode location: {cleaned_query}")
    item = payload[0]
    lat = float(item["lat"])
    lon = float(item["lon"])
    display_name: Optional[str] = item.get("display_name")
    result = (lat, lon, display_name or cleaned_query)
    _GEOCODE_CACHE[cache_key] = result
    return result

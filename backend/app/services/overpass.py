"""
Utilities for querying the Overpass API and normalising results.
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests

from app.core.config import DEFAULT_CATEGORIES, get_settings

EMAIL_REGEX = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)
_MOCK_CACHE: Optional[List[Dict]] = None


class OverpassError(RuntimeError):
    """Raised when the Overpass API cannot satisfy a request."""


def _value_regex(values: Iterable[str]) -> str:
    return "^(" + "|".join([re.escape(v) for v in values]) + ")$"


def build_area_query(lat: float, lon: float, radius_m: int, tag_key: str, tag_values: List[str]) -> str:
    """
    Build an Overpass QL query scoped to a circular area.
    """
    value_regex = _value_regex(tag_values)
    return f"""
    [out:json][timeout:900][maxsize:2000000000];

    (
      node["{tag_key}"~"{value_regex}"](around:{radius_m},{lat},{lon});
      way ["{tag_key}"~"{value_regex}"](around:{radius_m},{lat},{lon});
      relation ["{tag_key}"~"{value_regex}"](around:{radius_m},{lat},{lon});
    );

    out tags center qt;
    """


def build_california_query(tag_key: str, tag_values: List[str]) -> str:
    """
    Build an Overpass QL query covering the California administrative boundary.
    """
    value_regex = _value_regex(tag_values)
    return f"""
    [out:json][timeout:900][maxsize:2000000000];

    rel["name"="California"]["boundary"="administrative"]["admin_level"="4"]->.ca;
    area.ca->.searchArea;

    (
      node["{tag_key}"~"{value_regex}"](area.searchArea);
      way ["{tag_key}"~"{value_regex}"](area.searchArea);
      relation ["{tag_key}"~"{value_regex}"](area.searchArea);
    );

    out tags center qt;
    """


def call_overpass(query: str) -> Dict:
    """
    Attempt the query across the configured mirrors until one responds.
    """
    settings = get_settings()
    last_err: Optional[Exception] = None
    for url in settings.overpass_urls:
        for attempt in range(1, settings.overpass_retry_attempts + 1):
            try:
                resp = requests.post(url, data={"data": query}, timeout=settings.http_timeout)
                if resp.status_code == 429:
                    time.sleep(5)
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                backoff = min(5, attempt * 2)
                time.sleep(backoff)
    raise OverpassError(f"Overpass failed on all mirrors: {last_err}")


def normalize_record(el: Dict, category: str) -> Dict:
    """
    Convert Overpass elements into a consistent response dictionary.
    """
    tags = el.get("tags", {}) or {}

    phone = tags.get("contact:phone") or tags.get("phone")
    email = tags.get("contact:email") or tags.get("email")
    website = tags.get("contact:website") or tags.get("website") or tags.get("url")

    if "lat" in el and "lon" in el:
        lat, lon = el["lat"], el["lon"]
    else:
        center = el.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")

    try:
        lat = float(lat) if lat is not None else None
        lon = float(lon) if lon is not None else None
    except (TypeError, ValueError):
        lat, lon = None, None

    addr = ", ".join(
        [
            tags.get(k)
            for k in ["addr:housenumber", "addr:street", "addr:city", "addr:postcode", "addr:state"]
            if tags.get(k)
        ]
    ).strip(", ")

    name = tags.get("name")

    return {
        "osm_id": f"{el.get('type','')}/{el.get('id','')}",
        "category": category,
        "name": name,
        "phone": phone,
        "email": email,
        "website": website,
        "address": addr,
        "lat": lat,
        "lon": lon,
        "source_tags": json.dumps(tags, ensure_ascii=False),
    }


def try_discover_email_from_site(url: str) -> Optional[str]:
    """
    Fetch the homepage and well-known contact paths looking for an email address.
    """
    settings = get_settings()
    if not url or not isinstance(url, str):
        return None
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        from urllib.parse import urljoin
    except ImportError:  # pragma: no cover
        urljoin = None

    candidates = [url]
    if urljoin:
        candidates.append(urljoin(url, "/contact"))
        candidates.append(urljoin(url, "/contact-us"))

    headers = {"User-Agent": settings.user_agent}

    for candidate in candidates:
        try:
            resp = requests.get(candidate, headers=headers, timeout=settings.http_timeout)
            if resp.status_code >= 400:
                continue
            match = EMAIL_REGEX.search(resp.text or "")
            if match:
                found = match.group(0)
                if not any(bad in found.lower() for bad in ["example.com", "email@", "your@", "info@example"]):
                    return found
        except Exception:  # noqa: BLE001
            pass
        time.sleep(settings.crawl_sleep_seconds)
    return None


def dedupe(records: List[Dict]) -> List[Dict]:
    """
    Deduplicate records by (name, rounded lat/lon).
    """
    seen = set()
    out: List[Dict] = []
    for rec in records:
        key = (
            rec.get("name"),
            round(float(rec.get("lat") or 0), 6),
            round(float(rec.get("lon") or 0), 6),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two coordinates in metres.
    """
    radius_m = 6371000  # Mean Earth radius in metres.
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)

    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius_m * c


def fetch_places(
    lat: float,
    lon: float,
    radius_m: int,
    categories: Optional[List[str]] = None,
    enable_email_discovery: bool = False,
) -> List[Dict]:
    """
    Fetch normalised places around a coordinate for the selected categories.
    """
    settings = get_settings()
    categories = [category for category in (categories or list(DEFAULT_CATEGORIES.keys())) if DEFAULT_CATEGORIES.get(category)]
    if not categories:
        return []

    def _fetch_category(category: str) -> List[Dict]:
        spec = DEFAULT_CATEGORIES[category]
        query = build_area_query(lat, lon, radius_m, spec["key"], spec["values"])
        data = call_overpass(query)
        elements = data.get("elements", [])
        category_records: List[Dict] = []
        for element in elements:
            rec = normalize_record(element, category)
            if rec["name"] and rec["lat"] is not None and rec["lon"] is not None:
                category_records.append(rec)
        return category_records

    records: List[Dict] = []
    first_error: Optional[Exception] = None

    max_workers = min(settings.max_parallel_category_requests, len(categories))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_fetch_category, category): category for category in categories}
        for future in as_completed(futures):
            if first_error is not None:
                future.cancel()
                continue
            try:
                records.extend(future.result())
            except Exception as exc:  # noqa: BLE001
                first_error = exc

    if first_error is not None:
        if isinstance(first_error, OverpassError):
            raise first_error
        raise OverpassError(f"Failed to fetch places: {first_error}") from first_error

    tolerance = settings.distance_tolerance_factor
    filtered_records = [
        rec
        for rec in records
        if rec.get("lat") is not None
        and rec.get("lon") is not None
        and _haversine_distance_m(lat, lon, float(rec["lat"]), float(rec["lon"])) <= radius_m * tolerance
    ]

    records = dedupe(filtered_records)

    if enable_email_discovery and settings.enable_website_email_discovery:
        to_enrich = [record for record in records if not record.get("email") and record.get("website")]
        for idx, record in enumerate(to_enrich, start=1):
            email = try_discover_email_from_site(record["website"])
            if email:
                record["email"] = email
            if idx % 25 == 0:
                time.sleep(settings.crawl_sleep_seconds)

    return records


def load_mock_places() -> List[Dict]:
    """
    Load static places from disk for development/demo fallbacks.
    """
    global _MOCK_CACHE
    if _MOCK_CACHE is not None:
        return _MOCK_CACHE

    settings = get_settings()
    path = settings.mock_places_path
    if not path:
        _MOCK_CACHE = []
        return _MOCK_CACHE

    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path(__file__).resolve().parent.parent / path

    if not candidate.exists():
        _MOCK_CACHE = []
        return _MOCK_CACHE

    try:
        with candidate.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                _MOCK_CACHE = data
            else:
                _MOCK_CACHE = []
    except Exception:  # noqa: BLE001
        _MOCK_CACHE = []
    return _MOCK_CACHE


def get_mock_places(categories: Optional[List[str]] = None) -> List[Dict]:
    """
    Return mock places filtered by category if provided.
    """
    data = load_mock_places()
    if not data:
        return []
    if not categories:
        return data
    return [record for record in data if record.get("category") in categories]


def fetch_california_places(enable_email_discovery: bool = False) -> List[Dict]:
    """
    Fetch places for each default category across the state of California.
    """
    settings = get_settings()
    records: List[Dict] = []

    for category, spec in DEFAULT_CATEGORIES.items():
        query = build_california_query(spec["key"], spec["values"])
        data = call_overpass(query)
        elements = data.get("elements", [])
        for element in elements:
            rec = normalize_record(element, category)
            records.append(rec)

    records = [rec for rec in records if rec.get("name") and rec.get("lat") and rec.get("lon")]
    records = dedupe(records)

    if enable_email_discovery and settings.enable_website_email_discovery:
        to_enrich = [record for record in records if not record.get("email") and record.get("website")]
        for idx, record in enumerate(to_enrich, start=1):
            email = try_discover_email_from_site(record["website"])
            if email:
                record["email"] = email
            if idx % 25 == 0:
                time.sleep(settings.crawl_sleep_seconds)

    return records

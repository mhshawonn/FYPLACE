"""
API routes wiring the FastAPI application.
"""

from __future__ import annotations

import copy
import csv
import io
from collections import OrderedDict
from threading import Lock
from time import time
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.core.config import DEFAULT_CATEGORIES, get_settings
from app.schemas.search import Place, SearchRequest, SearchResponse
from app.services.geocode import GeocodingError, geocode_location
from app.services.overpass import OverpassError, fetch_california_places, fetch_places, get_mock_places

router = APIRouter(prefix="/api")

CacheKey = Tuple[float, float, int, Tuple[str, ...], bool]
CacheEntry = Dict[str, object]

_SEARCH_CACHE: "OrderedDict[CacheKey, CacheEntry]" = OrderedDict()
_SEARCH_CACHE_LOCK = Lock()


def _make_cache_key(lat: float, lon: float, radius_m: int, categories: List[str], with_email: bool) -> CacheKey:
    """
    Normalise search parameters into a hashable cache key.
    """
    normalized_categories = tuple(sorted(categories))
    return (round(lat, 5), round(lon, 5), radius_m, normalized_categories, with_email)


def _get_cached_response(key: CacheKey) -> Optional[Dict[str, object]]:
    """
    Return a cached result if it exists and has not expired.
    """
    now = time()
    with _SEARCH_CACHE_LOCK:
        entry = _SEARCH_CACHE.get(key)
        if not entry:
            return None
        expires_at = entry.get("expires_at")
        if isinstance(expires_at, (int, float)) and expires_at < now:
            del _SEARCH_CACHE[key]
            return None
        _SEARCH_CACHE.move_to_end(key)
        return {
            "label": entry["label"],
            "results": copy.deepcopy(entry["results"]),
        }


def _store_cached_response(
    key: CacheKey,
    label: str,
    results: List[Dict],
    ttl_seconds: int,
    max_entries: int,
) -> None:
    """
    Store a search response in the LRU cache subject to TTL and size limits.
    """
    if ttl_seconds <= 0:
        return

    expires_at = time() + ttl_seconds
    payload: CacheEntry = {
        "label": label,
        "results": copy.deepcopy(results),
        "expires_at": expires_at,
    }

    with _SEARCH_CACHE_LOCK:
        _SEARCH_CACHE[key] = payload
        _SEARCH_CACHE.move_to_end(key)
        while len(_SEARCH_CACHE) > max_entries:
            _SEARCH_CACHE.popitem(last=False)


def _perform_search(request: SearchRequest) -> SearchResponse:
    """
    Core search logic shared by search and export endpoints.
    """
    settings = get_settings()

    try:
        lat, lon, label = geocode_location(request.location)
    except GeocodingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    radius_m = int(request.radius_km * 1000)
    categories: List[str] = request.categories or list(DEFAULT_CATEGORIES.keys())
    cache_key = _make_cache_key(lat, lon, radius_m, categories, request.with_email_enrichment)

    cached = _get_cached_response(cache_key)
    if cached:
        cached_label = cached.get("label")
        if isinstance(cached_label, str):
            label = cached_label
        results = cached["results"]  # type: ignore[assignment]
    else:
        try:
            results = fetch_places(
                lat=lat,
                lon=lon,
                radius_m=radius_m,
                categories=categories,
                enable_email_discovery=request.with_email_enrichment,
            )
        except OverpassError as exc:
            results = get_mock_places(categories)
            if not results:
                raise HTTPException(
                    status_code=503,
                    detail="Overpass API is currently unavailable. Please retry shortly.",
                ) from exc
        _store_cached_response(
            cache_key,
            label,
            results,
            settings.search_cache_ttl_seconds,
            settings.search_cache_max_entries,
        )

    place_models = [Place(**place) for place in results]

    return SearchResponse(
        location_label=label,
        radius_km=request.radius_km,
        categories=categories,
        results=place_models,
    )


@router.get("/health")
def healthcheck() -> dict:
    """
    Lightweight readiness check.
    """
    return {"status": "ok"}


@router.post("/search", response_model=SearchResponse)
def search_places(request: SearchRequest) -> SearchResponse:
    """
    Geocode the provided location query and return nearby places.
    """
    return _perform_search(request)


@router.post("/export")
def export_places(request: SearchRequest) -> Response:
    """
    Return CSV for the same input parameters as `/search`.
    """
    try:
        response = _perform_search(request)
    except HTTPException as exc:
        if exc.status_code == 503:
            raise
        raise exc

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "category",
            "name",
            "phone",
            "email",
            "website",
            "address",
            "lat",
            "lon",
            "osm_id",
            "source_tags",
        ],
    )
    writer.writeheader()
    for place in response.results:
        writer.writerow(place.model_dump())

    filename = f"findyourplace_{response.location_label.replace(' ', '_')}.csv"

    csv_bytes = buffer.getvalue().encode("utf-8")

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/california/export")
def export_california_places(with_email_enrichment: bool = False) -> Response:
    """
    Generate a statewide CSV export for California using the standalone batch logic.
    """
    try:
        records = fetch_california_places(enable_email_discovery=with_email_enrichment)
    except OverpassError as exc:
        records = get_mock_places()
        if not records:
            raise HTTPException(status_code=503, detail="Overpass API is currently unavailable. Please retry shortly.") from exc

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "category",
            "name",
            "phone",
            "email",
            "website",
            "address",
            "lat",
            "lon",
            "osm_id",
            "source_tags",
        ],
    )
    writer.writeheader()
    for record in records:
        writer.writerow(record)

    csv_bytes = buffer.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="findyourplace_california.csv"'},
    )

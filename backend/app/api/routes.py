"""
API routes wiring the FastAPI application.
"""

from __future__ import annotations

import csv
import io
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import DEFAULT_CATEGORIES
from app.schemas.search import Place, SearchRequest, SearchResponse
from app.services.geocode import GeocodingError, geocode_location
from app.services.overpass import OverpassError, fetch_california_places, fetch_places, get_mock_places

router = APIRouter(prefix="/api")


def _perform_search(request: SearchRequest) -> SearchResponse:
    """
    Core search logic shared by search and export endpoints.
    """
    try:
        lat, lon, label = geocode_location(request.location)
    except GeocodingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    radius_m = int(request.radius_km * 1000)
    categories: List[str] = request.categories or list(DEFAULT_CATEGORIES.keys())

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
            raise HTTPException(status_code=503, detail="Overpass API is currently unavailable. Please retry shortly.") from exc

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
def export_places(request: SearchRequest) -> StreamingResponse:
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

    buffer.seek(0)
    filename = f"findyourplace_{response.location_label.replace(' ', '_')}.csv"

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/california/export")
def export_california_places(with_email_enrichment: bool = False) -> StreamingResponse:
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

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="findyourplace_california.csv"'},
    )

#!/usr/bin/env python3
"""
Fetch schools, colleges, hospitals, and hotels across California from OpenStreetMap (Overpass),
and export to CSV with name, phone, email, website, address, and coordinates.

Optional: try to discover an email from each website (simple, rate-limited crawl).
"""

import csv
import json
import re
import sys
import time
from typing import Dict, List, Tuple, Iterable, Optional

import requests

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

# Categories to fetch (OSM tags)
CATEGORIES = {
    "school":     {"key": "amenity", "values": ["school"]},
    "college":    {"key": "amenity", "values": ["college", "university"]},
    "hospital":   {"key": "amenity", "values": ["hospital", "clinic"]},
    "hotel":      {"key": "tourism", "values": ["hotel", "motel", "hostel", "guest_house"]},
}

# Toggle this ON to attempt email discovery from websites found in OSM tags.
ENABLE_WEBSITE_EMAIL_DISCOVERY = True
HTTP_TIMEOUT = 15
CRAWL_SLEEP_SEC = 1.0   # be gentle


def overpass_query_for_california(tag_key: str, tag_values: List[str]) -> str:
    """
    Build an Overpass QL query scoped to the California administrative boundary.
    We fetch nodes/ways/relations and ask for tags + center coordinates.
    """
    value_regex = "^(" + "|".join([re.escape(v) for v in tag_values]) + ")$"
    q = f"""
    [out:json][timeout:900][maxsize:2000000000];

    // California relation as area
    rel["name"="California"]["boundary"="administrative"]["admin_level"="4"]->.ca;
    area.ca->.searchArea;

    (
      node["{tag_key}"~"{value_regex}"](area.searchArea);
      way ["{tag_key}"~"{value_regex}"](area.searchArea);
      relation ["{tag_key}"~"{value_regex}"](area.searchArea);
    );

    out tags center qt;
    """
    return q


def call_overpass(query: str) -> Dict:
    last_err = None
    for url in OVERPASS_URLS:
        try:
            resp = requests.post(url, data={"data": query}, timeout=HTTP_TIMEOUT)
            if resp.status_code == 429:
                # too many requests – back off and retry a different mirror
                time.sleep(5)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_err = e
            time.sleep(2)
            continue
    raise RuntimeError(f"Overpass failed on all mirrors: {last_err}")


def normalize_record(el: Dict, category: str) -> Dict:
    tags = el.get("tags", {}) or {}

    # Prefer explicit contact:* tags; fall back to generic keys
    phone = tags.get("contact:phone") or tags.get("phone")
    email = tags.get("contact:email") or tags.get("email")
    website = tags.get("contact:website") or tags.get("website") or tags.get("url")

    # Coordinates: nodes have 'lat','lon'; ways/relations use 'center'
    if "lat" in el and "lon" in el:
        lat, lon = el["lat"], el["lon"]
    else:
        center = el.get("center") or {}
        lat, lon = center.get("lat"), center.get("lon")

    # Address fields if present
    addr = ", ".join(
        [tags.get(k) for k in ["addr:housenumber", "addr:street", "addr:city", "addr:postcode", "addr:state"] if tags.get(k)]
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


EMAIL_REGEX = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)

def try_discover_email_from_site(url: str) -> Optional[str]:
    """
    Best-effort: fetch the homepage (and /contact) and regex an email.
    Observes a small delay to respect servers. Skips non-HTTP(S).
    """
    if not url or not isinstance(url, str):
        return None
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    candidates = [url]
    # also look at a conventional contact page
    try:
        from urllib.parse import urljoin
        candidates.append(urljoin(url, "/contact"))
        candidates.append(urljoin(url, "/contact-us"))
    except Exception:
        pass

    headers = {"User-Agent": "CA-Institutions-Fetcher/1.0 (+research use)"}

    for u in candidates:
        try:
            resp = requests.get(u, headers=headers, timeout=HTTP_TIMEOUT)
            if resp.status_code >= 400:
                continue
            m = EMAIL_REGEX.search(resp.text or "")
            if m:
                # avoid obviously generic placeholders
                found = m.group(0)
                if not any(bad in found.lower() for bad in ["example.com", "email@", "your@", "info@example"]):
                    return found
        except Exception:
            pass
        time.sleep(CRAWL_SLEEP_SEC)
    return None


def dedupe(records: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for r in records:
        key = (r["name"], round(float(r["lat"] or 0), 6), round(float(r["lon"] or 0), 6))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def main():
    out_path = "california_small_institutions.csv"
    all_records: List[Dict] = []

    for label, spec in CATEGORIES.items():
        print(f"Fetching {label} ...", file=sys.stderr)
        q = overpass_query_for_california(spec["key"], spec["values"])
        data = call_overpass(q)
        elements = data.get("elements", [])
        print(f"  -> {len(elements)} features", file=sys.stderr)
        for el in elements:
            rec = normalize_record(el, label)
            all_records.append(rec)

    # Dedupe by (name, coords)
    all_records = [r for r in all_records if r["name"] and r["lat"] and r["lon"]]
    all_records = dedupe(all_records)

    # Optional: try to find missing emails from websites
    if ENABLE_WEBSITE_EMAIL_DISCOVERY:
        to_fill = [r for r in all_records if not r.get("email") and r.get("website")]
        print(f"Attempting email discovery from websites for {len(to_fill)} places ...", file=sys.stderr)
        for i, r in enumerate(to_fill, 1):
            email = try_discover_email_from_site(r["website"])
            if email:
                r["email"] = email
            if i % 25 == 0:
                print(f"  visited {i}/{len(to_fill)}", file=sys.stderr)

    # Write CSV
    fieldnames = ["category", "name", "phone", "email", "website", "address", "lat", "lon", "osm_id", "source_tags"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_records:
            w.writerow(r)

    print(f"\nSaved {len(all_records)} rows to {out_path}")


if __name__ == "__main__":
    main()

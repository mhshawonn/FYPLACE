# FindYourPlace

FindYourPlace is a geo discovery experience inspired by modern social feeds. It pairs a FastAPI backend with a React + Vite frontend so users can search any location, filter institutions (schools, colleges, hospitals, hotels), browse them in an immersive UI, and export results to CSV for downstream workflows.

## Features
- Sleek Instagram-style interface with glassmorphism touches and responsive layout.
- Search by any city, neighbourhood, or address using OpenStreetMap's Nominatim geocoder.
- Filter by institution type and radius, with optional email enrichment pulled from official websites.
- Export curated results to CSV directly from the browser.
- Modular Python service layer that wraps Overpass API querying and data normalisation.

## Tech Stack
- **Backend:** FastAPI, Pydantic, Requests, Uvicorn
- **Frontend:** React 18, Vite 5, React Icons
- **Data Providers:** OpenStreetMap Overpass API, Nominatim geocoding

## Project Structure
```
backend/
  app/
    api/            # FastAPI routes
    core/           # Configuration helpers
    schemas/        # Pydantic models
    services/       # Overpass + geocoding logic
    main.py         # Application entrypoint
  requirements.txt  # Backend dependencies
frontend/
  src/
    components/     # UI building blocks
    styles/         # Global + page styling
    App.jsx         # Root React component
    main.jsx        # Application bootstrap
  index.html        # Vite entrypoint
  package.json      # Frontend dependencies and scripts
main.py             # Original data export script (retained for reference)
README.md
```

## Getting Started

### 1. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API listens on `http://localhost:8000`. Adjustable environment variables (prefixed with `FYP_`):

| Variable | Default | Description |
| --- | --- | --- |
| `FYP_ENABLE_WEBSITE_EMAIL_DISCOVERY` | `False` | Set to `True` to crawl websites for missing emails (respectful, but slower). |
| `FYP_USER_AGENT` | `FindYourPlace/1.0 (+https://example.com)` | User agent used for HTTP requests. |
| `FYP_HTTP_TIMEOUT` | `15` | Timeout (seconds) for external HTTP calls. |
| `FYP_OVERPASS_RETRY_ATTEMPTS` | `3` | Attempts per Overpass mirror before moving to the next. |

### 2. Frontend
```bash
cd frontend
cp .env.example .env  # Edit VITE_API_URL if backend runs elsewhere
npm install
npm run dev
```

The UI is available at `http://localhost:5173` and proxies API calls to the configured `VITE_API_URL` (defaults to `http://localhost:8000/api`).

### 3. Using the App
1. Enter any location (e.g., *San Diego, CA*) and adjust the radius slider.
2. Toggle categories to curate the types of places shown.
3. Enable email enrichment if you need additional contact details.
4. Click **Explore** to populate the feed, then **Download CSV** for offline analysis.

## CSV Output
Exports include category, name, phone, email, website, address, latitude, longitude, OSM identifier, and the raw source tags for traceability.

## Testing & Future Enhancements
- Add automated tests using `pytest` on the service layer and component tests via Vitest/React Testing Library.
- Cache geocoding responses and Overpass queries to reduce external load.
- Add user authentication and saved searches for persistent dashboards.

---
Crafted with ❤️ as a foundation you can extend into a production-grade local discovery experience.
# FYPLACE

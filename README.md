# Lumo – Walk the (b)right Way

Lumo is an interactive web-based map application that supports nighttime pedestrian navigation in the city of Zürich. While conventional navigation tools primarily optimize routes based on distance and travel time, Lumo focuses on perceptual aspects of urban space that become particularly relevant after dark, such as street lighting and visible social activity.

The application visualizes open data on public street lighting and nighttime-related points of interest to highlight areas that feel brighter and more vibrant at night. Based on this information, Lumo offers comfort-oriented walking route suggestions that prioritize well-lit and socially active streets over purely shortest paths. Rather than making claims about safety, the application aims to increase transparency and support informed, comfort-based route choices.

The project lies at the intersection of cartography, urban perception, and user experience design, and demonstrates how digital maps can support more human-centered navigation experiences in nighttime urban environments.

---

## Tech Stack

| Layer | Library / Tool |
|---|---|
| UI framework | Vue 3 |
| Primary map engine | Mapbox GL JS |
| 3D globe viewer | Cesium |
| Build tool | Vite |
| Linting & formatting | ESLint, Prettier |

---

## Setup

**Prerequisites:** Node.js and npm installed.

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the project root and add your Mapbox access token:
   ```
   VITE_MAPBOX_TOKEN=your_mapbox_token_here
   ```

3. Start the development server (opens at `http://localhost:3000`):
   ```bash
   npm run dev
   ```

**Other scripts:**

| Command | Description |
|---|---|
| `npm run build` | Compile and bundle for production |
| `npm run preview` | Preview the production build at `http://localhost:3010` |
| `npm run lint` | Run ESLint across all source files |
| `npm run prettier` | Auto-format all files with Prettier |

---

## Code Structure

### Root

| File | Description |
|---|---|
| `index.html` | HTML entry point; mounts the Vue app to `#app` |
| `vite.config.js` | Vite configuration: Vue plugin, Cesium static asset copy, dev/preview ports, production base path |
| `.env` | Local environment variables; defines `VITE_MAPBOX_TOKEN` (not committed) |
| `.gitlab-ci.yml` | Two-stage GitLab CI/CD pipeline: build then deploy to `ikgcartoapps.ethz.ch` |

### `src/`

| File | Description |
|---|---|
| `main.js` | Creates the Vue application instance and mounts it to the DOM |
| `App.vue` | Root component; owns global UI state including the sidebar tabs (routing, layers, legend, info), route selection, animated popups, and the "Return to Zürich" overlay |
| `cesium.js` | Configures a Cesium `WebMapTileServiceImageryProvider` for the Swiss swisstopo basemap |
| `style.css` | Global stylesheet: dark theme, typography, button styles, and loading-screen state classes |

### `src/components/`

| File | Description |
|---|---|
| `MapboxViewer.vue` | Primary map component; renders all Mapbox GL layers (lighting, vibrancy, combined hexagons, routes, hubs, hotspots), handles user interactions, and drives route animations and security-alert overlays |
| `CesiumViewer.vue` | Alternative 3D globe viewer using Cesium; displays routing hubs and hexagon data with custom point styling and labels |
| `Legend.vue` | Interactive legend panel for the active layer mode (lighting, vibrancy, combined, security alerts); includes colour gradients, statistics, and a clickable hotspot-explorer card list |
| `GuidedTour.vue` | Multi-step onboarding dialog with navigation buttons, orbit/pulse animations, and a conclusion slide |
| `Walkthrough.vue` | Toast notification that displays the welcome message on first load, with a pulse background animation |
| `MapboxTest.vue` | Minimal Mapbox GL test component used during development (not part of the main application flow) |

### `public/data/`

| Path | Description |
|---|---|
| `routes/` | GeoJSON geometries and QGIS metadata files for all 45 hub-to-hub route combinations |
| `routes_wgs84/` | Route geometries reprojected to WGS 84 |
| `route_intersections/` | JSON files mapping each route to intersecting hexagon cells |
| `route_lumo_scores/` | Pre-computed Lumo comfort scores (lighting + vibrancy) per route |
| `route_comparisons/` | Metrics comparing alternative routes between the same origin/destination pair |
| `route_taxi_recommendations/` | Taxi-fallback recommendations keyed by route |
| `route_security_alerts/` | Security-incident data associated with each route |
| `hotspots_wgs84/` | GeoJSON and metadata for named nightlife hotspot areas |
| `hubs/` | GeoJSON for the routing hub locations across the city |
| `scripts/` | Python data-processing scripts (e.g. `calculate_route_lumo_scores.py`, `calculate_route_hexagon_intersections.py`) |
| `lighting_locations.geojson` | Point dataset of public street-lighting fixtures |
| `vibrancy_points.geojson` | Point dataset of nighttime vibrancy POIs |
| `hex_vibrancy_100m.geojson` | 100 m hexagon grid with aggregated vibrancy values |
| `hexagon_median.json` | Precomputed median statistics per hexagon cell |
| `combined_locations.json` | Merged index of lighting and vibrancy locations used by the search UI |

### `public/SVG/`

SVG icons used throughout the interface (routing, sidebar, layer toggles, the Lumo logo) and JPG neighbourhood photographs for the nine hotspot areas (Altstetten, Bahnhof, Bellevue, Central, Enge, Hardbrücke, Langstrasse, Niederdorf, Oerlikon).

---

## AI-Assisted Development

Cursor AI was used as a coding assistant during development to generate and refine code suggestions. All AI-generated suggestions were reviewed, adapted, and integrated by the author. The overall application architecture, data processing workflow, and core functionality were designed and implemented by the author.

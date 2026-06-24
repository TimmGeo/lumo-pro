# Lumo – Walk the (b)right Way

> Nighttime pedestrian routing for Zürich, weighted by street lighting and urban activity. Built with Vue 3 and Mapbox GL JS.

![Vue 3](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![Mapbox GL JS](https://img.shields.io/badge/Mapbox%20GL%20JS-000000?logo=mapbox&logoColor=white)
![Python](https://img.shields.io/badge/Python-preprocessing-3776AB?logo=python&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-data%20prep-589632?logo=qgis&logoColor=white)

> [!NOTE]
> Lumo is live at https://ikgcartoapps.ethz.ch/project/trogenmoser/

**Code repository:** https://gitlab.ethz.ch/ikgcartoapps-hs24/trogenmoser

<!-- Optional: add a hero screenshot once available -->
<!-- ![Lumo overview](docs/overview.png) -->

## About

Lumo is an interactive web-based map application that supports nighttime pedestrian navigation in the city of Zürich. While conventional navigation tools primarily optimize routes based on distance and travel time, Lumo focuses on perceptual aspects of urban space that become particularly relevant after dark, such as street lighting and visible social activity.

The application visualizes open data on public street lighting and nighttime-related points of interest to highlight areas that feel brighter and more vibrant at night. Based on this information, Lumo offers comfort-oriented walking route suggestions that prioritize well-lit and socially active streets over purely shortest paths. Rather than making claims about safety, the application aims to increase transparency and support informed, comfort-based route choices.

The project lies at the intersection of cartography, urban perception, and user experience design, and demonstrates how digital maps can support more human-centered navigation experiences in nighttime urban environments.

## Features

**Visualisation**
- **Lighting Intensity** rendered as a hexagonal choropleth conveying continuous brightness patterns.
- **Urban Vibrancy** shown as 3D hexbars whose height encodes relative nighttime activity.
- **Combined Score**, a bivariate layer where colour encodes lighting and height encodes vibrancy.

**Routing**
- Comfort-weighted routing between routing hubs, blending distance, lighting intensity, and urban vibrancy.
- Side-by-side comparison of a "fast" and a "bright" route, with per-route statistics.
- Animated route playback where hexbars grow along the path, taller where the combined score is higher.

**Exploration and UI**
- **Hotspot Explorer** revealing individual points of interest by category (bars, cafés, restaurants, music venues, night clubs).
- Globe-style zoom-out that clusters all routing hubs, with a prompt to fly back to Zürich.
- A dark, minimalist interface with a collapsible sidebar, interactive legend, feature queries, layer switcher, and a guided walkthrough.

## Data Processing

The thematic layers and walking routes are computed offline so the web client stays light and responsive. All datasets are open data from the City of Zürich and swisstopo, harmonised to a common coordinate reference system before processing.

1. **Grid** – a uniform 100 m × 100 m hexagonal grid covering the municipal area, generated in QGIS.
2. **Aggregation** – lighting points and points of interest aggregated to cells via point-in-polygon counts, producing brightness and activity values per cell.
3. **Scoring** – values normalised and combined into a single perceived-comfort score.
4. **Routing** – weighted shortest paths between predefined routing hubs precomputed in Python (distance + lighting + vibrancy), together with route–grid intersections, walking distances to hotspots, and global statistics.

The pipeline outputs preprocessed GeoJSON and JSON, which the application loads at runtime.

## Web Application

The application is a modular single-page app built with **Vue 3 and Vite** (Composition API), with clearly separated concerns for application state, map logic, and the user interface. **Mapbox GL JS** provides the interactive 3D map, including data-driven styling, click and hover interaction, and animated camera movements.

### Setup

```bash
# Install dependencies
npm install

# Create a .env file in the project root and add your Mapbox token:
# VITE_MAPBOX_TOKEN=your_mapbox_token_here

# Start the development server
npm run dev
```

> Assumes a Vue 3 + Vite setup. A [Mapbox access token](https://account.mapbox.com/access-tokens/) is required.

## Data sources

| Description | Source |
|---|---|
| Zürich communal boundary | https://www.stadt-zuerich.ch/geodaten/download/95 |
| Public illumination (points) | https://data.stadt-zuerich.ch/dataset/geo_oeffentliche_beleuchtung_der_stadt_zuerich |
| Night clubs (points) | https://data.stadt-zuerich.ch/dataset/zt_nachtleben |
| Bars and lounges (points) | https://data.stadt-zuerich.ch/dataset/zt_bars |
| Gastronomy (points) | https://data.stadt-zuerich.ch/dataset/zt_gastronomie |
| Street network for routing | https://www.swisstopo.admin.ch/de/landeskarte-swiss-map-vector10 |

## AI-Assisted Development

Cursor AI was used as a coding assistant during development to generate and refine code suggestions. All AI-generated suggestions were reviewed, adapted, and integrated by the author. The overall application architecture, data processing workflow, and core functionality were designed and implemented by the author.

## Attributions

**Data:** Open geodata from the City of Zürich (public street lighting, nightlife and gastronomy points of interest, communal boundary) and swisstopo (pedestrian street network).

**Basemaps:** © Mapbox © OpenStreetMap

## Credits

Created by **Timm Rogenmoser** for the course **Application Development in Cartography (103-0227-00L)** at ETH Zürich, Autumn Semester 2025. Course lead: Dr. Andreas Neumann.

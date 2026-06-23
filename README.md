# Lumo – Walk the (b)right Way

> Nighttime pedestrian routing for Zürich, weighted by street lighting and urban activity. Built with Vue 3 and Mapbox GL JS.

![Vue 3](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vuedotjs&logoColor=white)
![Mapbox GL JS](https://img.shields.io/badge/Mapbox%20GL%20JS-000000?logo=mapbox&logoColor=white)
![Python](https://img.shields.io/badge/Python-preprocessing-3776AB?logo=python&logoColor=white)
![QGIS](https://img.shields.io/badge/QGIS-data%20prep-589632?logo=qgis&logoColor=white)
![ETH Zürich](https://img.shields.io/badge/ETH%20Zürich-IKG-1F407A)

<!-- Optional: add a hero screenshot once available -->
<!-- ![Lumo overview](docs/overview.png) -->

**Live application:** https://ikgcartoapps.ethz.ch/project/trogenmoser/

**Code repository:** https://gitlab.ethz.ch/ikgcartoapps-hs24/trogenmoser

---

## Overview

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
- A dark, minimalist interface with a collapsible sidebar,

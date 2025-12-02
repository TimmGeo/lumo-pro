<template>
  <div
    ref="sceneEl"
    class="scene"
    :class="{ 'controls-collapsed': controlsCollapsed }"
  >
    <div ref="mapEl" class="map"></div>
    <!-- Map Controls Bar (hidden - moved to top bar in App.vue) -->
    <div
      class="map-controls-bar"
      :class="{ 'map-controls-bar--collapsed': controlsCollapsed }"
      @mouseenter="handleControlsBarMouseEnter"
      @mouseleave="handleControlsBarMouseLeave"
      style="display: none"
    >
      <div class="map-controls-content">
        <div class="map-controls-grid">
          <button
            class="map-control-btn zoom-in-btn"
            @click="zoomIn"
            aria-label="Zoom in"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 5V19M5 12H19"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <button
            class="map-control-btn zoom-out-btn"
            @click="zoomOut"
            aria-label="Zoom out"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M5 12H19"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <button
            class="map-control-btn north-btn"
            @click="resetNorth"
            aria-label="Reset to north"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 2V22M12 2L8 6M12 2L16 6"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <button
            class="map-control-btn tilt-btn"
            @click="toggleTilt"
            :class="{ active: isTilted }"
            aria-label="Toggle map tilt"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <!-- Flat view icon (2D square) -->
              <path
                v-if="!isTilted"
                d="M3 3H21V21H3V3Z"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <!-- Tilted view icon (3D perspective) -->
              <g v-else>
                <path
                  d="M3 3L12 8L21 3"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M3 21L12 16L21 21"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M3 3V21M21 3V21"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </g>
            </svg>
          </button>
        </div>
      </div>
      <div class="map-controls-header">
        <button
          class="map-controls-toggle"
          :class="{ 'map-controls-toggle--will-close': !controlsCollapsed }"
          @click="handleToggleControls"
          @mouseenter="handleControlsToggleHover"
          @mouseleave="handleControlsToggleLeave"
          :aria-expanded="!controlsCollapsed"
          aria-label="Toggle map controls"
        >
          <!-- Controls icon when collapsed -->
          <svg
            v-if="controlsCollapsed"
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
            />
          </svg>
          <!-- Chevron arrow only when expanded (to collapse) - pointing left -->
          <svg
            v-else
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M15 18L9 12L15 6"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              transform="rotate(180 12 12)"
            />
          </svg>
          <span class="map-controls-toggle-tooltip">
            {{ controlsCollapsed ? "Open Map Controls" : "Close Map Controls" }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  onMounted,
  onBeforeUnmount,
  ref,
  watch,
  nextTick,
  defineExpose,
} from "vue";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

const props = defineProps({
  lightingVisible: {
    type: Boolean,
    default: true,
  },
  vibrancyVisible: {
    type: Boolean,
    default: false,
  },
  combinedVisible: {
    type: Boolean,
    default: false,
  },
  heightScale: {
    type: Number,
    default: 1.5,
  },
  showHubs: {
    type: Boolean,
    default: true,
  },
  focusZurichKey: {
    type: Number,
    default: 0,
  },
  fromButton: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "zurichZoomComplete",
  "zoom",
  "move",
  "mapReady",
  "hubsUpdated",
  "routePopupClicked",
]);

const sceneEl = ref(null);
const mapEl = ref(null);
const isFullscreen = ref(false);
const isTilted = ref(false);
const controlsCollapsed = ref(false);
const isHoveringControls = ref(false);
let map = null;

// Hover timer for opening collapsed controls bar
let controlsHoverTimer = null;
const CONTROLS_HOVER_DELAY = 800; // 800ms delay before opening
// Hover timer for closing expanded controls bar
let controlsCloseTimer = null;
const CONTROLS_CLOSE_DELAY = 800; // 800ms delay before closing
let hubsData = null;
let hexData = null;
let hexVibrancyData = null;
let hubsLoaded = false;
let pendingZurichFocusKey = 0;

// Debounce ensureHubsOnTop to avoid excessive calls
let ensureHubsOnTopTimeout = null;
const debouncedEnsureHubsOnTop = () => {
  if (ensureHubsOnTopTimeout) {
    clearTimeout(ensureHubsOnTopTimeout);
  }
  ensureHubsOnTopTimeout = setTimeout(() => {
    ensureHubsOnTop();
    ensureHubsOnTopTimeout = null;
  }, 100);
};

// Routing state
let selectedHubId1 = null;
let selectedHubId2 = null;
let currentRouteSource = null;
let currentRouteLumoScore = null;
let currentRouteStats = null;
let routePopup = null;
let routePopupGeom = null; // Store route geometry for recreating popup

// Paths that work both locally and in deploy
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");
const lumoScoreUrl = `${BASE}data/lumo_score.geojson`.replace(/\/{2,}/g, "/");
const hexUrl = `${BASE}data/hex_light_100m.geojson`.replace(/\/{2,}/g, "/");
const hexVibrancyUrl = `${BASE}data/hex_vibrancy_100m.geojson`.replace(
  /\/{2,}/g,
  "/"
);
const vibrancyPointsUrl = `${BASE}data/vibrancy_points.geojson`.replace(
  /\/{2,}/g,
  "/"
);

// NavigationControl handles zoom and rotation

// Tilt function - toggle between flat (0°) and tilted (45°) view
function toggleTilt() {
  if (!map || !map.isStyleLoaded()) return;

  const targetPitch = isTilted.value ? 0 : 45;
  isTilted.value = !isTilted.value;

  map.easeTo({
    pitch: targetPitch,
    duration: 800,
    easing(t) {
      return t * (2 - t); // ease-out
    },
  });
}

// Fullscreen function - enter fullscreen on the app container (keeps sidebar and routing dock visible)
function toggleFullscreen() {
  if (!isFullscreen.value) {
    // Enter fullscreen on the app container (contains sidebar, routing dock, and map)
    const appElement =
      document.querySelector(".app") ||
      document.getElementById("app") ||
      document.body;

    if (appElement?.requestFullscreen) {
      appElement.requestFullscreen();
    } else if (appElement?.webkitRequestFullscreen) {
      // Safari
      appElement.webkitRequestFullscreen();
    } else if (appElement?.msRequestFullscreen) {
      // IE/Edge
      appElement.msRequestFullscreen();
    }
  } else {
    // Exit fullscreen
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      // Safari
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      // IE/Edge
      document.msExitFullscreen();
    }
  }
}

// Zoom in function
function zoomIn() {
  if (!map || !map.isStyleLoaded()) return;
  map.zoomIn();
}

// Zoom out function
function zoomOut() {
  if (!map || !map.isStyleLoaded()) return;
  map.zoomOut();
}

// Reset to north (reset bearing to 0)
function resetNorth() {
  if (!map || !map.isStyleLoaded()) return;
  map.easeTo({
    bearing: 0,
    duration: 500,
    easing(t) {
      return t * (2 - t); // ease-out
    },
  });
}

// Handle toggle button click - toggle controls bar with smooth transition
function handleToggleControls() {
  // Clear any hover timer
  if (controlsHoverTimer) {
    clearTimeout(controlsHoverTimer);
    controlsHoverTimer = null;
  }

  // Toggle controls bar (transition will handle the smooth animation)
  controlsCollapsed.value = !controlsCollapsed.value;
}

// Handle controls bar mouse enter - start hover timer if collapsed
function handleControlsBarMouseEnter() {
  isHoveringControls.value = true;

  // If controls bar is collapsed, start timer to open it
  if (controlsCollapsed.value) {
    // Clear any existing timer
    if (controlsHoverTimer) {
      clearTimeout(controlsHoverTimer);
    }

    // Start new timer
    controlsHoverTimer = setTimeout(() => {
      if (controlsCollapsed.value && isHoveringControls.value) {
        controlsCollapsed.value = false;
      }
      controlsHoverTimer = null;
    }, CONTROLS_HOVER_DELAY);
  }
}

// Handle controls bar mouse leave - clear hover timer
function handleControlsBarMouseLeave() {
  isHoveringControls.value = false;

  // Clear hover timer if it exists
  if (controlsHoverTimer) {
    clearTimeout(controlsHoverTimer);
    controlsHoverTimer = null;
  }
}

// Handle controls toggle button hover - close if expanded
function handleControlsToggleHover() {
  // Only close if controls are expanded (not collapsed)
  if (!controlsCollapsed.value) {
    // Clear any existing timer
    if (controlsCloseTimer) {
      clearTimeout(controlsCloseTimer);
    }

    // Start timer to close
    controlsCloseTimer = setTimeout(() => {
      if (!controlsCollapsed.value) {
        controlsCollapsed.value = true;
      }
      controlsCloseTimer = null;
    }, CONTROLS_CLOSE_DELAY);
  }
}

// Handle controls toggle button leave - clear close timer
function handleControlsToggleLeave() {
  if (controlsCloseTimer) {
    clearTimeout(controlsCloseTimer);
    controlsCloseTimer = null;
  }
}

// Listen to fullscreen changes
function handleFullscreenChange() {
  isFullscreen.value = !!(
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.msFullscreenElement
  );

  // Resize map after fullscreen change
  setTimeout(() => {
    if (map) {
      map.resize();
    }
  }, 100);
}

onMounted(async () => {
  await nextTick();

  // Listen to fullscreen events
  document.addEventListener("fullscreenchange", handleFullscreenChange);
  document.addEventListener("webkitfullscreenchange", handleFullscreenChange);
  document.addEventListener("msfullscreenchange", handleFullscreenChange);

  const token = import.meta.env.VITE_MAPBOX_TOKEN;

  if (!token) {
    console.error("❌ Mapbox token is missing! Check your .env file");
    return;
  }

  if (!mapEl.value) {
    console.error("❌ Map container not found!");
    return;
  }

  try {
    mapboxgl.accessToken = token;

    map = new mapboxgl.Map({
      container: mapEl.value,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [0, 18],
      zoom: 1.2,
      pitch: 0,
      bearing: 0,
      attributionControl: false,
    });

    // Emit zoom and move events for scale calculation
    map.on("zoom", () => {
      const zoom = map.getZoom();
      emit("zoom", { zoom: zoom, center: map.getCenter() });

      // Show/hide route popup based on zoom (same condition as zurich time display)
      handleRoutePopupVisibility(zoom);
    });

    map.on("move", () => {
      const zoom = map.getZoom();
      emit("move", { zoom: zoom, center: map.getCenter() });

      // Show/hide route popup based on zoom (same condition as zurich time display)
      handleRoutePopupVisibility(zoom);
    });

    map.on("load", async () => {
      console.log("✅ Mapbox map loaded successfully!");

      // Wait for map to be idle (tiles loaded) before emitting ready
      map.once("idle", () => {
        emit("mapReady");
      });

      // Note: We removed the styledata and idle event listeners to improve performance
      // ensureHubsOnTop() is now only called when layers are actually added or changed

      // Emit initial zoom/center
      emit("zoom", { zoom: map.getZoom(), center: map.getCenter() });

      try {
        // --- Load and add Routing Hubs (points) ---
        const hubsResponse = await fetch(hubsUrl);
        hubsData = await hubsResponse.json();

        map.addSource("hubs", {
          type: "geojson",
          data: hubsData,
          cluster: true,
          clusterMaxZoom: 14, // Max zoom to cluster points on
          clusterRadius: 50, // Radius of each cluster when clustering points
        });

        // Emit hubs ready event immediately (before locality names are fetched)
        emit("hubsUpdated");

        // Fetch locality names for each hub using reverse geocoding (async, in background)
        fetchLocalityNamesForHubs();

        // Add cluster circles (white circles for clusters)
        map.addLayer({
          id: "hubs-clusters",
          type: "circle",
          source: "hubs",
          filter: ["has", "point_count"],
          paint: {
            "circle-color": "#ffffff",
            "circle-radius": [
              "step",
              ["get", "point_count"],
              20, // Default radius for clusters
              10,
              25, // Larger radius for 10+ points
              50,
              30, // Even larger for 50+ points
              100,
              35, // Largest for 100+ points
            ],
            "circle-stroke-width": 0, // No contour
            "circle-opacity": 0.7, // Slightly transparent
          },
        });

        // Add cluster count labels (numbers on clusters)
        map.addLayer({
          id: "hubs-cluster-count",
          type: "symbol",
          source: "hubs",
          filter: ["has", "point_count"],
          layout: {
            "text-field": "{point_count_abbreviated}",
            "text-font": ["Open Sans Bold", "Arial Unicode MS Bold"],
            "text-size": [
              "step",
              ["get", "point_count"],
              12, // Default size
              10,
              14, // Larger for 10+ points
              50,
              16, // Even larger for 50+ points
              100,
              18, // Largest for 100+ points
            ],
          },
          paint: {
            "text-color": "#0b0b0c", // Black text, no halo
          },
        });

        // Add circles for unclustered hubs (matching Cesium styling)
        map.addLayer({
          id: "hubs-circles",
          type: "circle",
          source: "hubs",
          filter: ["!", ["has", "point_count"]],
          paint: {
            "circle-radius": 6,
            "circle-color": "#70f0c3", // Default green for all hubs
            "circle-stroke-color": "#0b0b0c",
            "circle-stroke-width": 0,
            "circle-opacity": 1,
          },
        });

        // Add click handler for clusters (zoom in when clicked)
        map.on("click", "hubs-clusters", (e) => {
          const features = map.queryRenderedFeatures(e.point, {
            layers: ["hubs-clusters"],
          });
          const clusterId = features[0].properties.cluster_id;
          const source = map.getSource("hubs");

          source.getClusterExpansionZoom(clusterId, (err, zoom) => {
            if (err) return;

            map.easeTo({
              center: features[0].geometry.coordinates,
              zoom: zoom,
              duration: 500,
            });
          });
        });

        // Add click handler for hubs
        map.on("click", "hubs-circles", (e) => {
          if (!e.features || e.features.length === 0) return;

          const clickedHub = e.features[0];
          const hubId = clickedHub.properties.id;

          handleHubClick(hubId);
        });

        // Change cursor on hover for clusters
        map.on("mouseenter", "hubs-clusters", () => {
          map.getCanvas().style.cursor = "pointer";
        });

        map.on("mouseleave", "hubs-clusters", () => {
          map.getCanvas().style.cursor = "";
        });

        // Change cursor on hover for hubs
        map.on("mouseenter", "hubs-circles", () => {
          map.getCanvas().style.cursor = "pointer";
        });

        map.on("mouseleave", "hubs-circles", () => {
          map.getCanvas().style.cursor = "";
        });

        // Add labels for hubs (matching Cesium styling)
        map.addLayer({
          id: "hubs-labels",
          type: "symbol",
          source: "hubs",
          minzoom: 12, // Show labels at moderate zoom level
          layout: {
            "text-field": [
              "coalesce",
              ["get", "locality"],
              ["get", "neighborhood"],
              "Hub",
            ],
            "text-font": ["Open Sans Bold", "Arial Unicode MS Bold"],
            "text-size": 14,
            "text-offset": [0.7, 0],
            "text-anchor": "left",
          },
          paint: {
            "text-color": "#e9f7f2",
            "text-halo-color": "#0b0b0c",
            "text-halo-width": 2,
          },
        });

        // --- Load and add Hexagons (polygons) ---
        const hexResponse = await fetch(hexUrl);
        hexData = await hexResponse.json();

        map.addSource("hex", {
          type: "geojson",
          data: hexData,
        });

        // Add hexagon fill layer (no fade, just original colors)
        map.addLayer({
          id: "hex-layer",
          type: "fill",
          source: "hex",
          paint: {
            "fill-color": ["coalesce", ["get", "color"], "#969696"],
            "fill-opacity": 0.65,
            "fill-outline-color": "transparent",
          },
        });

        // Initial visibility - only show hex layer when lighting layer is selected
        map.setLayoutProperty(
          "hex-layer",
          "visibility",
          props.lightingVisible ? "visible" : "none"
        );
        setHubsVisibility(props.showHubs);
        hubsLoaded = true;

        // Initialize hub colors
        updateHubColors();

        // Emit hubs ready event immediately (before locality names are fetched)
        emit("hubsUpdated");

        // --- Load and add Vibrancy Hexagons (3D extruded) ---
        try {
          const vibrancyResponse = await fetch(hexVibrancyUrl);
          hexVibrancyData = await vibrancyResponse.json();

          map.addSource("hex-vibrancy", {
            type: "geojson",
            data: hexVibrancyData,
          });

          // Add 3D extruded hexagon layer for vibrancy
          map.addLayer({
            id: "hex-vibrancy-layer",
            type: "fill-extrusion",
            source: "hex-vibrancy",
            filter: [">", ["get", "NUMPOINTS"], 0], // Only show hexagons with NUMPOINTS > 0
            paint: {
              "fill-extrusion-color": "#9ca3af",
              // Fade out hexagons as zoom increases (more drastic transition from zoom 15 to 15.3)
              "fill-extrusion-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0.4, // At zoom 15, opacity 0.4
                15.15,
                0.1, // At zoom 15.15, opacity 0.1 (more drastic drop)
                15.3,
                0, // At zoom 15.3+, opacity 0 (fully transparent)
              ],
              "fill-extrusion-height": [
                "*",
                ["get", "NUMPOINTS"],
                150, // Scale factor - extremely high for dramatic skyscraper effect
              ],
              "fill-extrusion-base": 0,
            },
          });

          // Initial visibility - only show vibrancy layer when vibrancy layer is selected
          map.setLayoutProperty(
            "hex-vibrancy-layer",
            "visibility",
            props.vibrancyVisible ? "visible" : "none"
          );

          // --- Load and add Vibrancy POI Points (visible when zoomed in) ---
          try {
            const vibrancyPointsResponse = await fetch(vibrancyPointsUrl);
            const vibrancyPointsData = await vibrancyPointsResponse.json();

            map.addSource("vibrancy-points", {
              type: "geojson",
              data: vibrancyPointsData,
            });

            // Color mapping for different POI types (bright, shining colors)
            const typeColors = {
              BarOrPub: "#ff4444", // Bright red
              CafeOrCoffeeShop: "#ffaa00", // Bright amber/orange
              Restaurant: "#00ff88", // Bright green
              MusicVenue: "#aa44ff", // Bright purple
              NightClub: "#ff44aa", // Bright pink/magenta
            };

            // Add circle layer for POI points
            map.addLayer({
              id: "vibrancy-points-layer",
              type: "circle",
              source: "vibrancy-points",
              minzoom: 15, // Only show when zoomed in
              paint: {
                "circle-radius": [
                  "interpolate",
                  ["linear"],
                  ["zoom"],
                  15,
                  5, // At zoom 15, radius 5 (bigger)
                  16,
                  6, // At zoom 16, radius 6
                  17,
                  7, // At zoom 17, radius 7
                  18,
                  8, // At zoom 18, radius 8
                ],
                "circle-color": [
                  "match",
                  ["get", "Type"],
                  "BarOrPub",
                  typeColors.BarOrPub,
                  "CafeOrCoffeeShop",
                  typeColors.CafeOrCoffeeShop,
                  "Restaurant",
                  typeColors.Restaurant,
                  "MusicVenue",
                  typeColors.MusicVenue,
                  "NightClub",
                  typeColors.NightClub,
                  "#9ca3af", // Default grey if type not found
                ],
                // Fade in points as zoom increases, then slightly decrease shininess when zooming in more
                "circle-opacity": [
                  "interpolate",
                  ["linear"],
                  ["zoom"],
                  15,
                  0, // At zoom 15, opacity 0 (invisible)
                  15.15,
                  0.8, // At zoom 15.15, opacity 0.8 (more drastic jump)
                  15.3,
                  1, // At zoom 15.3, opacity 1 (fully visible and shining)
                  17,
                  0.85, // At zoom 17, opacity 0.85 (slightly less shiny)
                  19,
                  0.8, // At zoom 19+, opacity 0.8 (less shiny when very zoomed in)
                ],
              },
            });

            // Initial visibility - only show POI points when vibrancy layer is selected
            map.setLayoutProperty(
              "vibrancy-points-layer",
              "visibility",
              props.vibrancyVisible ? "visible" : "none"
            );
          } catch (error) {
            console.error("Error loading vibrancy POI points:", error);
          }

          // Load lumo_score.geojson for combined layer
          const lumoScoreResponse = await fetch(lumoScoreUrl);
          const lumoScoreData = await lumoScoreResponse.json();
          console.log("Loaded lumo_score data:", lumoScoreData);

          // Add source for combined layer using lumo_score data
          map.addSource("hex-combined", {
            type: "geojson",
            data: lumoScoreData,
          });

          // Add 2D fill layer for combined (shows when zoomed in, after 3D disappears)
          map.addLayer({
            id: "hex-combined-fill",
            type: "fill",
            source: "hex-combined",
            filter: [">", ["get", "combined_score"], 0], // Only show hexagons with combined_score > 0
            paint: {
              "fill-color": [
                "interpolate",
                ["linear"],
                ["get", "combined_score"],
                0,
                "#0b0b0c", // Match dark background for low scores
                0.1,
                "#161718", // Slightly lighter, still blends with background
                0.5,
                "#2d3561", // Dark blue
                1,
                "#6c5ce7", // Medium purple-blue
                2,
                "#a29bfe", // Bright purple-blue
                5,
                "#e0e7ff", // Very bright light purple-blue for high scores
              ],
              // Fade in 2D hexagons as zoom increases (opposite of 3D layer)
              // Colors are opaque, but layer opacity is moderate to keep map readable
              "fill-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0, // At zoom 15, opacity 0 (invisible)
                15.15,
                0.4, // At zoom 15.15, opacity 0.4 (colors visible)
                15.3,
                0.5, // At zoom 15.3+, opacity 0.5 (colors visible but map still readable)
              ],
              "fill-outline-color": "transparent", // No outline on fill layer (we use separate line layer)
            },
          });

          // Add line layer for thicker, transparent white contours
          map.addLayer({
            id: "hex-combined-outline",
            type: "line",
            source: "hex-combined",
            filter: [">", ["get", "combined_score"], 0], // Only show hexagons with combined_score > 0
            paint: {
              "line-color": "#ffffff", // White
              "line-width": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                2, // At zoom 15, width 2
                15.3,
                2.5, // At zoom 15.3+, width 2.5 (thicker)
              ],
              // Fade in outline as zoom increases - very transparent and discrete
              "line-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0, // At zoom 15, opacity 0 (invisible)
                15.15,
                0.15, // At zoom 15.15, opacity 0.15 (very subtle)
                15.3,
                0.25, // At zoom 15.3+, opacity 0.25 (transparent, discrete)
              ],
            },
          });

          // Add 3D extruded hexagon layer for combined (height based on combined_score)
          map.addLayer({
            id: "hex-combined-layer",
            type: "fill-extrusion",
            source: "hex-combined",
            filter: [">", ["get", "combined_score"], 0], // Only show hexagons with combined_score > 0
            paint: {
              "fill-extrusion-color": [
                "interpolate",
                ["linear"],
                ["get", "combined_score"],
                0,
                "#0b0b0c", // Match dark background for low scores
                0.1,
                "#161718", // Slightly lighter, still blends with background
                0.5,
                "#2d3561", // Dark blue
                1,
                "#6c5ce7", // Medium purple-blue
                2,
                "#a29bfe", // Bright purple-blue
                5,
                "#e0e7ff", // Very bright light purple-blue for high scores
              ],
              // Fade out hexagons as zoom increases (same as vibrancy layer)
              "fill-extrusion-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0.6, // At zoom 15, opacity 0.6
                15.15,
                0.15, // At zoom 15.15, opacity 0.15 (more drastic drop)
                15.3,
                0, // At zoom 15.3+, opacity 0 (fully transparent - hexagons disappear)
              ],
              "fill-extrusion-height": [
                "*",
                ["get", "combined_score"],
                2500, // Higher scale factor for more visible height differences
              ],
              "fill-extrusion-base": 0,
            },
          });

          // Initial visibility - only show combined layers when combined layer is selected
          map.setLayoutProperty(
            "hex-combined-fill",
            "visibility",
            props.combinedVisible ? "visible" : "none"
          );
          map.setLayoutProperty(
            "hex-combined-outline",
            "visibility",
            props.combinedVisible ? "visible" : "none"
          );
          map.setLayoutProperty(
            "hex-combined-layer",
            "visibility",
            props.combinedVisible ? "visible" : "none"
          );
        } catch (error) {
          console.error("Failed to load vibrancy GeoJSON data:", error);
        }

        // Ensure hubs are always on top of all other layers
        ensureHubsOnTop();

        // Debug
        window.map = map;
        console.log("Loaded:", {
          hubs: hubsData.features.length,
          hex: hexData.features.length,
          hexVibrancy: hexVibrancyData ? hexVibrancyData.features.length : 0,
        });
        if (pendingZurichFocusKey) {
          performZurichFocus();
          pendingZurichFocusKey = 0;
        }
      } catch (error) {
        console.error("Failed to load GeoJSON data:", error);
      }
    });

    map.on("error", (e) => {
      if (e.error && e.error.status === 403) {
        console.error(
          "❌ 403 Forbidden - Your Mapbox token is invalid or doesn't have the right permissions"
        );
        console.error(
          "Check your token at: https://account.mapbox.com/access-tokens/"
        );
      } else {
        console.error("Mapbox error:", e.error?.message || e);
      }
    });
  } catch (error) {
    console.error("Failed to initialize map:", error);
  }
});

// Helper function to safely update layer visibility
function updateLayerVisibility(layerId, visible) {
  if (!map || !map.isStyleLoaded()) return false;
  const layer = map.getLayer(layerId);
  if (!layer) return false;
  try {
    map.setLayoutProperty(layerId, "visibility", visible ? "visible" : "none");
    return true;
  } catch (error) {
    console.warn(`Failed to update layer ${layerId}:`, error);
    return false;
  }
}

// React to layer visibility changes
watch(
  () => props.lightingVisible,
  (isVisible) => {
    if (!map) return;

    // Immediately hide vibrancy points when switching to lighting (no delay)
    if (isVisible && map.isStyleLoaded()) {
      const pointsLayer = map.getLayer("vibrancy-points-layer");
      if (pointsLayer) {
        map.setLayoutProperty("vibrancy-points-layer", "visibility", "none");
      }
    }

    // Use nextTick to ensure DOM and map are ready
    nextTick(() => {
      const updateVisibility = () => {
        if (!map.isStyleLoaded()) {
          setTimeout(updateVisibility, 50);
          return;
        }

        // Show/hide hex layer only when lighting layer is selected
        updateLayerVisibility("hex-layer", isVisible);

        // Ensure other layers are hidden when lighting is selected
        if (isVisible) {
          updateLayerVisibility("hex-vibrancy-layer", false);
          updateLayerVisibility("hex-combined-fill", false);
          updateLayerVisibility("hex-combined-outline", false);
          updateLayerVisibility("hex-combined-layer", false);
          updateLayerVisibility("vibrancy-points-layer", false);
        }

        // Ensure hubs are always on top after visibility changes (debounced)
        debouncedEnsureHubsOnTop();
      };

      updateVisibility();
    });
  },
  { immediate: true }
);

watch(
  () => props.vibrancyVisible,
  (isVisible) => {
    if (!map) return;

    // Use nextTick to ensure DOM and map are ready
    nextTick(() => {
      const updateVisibility = () => {
        if (!map.isStyleLoaded()) {
          setTimeout(updateVisibility, 50);
          return;
        }

        // Show/hide 3D vibrancy layer when vibrancy layer is selected
        const vibrancyLayerUpdated = updateLayerVisibility(
          "hex-vibrancy-layer",
          isVisible
        );
        // Show/hide POI points layer when vibrancy layer is selected
        const pointsLayerUpdated = updateLayerVisibility(
          "vibrancy-points-layer",
          isVisible
        );

        // If layers don't exist yet, retry after a short delay
        if (!vibrancyLayerUpdated || !pointsLayerUpdated) {
          setTimeout(updateVisibility, 100);
          return;
        }

        // Ensure other layers are hidden when vibrancy is selected
        if (isVisible) {
          updateLayerVisibility("hex-layer", false);
          updateLayerVisibility("hex-combined-fill", false);
          updateLayerVisibility("hex-combined-outline", false);
          updateLayerVisibility("hex-combined-layer", false);
        }

        // Ensure hubs are always on top after visibility changes (debounced)
        debouncedEnsureHubsOnTop();
      };

      updateVisibility();
    });
  },
  { immediate: true }
);

watch(
  () => props.combinedVisible,
  (isVisible) => {
    if (!map) return;

    // Immediately hide vibrancy points when switching to combined (no delay)
    if (isVisible && map.isStyleLoaded()) {
      const pointsLayer = map.getLayer("vibrancy-points-layer");
      if (pointsLayer) {
        map.setLayoutProperty("vibrancy-points-layer", "visibility", "none");
      }
    }

    // Use nextTick to ensure DOM and map are ready
    nextTick(() => {
      const updateVisibility = () => {
        if (!map.isStyleLoaded()) {
          setTimeout(updateVisibility, 50);
          return;
        }

        // Show/hide 2D, outline, and 3D combined layers when combined layer is selected
        const fillLayerUpdated = updateLayerVisibility(
          "hex-combined-fill",
          isVisible
        );
        const outlineLayerUpdated = updateLayerVisibility(
          "hex-combined-outline",
          isVisible
        );
        const extrusionLayerUpdated = updateLayerVisibility(
          "hex-combined-layer",
          isVisible
        );

        // If layers don't exist yet, retry after a short delay
        if (
          !fillLayerUpdated ||
          !outlineLayerUpdated ||
          !extrusionLayerUpdated
        ) {
          setTimeout(updateVisibility, 100);
          return;
        }

        // Ensure other layers are hidden when combined is selected
        if (isVisible) {
          updateLayerVisibility("hex-layer", false);
          updateLayerVisibility("hex-vibrancy-layer", false);
          updateLayerVisibility("vibrancy-points-layer", false);
        }

        // Ensure hubs are always on top after visibility changes (debounced)
        debouncedEnsureHubsOnTop();
      };

      updateVisibility();
    });
  },
  { immediate: true }
);

watch(
  () => props.showHubs,
  (visible) => {
    if (!map || !map.isStyleLoaded() || !hubsLoaded) return;
    setHubsVisibility(visible);
  }
);

watch(
  () => props.focusZurichKey,
  (key) => {
    requestZurichFocus(key);
  }
);

function ensureHubsOnTop() {
  if (!map || !map.isStyleLoaded()) return;

  const hubLayers = [
    "hubs-clusters", // Move first (will be at bottom of hub stack)
    "hubs-cluster-count",
    "hubs-circles",
    "hubs-labels", // Move last (will be on top of hub stack)
  ];

  // Check if all hub layers exist
  const existingHubLayers = hubLayers.filter((layerId) =>
    map.getLayer(layerId)
  );
  if (existingHubLayers.length === 0) return;

  // Get current layer order
  const style = map.getStyle();
  if (!style || !style.layers) return;

  const allLayers = style.layers;
  const layerIndices = {};
  allLayers.forEach((layer, index) => {
    layerIndices[layer.id] = index;
  });

  // Check if hubs are already on top
  // Find the last non-hub layer index
  let lastNonHubIndex = -1;
  for (let i = allLayers.length - 1; i >= 0; i--) {
    if (!hubLayers.includes(allLayers[i].id)) {
      lastNonHubIndex = i;
      break;
    }
  }

  // Check if all hub layers are after the last non-hub layer
  let needsReordering = false;
  for (const hubLayerId of existingHubLayers) {
    const hubIndex = layerIndices[hubLayerId];
    if (hubIndex === undefined || hubIndex <= lastNonHubIndex) {
      needsReordering = true;
      break;
    }
  }

  // Only move layers if they're not already on top
  if (needsReordering) {
    // Move each hub layer to the absolute top
    hubLayers.forEach((layerId) => {
      if (map.getLayer(layerId)) {
        map.moveLayer(layerId);
      }
    });
  }
}

function setHubsVisibility(visible) {
  if (!map || !map.isStyleLoaded()) return;
  const visibility = visible ? "visible" : "none";
  map.setLayoutProperty("hubs-clusters", "visibility", visibility);
  map.setLayoutProperty("hubs-cluster-count", "visibility", visibility);
  map.setLayoutProperty("hubs-circles", "visibility", visibility);
  map.setLayoutProperty("hubs-labels", "visibility", visibility);
  if (visible) {
    // Use debounced version for visibility toggles to avoid excessive calls
    debouncedEnsureHubsOnTop();
  }
}

// Handle hub click - select first hub, then second hub to show route
function handleHubClick(hubId) {
  if (!map || !map.isStyleLoaded()) return;

  // Convert to number for consistency
  const id = typeof hubId === "string" ? parseInt(hubId, 10) : hubId;

  // If clicking the same hub that's already selected, deselect it
  if (selectedHubId1 === id) {
    selectedHubId1 = null;
    selectedHubId2 = null;
    clearRoute();
    updateHubColors();
    return;
  }

  // If clicking the second selected hub, deselect it
  if (selectedHubId2 === id) {
    selectedHubId2 = null;
    clearRoute();
    updateHubColors();
    return;
  }

  // If no hub is selected, select this one as first
  if (selectedHubId1 === null) {
    selectedHubId1 = id;
    selectedHubId2 = null;
    clearRoute();
    updateHubColors();
    return;
  }

  // If first hub is selected, select this one as second and show route
  if (selectedHubId1 !== null && selectedHubId2 === null) {
    selectedHubId2 = id;
    loadAndDisplayRoute(selectedHubId1, selectedHubId2);
    updateHubColors();
    return;
  }

  // If both hubs are selected, replace first with this one
  selectedHubId1 = id;
  selectedHubId2 = null;
  clearRoute();
  updateHubColors();
}

// Update hub colors - ensure all hubs have the same default green color
function updateHubColors() {
  if (!map || !map.isStyleLoaded() || !hubsData) return;

  const layer = map.getLayer("hubs-circles");
  if (!layer) return;

  // Remove any selectedColor property from all hubs to ensure uniform coloring
  const updatedFeatures = hubsData.features.map((feature) => {
    const newProperties = { ...feature.properties };
    // Remove selectedColor to ensure all hubs use default green
    delete newProperties.selectedColor;

    return {
      ...feature,
      properties: newProperties,
    };
  });

  // Update the source with new data
  const updatedData = {
    ...hubsData,
    features: updatedFeatures,
  };

  map.getSource("hubs").setData(updatedData);

  // Set paint property to use default green for all hubs
  map.setPaintProperty("hubs-circles", "circle-color", "#70f0c3");
}

// Load and display route between two hubs
async function loadAndDisplayRoute(fromId, toId) {
  console.log("loadAndDisplayRoute called with", {
    fromId,
    toId,
    mapReady: !!map,
    styleLoaded: map?.isStyleLoaded(),
  });

  if (!map) {
    console.error("Map not initialized");
    return;
  }

  if (!map.isStyleLoaded()) {
    console.warn("Map style not loaded yet, waiting...");
    // Wait for style to load
    await new Promise((resolve) => {
      if (map.isStyleLoaded()) {
        resolve();
      } else {
        map.once("style.load", resolve);
      }
    });
    console.log("Map style loaded, proceeding with route");
  }

  // Determine route filename (always use smaller ID first for consistency)
  const routeId1 = Math.min(fromId, toId);
  const routeId2 = Math.max(fromId, toId);
  const routeFileName = `${routeId1}_${routeId2}.geojson`;
  const routeUrl = `${BASE}data/routes/${routeFileName}`.replace(
    /\/{2,}/g,
    "/"
  );

  console.log(`Loading route: ${routeFileName} from ${routeUrl}`);

  try {
    // Clear existing route first
    clearRoute();

    // Load route data
    const routeResponse = await fetch(routeUrl);
    if (!routeResponse.ok) {
      console.error(`Route not found: ${routeFileName}`, {
        status: routeResponse.status,
        statusText: routeResponse.statusText,
      });
      return;
    }

    const routeData = await routeResponse.json();
    console.log("Route data loaded:", routeData);

    // Validate route data
    if (!routeData || !routeData.features || routeData.features.length === 0) {
      console.error("Route data is empty or invalid:", routeData);
      return;
    }

    console.log(`Route has ${routeData.features.length} feature(s)`);

    // Extract route geometry for popup positioning
    let route_geom = null;
    if (routeData.features && routeData.features.length > 0) {
      const firstFeature = routeData.features[0];
      if (
        firstFeature.geometry &&
        firstFeature.geometry.type === "LineString"
      ) {
        route_geom = {
          coords: firstFeature.geometry.coordinates,
        };
      }
    }

    // Extract route statistics from route data
    currentRouteLumoScore = null;
    currentRouteStats = null;
    if (routeData.features && routeData.features.length > 0) {
      const firstFeature = routeData.features[0];
      if (firstFeature.properties) {
        const props = firstFeature.properties;

        // Extract lumo score
        if (props.lumo_score_percentage !== undefined) {
          currentRouteLumoScore = props.lumo_score_percentage;
        }

        // Extract all route statistics
        currentRouteStats = {
          lengthMeters: props.route_length_meters || null,
          lengthKm: props.route_length_km || null,
          walkDurationMinutes: props.walk_duration_minutes || null,
          walkDurationFormatted: props.walk_duration_formatted || null,
          poiCounts: props.poi_counts || {},
          poiFrequencies: props.poi_frequencies || {},
        };

        console.log(`Route Stats:`, currentRouteStats);
      }
    }

    // Add route source
    if (map.getSource("route")) {
      console.log("Updating existing route source");
      map.getSource("route").setData(routeData);
    } else {
      console.log("Creating new route source");
      map.addSource("route", {
        type: "geojson",
        data: routeData,
      });
    }

    // Wait a bit to ensure source is ready
    await nextTick();

    // Add route layers if they don't exist (glow + main line for techy effect)
    const beforeLayer = map.getLayer("hubs-circles")
      ? "hubs-circles"
      : undefined;

    // Glow/shadow layer (underneath main line) - blue glow
    if (!map.getLayer("route-line-glow")) {
      map.addLayer(
        {
          id: "route-line-glow",
          type: "line",
          source: "route",
          paint: {
            "line-color": "#00a8ff",
            "line-width": [
              "interpolate",
              ["linear"],
              ["zoom"],
              10,
              14,
              15,
              20,
              18,
              26,
            ],
            "line-opacity": 0.4,
            "line-blur": 10,
          },
          layout: {
            "line-join": "round",
            "line-cap": "round",
          },
        },
        beforeLayer
      );
    }

    // Main route line - thick, bright blue
    if (!map.getLayer("route-line")) {
      map.addLayer(
        {
          id: "route-line",
          type: "line",
          source: "route",
          paint: {
            "line-color": [
              "interpolate",
              ["linear"],
              ["zoom"],
              10,
              "#0099ff",
              15,
              "#00a8ff",
              18,
              "#00b8ff",
            ],
            "line-width": [
              "interpolate",
              ["linear"],
              ["zoom"],
              10,
              5,
              15,
              8,
              18,
              10,
            ],
            "line-opacity": 1,
          },
          layout: {
            "line-join": "round",
            "line-cap": "round",
          },
        },
        beforeLayer
      );
      console.log("Route layer added");
    } else {
      console.log("Route layer already exists");
      // Update existing layer properties
      map.setPaintProperty("route-line", "line-color", [
        "interpolate",
        ["linear"],
        ["zoom"],
        10,
        "#0099ff",
        15,
        "#00a8ff",
        18,
        "#00b8ff",
      ]);
      map.setPaintProperty("route-line", "line-width", [
        "interpolate",
        ["linear"],
        ["zoom"],
        10,
        5,
        15,
        8,
        18,
        10,
      ]);
    }

    // Highlight layer for extra shine (on top)
    if (!map.getLayer("route-line-highlight")) {
      map.addLayer(
        {
          id: "route-line-highlight",
          type: "line",
          source: "route",
          paint: {
            "line-color": "#ffffff",
            "line-width": [
              "interpolate",
              ["linear"],
              ["zoom"],
              10,
              1.5,
              15,
              2,
              18,
              2.5,
            ],
            "line-opacity": 0.6,
            "line-gap-width": [
              "interpolate",
              ["linear"],
              ["zoom"],
              10,
              3.5,
              15,
              6,
              18,
              7.5,
            ],
          },
          layout: {
            "line-join": "round",
            "line-cap": "round",
          },
        },
        "route-line"
      );
    }

    // Ensure all route layers are visible
    const routeLayers = [
      "route-line-glow",
      "route-line",
      "route-line-highlight",
    ];
    routeLayers.forEach((layerId) => {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, "visibility", "visible");
      }
    });
    console.log("Route layers visibility set to visible");

    // Verify the layer exists and is visible
    const routeLayer = map.getLayer("route-line");
    if (routeLayer) {
      const visibility = map.getLayoutProperty("route-line", "visibility");
      console.log("Route layer exists, visibility:", visibility);
    } else {
      console.error("Route layer does not exist after creation!");
    }

    // Move route layers to be above hex layers but below hubs (if not already positioned)
    if (map.getLayer("hubs-circles")) {
      try {
        // Move in reverse order to maintain correct stacking
        routeLayers.reverse().forEach((layerId) => {
          if (map.getLayer(layerId)) {
            map.moveLayer(layerId, "hubs-circles");
          }
        });
        console.log("Route layers moved before hubs-circles");
      } catch (e) {
        console.warn("Could not move route layers:", e);
      }
    }

    // Ensure hubs are always on top after routes are added
    ensureHubsOnTop();

    currentRouteSource = routeUrl;
    console.log(`✅ Route successfully loaded: ${routeFileName}`);

    // Force a repaint to ensure route is visible
    map.triggerRepaint();

    // Zoom and center map on the route
    if (route_geom && route_geom.coords && route_geom.coords.length > 0) {
      // Calculate bounding box of the route
      const coords = route_geom.coords;
      let minLng = coords[0][0];
      let maxLng = coords[0][0];
      let minLat = coords[0][1];
      let maxLat = coords[0][1];

      coords.forEach((coord) => {
        const [lng, lat] = coord;
        minLng = Math.min(minLng, lng);
        maxLng = Math.max(maxLng, lng);
        minLat = Math.min(minLat, lat);
        maxLat = Math.max(maxLat, lat);
      });

      // Add padding around the route (in degrees)
      const padding = 0.01; // Adjust this value to control how much padding around the route
      const bounds = [
        [minLng - padding, minLat - padding], // Southwest corner
        [maxLng + padding, maxLat + padding], // Northeast corner
      ];

      // Get current pitch and bearing to preserve them
      const currentPitch = map.getPitch();
      const currentBearing = map.getBearing();

      // Create LngLatBounds object
      const routeBounds = new mapboxgl.LngLatBounds(bounds[0], bounds[1]);

      // Calculate the center point
      const center = routeBounds.getCenter();

      // Calculate zoom level manually based on bounds
      // This is a simplified calculation - fitBounds does this more accurately
      // but we'll use a reasonable approximation
      const ne = routeBounds.getNorthEast();
      const sw = routeBounds.getSouthWest();
      const latDiff = ne.lat - sw.lat;
      const lngDiff = ne.lng - sw.lng;
      const maxDiff = Math.max(latDiff, lngDiff);

      // Estimate zoom level (this is approximate, fitBounds does it better)
      // We'll use fitBounds with duration 0 to get accurate zoom, then animate
      const originalCenter = map.getCenter();
      const originalZoom = map.getZoom();

      // Temporarily fit bounds to calculate optimal zoom
      map.fitBounds(routeBounds, {
        padding: { top: 50, bottom: 50, left: 50, right: 50 },
        duration: 0,
        maxZoom: 16,
      });

      const targetZoom = Math.min(map.getZoom(), 16);
      const targetCenter = map.getCenter();

      // Restore original position
      map.jumpTo({
        center: originalCenter,
        zoom: originalZoom,
        pitch: currentPitch,
        bearing: currentBearing,
      });

      // Now animate to the target position while preserving pitch
      map.easeTo({
        center: targetCenter,
        zoom: targetZoom,
        pitch: currentPitch, // Preserve current pitch (inclination)
        bearing: currentBearing, // Preserve current bearing
        duration: 1500,
        easing(t) {
          return t * (2 - t); // ease-out easing
        },
      });

      console.log("✅ Map zoomed and centered on route");
    }

    // Show route statistics popup after a short delay
    setTimeout(() => {
      if (route_geom && currentRouteStats) {
        showRouteStatsPopup(route_geom);
      }
    }, 300);
  } catch (error) {
    console.error(`Error loading route ${routeFileName}:`, error);
  }
}

// Handle route popup visibility based on zoom level
function handleRoutePopupVisibility(zoom) {
  if (!map) return;

  const shouldShow = zoom >= 11 && routePopupGeom && currentRouteStats;

  if (shouldShow) {
    // Show popup if it doesn't exist
    if (!routePopup) {
      showRouteStatsPopup(routePopupGeom);
    } else {
      // Fade in existing popup
      setTimeout(() => {
        const popupElement = document.querySelector(".route-stats-map-popup");
        if (popupElement) {
          popupElement.style.opacity = "1";
          popupElement.style.visibility = "visible";
          popupElement.style.pointerEvents = "auto";
          popupElement.style.transition =
            "opacity 0.4s ease, visibility 0.4s ease";
        }
      }, 10);
    }
  } else {
    // Fade out popup
    if (routePopup) {
      const popupElement = document.querySelector(".route-stats-map-popup");
      if (popupElement) {
        popupElement.style.opacity = "0";
        popupElement.style.visibility = "hidden";
        popupElement.style.pointerEvents = "none";
        popupElement.style.transition =
          "opacity 0.3s ease, visibility 0.3s ease";
      }
    }
  }
}

// Show route statistics popup on the map
function showRouteStatsPopup(routeGeom) {
  if (!map || !routeGeom || !currentRouteStats) return;

  // Store geometry for later recreation
  routePopupGeom = routeGeom;

  // Remove existing popup if any
  if (routePopup) {
    routePopup.remove();
    routePopup = null;
  }

  // Calculate midpoint of route for popup position
  const coords = routeGeom.coords;
  if (!coords || coords.length === 0) return;

  const midIndex = Math.floor(coords.length / 2);
  const midCoord = coords[midIndex];

  // Get route stats
  const stats = currentRouteStats;
  const duration =
    stats.walkDurationMinutes !== null
      ? Math.round(stats.walkDurationMinutes)
      : null;
  const distance = stats.lengthKm !== null ? stats.lengthKm.toFixed(1) : null;

  // Create HTML content for popup - simple style like navigation apps with walking icon
  const popupContent = document.createElement("div");
  popupContent.className = "route-stats-popup";

  // Get walking icon path
  const walkingIconUrl = `${BASE}walking.svg`.replace(/\/{2,}/g, "/");

  let html = "";

  // First row: Icon and duration on same horizontal line (inline)
  html += '<div class="route-stats-popup-top-line">';
  html += `
    <span class="route-stats-popup-icon">
      <img src="${walkingIconUrl}" alt="Walking" width="20" height="20" />
    </span>
  `;
  if (duration !== null) {
    html += `<span class="route-stats-popup-duration" style="color: #000000 !important; font-weight: 800 !important; font-size: 22px !important;">${duration} min</span>`;
  }
  html += "</div>";

  // Second row: Distance below, aligned with duration text
  if (distance !== null) {
    html += `<div class="route-stats-popup-bottom-line">`;
    html += `<span class="route-stats-popup-distance" style="color: #000000 !important;">${distance} km</span>`;
    html += `</div>`;
  }

  popupContent.innerHTML = html;

  // Add click handler to open route details in sidebar
  popupContent.addEventListener("click", (e) => {
    e.stopPropagation();
    // Add visual feedback
    popupContent.classList.add("route-popup-clicked");
    setTimeout(() => {
      popupContent.classList.remove("route-popup-clicked");
    }, 200);
    emit("routePopupClicked");
  });
  popupContent.style.cursor = "pointer";

  // Add hover timer for auto-opening sidebar
  let hoverTimer = null;
  const HOVER_DELAY = 1500; // 1.5 seconds hover to auto-open

  popupContent.addEventListener("mouseenter", (e) => {
    e.stopPropagation();
    hoverTimer = setTimeout(() => {
      emit("routePopupClicked");
      hoverTimer = null;
    }, HOVER_DELAY);
  });

  popupContent.addEventListener("mouseleave", (e) => {
    e.stopPropagation();
    if (hoverTimer) {
      clearTimeout(hoverTimer);
      hoverTimer = null;
    }
  });

  // Calculate position closer to route - find a point on the route line
  // Use a point that's slightly offset from the midpoint to position the popup better
  const routePointIndex = Math.floor(coords.length * 0.4); // Use 40% along the route
  const routePoint = coords[routePointIndex];

  // Create and show popup with tip pointing to route
  routePopup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    className: "route-stats-map-popup",
    anchor: "bottom",
    offset: [0, -5], // Smaller offset so tip is closer to route
  })
    .setLngLat([routePoint[0], routePoint[1]])
    .setDOMContent(popupContent)
    .addTo(map);

  // Set initial visibility based on current zoom after popup is added
  setTimeout(() => {
    const currentZoom = map.getZoom();
    const popupElement = document.querySelector(".route-stats-map-popup");
    if (popupElement) {
      if (currentZoom >= 11) {
        popupElement.style.opacity = "1";
        popupElement.style.visibility = "visible";
        popupElement.style.pointerEvents = "auto";
        popupElement.style.transition =
          "opacity 0.4s ease, visibility 0.4s ease";
      } else {
        popupElement.style.opacity = "0";
        popupElement.style.visibility = "hidden";
        popupElement.style.pointerEvents = "none";
        popupElement.style.transition =
          "opacity 0.3s ease, visibility 0.3s ease";
      }
    }
  }, 50);

  // Set glassmorphism effect directly on the popup element
  setTimeout(() => {
    const popupContentEl = document.querySelector(
      ".route-stats-map-popup .mapboxgl-popup-content"
    );
    if (popupContentEl) {
      popupContentEl.style.background = "rgba(255, 255, 255, 0.25)";
      popupContentEl.style.backgroundColor = "rgba(255, 255, 255, 0.25)";
      popupContentEl.style.backdropFilter = "blur(20px) saturate(180%)";
      popupContentEl.style.webkitBackdropFilter = "blur(20px) saturate(180%)";
      popupContentEl.style.boxShadow = "0 8px 32px 0 rgba(0, 0, 0, 0.1)";
      popupContentEl.style.transition =
        "transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease, border-color 0.2s ease";

      // Add hover event listeners to manually change styles (since CSS hover might be overridden)
      popupContentEl.addEventListener("mouseenter", () => {
        popupContentEl.style.background = "rgba(255, 255, 255, 0.5)";
        popupContentEl.style.backgroundColor = "rgba(255, 255, 255, 0.5)";
        popupContentEl.style.borderColor = "rgba(255, 255, 255, 0.5)";
        popupContentEl.style.transform = "scale(1.08)";
        popupContentEl.style.boxShadow = "0 12px 40px 0 rgba(0, 0, 0, 0.2)";
      });

      popupContentEl.addEventListener("mouseleave", () => {
        popupContentEl.style.background = "rgba(255, 255, 255, 0.25)";
        popupContentEl.style.backgroundColor = "rgba(255, 255, 255, 0.25)";
        popupContentEl.style.borderColor = "rgba(255, 255, 255, 0.18)";
        popupContentEl.style.transform = "scale(1)";
        popupContentEl.style.boxShadow = "0 8px 32px 0 rgba(0, 0, 0, 0.1)";
      });
    }
    const popupTip = document.querySelector(
      ".route-stats-map-popup .mapboxgl-popup-tip"
    );
    if (popupTip) {
      popupTip.style.borderTopColor = "rgba(255, 255, 255, 0.25)";
      popupTip.style.borderTopWidth = "6px";
      popupTip.style.borderLeft = "6px solid transparent";
      popupTip.style.borderRight = "6px solid transparent";
      popupTip.style.borderBottom = "none";
      popupTip.style.width = "0";
      popupTip.style.height = "0";
      popupTip.style.display = "block";
      popupTip.style.visibility = "visible";
      popupTip.style.opacity = "1";
      popupTip.style.position = "relative";
      popupTip.style.zIndex = "1";
      popupTip.style.marginTop = "0";
      popupTip.style.marginLeft = "auto";
      popupTip.style.marginRight = "auto";
      popupTip.style.boxShadow = "0 2px 8px 0 rgba(0, 0, 0, 0.1)";
    }
  }, 10);
}

// Clear the displayed route
function clearRoute() {
  if (!map || !map.isStyleLoaded()) return;

  // Remove popup if exists
  if (routePopup) {
    routePopup.remove();
    routePopup = null;
  }

  // Clear stored data
  currentRouteStats = null;
  routePopupGeom = null;

  // Hide all route layers
  const routeLayers = ["route-line-glow", "route-line", "route-line-highlight"];
  routeLayers.forEach((layerId) => {
    if (map.getLayer(layerId)) {
      map.setLayoutProperty(layerId, "visibility", "none");
    }
  });

  if (map.getSource("route")) {
    map.getSource("route").setData({
      type: "FeatureCollection",
      features: [],
    });
  }

  currentRouteSource = null;
}

// Fetch locality names for hubs using reverse geocoding
async function fetchLocalityNamesForHubs() {
  if (!hubsData || !hubsData.features) return;

  const token = import.meta.env.VITE_MAPBOX_TOKEN;
  if (!token) {
    console.warn("Mapbox token not available, skipping locality name lookup");
    return;
  }

  // Process hubs in parallel with rate limiting
  const batchSize = 3; // Process 3 at a time to avoid rate limits
  for (let i = 0; i < hubsData.features.length; i += batchSize) {
    const batch = hubsData.features.slice(i, i + batchSize);

    await Promise.all(
      batch.map(async (feature) => {
        const [lng, lat] = feature.geometry.coordinates;

        try {
          // Use Mapbox reverse geocoding API
          const response = await fetch(
            `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?types=locality,neighborhood,place&access_token=${token}`
          );

          if (!response.ok) {
            console.warn(
              `Failed to fetch locality for hub ${feature.properties.id}`
            );
            return;
          }

          const data = await response.json();

          // Extract locality name (prefer locality, then neighborhood, then place)
          let localityName = null;
          if (data.features && data.features.length > 0) {
            // Look for locality first
            const locality = data.features.find(
              (f) => f.place_type && f.place_type.includes("locality")
            );
            if (locality) {
              localityName = locality.text || locality.properties?.name;
            } else {
              // Fall back to neighborhood
              const neighborhood = data.features.find(
                (f) => f.place_type && f.place_type.includes("neighborhood")
              );
              if (neighborhood) {
                localityName =
                  neighborhood.text || neighborhood.properties?.name;
              } else {
                // Fall back to place
                const place = data.features.find(
                  (f) => f.place_type && f.place_type.includes("place")
                );
                if (place) {
                  localityName = place.text || place.properties?.name;
                }
              }
            }
          }

          // Update feature properties with locality name
          if (localityName) {
            feature.properties.locality = localityName;
            feature.properties.neighborhood = localityName; // Also set as fallback
          }
        } catch (error) {
          console.warn(
            `Error fetching locality for hub ${feature.properties.id}:`,
            error
          );
        }
      })
    );

    // Small delay between batches to respect rate limits
    if (i + batchSize < hubsData.features.length) {
      await new Promise((resolve) => setTimeout(resolve, 200));
    }
  }

  // Update the map source with the new locality data
  // Wait for map to be ready if it's not yet
  const updateSource = () => {
    if (map && map.isStyleLoaded() && map.getSource("hubs")) {
      map.getSource("hubs").setData(hubsData);
      console.log("✅ Locality names fetched and updated for hubs");

      // Emit event to notify parent that hubs are ready
      emit("hubsUpdated");
    } else if (map) {
      // Map not ready yet, wait a bit and try again
      setTimeout(updateSource, 100);
    }
  };

  updateSource();
}

// Get current route lumo score
function getCurrentRouteLumoScore() {
  return currentRouteLumoScore;
}

// Expose methods for parent component
defineExpose({
  selectHubs: (hubId1, hubId2, loadRoute = true) => {
    console.log("selectHubs called", { hubId1, hubId2, loadRoute });
    // Convert to numbers for consistency
    const id1 = hubId1
      ? typeof hubId1 === "string"
        ? parseInt(hubId1, 10)
        : hubId1
      : null;
    const id2 = hubId2
      ? typeof hubId2 === "string"
        ? parseInt(hubId2, 10)
        : hubId2
      : null;

    console.log("Converted IDs", { id1, id2 });

    if (id1 && id2) {
      selectedHubId1 = id1;
      selectedHubId2 = id2;
      // Only load route if loadRoute is true (default true for backward compatibility)
      if (loadRoute) {
        console.log("Loading route between", id1, "and", id2);
        loadAndDisplayRoute(id1, id2);
      } else {
        // Just update colors without loading route
        console.log("Not loading route, just updating colors");
        clearRoute();
      }
      updateHubColors();
    } else if (id1) {
      selectedHubId1 = id1;
      selectedHubId2 = null;
      clearRoute();
      updateHubColors();
    } else {
      selectedHubId1 = null;
      selectedHubId2 = null;
      clearRoute();
      updateHubColors();
    }
  },
  getHubs: () => {
    if (!hubsData || !hubsData.features) {
      console.warn("getHubs: hubsData not available");
      return [];
    }
    const hubList = hubsData.features.map((feature) => {
      const id = feature.properties.id;
      // Use locality name if available, otherwise use a fallback
      const name =
        feature.properties.locality ||
        feature.properties.neighborhood ||
        `Hub ${id}`;
      return { id, name };
    });
    console.log("getHubs returning:", hubList);
    return hubList;
  },
  getCurrentRouteLumoScore: () => {
    return currentRouteLumoScore;
  },
  getCurrentRouteStats: () => {
    return currentRouteStats;
  },
  zoomIn,
  zoomOut,
  resetNorth,
  toggleTilt,
  getIsTilted: () => isTilted.value,
});

function requestZurichFocus(key) {
  if (!key) return;
  pendingZurichFocusKey = key;
  if (map && map.isStyleLoaded()) {
    performZurichFocus();
    pendingZurichFocusKey = 0;
  }
}

function performZurichFocus() {
  if (!map || !map.isStyleLoaded()) return;

  const zurichCenter = [8.55, 47.37];
  const startZoom = 11.5; // Higher zoom level - more zoomed in
  const endZoom = 14; // City level zoom

  // If triggered from button click, always zoom from current location
  if (props.fromButton) {
    const currentCenter = map.getCenter();
    const currentZoom = map.getZoom();

    // Calculate distance to determine animation duration
    const distance = Math.sqrt(
      Math.pow(currentCenter.lng - zurichCenter[0], 2) +
        Math.pow(currentCenter.lat - zurichCenter[1], 2)
    );

    // Adjust duration based on distance and zoom difference
    const zoomDiff = Math.abs(currentZoom - endZoom);
    const baseDuration = 3000;
    const distanceMultiplier = Math.min(distance * 500, 2000);
    const zoomMultiplier = zoomDiff * 100;
    const duration = Math.min(
      baseDuration + distanceMultiplier + zoomMultiplier,
      5000
    );

    // Smoothly fly from current position to Zurich
    map.flyTo({
      center: zurichCenter,
      zoom: endZoom,
      pitch: 45,
      bearing: -5,
      duration: duration,
      speed: 0.25,
      curve: 1.2,
      easing(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      },
      essential: true,
    });

    map.once("moveend", () => {
      emit("zurichZoomComplete");
    });
    return;
  }

  // Original behavior for walkthrough entry
  const currentZoom = map.getZoom();

  // If we're at global level, immediately jump to higher zoom level (no animation)
  // Then smoothly zoom in to city level
  if (currentZoom < 5) {
    // Jump immediately to higher zoom level with bird's eye view (pitch 0)
    map.jumpTo({
      center: zurichCenter,
      zoom: startZoom,
      pitch: 0, // Bird's eye view
      bearing: 0,
    });

    // Small delay to ensure jump is complete, then smoothly zoom to city
    setTimeout(() => {
      map.flyTo({
        center: zurichCenter,
        zoom: endZoom,
        pitch: 45,
        bearing: -5,
        duration: 4000,
        speed: 0.25,
        curve: 1.1,
        easing(t) {
          return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        },
        essential: true,
      });
      map.once("moveend", () => {
        emit("zurichZoomComplete");
      });
    }, 100);
  } else {
    // Already closer to zoom level, do smooth two-step animation
    map.flyTo({
      center: zurichCenter,
      zoom: startZoom,
      pitch: 0, // Bird's eye view
      bearing: 0,
      duration: 2000,
      speed: 0.4,
      curve: 1.2,
      easing(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
      },
      essential: true,
    });

    // Then zoom in to city level
    map.once("moveend", () => {
      map.flyTo({
        center: zurichCenter,
        zoom: endZoom,
        pitch: 45,
        bearing: -5,
        duration: 4000,
        speed: 0.25,
        curve: 1.1,
        easing(t) {
          return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        },
        essential: true,
      });
      map.once("moveend", () => {
        emit("zurichZoomComplete");
      });
    });
  }
}

onBeforeUnmount(() => {
  // Remove fullscreen event listeners
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
  document.removeEventListener(
    "webkitfullscreenchange",
    handleFullscreenChange
  );
  document.removeEventListener("msfullscreenchange", handleFullscreenChange);

  // Clear hover timers
  if (controlsHoverTimer) {
    clearTimeout(controlsHoverTimer);
  }
  if (controlsCloseTimer) {
    clearTimeout(controlsCloseTimer);
  }

  if (map) {
    map.remove();
    map = null;
  }
});
</script>

<style scoped>
.scene,
.map {
  position: fixed;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
}

/* Hide Mapbox watermark/attribution */
:deep(.mapboxgl-ctrl-attrib) {
  display: none !important;
}

:deep(.mapboxgl-ctrl-logo) {
  display: none !important;
}

/* Map Controls Bar - Sidebar Style */
.map-controls-bar {
  position: fixed;
  top: 20px;
  right: 20px; /* Aligned with route details popup */
  z-index: 15;
  background: #151517;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: row;
  gap: 8px;
  width: 380px; /* Same width as route details popup */
  height: 80px;
  min-width: 380px;
  max-width: 380px;
  box-sizing: border-box;
  transition:
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease;
  align-items: center;
  justify-content: center;
}

.map-controls-bar--collapsed {
  background: transparent;
  box-shadow: none;
  width: 80px;
  height: 80px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
  max-width: 80px;
  transition:
    width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease;
}

.map-controls-bar--collapsed:hover {
  background: transparent;
  box-shadow: none;
}

.map-controls-bar--collapsed .map-controls-toggle {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: rgba(28, 30, 33, 0.5);
  transition: background 0.15s ease;
}

.map-controls-bar--collapsed .map-controls-toggle:hover {
  background: #1c1e21;
}

.map-controls-bar--collapsed .map-controls-toggle svg {
  opacity: 1;
}

.map-controls-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  margin-bottom: 0;
  flex-shrink: 0;
  order: 2; /* Place toggle button after the controls */
}

.map-controls-toggle {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: #ffffff;
  border-radius: 6px;
  cursor: e-resize; /* Default: pointing right (will expand to the left) */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
  padding: 0;
  box-sizing: border-box;
  position: relative;
  /* Always fully visible, even when bar is collapsed */
  opacity: 1 !important;
  isolation: isolate;
}

.map-controls-toggle--will-close {
  cursor: w-resize; /* Pointing left (will collapse to the right) */
}

.map-controls-toggle:hover {
  background: #2a2f34;
}

.map-controls-toggle:active {
  background: #1c1e21;
}

.map-controls-toggle svg {
  color: #ffffff;
  stroke: #ffffff;
}

.map-controls-toggle-tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: #ffffff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0ms,
    visibility 0ms;
  z-index: 10000;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
}

.map-controls-toggle-tooltip::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: rgba(0, 0, 0, 0.9);
}

.map-controls-toggle:hover .map-controls-toggle-tooltip {
  opacity: 1;
  visibility: visible;
  transition:
    opacity 0ms,
    visibility 0ms;
}

.map-controls-toggle:hover {
  background: #2a2f34;
}

.map-controls-toggle:active {
  background: #1c1e21;
}

.map-controls-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 1;
  width: 100%;
  height: 100%;
  overflow: hidden;
  transform: translateX(0);
  transition:
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s,
    max-width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.map-controls-grid {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 100%;
}

.map-controls-bar--collapsed .map-controls-content {
  opacity: 0;
  max-width: 0;
  transform: translateX(-10px);
  pointer-events: none;
  transition:
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s,
    max-width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.map-controls-bar--collapsed .map-controls-header {
  margin-right: 0;
  margin-bottom: 0;
}

/* Map Control Buttons - Sidebar Style */
.map-control-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #1c1e21;
  color: #e6e6e8;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
  padding: 0;
  box-sizing: border-box;
}

.map-control-btn:hover {
  background: #2a2f34;
}

.map-control-btn:active {
  background: #1c1e21;
}

.map-control-btn.active {
  background: #2a2f34;
}

.map-control-btn svg {
  display: block;
  margin: 0 auto;
  color: #ffffff;
  stroke: #ffffff;
  fill: none;
  width: 18px;
  height: 18px;
}

.tilt-btn svg {
  stroke-width: 2.5;
}

.fullscreen-btn svg {
  width: 16px;
  height: 16px;
}

/* Route Stats Popup - Glassmorphism style */
.route-stats-map-popup .mapboxgl-popup-content {
  background: rgba(255, 255, 255, 0.25) !important;
  background-color: rgba(255, 255, 255, 0.25) !important;
  color: #000000 !important;
  padding: 5px 8px !important;
  border-radius: 6px !important;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  min-width: auto !important;
  max-width: none !important;
  width: auto !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
  opacity: 1 !important;
  cursor: pointer !important;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background-color 0.2s ease,
    border-color 0.2s ease !important;
}

.route-stats-map-popup .mapboxgl-popup-content:hover {
  transform: scale(1.08) !important;
  box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.2) !important;
  background-color: rgba(255, 255, 255, 0.5) !important;
  background: rgba(255, 255, 255, 0.5) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
}

.route-stats-map-popup .mapboxgl-popup-content.route-popup-clicked {
  transform: scale(0.95) !important;
  background-color: rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.25) !important;
}

.route-stats-map-popup .mapboxgl-popup-tip {
  border-top-color: rgba(255, 255, 255, 0.25) !important;
  border-top-width: 6px !important;
  border-left: 6px solid transparent !important;
  border-right: 6px solid transparent !important;
  border-bottom: none !important;
  width: 0 !important;
  height: 0 !important;
  margin-top: 0 !important;
  margin-left: auto !important;
  margin-right: auto !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: relative !important;
  z-index: 1 !important;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1) !important;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1)) !important;
}

/* Fade transitions for route popup - matching zurich time display */
.route-stats-map-popup {
  opacity: 0 !important;
  visibility: hidden !important;
  transition:
    opacity 0.4s ease,
    visibility 0.4s ease !important;
  pointer-events: none !important;
}

.route-stats-map-popup.route-stats-popup--visible {
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: auto !important;
}

.route-stats-map-popup.route-stats-popup--hidden {
  opacity: 0 !important;
  visibility: hidden !important;
  pointer-events: none !important;
  transition:
    opacity 0.3s ease,
    visibility 0.3s ease !important;
}

.route-stats-map-popup .mapboxgl-popup-content * {
  color: #000000 !important;
}

.route-stats-map-popup .mapboxgl-popup-tip {
  border-top-color: #ffffff !important;
}

.route-stats-popup {
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue",
    Arial, sans-serif !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000 !important;
}

.route-stats-popup,
.route-stats-popup *,
.route-stats-popup div,
.route-stats-popup span {
  color: #000000 !important;
}

.route-stats-popup-top-line {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  color: #000000 !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
  vertical-align: top !important;
}

.route-stats-popup-bottom-line {
  display: block !important;
  color: #000000 !important;
  line-height: 1.2 !important;
  margin-top: 1px !important;
  padding-left: 22px !important;
}

.route-stats-popup-icon {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  color: #000000 !important;
  flex-shrink: 0 !important;
  width: 20px !important;
  height: 20px !important;
  vertical-align: middle !important;
}

.route-stats-popup-icon svg {
  width: 20px !important;
  height: 20px !important;
  fill: #000000 !important;
  color: #000000 !important;
  display: block !important;
}

.route-stats-popup-icon img {
  width: 20px !important;
  height: 20px !important;
  display: block !important;
  object-fit: contain !important;
  filter: brightness(0) !important; /* Make icon black */
}

.route-stats-popup-text {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  line-height: 1.2 !important;
  color: #000000 !important;
}

.route-stats-popup-duration,
.route-stats-map-popup .route-stats-popup-duration,
.route-stats-popup .route-stats-popup-duration {
  font-size: 22px !important;
  font-weight: 800 !important;
  color: #000000 !important;
  line-height: 1.2 !important;
  margin: 0 !important;
  padding: 0 !important;
  display: inline !important;
  white-space: nowrap !important;
  vertical-align: middle !important;
}

.route-stats-popup-distance,
.route-stats-map-popup .route-stats-popup-distance,
.route-stats-popup .route-stats-popup-distance {
  font-size: 12px !important;
  font-weight: 400 !important;
  color: #000000 !important;
  line-height: 1.2 !important;
  margin: 0 !important;
  padding: 0 !important;
  display: inline !important;
  white-space: nowrap !important;
}
</style>

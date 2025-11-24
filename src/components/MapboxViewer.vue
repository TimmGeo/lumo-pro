<template>
  <div
    ref="sceneEl"
    class="scene"
    :class="{ 'controls-collapsed': controlsCollapsed }"
  >
    <div ref="mapEl" class="map"></div>
    <!-- Map Controls Bar -->
    <div
      class="map-controls-bar"
      :class="{ 'map-controls-bar--collapsed': controlsCollapsed }"
      @mouseenter="handleControlsBarMouseEnter"
      @mouseleave="handleControlsBarMouseLeave"
    >
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
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="3" y="8" width="18" height="2" rx="1" fill="currentColor"/>
            <circle cx="7" cy="9" r="2" fill="currentColor"/>
            <rect x="3" y="14" width="18" height="2" rx="1" fill="currentColor"/>
            <circle cx="17" cy="15" r="2" fill="currentColor"/>
          </svg>
          <!-- Chevron arrow only when expanded (to collapse) -->
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
            />
          </svg>
          <span class="map-controls-toggle-tooltip">
            {{ controlsCollapsed ? "Open Map Controls" : "Close Map Controls" }}
          </span>
        </button>
      </div>
      <div class="map-controls-content">
        <div class="map-controls-grid">
          <!-- Mapbox NavigationControl (zoom/rotation) will be positioned here -->
          <div class="mapbox-nav-control-wrapper"></div>
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
          <button
            class="map-control-btn fullscreen-btn"
            @click="toggleFullscreen"
            :class="{ active: isFullscreen }"
            aria-label="Toggle fullscreen"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                v-if="!isFullscreen"
                d="M8 3H5C3.89543 3 3 3.89543 3 5V8M21 8V5C21 3.89543 20.1046 3 19 3H16M16 21H19C20.1046 21 21 20.1046 21 19V16M3 16V19C3 20.1046 3.89543 21 5 21H8"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                v-else
                d="M8 3V8M8 21V16M16 3V8M16 21V16M3 8H8M16 8H21M3 16H8M16 16H21"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from "vue";
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

const emit = defineEmits(["zurichZoomComplete", "zoom", "move", "mapReady"]);

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

// Paths that work both locally and in deploy
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");
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
      emit("zoom", { zoom: map.getZoom(), center: map.getCenter() });
    });

    map.on("move", () => {
      emit("move", { zoom: map.getZoom(), center: map.getCenter() });
    });

    map.on("load", async () => {
      console.log("✅ Mapbox map loaded successfully!");

      // Add zoom and rotation controls to the map
      const navControl = new mapboxgl.NavigationControl();
      map.addControl(navControl);
      
      // Wait for map to be idle (tiles loaded) before emitting ready
      map.once("idle", () => {
        emit("mapReady");
      });

      // Move NavigationControl into the controls bar after a short delay
      nextTick(() => {
        setTimeout(() => {
          const navControlEl = document.querySelector(
            ".mapboxgl-ctrl-top-right"
          );
          const wrapperEl = document.querySelector(
            ".mapbox-nav-control-wrapper"
          );
          if (navControlEl && wrapperEl) {
            wrapperEl.appendChild(navControlEl);
          }
        }, 100);
      });

      // Emit initial zoom/center
      emit("zoom", { zoom: map.getZoom(), center: map.getCenter() });

      try {
        // --- Load and add Routing Hubs (points) ---
        const hubsResponse = await fetch(hubsUrl);
        hubsData = await hubsResponse.json();

        map.addSource("hubs", {
          type: "geojson",
          data: hubsData,
        });

        // Add circles for hubs (matching Cesium styling)
        map.addLayer({
          id: "hubs-circles",
          type: "circle",
          source: "hubs",
          paint: {
            "circle-radius": 6,
            "circle-color": "#70f0c3",
            "circle-stroke-color": "#0b0b0c",
            "circle-stroke-width": 0,
            "circle-opacity": 1,
          },
        });

        // Add labels for hubs (matching Cesium styling)
        map.addLayer({
          id: "hubs-labels",
          type: "symbol",
          source: "hubs",
          minzoom: 15, // Only show labels at very high zoom level
          layout: {
            "text-field": ["get", "CHSTNAME"],
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

          // Create combined layer: vibrancy 3D hexagons with lighting colors
          // Create a color lookup map from lighting data
          const colorLookup = new Map();
          if (hexData && hexData.features) {
            hexData.features.forEach((feature) => {
              if (feature.properties && feature.properties.id) {
                colorLookup.set(
                  feature.properties.id,
                  feature.properties.color || "#969696"
                );
              }
            });
          }

          // Merge vibrancy geometry with lighting colors
          const combinedData = {
            type: "FeatureCollection",
            features: hexVibrancyData.features.map((feature) => {
              const color = colorLookup.get(feature.properties.id) || "#969696";
              return {
                ...feature,
                properties: {
                  ...feature.properties,
                  lightingColor: color,
                },
              };
            }),
          };

          map.addSource("hex-combined", {
            type: "geojson",
            data: combinedData,
          });

          // Add 3D extruded hexagon layer for combined (vibrancy height + lighting color)
          map.addLayer({
            id: "hex-combined-layer",
            type: "fill-extrusion",
            source: "hex-combined",
            filter: [">", ["get", "NUMPOINTS"], 0], // Only show hexagons with NUMPOINTS > 0
            paint: {
              "fill-extrusion-color": [
                "coalesce",
                ["get", "lightingColor"],
                "#969696",
              ],
              "fill-extrusion-opacity": 0.7,
              "fill-extrusion-height": [
                "*",
                ["get", "NUMPOINTS"],
                150, // Scale factor - extremely high for dramatic skyscraper effect
              ],
              "fill-extrusion-base": 0,
            },
          });

          // Initial visibility - only show combined layer when combined layer is selected
          map.setLayoutProperty(
            "hex-combined-layer",
            "visibility",
            props.combinedVisible ? "visible" : "none"
          );
        } catch (error) {
          console.error("Failed to load vibrancy GeoJSON data:", error);
        }

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
          updateLayerVisibility("hex-combined-layer", false);
          updateLayerVisibility("vibrancy-points-layer", false);
        }
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
          updateLayerVisibility("hex-combined-layer", false);
        }
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

        // Show/hide 3D combined layer when combined layer is selected
        updateLayerVisibility("hex-combined-layer", isVisible);

        // Ensure other layers are hidden when combined is selected
        if (isVisible) {
          updateLayerVisibility("hex-layer", false);
          updateLayerVisibility("hex-vibrancy-layer", false);
          updateLayerVisibility("vibrancy-points-layer", false);
        }
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
  if (map.getLayer("hubs-labels")) {
    map.moveLayer("hubs-labels");
  }
  if (map.getLayer("hubs-circles")) {
    map.moveLayer("hubs-circles");
  }
}

function setHubsVisibility(visible) {
  if (!map || !map.isStyleLoaded()) return;
  const visibility = visible ? "visible" : "none";
  map.setLayoutProperty("hubs-circles", "visibility", visibility);
  map.setLayoutProperty("hubs-labels", "visibility", visibility);
  if (visible) {
    ensureHubsOnTop();
  }
}

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
    const duration = Math.min(baseDuration + distanceMultiplier + zoomMultiplier, 5000);
    
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

/* Position Mapbox NavigationControl inside the controls bar */
:deep(.mapboxgl-ctrl-top-right) {
  position: relative !important;
  top: auto !important;
  bottom: auto !important;
  right: auto !important;
  left: auto !important;
  margin: 0 !important;
}

.mapbox-nav-control-wrapper {
  display: contents; /* Make it part of the grid */
}

/* Style Mapbox NavigationControl buttons to fit in grid */
:deep(.mapboxgl-ctrl-top-right) {
  display: contents !important; /* Make the container part of the grid */
}

:deep(.mapboxgl-ctrl-top-right .mapboxgl-ctrl-group) {
  display: contents !important; /* Make the group part of the grid */
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

:deep(.mapboxgl-ctrl-top-right button) {
  width: 40px !important;
  height: 40px !important;
  background: #1c1e21 !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 6px !important;
  margin: 0 !important;
  transition: background 0.15s ease !important;
}

:deep(.mapboxgl-ctrl-top-right button:hover) {
  background: #2a2f34 !important;
}

:deep(.mapboxgl-ctrl-top-right button:active) {
  background: #1c1e21 !important;
}

/* Make NavigationControl icons white */
:deep(.mapboxgl-ctrl-top-right button svg) {
  fill: #ffffff !important;
}

:deep(.mapboxgl-ctrl-top-right button path) {
  fill: #ffffff !important;
  stroke: #ffffff !important;
}

:deep(.mapboxgl-ctrl-top-right .mapboxgl-ctrl-group) {
  margin: 0 !important;
  box-shadow: 0 0 0 0 rgba(0, 0, 0, 0) !important;
}

:deep(.mapboxgl-ctrl-top-right button) {
  margin: 0 !important;
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
  top: 100px;
  right: 20px;
  z-index: 15;
  background: #151517;
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 56px;
  min-height: 56px;
  box-sizing: border-box;
  transition:
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease;
}

.map-controls-bar--collapsed {
  background: transparent;
  box-shadow: none;
  width: 56px;
  height: 56px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 56px;
  transition:
    height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    padding 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    background 0.3s ease,
    box-shadow 0.3s ease;
}

.map-controls-bar--collapsed:hover {
  background: transparent;
  box-shadow: none;
}

.map-controls-bar--collapsed .map-controls-toggle {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: rgba(28, 30, 33, 0.3);
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
  margin-bottom: 8px;
  margin-right: 0;
}

.map-controls-toggle {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: #ffffff;
  border-radius: 6px;
  cursor: s-resize; /* Default: pointing down (will expand downward) */
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
  cursor: n-resize; /* Pointing up (will collapse upward) */
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
  top: 50%;
  right: calc(100% + 8px);
  transform: translateY(-50%);
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
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 1;
  max-height: 500px;
  overflow: hidden;
  transform: translateY(0);
  transition:
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s,
    max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.map-controls-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.map-controls-bar--collapsed .map-controls-content {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
  pointer-events: none;
  transition:
    opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s,
    max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.map-controls-bar--collapsed .map-controls-header {
  margin-right: 0;
  margin-bottom: 0;
}

/* Map Control Buttons - Sidebar Style */
.map-control-btn {
  width: 40px;
  height: 40px;
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
}

.tilt-btn svg {
  stroke-width: 2.5;
}

.fullscreen-btn svg {
  width: 16px;
  height: 16px;
}
</style>

<template>
  <div ref="sceneEl" class="scene">
    <div ref="mapEl" class="map"></div>
    <button
      class="fullscreen-btn"
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
});

const emit = defineEmits(["zurichZoomComplete", "zoom", "move"]);

const sceneEl = ref(null);
const mapEl = ref(null);
const isFullscreen = ref(false);
let map = null;
let hubsData = null;
let hexData = null;
let hexVibrancyData = null;
let hubsLoaded = false;
let pendingZurichFocusKey = 0;

// Paths that work both locally and in deploy
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");
const hexUrl = `${BASE}data/hex_light_100m.geojson`.replace(/\/{2,}/g, "/");
const hexVibrancyUrl = `${BASE}data/hex_vibrancy_100m.geojson`.replace(/\/{2,}/g, "/");

// NavigationControl handles zoom and rotation

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
      map.addControl(new mapboxgl.NavigationControl());
      
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
              "fill-extrusion-opacity": 0.4,
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
              const color =
                colorLookup.get(feature.properties.id) || "#969696";
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
        updateLayerVisibility("hex-vibrancy-layer", isVisible);
        
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
  map.flyTo({
    center: [8.55, 47.37],
    zoom: 12.4,
    pitch: 45,
    bearing: -5,
    duration: 5200,
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
}

onBeforeUnmount(() => {
  // Remove fullscreen event listeners
  document.removeEventListener("fullscreenchange", handleFullscreenChange);
  document.removeEventListener(
    "webkitfullscreenchange",
    handleFullscreenChange
  );
  document.removeEventListener("msfullscreenchange", handleFullscreenChange);

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

/* Position Mapbox NavigationControl in bottom right, above scale */
:deep(.mapboxgl-ctrl-top-right) {
  top: auto !important;
  bottom: 120px !important;
  right: 20px !important;
  left: auto !important;
  margin: 0 !important;
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

/* Fullscreen button */
.fullscreen-btn {
  position: fixed;
  bottom: 220px;
  right: 20px;
  width: 29px;
  height: 29px;
  min-width: 29px;
  min-height: 29px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 15;
  transition: background 0.15s ease;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(10px);
  box-sizing: border-box;
  padding: 0;
}

.fullscreen-btn:hover {
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.fullscreen-btn:active {
  background: rgba(245, 245, 245, 1);
}

.fullscreen-btn.active {
  background: rgba(240, 240, 240, 1);
}

.fullscreen-btn svg {
  width: 16px;
  height: 16px;
  display: block;
  margin: 0 auto;
}
</style>

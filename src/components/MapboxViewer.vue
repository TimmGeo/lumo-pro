<template>
  <div ref="sceneEl" class="scene">
    <div ref="mapEl" class="map"></div>

    <!-- Zoom controls -->
    <div class="zoom-controls">
      <button class="zoom-btn" @click="zoomIn" aria-label="Zoom in">
        <span class="zoom-icon">+</span>
      </button>
      <button class="zoom-btn" @click="zoomOut" aria-label="Zoom out">
        <span class="zoom-icon">−</span>
      </button>
      <button
        class="zoom-btn"
        @click="toggleFullscreen"
        aria-label="Toggle fullscreen"
      >
        <span class="zoom-icon">{{ isFullscreen ? "✕" : "⛶" }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from "vue";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

const props = defineProps({
  mode: {
    type: String,
    default: "combined",
  },
  heightScale: {
    type: Number,
    default: 1.5,
  },
});

const sceneEl = ref(null);
const mapEl = ref(null);
const isFullscreen = ref(false);
let map = null;
let hubsData = null;
let hexData = null;

// Paths that work both locally and in deploy
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");
const hexUrl = `${BASE}data/hex_kreis_light_300m.geojson`.replace(
  /\/{2,}/g,
  "/"
);

// Zoom functions
function zoomIn() {
  if (map) {
    map.zoomIn({ duration: 300 });
  }
}

function zoomOut() {
  if (map) {
    map.zoomOut({ duration: 300 });
  }
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
      center: [8.55, 47.37], // Zürich
      zoom: 12,
      pitch: 0,
      bearing: 0,
    });

    map.on("load", async () => {
      console.log("✅ Mapbox map loaded successfully!");

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

        // Initial visibility based on mode
        map.setLayoutProperty(
          "hex-layer",
          "visibility",
          props.mode === "lighting" ? "visible" : "none"
        );

        // Zoom to hex bounds
        if (hexData.features.length > 0) {
          const bounds = new mapboxgl.LngLatBounds();
          hexData.features.forEach((feature) => {
            if (feature.geometry.type === "Polygon") {
              feature.geometry.coordinates[0].forEach((coord) => {
                bounds.extend(coord);
              });
            }
          });
          map.fitBounds(bounds, {
            padding: 50,
            duration: 1000,
          });
        }

        // Debug
        window.map = map;
        console.log("Loaded:", {
          hubs: hubsData.features.length,
          hex: hexData.features.length,
        });
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

// React to sidebar mode changes
watch(
  () => props.mode,
  (newMode) => {
    if (!map || !map.isStyleLoaded()) return;

    // Show/hide hex layer based on mode
    map.setLayoutProperty(
      "hex-layer",
      "visibility",
      newMode === "lighting" ? "visible" : "none"
    );
  }
);

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

/* Zoom controls - positioned on the right side */
.zoom-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.zoom-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #151517;
  border: 1px solid #202124;
  color: #eaeaea;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.zoom-btn:hover {
  background: #1c1e21;
  border-color: #2a2f34;
}

.zoom-btn:active {
  background: #0f1011;
  transform: scale(0.95);
}

.zoom-icon {
  font-size: 24px;
  font-weight: 300;
  line-height: 1;
  user-select: none;
}
</style>

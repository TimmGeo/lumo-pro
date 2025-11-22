<template>
  <div ref="sceneEl" class="scene">
    <div ref="mapEl" class="map"></div>

    <!-- Fullscreen control -->
    <button
      class="fullscreen-btn"
      @click="toggleFullscreen"
      aria-label="Toggle fullscreen"
    >
      {{ isFullscreen ? "✕" : "⛶" }}
    </button>
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
let hubsLoaded = false;
let pendingZurichFocusKey = 0;

// Paths that work both locally and in deploy
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");
const hexUrl = `${BASE}data/hex_light_100m.geojson`.replace(/\/{2,}/g, "/");

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

        // Initial visibility based on mode
        map.setLayoutProperty(
          "hex-layer",
          "visibility",
          props.mode === "lighting" ? "visible" : "none"
        );
        setHubsVisibility(props.showHubs);
        hubsLoaded = true;

        // Debug
        window.map = map;
        console.log("Loaded:", {
          hubs: hubsData.features.length,
          hex: hexData.features.length,
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

/* Position Mapbox NavigationControl lower to avoid routing bar */
:deep(.mapboxgl-ctrl-top-right) {
  top: 100px !important;
  right: 20px;
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
  position: absolute;
  right: 20px;
  top: 200px;
  width: 29px;
  height: 29px;
  border: none;
  background: #ffffff;
  color: #333;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
  transition: background 0.15s ease;
  z-index: 15;
}

.fullscreen-btn:hover {
  background: #f5f5f5;
}

.fullscreen-btn:active {
  background: #eeeeee;
}
</style>

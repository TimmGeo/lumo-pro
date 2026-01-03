<template>
  <div
    ref="sceneEl"
    class="scene"
    :class="{ 'controls-collapsed': controlsCollapsed }"
  >
    <!-- Loading Screen -->
    <transition name="loading-fade">
      <div v-if="!isMapReady" class="loading-screen">
        <div class="loading-content">
          <h1 class="loading-logo">Lumo</h1>
          <div class="loading-dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </transition>
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

// Add loading class immediately to prevent flash of normal styles
if (typeof document !== "undefined") {
  document.body.classList.add("map-loading");
}

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
  "hubsSelected",
  "polygonClicked",
  "mapClicked",
]);

const sceneEl = ref(null);
const mapEl = ref(null);
const isFullscreen = ref(false);
const isTilted = ref(false);
const controlsCollapsed = ref(false);
const isHoveringControls = ref(false);
const isMapReady = ref(false);
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
let initialMapZoom = 12; // Store initial zoom level for reuse

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
// Separate stats and popups for fast and bright routes
let fastRouteStats = null;
let brightRouteStats = null;
let fastRoutePopup = null;
let brightRoutePopup = null;
let fastRouteGeom = null;
let brightRouteGeom = null;

// Animation state
let routeAnimationActive = false;
let originalHexFilter = null;
let intersectionData = null;
let hexagonMedian = null; // Store median score for coloring

// Route security alerts state
let routeSecurityAlertsActive = false;
let routeSecurityAlertsData = null;

// Apply security alerts to routes by creating red segments for unsafe parts
async function applyRouteSecurityAlerts() {
  if (!map || !map.isStyleLoaded() || !routeSecurityAlertsData) {
    return;
  }

  const beforeLayer = map.getLayer("hubs-circles") ? "hubs-circles" : undefined;

  // Process fast route
  if (
    routeSecurityAlertsData.fast &&
    routeSecurityAlertsData.fast.unsafe_segments.length > 0
  ) {
    await createUnsafeRouteSegments(
      "route-fast",
      "fast",
      routeSecurityAlertsData.fast.unsafe_segments,
      beforeLayer
    );
  }

  // Process bright route
  if (
    routeSecurityAlertsData.bright &&
    routeSecurityAlertsData.bright.unsafe_segments.length > 0
  ) {
    await createUnsafeRouteSegments(
      "route-bright",
      "bright",
      routeSecurityAlertsData.bright.unsafe_segments,
      beforeLayer
    );
  }
}

// Create unsafe route segments as red overlays
async function createUnsafeRouteSegments(
  sourceId,
  routeType,
  unsafeSegmentIndices,
  beforeLayer
) {
  const source = map.getSource(sourceId);
  if (
    !source ||
    !source._data ||
    !source._data.features ||
    source._data.features.length === 0
  ) {
    return;
  }

  const routeFeature = source._data.features[0];
  const routeCoords = routeFeature.geometry.coordinates;

  if (!routeCoords || routeCoords.length < 2) {
    return;
  }

  // Create LineString segments for unsafe parts
  // Create a segment for EVERY unsafe index to ensure complete coverage
  const unsafeSegments = [];
  const processedIndices = new Set();

  // Sort indices for processing
  const sortedIndices = [...unsafeSegmentIndices]
    .filter((idx) => idx >= 0 && idx < routeCoords.length - 1)
    .sort((a, b) => a - b);

  if (sortedIndices.length === 0) {
    return;
  }

  // First, create continuous segments for consecutive indices (more efficient)
  let rangeStart = sortedIndices[0];
  let rangeEnd = sortedIndices[0];

  for (let i = 1; i < sortedIndices.length; i++) {
    const currentIdx = sortedIndices[i];

    // If indices are consecutive or very close (within 2), extend the range
    if (currentIdx <= rangeEnd + 2) {
      rangeEnd = currentIdx;
    } else {
      // Create continuous segment for the completed range
      const startIdx = Math.max(0, rangeStart);
      const endIdx = Math.min(routeCoords.length - 1, rangeEnd + 1);

      if (startIdx < endIdx) {
        const segmentCoords = routeCoords.slice(startIdx, endIdx + 1);
        unsafeSegments.push({
          type: "Feature",
          geometry: {
            type: "LineString",
            coordinates: segmentCoords,
          },
          properties: {
            route_type: routeType,
            is_unsafe: true,
          },
        });

        // Mark all indices in this range as processed
        for (let j = rangeStart; j <= rangeEnd; j++) {
          processedIndices.add(j);
        }
      }

      // Start new range
      rangeStart = currentIdx;
      rangeEnd = currentIdx;
    }
  }

  // Add the final range
  const startIdx = Math.max(0, rangeStart);
  const endIdx = Math.min(routeCoords.length - 1, rangeEnd + 1);

  if (startIdx < endIdx) {
    const segmentCoords = routeCoords.slice(startIdx, endIdx + 1);
    unsafeSegments.push({
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: segmentCoords,
      },
      properties: {
        route_type: routeType,
        is_unsafe: true,
      },
    });

    // Mark all indices in this range as processed
    for (let j = rangeStart; j <= rangeEnd; j++) {
      processedIndices.add(j);
    }
  }

  // Ensure ALL unsafe indices have segments (add individual segments for any missed)
  sortedIndices.forEach((segmentIndex) => {
    if (
      !processedIndices.has(segmentIndex) &&
      segmentIndex < routeCoords.length - 1
    ) {
      unsafeSegments.push({
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: [
            routeCoords[segmentIndex],
            routeCoords[segmentIndex + 1],
          ],
        },
        properties: {
          route_type: routeType,
          is_unsafe: true,
        },
      });
    }
  });

  if (unsafeSegments.length === 0) {
    return;
  }

  const unsafeSourceId = `${sourceId}-unsafe`;
  const unsafeData = {
    type: "FeatureCollection",
    features: unsafeSegments,
  };

  // Add or update source
  if (map.getSource(unsafeSourceId)) {
    map.getSource(unsafeSourceId).setData(unsafeData);
  } else {
    map.addSource(unsafeSourceId, {
      type: "geojson",
      data: unsafeData,
    });
  }

  // Add red overlay layers for unsafe segments
  const unsafeLayerIds = [`${unsafeSourceId}-glow`, `${unsafeSourceId}-line`];

  // Red glow layer
  if (!map.getLayer(unsafeLayerIds[0])) {
    map.addLayer(
      {
        id: unsafeLayerIds[0],
        type: "line",
        source: unsafeSourceId,
        paint: {
          "line-color": "#ff0000",
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
          "line-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            11.4,
            0,
            11.5,
            0.4,
          ],
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

  // Red main line
  if (!map.getLayer(unsafeLayerIds[1])) {
    map.addLayer(
      {
        id: unsafeLayerIds[1],
        type: "line",
        source: unsafeSourceId,
        paint: {
          "line-color": "#ff4444",
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
          "line-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            11.4,
            0,
            11.5,
            1,
          ],
        },
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
      },
      beforeLayer
    );
  }

  // Ensure layers are visible
  unsafeLayerIds.forEach((layerId) => {
    if (map.getLayer(layerId)) {
      map.setLayoutProperty(layerId, "visibility", "visible");
    }
  });
}

// Remove security alert layers
function removeRouteSecurityAlerts() {
  if (!map || !map.isStyleLoaded()) {
    return;
  }

  ["route-fast-unsafe", "route-bright-unsafe"].forEach((sourceId) => {
    // Remove layers
    ["glow", "line"].forEach((suffix) => {
      const layerId = `${sourceId}-${suffix}`;
      if (map.getLayer(layerId)) {
        map.removeLayer(layerId);
      }
    });

    // Remove source
    if (map.getSource(sourceId)) {
      map.removeSource(sourceId);
    }
  });
}

// Update layer coloring based on mode
function updateLayerColoring(layerId, coloringMode) {
  if (!map) {
    console.warn(`Cannot update layer ${layerId}: map not available`);
    return;
  }

  // Check if layer exists and map is ready
  if (!map.getLayer(layerId)) {
    console.warn(`Layer ${layerId} does not exist`);
    return;
  }

  // More lenient check - try to update even if map is not fully loaded
  // During animations, the style might be in transition, but layers can still be updated
  if (!map.loaded() && !map.isStyleLoaded()) {
    console.warn(
      `Map not fully loaded, but attempting to update ${layerId} anyway`
    );
    // Don't return - try anyway as the layer might still be updatable
  }

  // Get layer (already checked above, but double-check)
  const layer = map.getLayer(layerId);
  if (!layer) {
    console.warn(`Layer ${layerId} not found`);
    return;
  }

  // Determine color property based on layer type
  let colorProperty;
  if (layer.type === "fill-extrusion") {
    colorProperty = "fill-extrusion-color";
  } else if (layer.type === "fill") {
    colorProperty = "fill-color";
  } else {
    console.warn(`Unknown layer type "${layer.type}" for layer ${layerId}`);
    return;
  }

  console.log(
    `Updating ${layerId} (type: ${layer.type}) with ${coloringMode} mode, property: ${colorProperty}`
  );

  if (coloringMode === "median") {
    // Median-based coloring: green for above median, red for below
    if (!hexagonMedian && hexagonMedian !== 0) {
      console.warn("Hexagon median not loaded, cannot apply median coloring");
      return;
    }

    // Ensure median is a number
    const medianValue =
      typeof hexagonMedian === "number"
        ? hexagonMedian
        : parseFloat(hexagonMedian);
    if (isNaN(medianValue)) {
      console.error(`Invalid median value: ${hexagonMedian}`);
      return;
    }

    console.log(`Applying median coloring with median value: ${medianValue}`);
    console.log(`Layer ID: ${layerId}, Color property: ${colorProperty}`);

    const colorExpression = [
      "case",
      [">", ["get", "combined_score"], medianValue],
      "#22c55e", // Green - above median
      "#ef4444", // Red - below median
    ];

    console.log("Color expression:", JSON.stringify(colorExpression));

    try {
      map.setPaintProperty(layerId, colorProperty, colorExpression);
      console.log(`✓ Successfully updated ${layerId} with median coloring`);

      // Verify the update worked
      const updatedValue = map.getPaintProperty(layerId, colorProperty);
      console.log(`Verified paint property value:`, updatedValue);
    } catch (error) {
      console.error(`✗ Error updating ${layerId} paint property:`, error);
      console.error("Error details:", error.message);
      if (error.stack) {
        console.error("Stack trace:", error.stack);
      }
      // Re-throw to help with debugging
      throw error;
    }
  } else {
    // Route-based coloring: blue for bright, orange for fast
    console.log("Applying route-based coloring");
    console.log(`Layer ID: ${layerId}, Color property: ${colorProperty}`);

    const colorExpression = [
      "case",
      ["has", "route_type"],
      [
        "match",
        ["get", "route_type"],
        "bright",
        "#64b4ff", // Blue for bright route
        "fast",
        "#888888", // Grey for fast route
        "both",
        "#8b5cf6", // Purple for both routes
        "#6c5ce7", // Default purple-blue
      ],
      "#6c5ce7", // Default if no route_type
    ];

    console.log("Color expression:", JSON.stringify(colorExpression));

    try {
      map.setPaintProperty(layerId, colorProperty, colorExpression);
      console.log(`✓ Successfully updated ${layerId} with route coloring`);

      // Verify the update worked
      const updatedValue = map.getPaintProperty(layerId, colorProperty);
      console.log(`Verified paint property value:`, updatedValue);
    } catch (error) {
      console.error(`✗ Error updating ${layerId} paint property:`, error);
      console.error("Error details:", error.message);
      if (error.stack) {
        console.error("Stack trace:", error.stack);
      }
    }
  }
}

async function animateHexagonsReveal(
  hexIds,
  intersectionData,
  coloringMode = "route"
) {
  if (!map || !map.isStyleLoaded() || !hexIds || hexIds.length === 0) {
    return;
  }

  // Get the hex-combined source to extract hexagon features
  const hexCombinedSource = map.getSource("hex-combined");
  if (!hexCombinedSource) {
    console.warn("hex-combined source not found");
    return;
  }

  // Get the hexagon data
  const hexData = hexCombinedSource._data;
  if (!hexData || !hexData.features) {
    console.warn("hex-combined data not available");
    return;
  }

  // Create Sets for fast lookup
  const hexIdSet = new Set(hexIds);
  const fastHexIds = new Set(intersectionData?.fast_hex_ids || []);
  const brightHexIds = new Set(intersectionData?.bright_hex_ids || []);

  // Extract features that match the hexagon IDs and add route information
  const intersectingFeatures = hexData.features
    .filter((feature) => {
      const hexId = feature.properties?.id || feature.properties?.fid;
      return hexIdSet.has(hexId);
    })
    .map((feature) => {
      // Create a copy of the feature to avoid mutating the original
      const hexId = feature.properties?.id || feature.properties?.fid;
      const isFast = fastHexIds.has(hexId);
      const isBright = brightHexIds.has(hexId);

      // Determine route type
      let routeType = null;
      if (isFast && isBright) {
        routeType = "both";
      } else if (isBright) {
        routeType = "bright";
      } else if (isFast) {
        routeType = "fast";
      }

      return {
        ...feature,
        properties: {
          ...feature.properties,
          route_type: routeType,
          animation_height: 0, // Start with 0 height
        },
      };
    });

  console.log(
    `Found ${intersectingFeatures.length} hexagon features out of ${hexIds.length} IDs`
  );

  // Get the animation source
  const animationSource = map.getSource("hex-route-animation");
  if (!animationSource) {
    console.warn("hex-route-animation source not found");
    return;
  }

  // Show animation layers only if zoom is sufficient (same threshold as route buttons: 11.5)
  const currentZoom = map.getZoom();
  const zoomThreshold = 11.5;
  const visibility = currentZoom >= zoomThreshold ? "visible" : "none";

  if (map.getLayer("hex-route-animation-fill")) {
    map.setLayoutProperty("hex-route-animation-fill", "visibility", visibility);
  }
  if (map.getLayer("hex-route-animation-layer")) {
    map.setLayoutProperty(
      "hex-route-animation-layer",
      "visibility",
      visibility
    );
  }

  // Apply coloring mode immediately before animation starts
  if (map.getLayer("hex-route-animation-fill")) {
    updateLayerColoring("hex-route-animation-fill", coloringMode);
  }
  if (map.getLayer("hex-route-animation-layer")) {
    updateLayerColoring("hex-route-animation-layer", coloringMode);
  }

  // First, add all hexagons with height 0
  const initialData = {
    type: "FeatureCollection",
    features: intersectingFeatures.map((f) => ({
      ...f,
      properties: { ...f.properties, animation_height: 0 },
    })),
  };
  animationSource.setData(initialData);

  // Wait a moment for the initial data to render
  await new Promise((resolve) => setTimeout(resolve, 100));

  // Animate height growth from 0 to 1 with smooth easing
  const animationDuration = 2000; // Total duration in ms
  const startTime = Date.now();

  // Use requestAnimationFrame for smoother animation
  const animate = () => {
    const currentTime = Date.now();
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / animationDuration, 1); // 0 to 1

    // Apply ease-out cubic easing for smooth deceleration
    // Easing function: 1 - (1 - t)^3
    const easedProgress = 1 - Math.pow(1 - progress, 3);

    // Update all features with new height
    const animatedFeatures = intersectingFeatures.map((feature) => ({
      ...feature,
      properties: {
        ...feature.properties,
        animation_height: easedProgress,
      },
    }));

    const animatedData = {
      type: "FeatureCollection",
      features: animatedFeatures,
    };

    animationSource.setData(animatedData);

    // Continue animation if not complete
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };

  // Start animation
  requestAnimationFrame(animate);

  // Wait for animation to complete
  await new Promise((resolve) => setTimeout(resolve, animationDuration + 50));

  // Colors are already applied at the start, but ensure they're still correct after animation
  // (in case something changed during animation)
  if (map.getLayer("hex-route-animation-fill")) {
    updateLayerColoring("hex-route-animation-fill", coloringMode);
  }
  if (map.getLayer("hex-route-animation-layer")) {
    updateLayerColoring("hex-route-animation-layer", coloringMode);
  }

  console.log(
    `Hexagon animation complete - showing ${intersectingFeatures.length} hexagons with height animation (${coloringMode} mode)`
  );
}

// Paths that work both locally and in deploy
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_HUBS/routing_HUBS.geojson`.replace(
  /\/{2,}/g,
  "/"
);
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
  // Loading class already added at component creation

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

    // Load hubs data first to calculate the center and reuse the data
    let initialCenter = [8.55, 47.37]; // Default Zurich center
    let initialZoom = 12;
    initialMapZoom = 12; // Initialize stored zoom value

    try {
      const hubsResponse = await fetch(hubsUrl);
      hubsData = await hubsResponse.json(); // Store for later use

      if (hubsData && hubsData.features && hubsData.features.length > 0) {
        // Calculate bounds from all hub coordinates
        const bounds = new mapboxgl.LngLatBounds();
        hubsData.features.forEach((feature) => {
          // Skip clusters
          if (feature.properties && feature.properties.point_count) {
            return;
          }
          if (feature.geometry && feature.geometry.type === "Point") {
            const [lon, lat] = feature.geometry.coordinates;
            bounds.extend([lon, lat]);
          }
        });

        if (!bounds.isEmpty()) {
          const ne = bounds.getNorthEast();
          const sw = bounds.getSouthWest();

          // Calculate center
          initialCenter = [(ne.lng + sw.lng) / 2, (ne.lat + sw.lat) / 2];

          // Calculate zoom level manually
          const padding = 80;
          const mapWidth = mapEl.value.clientWidth || 1920;
          const mapHeight = mapEl.value.clientHeight || 1080;

          const latDiff = ne.lat - sw.lat;
          const lngDiff = ne.lng - sw.lng;

          const latZoom = Math.log2(
            360 / ((latDiff * (mapHeight - padding * 2)) / 256)
          );
          const lngZoom = Math.log2(
            360 / ((lngDiff * (mapWidth - padding * 2)) / 256)
          );

          initialZoom = Math.min(Math.min(latZoom, lngZoom), 15);
          initialZoom = Math.max(initialZoom, 12);
          initialMapZoom = initialZoom; // Store the calculated zoom level
        }
      }
    } catch (error) {
      console.warn(
        "Failed to load hubs for initial center calculation, using default:",
        error
      );
    }

    map = new mapboxgl.Map({
      container: mapEl.value,
      style: "mapbox://styles/mapbox/dark-v11",
      center: initialCenter, // Center calculated from hubs
      zoom: initialZoom, // Zoom calculated from hubs
      pitch: 45,
      bearing: -5,
      attributionControl: false,
    });

    // Emit zoom and move events for scale calculation
    map.on("zoom", () => {
      const zoom = map.getZoom();
      emit("zoom", { zoom: zoom, center: map.getCenter() });

      // Show/hide route popup based on zoom (same condition as zurich time display)
      handleRoutePopupVisibility(zoom);

      // Hide animation hexagons when zoomed out (same threshold as route buttons: 11.5)
      const zoomThreshold = 11.5;
      if (routeAnimationActive) {
        const visibility = zoom >= zoomThreshold ? "visible" : "none";
        if (map.getLayer("hex-route-animation-fill")) {
          map.setLayoutProperty(
            "hex-route-animation-fill",
            "visibility",
            visibility
          );
        }
        if (map.getLayer("hex-route-animation-layer")) {
          map.setLayoutProperty(
            "hex-route-animation-layer",
            "visibility",
            visibility
          );
        }
      }
    });

    map.on("move", () => {
      const zoom = map.getZoom();
      emit("move", { zoom: zoom, center: map.getCenter() });

      // Show/hide route popup based on zoom (same condition as zurich time display)
      handleRoutePopupVisibility(zoom);

      // Hide animation hexagons when zoomed out (same threshold as route buttons: 11.5)
      const zoomThreshold = 11.5;
      if (routeAnimationActive) {
        const visibility = zoom >= zoomThreshold ? "visible" : "none";
        if (map.getLayer("hex-route-animation-fill")) {
          map.setLayoutProperty(
            "hex-route-animation-fill",
            "visibility",
            visibility
          );
        }
        if (map.getLayer("hex-route-animation-layer")) {
          map.setLayoutProperty(
            "hex-route-animation-layer",
            "visibility",
            visibility
          );
        }
      }
    });

    map.on("load", async () => {
      console.log("✅ Mapbox map loaded successfully!");

      // Wait for map to be idle (tiles loaded) before emitting ready
      map.once("idle", () => {
        isMapReady.value = true;
        // Remove loading class from body
        document.body.classList.remove("map-loading");
        emit("mapReady");
        
        // Animate hubs in with delay (after chat bubbles start appearing)
        // Chat bubbles start at 0.3s, so hubs appear shortly after
        setTimeout(() => {
          if (map.getLayer("hubs-circles")) {
            // Use transition for smooth animation
            map.setPaintProperty("hubs-circles", "circle-opacity", 1, {
              duration: 400,
            });
          }
          if (map.getLayer("hubs-clusters")) {
            // Animate clusters in at the same time
            map.setPaintProperty("hubs-clusters", "circle-opacity", 1, {
              duration: 400,
            });
          }
          if (map.getLayer("hubs-cluster-count")) {
            // Animate cluster count labels in at the same time
            map.setPaintProperty("hubs-cluster-count", "text-opacity", 1, {
              duration: 400,
            });
          }
        }, 600);
        
        // Animate labels in with more delay
        setTimeout(() => {
          if (map.getLayer("hubs-labels")) {
            map.setPaintProperty("hubs-labels", "text-opacity", 1, {
              duration: 400,
            });
          }
        }, 1100);
      });

      // Note: We removed the styledata and idle event listeners to improve performance
      // ensureHubsOnTop() is now only called when layers are actually added or changed

      // Emit initial zoom/center
      emit("zoom", { zoom: map.getZoom(), center: map.getCenter() });

      try {
        // --- Load and add Routing Hubs (points) ---
        // Reuse hubsData if already loaded, otherwise fetch it
        if (!hubsData) {
          const hubsResponse = await fetch(hubsUrl);
          hubsData = await hubsResponse.json();
        }

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

        // Add cluster circles (white circles for clusters) - initially hidden
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
            "circle-opacity": 0, // Start hidden, will animate in
          },
        });

        // Add cluster count labels (numbers on clusters) - initially hidden
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
            "text-opacity": 0, // Start hidden, will animate in
          },
        });

        // Add circles for unclustered hubs (initially hidden, will animate in)
        map.addLayer({
          id: "hubs-circles",
          type: "circle",
          source: "hubs",
          filter: ["!", ["has", "point_count"]],
          paint: {
            "circle-radius": 12,
            "circle-color": "#888888", // Medium gray for unselected hubs (more contrast)
            "circle-stroke-color": "#0b0b0c",
            "circle-stroke-width": 0,
            "circle-opacity": 0, // Start hidden, will animate in
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

        // Add labels for hubs (anchored above points)
        map.addLayer({
          id: "hubs-labels",
          type: "symbol",
          source: "hubs",
          minzoom: 11.5, // Show labels at same threshold as routes (disappear when zoomed out)
          layout: {
            "text-field": [
              "case",
              ["==", ["get", "id"], 1],
              "Wollishofen",
              ["==", ["get", "id"], 2],
              "Friesenberg",
              ["==", ["get", "id"], 3],
              "Albisrieden",
              ["==", ["get", "id"], 4],
              "Höngg",
              ["==", ["get", "id"], 5],
              "Affoltern",
              ["==", ["get", "id"], 6],
              "Oerlikon",
              ["==", ["get", "id"], 7],
              "Schwamendingen Mitte",
              ["==", ["get", "id"], 8],
              "Seefeld",
              ["==", ["get", "id"], 9],
              "Stampfenbachplatz",
              ["concat", "Hub ", ["to-string", ["get", "id"]]],
            ],
            "text-font": [
              "SF Pro Text Medium",
              "SF Pro Display Medium",
              "-apple-system",
              "BlinkMacSystemFont",
              "Helvetica Neue",
              "Arial Unicode MS Regular",
            ],
            "text-size": 15, // Larger font size for better visibility
            "text-offset": [0, -1.5], // Position above point (negative Y moves up)
            "text-anchor": "bottom", // Anchor at bottom of text
            "text-letter-spacing": 0.05, // Tighter letter spacing for techy look
          },
          paint: {
            "text-color": "#ffffff", // Pure white text
            "text-opacity": 0, // Start hidden, will animate in
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

        // Add click handler for hex polygons (lighting layer)
        map.on("click", "hex-layer", (e) => {
          if (e.features && e.features.length > 0) {
            emit("polygonClicked", {
              type: "lighting",
              feature: e.features[0],
            });
          }
        });

        setHubsVisibility(props.showHubs);
        hubsLoaded = true;

        // Initialize hub colors
        updateHubColors();

        // Map is already positioned correctly from initial load, no need to zoom again

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

          // Add click handler for vibrancy polygons
          map.on("click", "hex-vibrancy-layer", (e) => {
            if (e.features && e.features.length > 0) {
              emit("polygonClicked", {
                type: "vibrancy",
                feature: e.features[0],
              });
            }
          });

          // --- Load and add Vibrancy POI Points (visible when zoomed in) ---
          try {
            const vibrancyPointsResponse = await fetch(vibrancyPointsUrl);
            const vibrancyPointsData = await vibrancyPointsResponse.json();

            map.addSource("vibrancy-points", {
              type: "geojson",
              data: vibrancyPointsData,
            });

            // Color mapping for different POI types (bright, luminous, highly differentiable)
            const typeColors = {
              BarOrPub: "#ff6348", // Bright coral/orange-red - warmer, more orange
              CafeOrCoffeeShop: "#ffa502", // Bright orange - distinct warm tone
              Restaurant: "#00d2d3", // Bright teal/cyan - cool green-blue
              MusicVenue: "#5f27cd", // Bright purple/violet - distinct purple
              NightClub: "#ff1493", // Deep pink/hot pink - distinct from red/coral
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

          // Add source for animated route hexagons (separate from combined layer)
          map.addSource("hex-route-animation", {
            type: "geojson",
            data: {
              type: "FeatureCollection",
              features: [],
            },
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
            "hex-combined-layer",
            "visibility",
            props.combinedVisible ? "visible" : "none"
          );

          // Add 2D fill layer for animated route hexagons
          map.addLayer({
            id: "hex-route-animation-fill",
            type: "fill",
            source: "hex-route-animation",
            paint: {
              // Color will be updated dynamically based on coloring mode
              // Default to route-based coloring
              "fill-color": [
                "case",
                ["has", "route_type"],
                [
                  "match",
                  ["get", "route_type"],
                  "bright",
                  "#64b4ff", // Blue for bright route
                  "fast",
                  "#ff9500", // Orange for fast route
                  "both",
                  "#8b5cf6", // Purple for both routes
                  "#6c5ce7", // Default purple-blue
                ],
                "#6c5ce7", // Default if no route_type
              ],
              "fill-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0,
                15.15,
                0.4,
                15.3,
                0.5,
              ],
              "fill-outline-color": "transparent",
            },
          });

          // Add 3D extruded hexagon layer for animated route hexagons
          map.addLayer({
            id: "hex-route-animation-layer",
            type: "fill-extrusion",
            source: "hex-route-animation",
            paint: {
              // Color will be updated dynamically based on coloring mode
              // Default to route-based coloring
              "fill-extrusion-color": [
                "case",
                ["has", "route_type"],
                [
                  "match",
                  ["get", "route_type"],
                  "bright",
                  "#64b4ff", // Blue for bright route
                  "fast",
                  "#ff9500", // Orange for fast route
                  "both",
                  "#8b5cf6", // Purple for both routes
                  "#6c5ce7", // Default purple-blue
                ],
                "#6c5ce7", // Default if no route_type
              ],
              "fill-extrusion-opacity": [
                "interpolate",
                ["linear"],
                ["zoom"],
                15,
                0.6,
                15.15,
                0.15,
                15.3,
                0,
              ],
              // Height will be animated from 0 to full height
              // Use animation_height property that starts at 0 and animates to full height
              "fill-extrusion-height": [
                "*",
                ["get", "animation_height"],
                ["*", ["get", "combined_score"], 2500],
              ],
              "fill-extrusion-base": 0,
            },
          });

          // Initially hide animation layers
          map.setLayoutProperty(
            "hex-route-animation-fill",
            "visibility",
            "none"
          );
          map.setLayoutProperty(
            "hex-route-animation-layer",
            "visibility",
            "none"
          );

          // Combined layer click handlers are handled in the general map click handler
          // (both fill and 3D layers are handled there for consistency and reliability)
        } catch (error) {
          console.error("Failed to load vibrancy GeoJSON data:", error);
        }

        // Ensure hubs are always on top of all other layers
        ensureHubsOnTop();

        // Add general map click handler (for empty map area clicks)
        // This fires when clicking on empty map space (not on features)
        map.on("click", (e) => {
          // First, check specifically for combined layer clicks (priority check)
          const combinedFeatures = map.queryRenderedFeatures(e.point, {
            layers: ["hex-combined-fill", "hex-combined-layer"],
          });
          if (combinedFeatures.length > 0) {
            emit("polygonClicked", {
              type: "combined",
              feature: combinedFeatures[0],
            });
            return;
          }

          // Then check for other interactive features
          const features = map.queryRenderedFeatures(e.point, {
            layers: [
              "hubs-circles",
              "hubs-clusters",
              "hex-layer",
              "hex-vibrancy-layer",
              "vibrancy-points-layer",
            ],
          });

          // Only emit if no interactive features are clicked
          if (features.length === 0) {
            emit("mapClicked");
          }
        });

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

        // Show/hide 2D and 3D combined layers when combined layer is selected
        const fillLayerUpdated = updateLayerVisibility(
          "hex-combined-fill",
          isVisible
        );
        const extrusionLayerUpdated = updateLayerVisibility(
          "hex-combined-layer",
          isVisible
        );

        // If layers don't exist yet, retry after a short delay
        if (!fillLayerUpdated || !extrusionLayerUpdated) {
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

  // Animation layers should be above combined layers but below hubs
  const animationLayers = [
    "hex-route-animation-fill",
    "hex-route-animation-layer",
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

  // Always move hubs to the top (don't check if they're already on top,
  // as routes might be above them)
  // Move animation layers to be just before hubs (if they exist)
  animationLayers.forEach((layerId) => {
    if (map.getLayer(layerId)) {
      try {
        // Move animation layer to be just before the first hub layer
        if (existingHubLayers.length > 0) {
          map.moveLayer(layerId, existingHubLayers[0]);
        } else {
          map.moveLayer(layerId);
        }
      } catch (e) {
        // Layer might not exist yet, that's okay
      }
    }
  });

  // Move each hub layer to the absolute top
  // Move in forward order so that the last layer (hubs-labels) ends up on top
  // Each moveLayer() call moves the layer to the absolute top, so we want labels on top
  hubLayers.forEach((layerId) => {
    if (map.getLayer(layerId)) {
      try {
        map.moveLayer(layerId);
      } catch (e) {
        // Layer might not exist, ignore
        console.warn(`Could not move layer ${layerId}:`, e);
      }
    }
  });
  
  // Force a repaint to ensure changes are visible
  map.triggerRepaint();
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

// Filter hubs to show only selected ones when a route is active
function filterHubsByRoute(hubId1, hubId2, retryCount = 0) {
  const MAX_RETRIES = 10;
  const RETRY_DELAY = 50;

  if (!map) {
    if (retryCount < MAX_RETRIES) {
      console.log(
        `Map not initialized, retrying filter (${retryCount + 1}/${MAX_RETRIES})...`
      );
      setTimeout(
        () => filterHubsByRoute(hubId1, hubId2, retryCount + 1),
        RETRY_DELAY
      );
      return;
    }
    console.warn("Cannot filter hubs: map not initialized after retries");
    return;
  }

  if (!map.isStyleLoaded()) {
    if (retryCount < MAX_RETRIES) {
      console.log(
        `Map style not loaded, retrying filter (${retryCount + 1}/${MAX_RETRIES})...`
      );
      setTimeout(
        () => filterHubsByRoute(hubId1, hubId2, retryCount + 1),
        RETRY_DELAY
      );
      return;
    }
    console.warn("Cannot filter hubs: map style not loaded after retries");
    return;
  }

  // Check if layers exist
  if (!map.getLayer("hubs-circles") || !map.getLayer("hubs-labels")) {
    if (retryCount < MAX_RETRIES) {
      console.log(
        `Hub layers not found, retrying filter (${retryCount + 1}/${MAX_RETRIES})...`
      );
      setTimeout(
        () => filterHubsByRoute(hubId1, hubId2, retryCount + 1),
        RETRY_DELAY
      );
      return;
    }
    console.warn("Cannot filter hubs: layers not found after retries");
    return;
  }

  // If no route is active, show all hubs
  if (hubId1 === null && hubId2 === null) {
    // Show all hubs - remove filter or use a filter that always passes
    const showAllFilter = ["!", ["has", "point_count"]]; // Original filter for unclustered hubs

    // Show clusters when route is cleared
    map.setLayoutProperty("hubs-clusters", "visibility", "visible");
    map.setLayoutProperty("hubs-cluster-count", "visibility", "visible");

    // Show all unclustered hubs
    if (map.getLayer("hubs-circles")) {
      map.setFilter("hubs-circles", showAllFilter);
      // Reset opacity to always visible (no route, so no zoom-based hiding)
      map.setPaintProperty("hubs-circles", "circle-opacity", 1);
      console.log("Showing all hubs - filter reset");
    }
    if (map.getLayer("hubs-labels")) {
      map.setFilter("hubs-labels", showAllFilter);
      // Reset label minzoom to match route threshold (disappear when zoomed out below 11.5)
      map.setLayoutProperty("hubs-labels", "minzoom", 11.5);
      console.log("Showing all hub labels - filter reset");
    }
    // Force a repaint
    map.triggerRepaint();
    return;
  }

  // When route is active, hide clusters and show only the two selected hubs
  // Ensure IDs are numbers for comparison
  const selectedIds = [];
  if (hubId1 !== null) {
    const id1 = typeof hubId1 === "string" ? parseInt(hubId1, 10) : hubId1;
    selectedIds.push(id1);
  }
  if (hubId2 !== null) {
    const id2 = typeof hubId2 === "string" ? parseInt(hubId2, 10) : hubId2;
    selectedIds.push(id2);
  }

  // Debug: Check what hub IDs exist in the data
  if (hubsData && hubsData.features) {
    const allHubIds = hubsData.features
      .filter((f) => !f.properties.point_count)
      .map((f) => f.properties.id);
    console.log("All hub IDs in data:", allHubIds);
  }

  console.log(
    "Filtering hubs to show only:",
    selectedIds,
    "from input:",
    hubId1,
    hubId2
  );

  // Hide clusters when route is active
  if (map.getLayer("hubs-clusters")) {
    map.setLayoutProperty("hubs-clusters", "visibility", "none");
  }
  if (map.getLayer("hubs-cluster-count")) {
    map.setLayoutProperty("hubs-cluster-count", "visibility", "none");
  }

  // Filter to show only selected hubs
  // Use "any" with multiple equality checks
  if (selectedIds.length === 1) {
    // Single hub selected
    const routeFilter = [
      "all",
      ["!", ["has", "point_count"]], // Not a cluster
      ["==", ["get", "id"], selectedIds[0]], // ID matches
    ];
    console.log("Applying filter (single hub):", routeFilter);
    if (map.getLayer("hubs-circles")) {
      map.setFilter("hubs-circles", routeFilter);
      // Reset opacity to always visible (no route, so no zoom-based hiding)
      map.setPaintProperty("hubs-circles", "circle-opacity", 1);
    }
    if (map.getLayer("hubs-labels")) {
      map.setFilter("hubs-labels", routeFilter);
      // Set label minzoom to match route threshold (disappear when zoomed out below 11.5)
      map.setLayoutProperty("hubs-labels", "minzoom", 11.5);
    }
  } else if (selectedIds.length === 2) {
    // Two hubs selected - add zoom-based visibility to match route disappearance
    const routeFilter = [
      "all",
      ["!", ["has", "point_count"]], // Not a cluster
      [
        "any",
        ["==", ["get", "id"], selectedIds[0]], // ID matches first hub
        ["==", ["get", "id"], selectedIds[1]], // ID matches second hub
      ],
    ];
    console.log("Applying filter (two hubs):", routeFilter);
    try {
      if (map.getLayer("hubs-circles")) {
        map.setFilter("hubs-circles", routeFilter);
        // Add zoom-based opacity to match route disappearance (smooth fade like route)
        map.setPaintProperty("hubs-circles", "circle-opacity", [
          "interpolate",
          ["linear"],
          ["zoom"],
          11.4,
          0, // Invisible at zoom 11.4 and below
          11.5,
          1, // Fully visible at zoom 11.5 and above
        ]);
        const currentFilter = map.getFilter("hubs-circles");
        console.log(
          "Filter applied to hubs-circles. Current filter:",
          currentFilter
        );
      }
      if (map.getLayer("hubs-label-connectors")) {
        map.setFilter("hubs-label-connectors", routeFilter);
      }
      if (map.getLayer("hubs-labels")) {
        map.setFilter("hubs-labels", routeFilter);
        // Set minzoom to match route disappearance (disappears at zoom 12, same as route)
        map.setLayoutProperty("hubs-labels", "minzoom", 11.5);
        const currentFilter = map.getFilter("hubs-labels");
        console.log(
          "Filter applied to hubs-labels. Current filter:",
          currentFilter
        );
      }
      // Force a repaint to ensure filter is visible
      map.triggerRepaint();
    } catch (error) {
      console.error("Error applying filter:", error);
    }
  } else {
    console.warn("No selected IDs to filter:", selectedIds);
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
    clearRoute(); // This will show all hubs immediately
    updateHubColors();
    return;
  }

  // If clicking the second selected hub, deselect it
  if (selectedHubId2 === id) {
    selectedHubId2 = null;
    clearRoute(); // This will show only selectedHubId1 if it exists, or all hubs if null
    updateHubColors();
    return;
  }

  // If no hub is selected, select this one as first
  if (selectedHubId1 === null) {
    selectedHubId1 = id;
    selectedHubId2 = null;
    clearRoute(); // This will show all hubs (only one hub selected, not a route)
    updateHubColors();
    return;
  }

  // If first hub is selected, select this one as second and show route
  if (selectedHubId1 !== null && selectedHubId2 === null) {
    selectedHubId2 = id;
    loadAndDisplayRoute(selectedHubId1, selectedHubId2);
    updateHubColors();
    // Emit event to notify parent that route was created via hub clicks
    emit("hubsSelected", { hubId1: selectedHubId1, hubId2: selectedHubId2 });
    return;
  }

  // If both hubs are selected, replace first with this one
  selectedHubId1 = id;
  selectedHubId2 = null;
  clearRoute(); // This will show all hubs (only one hub selected, not a route)
  updateHubColors();
}

// Update hub colors - ensure all hubs have the same default green color
function updateHubColors() {
  if (!map || !map.isStyleLoaded() || !hubsData) {
    // Retry if map isn't ready yet
    setTimeout(() => updateHubColors(), 50);
    return;
  }

  const layer = map.getLayer("hubs-circles");
  if (!layer) {
    // Retry if layer isn't ready yet
    setTimeout(() => updateHubColors(), 50);
    return;
  }

  // Build match expression for selected hubs (white) vs unselected (light gray)
  const selectedIds = [];
  if (selectedHubId1 !== null) selectedIds.push(selectedHubId1);
  if (selectedHubId2 !== null) selectedIds.push(selectedHubId2);

  try {
    // Create match expression: white for selected hubs, medium gray for others
    if (selectedIds.length === 0) {
      // No hubs selected - all medium gray
      map.setPaintProperty("hubs-circles", "circle-color", "#888888");
    } else if (selectedIds.length === 1) {
      // One hub selected
      map.setPaintProperty("hubs-circles", "circle-color", [
        "match",
        ["get", "id"],
        selectedIds[0],
        "#ffffff", // White for selected hub
        "#888888", // Medium gray for others (more contrast)
      ]);
    } else {
      // Two hubs selected
      map.setPaintProperty("hubs-circles", "circle-color", [
        "match",
        ["get", "id"],
        selectedIds[0],
        "#ffffff", // White for first selected hub
        selectedIds[1],
        "#ffffff", // White for second selected hub
        "#888888", // Medium gray for others (more contrast)
      ]);
    }
    // Force repaint after color update
    map.triggerRepaint();
  } catch (error) {
    console.warn("Error updating hub colors:", error);
  }
}

// Helper function to add route layers for a given source
// routeType: "fast" (orange) or "bright" (blue)
function addRouteLayers(sourceId, beforeLayer, routeType = "bright") {
  const routeLayers = [];
  const isFast = routeType === "fast";

  // Define colors based on route type
  const glowColor = isFast ? "#888888" : "#00a8ff"; // Grey for fast, blue for bright
  const mainColor = isFast
    ? ["#777777", "#888888", "#999999"] // Grey shades for fast
    : ["#0099ff", "#00a8ff", "#00b8ff"]; // Blue shades for bright
  const highlightColor = isFast ? "#aaaaaa" : "#ffffff"; // Light grey for fast, white for bright

  // Glow/shadow layer (underneath main line)
  const glowLayerId = `${sourceId}-glow`;
  if (!map.getLayer(glowLayerId)) {
    map.addLayer(
      {
        id: glowLayerId,
        type: "line",
        source: sourceId,
        paint: {
          "line-color": glowColor,
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
          "line-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            11.4,
            0, // Invisible at zoom 11.4 and below
            11.5,
            0.4, // Fully visible at zoom 11.5 and above
          ],
          "line-blur": 10,
        },
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
      },
      beforeLayer
    );
    routeLayers.push(glowLayerId);
  } else {
    // Update existing layer color if it exists
    map.setPaintProperty(glowLayerId, "line-color", glowColor);
  }

  // Main route line
  const mainLayerId = `${sourceId}-line`;
  if (!map.getLayer(mainLayerId)) {
    map.addLayer(
      {
        id: mainLayerId,
        type: "line",
        source: sourceId,
        paint: {
          "line-color": [
            "interpolate",
            ["linear"],
            ["zoom"],
            10,
            mainColor[0],
            15,
            mainColor[1],
            18,
            mainColor[2],
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
          "line-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            11.4,
            0, // Invisible at zoom 11.4 and below
            11.5,
            1, // Fully visible at zoom 11.5 and above
          ],
        },
        layout: {
          "line-join": "round",
          "line-cap": "round",
        },
      },
      beforeLayer
    );
    routeLayers.push(mainLayerId);
  } else {
    // Update existing layer color if it exists
    map.setPaintProperty(mainLayerId, "line-color", [
      "interpolate",
      ["linear"],
      ["zoom"],
      10,
      mainColor[0],
      15,
      mainColor[1],
      18,
      mainColor[2],
    ]);
  }

  // Highlight layer for extra shine (on top)
  const highlightLayerId = `${sourceId}-highlight`;
  if (!map.getLayer(highlightLayerId)) {
    map.addLayer(
      {
        id: highlightLayerId,
        type: "line",
        source: sourceId,
        paint: {
          "line-color": highlightColor,
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
          "line-opacity": [
            "interpolate",
            ["linear"],
            ["zoom"],
            11.4,
            0, // Invisible at zoom 11.4 and below
            11.5,
            0.6, // Fully visible at zoom 11.5 and above
          ],
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
      mainLayerId
    );
    routeLayers.push(highlightLayerId);
  } else {
    // Update existing layer color if it exists
    map.setPaintProperty(highlightLayerId, "line-color", highlightColor);
  }

  // Always ensure all layers are visible (including existing ones)
  const allLayerIds = [glowLayerId, mainLayerId, highlightLayerId];
  allLayerIds.forEach((layerId) => {
    if (map.getLayer(layerId)) {
      map.setLayoutProperty(layerId, "visibility", "visible");
    }
  });

  return allLayerIds;
}

// Load and display route between two hubs (both fast and bright routes)
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

  // Determine route filenames (always use smaller ID first for consistency)
  const routeId1 = Math.min(fromId, toId);
  const routeId2 = Math.max(fromId, toId);
  const fastRouteFileName = `${routeId1}_${routeId2}_f.geojson`;
  const brightRouteFileName = `${routeId1}_${routeId2}_b.geojson`;
  const fastRouteUrl = `${BASE}data/routes_wgs84/${fastRouteFileName}`.replace(
    /\/{2,}/g,
    "/"
  );
  const brightRouteUrl =
    `${BASE}data/routes_wgs84/${brightRouteFileName}`.replace(/\/{2,}/g, "/");

  console.log(
    `Loading routes: ${fastRouteFileName} and ${brightRouteFileName}`
  );

  try {
    // Clear existing routes first (but don't reset hub filter - we'll set it after loading)
    clearRoute(true);

    // Load both route files in parallel
    const [fastResponse, brightResponse] = await Promise.all([
      fetch(fastRouteUrl),
      fetch(brightRouteUrl),
    ]);

    // Check if routes exist
    if (!fastResponse.ok && !brightResponse.ok) {
      console.error(
        `Routes not found: ${fastRouteFileName} and ${brightRouteFileName}`,
        {
          fastStatus: fastResponse.status,
          brightStatus: brightResponse.status,
        }
      );
      return;
    }

    let fastRouteData = null;
    let brightRouteData = null;
    let route_geom = null;
    let allCoords = []; // Collect all coordinates for bounding box

    // Load fast route if available
    if (fastResponse.ok) {
      fastRouteData = await fastResponse.json();
      console.log("Fast route data loaded:", fastRouteData);

      if (
        fastRouteData &&
        fastRouteData.features &&
        fastRouteData.features.length > 0
      ) {
        const firstFeature = fastRouteData.features[0];
        if (
          firstFeature.geometry &&
          firstFeature.geometry.type === "LineString"
        ) {
          allCoords.push(...firstFeature.geometry.coordinates);
          fastRouteGeom = {
            coords: firstFeature.geometry.coordinates,
          };
          if (!route_geom) {
            route_geom = {
              coords: firstFeature.geometry.coordinates,
            };
          }

          // Extract fast route statistics
          if (firstFeature.properties) {
            const props = firstFeature.properties;
            fastRouteStats = {
              lengthMeters: props.route_length_meters || null,
              lengthKm: props.route_length_km || null,
              walkDurationMinutes: props.walk_duration_minutes || null,
              walkDurationFormatted: props.walk_duration_formatted || null,
              poiCounts: props.poi_counts || {},
              poiFrequencies: props.poi_frequencies || {},
            };
            console.log(`Fast Route Stats:`, fastRouteStats);
          }
        }
      }
    }

    // Load bright route if available
    if (brightResponse.ok) {
      brightRouteData = await brightResponse.json();
      console.log("Bright route data loaded:", brightRouteData);

      if (
        brightRouteData &&
        brightRouteData.features &&
        brightRouteData.features.length > 0
      ) {
        const firstFeature = brightRouteData.features[0];
        if (
          firstFeature.geometry &&
          firstFeature.geometry.type === "LineString"
        ) {
          allCoords.push(...firstFeature.geometry.coordinates);
          brightRouteGeom = {
            coords: firstFeature.geometry.coordinates,
          };
          if (!route_geom) {
            route_geom = {
              coords: firstFeature.geometry.coordinates,
            };
          }

          // Extract bright route statistics
          if (firstFeature.properties) {
            const props = firstFeature.properties;
            brightRouteStats = {
              lengthMeters: props.route_length_meters || null,
              lengthKm: props.route_length_km || null,
              walkDurationMinutes: props.walk_duration_minutes || null,
              walkDurationFormatted: props.walk_duration_formatted || null,
              poiCounts: props.poi_counts || {},
              poiFrequencies: props.poi_frequencies || {},
            };

            // Extract lumo score from bright route
            if (props.lumo_score_percentage !== undefined) {
              currentRouteLumoScore = props.lumo_score_percentage;
            }

            console.log(`Bright Route Stats:`, brightRouteStats);
          }
        }
      }
    }

    // Set currentRouteStats to bright route stats for backward compatibility
    currentRouteStats = brightRouteStats || fastRouteStats;

    // Don't use beforeLayer - add routes at the end, then we'll move them appropriately
    const beforeLayer = undefined;

    // Add fast route if available
    if (
      fastRouteData &&
      fastRouteData.features &&
      fastRouteData.features.length > 0
    ) {
      const sourceId = "route-fast";
      if (map.getSource(sourceId)) {
        map.getSource(sourceId).setData(fastRouteData);
      } else {
        map.addSource(sourceId, {
          type: "geojson",
          data: fastRouteData,
        });
      }

      // Wait for source to be ready
      await nextTick();
      await new Promise((resolve) => setTimeout(resolve, 50));

      const fastRouteLayers = addRouteLayers(sourceId, beforeLayer, "fast");

      // Explicitly ensure all layers are visible
      fastRouteLayers.forEach((layerId) => {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, "visibility", "visible");
        }
      });
    }

    // Add bright route if available
    if (
      brightRouteData &&
      brightRouteData.features &&
      brightRouteData.features.length > 0
    ) {
      const sourceId = "route-bright";
      if (map.getSource(sourceId)) {
        map.getSource(sourceId).setData(brightRouteData);
      } else {
        map.addSource(sourceId, {
          type: "geojson",
          data: brightRouteData,
        });
      }

      // Wait for source to be ready
      await nextTick();
      await new Promise((resolve) => setTimeout(resolve, 50));

      const brightRouteLayers = addRouteLayers(sourceId, beforeLayer, "bright");

      // Explicitly ensure all layers are visible
      brightRouteLayers.forEach((layerId) => {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, "visibility", "visible");
        }
      });
    }

    // Collect all route layers for positioning
    const allRouteLayers = [];
    ["route-fast", "route-bright"].forEach((sourceId) => {
      ["glow", "line", "highlight"].forEach((suffix) => {
        const layerId = `${sourceId}-${suffix}`;
        if (map.getLayer(layerId)) {
          allRouteLayers.push(layerId);
        }
      });
    });

    console.log("Route layers visibility set to visible");

    // Move route layers to the absolute top (above all other layers)
    try {
      // Move in reverse order to maintain correct stacking within route layers
      // Then move each to the top so they render above everything
      allRouteLayers.reverse().forEach((layerId) => {
        if (map.getLayer(layerId)) {
          // Move to top by calling moveLayer without beforeId
          map.moveLayer(layerId);
        }
      });
      console.log("Route layers moved to top of layer stack");
    } catch (e) {
      console.warn("Could not move route layers:", e);
    }

    // Ensure hubs are always on top of route layers
    // Use nextTick and a small delay to ensure route layers are fully processed
    await nextTick();
    setTimeout(() => {
      ensureHubsOnTop();
      // Also ensure after repaint
      setTimeout(() => {
        ensureHubsOnTop();
      }, 50);
    }, 100);

    currentRouteSource = fastRouteUrl; // Store fast route URL as primary
    console.log(
      `✅ Routes successfully loaded: ${fastRouteFileName} and ${brightRouteFileName}`
    );

    // Force a repaint to ensure routes are visible
    map.triggerRepaint();

    // Zoom and center map on the routes (using all coordinates from both routes)
    if (allCoords.length > 0) {
      // Calculate bounding box of all routes
      let minLng = allCoords[0][0];
      let maxLng = allCoords[0][0];
      let minLat = allCoords[0][1];
      let maxLat = allCoords[0][1];

      allCoords.forEach((coord) => {
        const [lng, lat] = coord;
        minLng = Math.min(minLng, lng);
        maxLng = Math.max(maxLng, lng);
        minLat = Math.min(minLat, lat);
        maxLat = Math.max(maxLat, lat);
      });

      // Add padding around the routes (in degrees)
      const padding = 0.01;
      const bounds = [
        [minLng - padding, minLat - padding],
        [maxLng + padding, maxLat + padding],
      ];

      // Get current pitch and bearing to preserve them
      const currentPitch = map.getPitch();
      const currentBearing = map.getBearing();

      // Create LngLatBounds object
      const routeBounds = new mapboxgl.LngLatBounds(bounds[0], bounds[1]);

      // Calculate optimal zoom and center
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
        pitch: currentPitch,
        bearing: currentBearing,
        duration: 1500,
        easing(t) {
          return t * (2 - t); // ease-out easing
        },
      });

      console.log("✅ Map zoomed and centered on routes");
      
      // Ensure hubs are on top after zoom animation completes
      setTimeout(() => {
        ensureHubsOnTop();
      }, 1600); // Slightly longer than animation duration
    } else {
      // Even if no zoom happens, ensure hubs are on top after a delay
      setTimeout(() => {
        ensureHubsOnTop();
      }, 200);
    }

    // Filter hubs to show only the two selected hubs immediately
    // Use the global selectedHubId variables to ensure consistency
    // Apply filter immediately - retry logic in filterHubsByRoute will handle if map isn't ready
    filterHubsByRoute(selectedHubId1, selectedHubId2);

    // Ensure hubs are on top after filtering (with a delay to ensure filter is applied)
    setTimeout(() => {
      ensureHubsOnTop();
    }, 150);

    // Show route statistics popups after a short delay
    setTimeout(() => {
      // Show popup for fast route if available
      if (fastRouteGeom && fastRouteStats) {
        showRouteStatsPopup(fastRouteGeom, fastRouteStats, "fast");
      }

      // Show popup for bright route if available
      if (brightRouteGeom && brightRouteStats) {
        showRouteStatsPopup(brightRouteGeom, brightRouteStats, "bright");
      }
      
      // Final check to ensure hubs are on top after popups are shown
      ensureHubsOnTop();
    }, 300);
  } catch (error) {
    console.error(`Error loading routes:`, error);
  }
}

// Handle route popup visibility based on zoom level
function handleRoutePopupVisibility(zoom) {
  if (!map) return;

  const shouldShow = zoom >= 11.5;

  // Handle fast route popup
  if (shouldShow && fastRouteGeom && fastRouteStats) {
    if (!fastRoutePopup) {
      showRouteStatsPopup(fastRouteGeom, fastRouteStats, "fast");
    } else {
      // Fade in existing popup
      setTimeout(() => {
        const popupElement = document.querySelector(
          ".route-stats-map-popup--fast"
        );
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
    // Fade out fast route popup
    const fastPopupElement = document.querySelector(
      ".route-stats-map-popup--fast"
    );
    if (fastPopupElement) {
      fastPopupElement.style.opacity = "0";
      fastPopupElement.style.visibility = "hidden";
      fastPopupElement.style.pointerEvents = "none";
      fastPopupElement.style.transition =
        "opacity 0.3s ease, visibility 0.3s ease";
    }
  }

  // Handle bright route popup
  if (shouldShow && brightRouteGeom && brightRouteStats) {
    if (!brightRoutePopup) {
      showRouteStatsPopup(brightRouteGeom, brightRouteStats, "bright");
    } else {
      // Fade in existing popup
      setTimeout(() => {
        const popupElement = document.querySelector(
          ".route-stats-map-popup--bright"
        );
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
    // Fade out bright route popup
    const brightPopupElement = document.querySelector(
      ".route-stats-map-popup--bright"
    );
    if (brightPopupElement) {
      brightPopupElement.style.opacity = "0";
      brightPopupElement.style.visibility = "hidden";
      brightPopupElement.style.pointerEvents = "none";
      brightPopupElement.style.transition =
        "opacity 0.3s ease, visibility 0.3s ease";
    }
  }
}

// Show route statistics popup on the map
function showRouteStatsPopup(routeGeom, stats, routeType = "fast") {
  if (!map || !routeGeom || !stats) return;

  // Store geometry for later recreation based on route type
  if (routeType === "fast") {
    fastRouteGeom = routeGeom;
  } else {
    brightRouteGeom = routeGeom;
  }

  // Remove existing popup for this route type
  if (routeType === "fast" && fastRoutePopup) {
    fastRoutePopup.remove();
    fastRoutePopup = null;
  } else if (routeType === "bright" && brightRoutePopup) {
    brightRoutePopup.remove();
    brightRoutePopup = null;
  }

  // Calculate position along route for popup
  const coords = routeGeom.coords;
  if (!coords || coords.length === 0) return;

  // Position fast route popup at 40% along route, bright at 60% to avoid overlap
  const positionPercent = routeType === "fast" ? 0.4 : 0.6;
  const routePointIndex = Math.floor(coords.length * positionPercent);
  const routePoint = coords[routePointIndex];

  // Get route stats
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
      <img src="${walkingIconUrl}" alt="Walking" width="20" height="20" style="vertical-align: middle;" />
    </span>
  `;
  if (duration !== null) {
    html += `<span class="route-stats-popup-duration" style="color: #ffffff !important; font-weight: 800 !important; font-size: 16px !important;">${duration} min</span>`;
  }
  html += "</div>";

  // Second row: Distance below, aligned with duration text
  if (distance !== null) {
    html += `<div class="route-stats-popup-bottom-line">`;
    html += `<span class="route-stats-popup-distance" style="color: #ffffff !important;">${distance} km</span>`;
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

  // Create and show popup with tip pointing to route
  // Use different CSS class based on route type
  const popupClassName = `route-stats-map-popup route-stats-map-popup--${routeType}`;
  const popupInstance = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    className: popupClassName,
    anchor: "bottom",
    offset: [0, -5], // Smaller offset so tip is closer to route
  })
    .setLngLat([routePoint[0], routePoint[1]])
    .setDOMContent(popupContent)
    .addTo(map);

  // Store popup instance based on route type
  if (routeType === "fast") {
    fastRoutePopup = popupInstance;
  } else {
    brightRoutePopup = popupInstance;
  }

  // Set initial visibility based on current zoom after popup is added
  setTimeout(() => {
    const currentZoom = map.getZoom();
    const popupElement = document.querySelector(
      `.route-stats-map-popup--${routeType}`
    );
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
      `.route-stats-map-popup--${routeType} .mapboxgl-popup-content`
    );
    if (popupContentEl) {
      // Use more translucent glassmorphic effect - blue tint for bright route, neutral for fast route
      if (routeType === "bright") {
        popupContentEl.style.background = "rgba(100, 180, 255, 0.22)";
        popupContentEl.style.backgroundColor = "rgba(100, 180, 255, 0.22)";
      } else {
        popupContentEl.style.background = "rgba(255, 255, 255, 0.1)";
        popupContentEl.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
      }
      popupContentEl.style.border = "none";
      popupContentEl.style.backdropFilter = "blur(30px) saturate(180%)";
      popupContentEl.style.webkitBackdropFilter = "blur(30px) saturate(180%)";
      popupContentEl.style.boxShadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)";
      popupContentEl.style.borderRadius = "8px";
      popupContentEl.style.transition =
        "transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease";

      // Add hover event listeners to manually change styles (since CSS hover might be overridden)
      popupContentEl.addEventListener("mouseenter", () => {
        if (routeType === "bright") {
          popupContentEl.style.background = "rgba(100, 180, 255, 0.22)";
          popupContentEl.style.backgroundColor = "rgba(100, 180, 255, 0.22)";
        } else {
          popupContentEl.style.background = "rgba(255, 255, 255, 0.18)";
          popupContentEl.style.backgroundColor = "rgba(255, 255, 255, 0.18)";
        }
        popupContentEl.style.transform = "scale(1.08)";
        popupContentEl.style.boxShadow = "0 12px 40px 0 rgba(0, 0, 0, 0.4)";
      });

      popupContentEl.addEventListener("mouseleave", () => {
        if (routeType === "bright") {
          popupContentEl.style.background = "rgba(100, 180, 255, 0.15)";
          popupContentEl.style.backgroundColor = "rgba(100, 180, 255, 0.15)";
        } else {
          popupContentEl.style.background = "rgba(255, 255, 255, 0.1)";
          popupContentEl.style.backgroundColor = "rgba(255, 255, 255, 0.1)";
        }
        popupContentEl.style.transform = "scale(1)";
        popupContentEl.style.boxShadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)";
      });
    }
    const popupTip = document.querySelector(
      `.route-stats-map-popup--${routeType} .mapboxgl-popup-tip`
    );
    if (popupTip) {
      // Use blue tint for bright route tip, neutral for fast route tip
      if (routeType === "bright") {
        popupTip.style.borderTopColor = "rgba(100, 180, 255, 0.15)";
      } else {
        popupTip.style.borderTopColor = "rgba(255, 255, 255, 0.1)";
      }
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

// Reset route animation (internal function)
function resetRouteAnimation() {
  if (!map || !map.isStyleLoaded()) {
    return;
  }

  // Hide animation layers
  if (map.getLayer("hex-route-animation-fill")) {
    map.setLayoutProperty("hex-route-animation-fill", "visibility", "none");
  }
  if (map.getLayer("hex-route-animation-layer")) {
    map.setLayoutProperty("hex-route-animation-layer", "visibility", "none");
  }

  // Clear the animation source data
  const animationSource = map.getSource("hex-route-animation");
  if (animationSource) {
    animationSource.setData({
      type: "FeatureCollection",
      features: [],
    });
  }

  routeAnimationActive = false;
  intersectionData = null;
  console.log("Route animation reset");
}

// Clear the displayed routes (both fast and bright)
function clearRoute(skipHubFilter = false) {
  // Clear security alerts when route is cleared
  if (routeSecurityAlertsActive) {
    removeRouteSecurityAlerts();
    routeSecurityAlertsActive = false;
    routeSecurityAlertsData = null;
  }
  if (!map || !map.isStyleLoaded()) return;

  // Reset route animation if active
  if (routeAnimationActive) {
    resetRouteAnimation();
  }

  // Remove popups if they exist
  if (fastRoutePopup) {
    fastRoutePopup.remove();
    fastRoutePopup = null;
  }
  if (brightRoutePopup) {
    brightRoutePopup.remove();
    brightRoutePopup = null;
  }
  // Also remove legacy popup for backward compatibility
  if (routePopup) {
    routePopup.remove();
    routePopup = null;
  }

  // Clear stored data
  currentRouteStats = null;
  routePopupGeom = null;
  fastRouteStats = null;
  brightRouteStats = null;
  fastRouteGeom = null;
  brightRouteGeom = null;

  // Hide all route layers (both fast and bright)
  const routeSources = ["route-fast", "route-bright"];
  routeSources.forEach((sourceId) => {
    ["glow", "line", "highlight"].forEach((suffix) => {
      const layerId = `${sourceId}-${suffix}`;
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(layerId, "visibility", "none");
      }
    });
  });

  // Clear route sources
  routeSources.forEach((sourceId) => {
    if (map.getSource(sourceId)) {
      map.getSource(sourceId).setData({
        type: "FeatureCollection",
        features: [],
      });
    }
  });

  currentRouteSource = null;

  // If both hubs were selected (full route), reset them when route is actually deleted
  // Only reset when skipHubFilter is false (real deletion), not during route loading (skipHubFilter = true)
  // This ensures colors update back to unselected state only when route is deleted, not during generation
  if (selectedHubId1 !== null && selectedHubId2 !== null && !skipHubFilter) {
    selectedHubId1 = null;
    selectedHubId2 = null;
  }

  // Update hub colors - will keep selected hubs white during route loading, or reset to grey when route is deleted
  updateHubColors();

  // Show all hubs again when route is cleared (only if not skipping filter)
  // Only filter when both hubs are selected (active route). Otherwise show all hubs.
  if (!skipHubFilter) {
    if (selectedHubId1 === null && selectedHubId2 === null) {
      // No hubs selected - show all hubs immediately
      filterHubsByRoute(null, null);
      // Zoom to show all hubs
      zoomToAllHubs();
    } else if (selectedHubId1 !== null && selectedHubId2 === null) {
      // Only one hub selected - show all hubs (not a complete route yet)
      filterHubsByRoute(null, null);
      // Zoom to show all hubs
      zoomToAllHubs();
    } else if (selectedHubId1 !== null && selectedHubId2 !== null) {
      // Both hubs were selected (route was cleared), zoom to show all hubs
      // Use setTimeout to ensure the route is fully cleared first
      setTimeout(() => {
        zoomToAllHubs();
      }, 100);
    }
    // If both hubs are selected, filter will be set by loadAndDisplayRoute
  }
}

// Zoom to show all routing hubs
function zoomToAllHubs(animate = true) {
  console.log("zoomToAllHubs called", {
    map: !!map,
    mapLoaded: map?.isStyleLoaded(),
    hubsData: !!hubsData,
    featuresCount: hubsData?.features?.length,
    hasHubsSource: map?.getSource("hubs") ? true : false,
  });

  if (!map) {
    console.warn("zoomToAllHubs: Map not available");
    return;
  }

  // Try to get hubs from map source first, fallback to hubsData
  let features = null;
  const hubsSource = map.getSource("hubs");
  if (hubsSource && hubsSource._data) {
    features = hubsSource._data.features;
    console.log(
      "zoomToAllHubs: Using features from map source",
      features?.length
    );
  } else if (hubsData && hubsData.features) {
    features = hubsData.features;
    console.log(
      "zoomToAllHubs: Using features from hubsData",
      features?.length
    );
  }

  if (!features || features.length === 0) {
    console.warn("zoomToAllHubs: No features available");
    return;
  }

  // Calculate bounds from all hub coordinates (excluding clusters)
  const bounds = new mapboxgl.LngLatBounds();

  // Add all hub coordinates to bounds (exclude clusters which have point_count)
  let hubCount = 0;
  features.forEach((feature) => {
    // Skip clusters (they have point_count property)
    if (feature.properties && feature.properties.point_count) {
      return;
    }
    if (feature.geometry && feature.geometry.type === "Point") {
      const [lon, lat] = feature.geometry.coordinates;
      bounds.extend([lon, lat]);
      hubCount++;
    }
  });

  console.log(
    "zoomToAllHubs: Found",
    hubCount,
    "hubs, bounds empty:",
    bounds.isEmpty()
  );

  // If we have valid bounds, zoom to them
  if (!bounds.isEmpty()) {
    try {
      // Get current pitch and bearing to preserve them
      const currentPitch = map.getPitch();
      const currentBearing = map.getBearing();

      let targetZoom, targetCenter;

      if (animate) {
        // Calculate target view using fitBounds (for animated case)
        // Store current state
        const originalCenter = map.getCenter();
        const originalZoom = map.getZoom();

        // Temporarily fit bounds to calculate optimal zoom and center
        map.fitBounds(bounds, {
          padding: { top: 80, bottom: 80, left: 80, right: 80 },
          duration: 0,
          maxZoom: 15,
        });

        targetZoom = Math.max(Math.min(map.getZoom(), 15), 12);
        targetCenter = map.getCenter();

        // Restore original position immediately
        map.jumpTo({
          center: originalCenter,
          zoom: originalZoom,
          pitch: currentPitch,
          bearing: currentBearing,
        });

        // Use easeTo with custom easing for smoother animation
        map.easeTo({
          center: targetCenter,
          zoom: targetZoom,
          pitch: currentPitch,
          bearing: currentBearing,
          duration: 1200, // Slightly longer for smoother feel
          easing(t) {
            // Ease-out easing for smooth deceleration
            return t * (2 - t);
          },
        });
      } else {
        // Calculate center and zoom manually without using fitBounds (no visual jump)
        const ne = bounds.getNorthEast();
        const sw = bounds.getSouthWest();

        // Calculate center
        targetCenter = [(ne.lng + sw.lng) / 2, (ne.lat + sw.lat) / 2];

        // Calculate zoom level manually
        const padding = 80;
        const mapWidth = map.getContainer().clientWidth;
        const mapHeight = map.getContainer().clientHeight;

        const latDiff = ne.lat - sw.lat;
        const lngDiff = ne.lng - sw.lng;

        const latZoom = Math.log2(
          360 / ((latDiff * (mapHeight - padding * 2)) / 256)
        );
        const lngZoom = Math.log2(
          360 / ((lngDiff * (mapWidth - padding * 2)) / 256)
        );

        targetZoom = Math.min(Math.min(latZoom, lngZoom), 15);
        targetZoom = Math.max(targetZoom, 12);

        // Jump immediately without animation
        map.jumpTo({
          center: targetCenter,
          zoom: targetZoom,
          pitch: currentPitch,
          bearing: currentBearing,
        });
      }

      console.log(
        "zoomToAllHubs: Called flyTo successfully with preserved pitch"
      );
    } catch (error) {
      console.error("zoomToAllHubs: Error calculating or animating", error);
      // Fallback: use fitBounds directly
      try {
        const currentPitch = map.getPitch();
        const currentBearing = map.getBearing();
        map.fitBounds(bounds, {
          padding: { top: 80, bottom: 80, left: 80, right: 80 },
          duration: animate ? 1200 : 0,
          maxZoom: 15,
        });
        // Restore pitch and bearing
        if (animate) {
          // Restore pitch and bearing after a short delay
          setTimeout(() => {
            map.easeTo({
              pitch: currentPitch,
              bearing: currentBearing,
              duration: 300,
            });
          }, 1250);
        } else {
          // Jump immediately to restore pitch and bearing
          map.jumpTo({
            pitch: currentPitch,
            bearing: currentBearing,
          });
        }
        console.log("zoomToAllHubs: Fallback to fitBounds");
      } catch (fallbackError) {
        console.error("zoomToAllHubs: Fallback also failed", fallbackError);
      }
    }
  } else {
    console.warn("zoomToAllHubs: Bounds are empty, cannot zoom");
  }
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
        clearRoute(true); // Skip filter update, we'll do it here
        // Show only the two selected hubs (both are selected, so filter them)
        setTimeout(() => {
          filterHubsByRoute(id1, id2);
        }, 10);
      }
      updateHubColors();
    } else if (id1) {
      selectedHubId1 = id1;
      selectedHubId2 = null;
      clearRoute(true); // Skip filter update in clearRoute, we'll do it here
      updateHubColors();
      // Show all hubs when only one hub is selected (not a complete route)
      // Use setTimeout to ensure clearRoute has finished
      setTimeout(() => {
        filterHubsByRoute(null, null);
      }, 10);
    } else {
      selectedHubId1 = null;
      selectedHubId2 = null;
      clearRoute(true); // Skip filter update in clearRoute, we'll do it here
      // Update colors immediately
      updateHubColors();
      // Show all hubs immediately (with retry logic)
      // Use setTimeout to ensure clearRoute has finished
      setTimeout(() => {
        filterHubsByRoute(null, null);
        // Update colors again after filter is applied to ensure they're correct
        updateHubColors();
        // Zoom to show all hubs when route is cleared
        // Use another setTimeout to ensure filter is applied
        setTimeout(() => {
          zoomToAllHubs();
        }, 100);
      }, 50);
    }
  },
  getHubs: () => {
    if (!hubsData || !hubsData.features) {
      console.warn("getHubs: hubsData not available");
      return [];
    }
    const hubNames = {
      1: "Wollishofen",
      2: "Friesenberg",
      3: "Albisrieden",
      4: "Höngg",
      5: "Affoltern",
      6: "Oerlikon",
      7: "Schwamendingen Mitte",
      8: "Seefeld",
      9: "Stampfenbachplatz",
    };
    const hubList = hubsData.features.map((feature) => {
      const id = feature.properties.id;
      // Use predefined hub names
      const name = hubNames[id] || `Hub ${id}`;
      return { id, name };
    });
    console.log("getHubs returning:", hubList);
    return hubList;
  },
  getCurrentRouteLumoScore: () => {
    return currentRouteLumoScore;
  },
  getCurrentRouteStats: () => {
    return {
      fast: fastRouteStats,
      bright: brightRouteStats,
      current: currentRouteStats, // For backward compatibility
    };
  },
  zoomIn,
  zoomOut,
  resetNorth,
  toggleTilt,
  toggleFullscreen,
  getIsTilted: () => isTilted.value,
  clearRoute,
  zoomToCoordinates: (lon, lat, zoom = 15) => {
    if (!map || !map.isStyleLoaded()) {
      console.warn("Map not ready for zoom");
      return;
    }
    map.flyTo({
      center: [lon, lat],
      zoom: zoom,
      duration: 2000, // 2 seconds for smooth animation
      essential: true,
    });
  },
  zoomToAllHubs,
  animateRouteHexagons: async (routeId1, routeId2, coloringMode = "route") => {
    if (!map || !map.isStyleLoaded()) {
      console.warn("Map not ready for animation");
      return;
    }

    const routeName = `${Math.min(routeId1, routeId2)}_${Math.max(routeId1, routeId2)}`;
    const intersectionUrl =
      `${BASE}data/route_intersections/${routeName}.json`.replace(
        /\/{2,}/g,
        "/"
      );

    try {
      // Load intersection data
      const response = await fetch(intersectionUrl);
      if (!response.ok) {
        console.warn(`Intersection data not found for route ${routeName}`);
        return;
      }

      intersectionData = await response.json();
      console.log("Loaded intersection data:", intersectionData);

      // Load median data if in median mode
      if (coloringMode === "median" && !hexagonMedian) {
        const medianUrl = `${BASE}data/hexagon_median.json`.replace(
          /\/{2,}/g,
          "/"
        );
        try {
          const medianResponse = await fetch(medianUrl);
          if (medianResponse.ok) {
            const medianData = await medianResponse.json();
            hexagonMedian = medianData.median_score;
            console.log("Loaded hexagon median:", hexagonMedian);
          } else {
            console.warn("Median data not found, using route coloring");
            coloringMode = "route";
          }
        } catch (error) {
          console.warn("Error loading median data:", error);
          coloringMode = "route";
        }
      }

      // Get all hexagon IDs that intersect with either route
      const allIntersectingIds = new Set([
        ...intersectionData.fast_hex_ids,
        ...intersectionData.bright_hex_ids,
      ]);

      console.log(
        `Animating ${allIntersectingIds.size} hexagons (fast: ${intersectionData.fast_count}, bright: ${intersectionData.bright_count})`
      );

      // Animate hexagons appearing (using independent animation layers)
      await animateHexagonsReveal(
        Array.from(allIntersectingIds),
        intersectionData,
        coloringMode
      );

      routeAnimationActive = true;
    } catch (error) {
      console.error("Error loading or animating route hexagons:", error);
    }
  },
  updateAnimationColoring: async (routeId1, routeId2, coloringMode) => {
    // This function is kept for backward compatibility but is now mainly
    // used internally. External calls should use animateRouteHexagons instead.
    if (!map || !routeAnimationActive) {
      console.warn(
        "Cannot update coloring: map not available or animation not active"
      );
      return;
    }

    console.log(`Updating animation coloring to ${coloringMode} mode`);

    // Load median data if in median mode and not already loaded
    if (coloringMode === "median") {
      if (!hexagonMedian) {
        const medianUrl = `${BASE}data/hexagon_median.json`.replace(
          /\/{2,}/g,
          "/"
        );
        try {
          console.log("Loading median data from:", medianUrl);
          const medianResponse = await fetch(medianUrl);
          if (medianResponse.ok) {
            const medianData = await medianResponse.json();
            hexagonMedian = medianData.median_score;
            console.log("✓ Loaded hexagon median for update:", hexagonMedian);
          } else {
            console.error(
              `✗ Median data file not found (status: ${medianResponse.status})`
            );
            return; // Don't update if median can't be loaded
          }
        } catch (error) {
          console.error("✗ Error loading median data:", error);
          return; // Don't update if median can't be loaded
        }
      } else {
        console.log("Using cached hexagon median:", hexagonMedian);
      }
    }

    // Verify that features have required properties
    const animationSource = map.getSource("hex-route-animation");
    if (
      animationSource &&
      animationSource._data &&
      animationSource._data.features
    ) {
      const sampleFeature = animationSource._data.features[0];
      if (sampleFeature) {
        console.log(
          "Sample feature properties:",
          Object.keys(sampleFeature.properties)
        );
        if (coloringMode === "median") {
          console.log(
            "Sample combined_score:",
            sampleFeature.properties.combined_score
          );
          if (sampleFeature.properties.combined_score === undefined) {
            console.warn("Features don't have combined_score property!");
          }
        } else {
          console.log(
            "Sample route_type:",
            sampleFeature.properties.route_type
          );
          if (sampleFeature.properties.route_type === undefined) {
            console.warn("Features don't have route_type property!");
          }
        }
      }
    }

    // Update layer paint properties based on coloring mode immediately
    const fillLayerExists = map.getLayer("hex-route-animation-fill");
    const extrusionLayerExists = map.getLayer("hex-route-animation-layer");

    console.log(
      `Fill layer exists: ${!!fillLayerExists}, Extrusion layer exists: ${!!extrusionLayerExists}`
    );

    // Update both layers synchronously for instant color change
    // Apply colors immediately - no delays
    if (fillLayerExists) {
      updateLayerColoring("hex-route-animation-fill", coloringMode);
    }
    if (extrusionLayerExists) {
      updateLayerColoring("hex-route-animation-layer", coloringMode);
    }

    console.log(
      `✓ Updated animation coloring to ${coloringMode} mode (instant)`
    );
  },
  resetRouteAnimation,
  toggleRouteSecurityAlerts: async (routeId1, routeId2, enabled) => {
    if (!map || !map.isStyleLoaded()) {
      console.warn("Map not ready for security alerts");
      return;
    }

    routeSecurityAlertsActive = enabled;

    if (enabled) {
      // Load security alerts data
      const routeName = `${Math.min(routeId1, routeId2)}_${Math.max(routeId1, routeId2)}`;
      const alertsUrl =
        `${BASE}data/route_security_alerts/${routeName}.json`.replace(
          /\/{2,}/g,
          "/"
        );

      try {
        const response = await fetch(alertsUrl);
        if (!response.ok) {
          console.warn(`Security alerts data not found for route ${routeName}`);
          routeSecurityAlertsActive = false;
          return;
        }

        routeSecurityAlertsData = await response.json();
        console.log("Loaded security alerts:", routeSecurityAlertsData);

        // Apply security alerts to routes
        await applyRouteSecurityAlerts();
      } catch (error) {
        console.error("Error loading security alerts:", error);
        routeSecurityAlertsActive = false;
      }
    } else {
      // Remove security alert layers
      removeRouteSecurityAlerts();
      routeSecurityAlertsData = null;
    }
  },
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
  const endZoom = initialMapZoom; // Use the same zoom level as initial app load

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
  // Remove loading class from body
  document.body.classList.remove("map-loading");
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

/* Route Stats Popup - Glassmorphism style (more translucent) */
.route-stats-map-popup .mapboxgl-popup-content {
  background: rgba(255, 255, 255, 0.1) !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #000000 !important;
  padding: 1px 3px !important;
  border-radius: 8px !important;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
  border: none !important;
  min-width: auto !important;
  max-width: none !important;
  width: auto !important;
  backdrop-filter: blur(30px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
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
  box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4) !important;
  background-color: rgba(255, 255, 255, 0.18) !important;
  background: rgba(255, 255, 255, 0.18) !important;
}

.route-stats-map-popup .mapboxgl-popup-content.route-popup-clicked {
  transform: scale(0.95) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3) !important;
}

/* Bright route popup - slight bright blue tint */
.route-stats-map-popup--bright .mapboxgl-popup-content {
  background: rgba(100, 180, 255, 0.22) !important;
  background-color: rgba(100, 180, 255, 0.22) !important;
}

.route-stats-map-popup--bright .mapboxgl-popup-content:hover {
  background-color: rgba(100, 180, 255, 0.30) !important;
  background: rgba(100, 180, 255, 0.30) !important;
}

.route-stats-map-popup--bright .mapboxgl-popup-content.route-popup-clicked {
  background-color: rgba(100, 180, 255, 0.27) !important;
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

/* Bright route popup tip - slight bright blue tint */
.route-stats-map-popup--bright .mapboxgl-popup-tip {
  border-top-color: rgba(100, 180, 255, 0.22) !important;
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
  color: #ffffff !important;
}

.route-stats-map-popup .mapboxgl-popup-tip {
  border-top-color: rgba(255, 255, 255, 0.1) !important;
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
  gap: 3px !important;
  color: #ffffff !important;
  line-height: 1.1 !important;
  white-space: nowrap !important;
  vertical-align: top !important;
}

.route-stats-popup-label {
  display: block !important;
  color: #ffffff !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  line-height: 1.1 !important;
  margin-bottom: 2px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}

.route-stats-popup-bottom-line {
  display: block !important;
  color: #ffffff !important;
  line-height: 1.1 !important;
  margin-top: 1px !important;
  padding-left: 17px !important;
}

.route-stats-popup-icon {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  color: #ffffff !important;
  flex-shrink: 0 !important;
  width: 14px !important;
  height: 14px !important;
  vertical-align: middle !important;
}

.route-stats-popup-icon svg {
  width: 14px !important;
  height: 14px !important;
  fill: #ffffff !important;
  color: #ffffff !important;
  display: block !important;
}

.route-stats-popup-icon img {
  width: 14px !important;
  height: 14px !important;
  display: block !important;
  object-fit: contain !important;
  filter: brightness(0) invert(1) !important; /* Make icon white */
}

.route-stats-popup-text {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  line-height: 1.2 !important;
  color: #ffffff !important;
}

.route-stats-popup-duration,
.route-stats-map-popup .route-stats-popup-duration,
.route-stats-popup .route-stats-popup-duration {
  font-size: 16px !important;
  font-weight: 800 !important;
  color: #ffffff !important;
  line-height: 1.1 !important;
  margin: 0 !important;
  padding: 0 !important;
  display: inline !important;
  white-space: nowrap !important;
  vertical-align: middle !important;
}

.route-stats-popup-distance,
.route-stats-map-popup .route-stats-popup-distance,
.route-stats-popup .route-stats-popup-distance {
  font-size: 9px !important;
  font-weight: 400 !important;
  color: #ffffff !important;
  line-height: 1.1 !important;
  margin: 0 !important;
  padding: 0 !important;
  display: inline !important;
  white-space: nowrap !important;
}

/* Loading Screen */
.loading-screen {
  position: absolute;
  inset: 0;
  background: #1f1f21;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  pointer-events: none;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.loading-logo {
  font-size: 96px;
  font-weight: 600;
  color: #2f2f31;
  margin: 0;
  font-family: "Google Sans", "Product Sans", "Nunito", "Quicksand", "Comfortaa", "Varela Round", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  animation: loading-logo-fade 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.loading-dots {
  display: flex;
  gap: 10px;
  align-items: center;
  height: 16px;
}

.loading-dots .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #2f2f31;
  animation: loading-dot-wave 1.6s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  opacity: 0.4;
}

.loading-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.loading-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loading-logo-fade {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

@keyframes loading-dot-wave {
  0%,
  100% {
    opacity: 0.3;
    transform: translateY(0) scale(0.95);
  }
  50% {
    opacity: 1;
    transform: translateY(-4px) scale(1);
  }
}

/* Loading fade transition */
.loading-fade-enter-active,
.loading-fade-leave-active {
  transition: opacity 300ms ease;
}

.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
}

</style>

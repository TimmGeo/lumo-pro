<template>
  <div class="app">
    <!-- Main map viewer -->
    <MapboxViewer
      :mode="mode"
      :heightScale="heightScale"
      :showHubs="routingHubsVisible"
      @ready="onViewerReady"
      :focusZurichKey="zurichFocusKey"
      @zurichZoomComplete="handleZurichZoomComplete"
      @zoom="handleMapZoom"
      @move="handleMapMove"
    />

    <!-- Sidebar controls -->
    <aside
      :class="['sidebar', { 'sidebar--collapsed': sidebarCollapsed }]"
      :style="!sidebarCollapsed ? { width: sidebarWidth + 'px' } : {}"
      @mouseenter="isHovering = true"
      @mouseleave="handleMouseLeave"
    >
      <!-- Resize handle -->
      <div
        class="sidebar-resize-handle"
        @mousedown="startResize"
        @mouseenter="isResizing = true"
        @mouseleave="isResizing = false"
      ></div>
      <div class="sidebar-header">
        <h2 class="nowrap">Lumo <span class="muted">Pro</span></h2>

        <!-- square collapse button (quadratic) -->
        <button
          class="sidebar-toggle"
          @click="sidebarCollapsed = !sidebarCollapsed"
          :aria-expanded="!sidebarCollapsed"
          :aria-label="sidebarCollapsed ? 'Open sidebar' : 'Close sidebar'"
          title="Toggle sidebar"
        >
          <img
            src="/sidebar.svg"
            alt="Toggle sidebar"
            class="sidebar-toggle-icon"
            aria-hidden="true"
          />
        </button>
      </div>

      <!-- Scrollable content area -->
      <div
        ref="scrollableRef"
        class="sidebar-scrollable"
        :class="{ 'sidebar-scrollable--scrolling': isScrolling }"
      >
        <!-- Routing section -->
        <div class="group sidebar-content sidebar-routing">
          <div
            class="title title-collapsible"
            @click="routingCollapsed = !routingCollapsed"
          >
            Routing
            <span
              class="chevron"
              :class="{ 'chevron--expanded': !routingCollapsed }"
            >
              >
            </span>
          </div>
          <div
            class="section-content"
            :class="{ 'section-content--collapsed': routingCollapsed }"
          >
            <button
              :class="{ active: routingHubsVisible }"
              @click="toggleRoutingHubs"
            >
              <span class="button-icon">
                <img src="/routing_hubs.svg" alt="Routing hubs icon" />
              </span>
              Routing Hubs
            </button>

            <!-- Route planning -->
            <div class="sidebar-route-planning">
              <div class="route-clean">
                <div class="route-connector">
                  <div class="route-line"></div>
                  <div class="route-marker route-marker-start"></div>
                  <div class="route-marker route-marker-end"></div>
                </div>
                <div class="route-inputs">
                  <div class="route-input-wrapper">
                    <label
                      class="route-label-float"
                      :class="{ 'route-label-float--active': startHub }"
                      >From</label
                    >
                    <select v-model="startHub" class="route-select-clean">
                      <option disabled value=""></option>
                      <option v-for="h in hubs" :key="h.id" :value="h.id">
                        {{ h.name }}
                      </option>
                    </select>
                  </div>
                  <div class="route-input-wrapper">
                    <label
                      class="route-label-float"
                      :class="{ 'route-label-float--active': endHub }"
                      >To</label
                    >
                    <select v-model="endHub" class="route-select-clean">
                      <option disabled value=""></option>
                      <option v-for="h in hubs" :key="h.id" :value="h.id">
                        {{ h.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Layers -->
        <div class="group sidebar-content">
          <div
            class="title title-collapsible"
            @click="layersCollapsed = !layersCollapsed"
          >
            Layers
            <span
              class="chevron"
              :class="{ 'chevron--expanded': !layersCollapsed }"
            >
              >
            </span>
          </div>
          <div
            class="section-content"
            :class="{ 'section-content--collapsed': layersCollapsed }"
          >
            <button
              :class="{ active: mode === 'lighting' }"
              @click="mode = 'lighting'"
            >
              <span class="button-icon">
                <img src="/lighting.svg" alt="Lighting layer icon" />
              </span>
              Lighting
            </button>
            <button
              :class="{ active: mode === 'vibrancy' }"
              @click="mode = 'vibrancy'"
            >
              <span class="button-icon">
                <img src="/vibrancy.svg" alt="Vibrancy layer icon" />
              </span>
              Vibrancy
            </button>
            <button
              :class="{ active: mode === 'combined' }"
              @click="mode = 'combined'"
            >
              <span class="button-icon">
                <img src="/combined.svg" alt="Combined layer icon" />
              </span>
              Combined
            </button>
          </div>
        </div>

        <!-- Legend box placed inside the sidebar -->
        <div class="group sidebar-legend sidebar-content">
          <div
            class="title title-collapsible"
            @click="legendCollapsed = !legendCollapsed"
          >
            Color Legend
            <span
              class="chevron"
              :class="{ 'chevron--expanded': !legendCollapsed }"
            >
              >
            </span>
          </div>
          <div
            class="section-content"
            :class="{ 'section-content--collapsed': legendCollapsed }"
          >
            <div class="legend-box">
              <Legend :mode="mode" />
            </div>
          </div>
        </div>
      </div>

      <!-- Profile section (stays visible, text hides when collapsed) -->
      <div class="profile">
        <div class="avatar">JD</div>
        <div class="info">
          <div class="name">John Doe</div>
          <div class="tier">Plus</div>
        </div>
      </div>
    </aside>

    <!-- Hover popup -->
    <div
      v-if="popup.show"
      class="popup"
      :style="{ left: popup.x + 'px', top: popup.y + 'px' }"
    >
      <div class="row">
        <span>Lights</span><b>{{ popup.lights }}</b>
      </div>
      <div class="row">
        <span>POIs</span><b>{{ popup.pois }}</b>
      </div>
      <div class="row">
        <span>Nearest hub</span><b>{{ popup.hub }}</b>
      </div>
    </div>

    <!-- Walkthrough overlay shown on initial load -->
    <Walkthrough
      v-if="showWalkthrough"
      @close="showWalkthrough = false"
      @takeTour="startTour"
      @enterMap="focusZurich"
    />
    <GuidedTour v-if="showGuidedTour" @close="finishTour" />

    <!-- Scale indicator -->
    <div class="map-scale" :class="{ 'map-scale--visible': mapZoom >= 11 }">
      <div class="scale-line"></div>
      <div class="scale-label">{{ scaleText }}</div>
    </div>

    <!-- Location indicator -->
    <div
      class="map-location"
      :class="{ 'map-location--visible': mapZoom >= 11 && locationText }"
    >
      <div class="location-name">{{ locationText }}</div>
      <div class="location-time">{{ zurichTime }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue";
import MapboxViewer from "./components/MapboxViewer.vue";
import Legend from "./components/Legend.vue";
import Walkthrough from "./components/Walkthrough.vue";
import GuidedTour from "./components/GuidedTour.vue";

// UI state
const mode = ref("combined");
const heightScale = ref(1.5);
const startHub = ref("");
const endHub = ref("");
const hubs = ref([
  { id: "HB", name: "Zürich HB" },
  { id: "BEL", name: "Bellevue" },
  { id: "LS", name: "Langstrasse" },
  { id: "EW", name: "Escher-Wyss" },
]);

// Hover popup data
const popup = ref({ show: false, x: 0, y: 0, lights: 0, pois: 0, hub: "—" });

let api = null;

// sidebar collapse state
const sidebarCollapsed = ref(false);
const sidebarWidth = ref(320);
const isResizing = ref(false);
const showWalkthrough = ref(true);
const routingHubsVisible = ref(true);
const showGuidedTour = ref(false);
const zurichFocusKey = ref(0);
const pendingTourAfterZoom = ref(false);

// Section collapse states
const routingCollapsed = ref(false);
const layersCollapsed = ref(false);
const legendCollapsed = ref(false);

// Map scale state
const mapZoom = ref(1.2);
const mapCenter = ref([0, 18]);
const scaleText = ref("1 km");
const locationText = ref("");
const zurichTime = ref("");

// Update Zürich time
function updateZurichTime() {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Zurich",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  zurichTime.value = formatter.format(now);
}

// Set up time update interval
let timeInterval = null;
onMounted(() => {
  updateZurichTime();
  timeInterval = setInterval(updateZurichTime, 1000); // Update every second
});

onBeforeUnmount(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
});

// Calculate scale based on zoom level
function calculateScale(zoom, center) {
  // Reference: 120px on screen at current zoom
  const pixels = 120;
  const metersPerPixel =
    (156543.03392 * Math.cos((center[1] * Math.PI) / 180)) / Math.pow(2, zoom);
  const meters = metersPerPixel * pixels;

  // Format the scale text adaptively
  if (meters >= 1000) {
    const km = meters / 1000;
    if (km >= 10) {
      return `${Math.round(km)} km`;
    } else if (km >= 1) {
      return `${(Math.round(km * 10) / 10).toFixed(1)} km`;
    } else {
      return `${Math.round(meters)} m`;
    }
  } else if (meters >= 100) {
    return `${Math.round(meters / 50) * 50} m`;
  } else if (meters >= 10) {
    return `${Math.round(meters / 10) * 10} m`;
  } else {
    return `${Math.round(meters)} m`;
  }
}

function updateLocation(zoom) {
  // Simply show "Zürich" when zoomed in enough
  if (zoom >= 11) {
    locationText.value = "Zürich";
  } else {
    locationText.value = "";
  }
}

function handleMapZoom(event) {
  mapZoom.value = event.zoom;
  mapCenter.value = [event.center.lng, event.center.lat];
  scaleText.value = calculateScale(event.zoom, [
    event.center.lng,
    event.center.lat,
  ]);
  updateLocation(event.zoom);
}

function handleMapMove(event) {
  mapZoom.value = event.zoom;
  mapCenter.value = [event.center.lng, event.center.lat];
  scaleText.value = calculateScale(event.zoom, [
    event.center.lng,
    event.center.lat,
  ]);
  updateLocation(event.zoom);
}

// Scrollbar visibility
const scrollableRef = ref(null);
const isScrolling = ref(false);
let scrollTimeout = null;

function handleScroll() {
  // Show scrollbar immediately when scrolling
  isScrolling.value = true;

  // Clear existing timeout
  if (scrollTimeout) {
    clearTimeout(scrollTimeout);
  }

  // Hide scrollbar after scrolling stops (0.3s delay)
  scrollTimeout = setTimeout(() => {
    isScrolling.value = false;
    scrollTimeout = null;
  }, 300);
}

onMounted(async () => {
  await nextTick();
  if (scrollableRef.value) {
    scrollableRef.value.addEventListener("scroll", handleScroll, {
      passive: true,
    });
    // Also listen for wheel events to catch mouse wheel scrolling
    scrollableRef.value.addEventListener("wheel", handleScroll, {
      passive: true,
    });
    // Listen for touch events on mobile
    scrollableRef.value.addEventListener("touchmove", handleScroll, {
      passive: true,
    });
  }
});

onBeforeUnmount(() => {
  if (scrollTimeout) {
    clearTimeout(scrollTimeout);
  }
  if (scrollableRef.value) {
    scrollableRef.value.removeEventListener("scroll", handleScroll);
    scrollableRef.value.removeEventListener("wheel", handleScroll);
    scrollableRef.value.removeEventListener("touchmove", handleScroll);
  }
});

// When Mapbox viewer is ready (will be implemented in MapboxViewer)
function onViewerReady(exposed) {
  api = exposed;
  if (api && api.onHover) {
    api.onHover((info) => {
      if (!info) {
        popup.value.show = false;
        return;
      }
      popup.value = { show: true, ...info };
    });
  }
}

// Trigger routing between hubs
async function route() {
  if (
    !api ||
    !startHub.value ||
    !endHub.value ||
    startHub.value === endHub.value
  )
    return;

  if (api.drawRoute) {
    await api.drawRoute(startHub.value, endHub.value);
  }
}

// Swap hubs function
function swapHubs() {
  const a = startHub.value;
  startHub.value = endHub.value;
  endHub.value = a;
}

function toggleRoutingHubs() {
  routingHubsVisible.value = !routingHubsVisible.value;
}

function startTour() {
  showWalkthrough.value = false;
  pendingTourAfterZoom.value = true;
}

function finishTour() {
  showGuidedTour.value = false;
}

function focusZurich() {
  zurichFocusKey.value = Date.now();
}

function handleZurichZoomComplete() {
  if (!pendingTourAfterZoom.value) return;
  showGuidedTour.value = true;
  pendingTourAfterZoom.value = false;
}

// Sidebar resize functionality
function startResize(e) {
  e.preventDefault();
  const startX = e.clientX;
  const startWidth = sidebarWidth.value;

  function handleMouseMove(e) {
    const diff = e.clientX - startX;
    const newWidth = Math.max(240, Math.min(600, startWidth + diff));
    sidebarWidth.value = newWidth;
  }

  function handleMouseUp() {
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
    isResizing.value = false;
  }

  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseup", handleMouseUp);
  isResizing.value = true;
}
</script>

<style>
/* -------- GLOBAL LAYOUT -------- */
html,
body,
#app {
  height: 100%;
  margin: 0;
  background: #0b0b0c;
  color: #eaeaea;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.app {
  position: relative;
  height: 100%;
  overflow: hidden;
}

/* Remove blue focus outlines globally */
*:focus,
*:focus-visible,
*:focus-within {
  outline: none !important;
  box-shadow: none !important;
}

button:focus,
button:focus-visible,
input:focus,
input:focus-visible,
select:focus,
select:focus-visible,
textarea:focus,
textarea:focus-visible {
  outline: none !important;
  box-shadow: none !important;
  border-color: transparent !important;
}

/* -------- SIDEBAR -------- */
.sidebar {
  position: absolute;
  top: 20px;
  left: 20px;
  bottom: 20px;
  width: 320px;
  padding: 20px 16px 16px 20px;
  background: #151517;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  z-index: 10;
  border-radius: 16px;

  display: flex;
  flex-direction: column;
  justify-content: space-between; /* keep profile pinned */
}

/* Resize handle */
.sidebar-resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  z-index: 11;
  background: transparent;
  transition: background-color 0.2s ease;
}

.sidebar-resize-handle:hover,
.sidebar-resize-handle:active {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar--collapsed .sidebar-resize-handle {
  display: none;
}

/* Scrollable content area */
.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  margin-right: -4px;
}

/* Custom scrollbar styling */
.sidebar-scrollable::-webkit-scrollbar {
  width: 8px;
}

.sidebar-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-scrollable::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sidebar-scrollable--scrolling::-webkit-scrollbar-thumb {
  opacity: 1;
}

.sidebar-scrollable--scrolling::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.sidebar h2 {
  margin: 6px 0 0 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.sidebar h2 .muted {
  color: #b9b9c0;
  font-weight: 600;
}
.nowrap {
  white-space: nowrap;
}

.sidebar .group {
  margin-top: 18px;
}

.sidebar-routing {
  position: relative;
  padding-top: 20px;
  margin-top: 24px;
}

.sidebar-routing::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
}
.sidebar .title {
  color: #b8bcc0;
  font-size: 14px;
  letter-spacing: 0.02em;
  margin-bottom: 16px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.title-collapsible {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.chevron {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
  line-height: 1;
  flex-shrink: 0;
  display: inline-block;
  transform: scaleY(1.3);
  opacity: 0;
}

.group:hover .chevron {
  opacity: 1;
}

.chevron--expanded {
  transform: scaleX(1.3) rotate(90deg);
}

.section-content {
  overflow: hidden;
  max-height: 1000px;
  transition:
    max-height 0.3s ease,
    opacity 0.2s ease;
  opacity: 1;
}

.section-content--collapsed {
  max-height: 0;
  opacity: 0;
  margin-bottom: 0;
}
.sidebar .hint {
  color: #eaeaea;
  font-size: 13px;
  margin-bottom: 8px;
}

/* generic sidebar controls – exclude the toggle from this rule */
.sidebar button:not(.sidebar-toggle),
.sidebar select,
.sidebar input[type="range"] {
  width: 100%;
  margin-bottom: 8px;
  padding: 12px 12px;
  border-radius: 12px;
  background: #151517;
  border: 1px solid transparent;
  color: #eaeaea;
  font-size: 14px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  text-align: left;
  cursor: pointer;
  outline: none;
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar button.active {
  background: #1c1e21;
}
.sidebar button .button-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.sidebar button .button-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.sidebar button:not(.sidebar-toggle):hover {
  background: #2a2f34;
}

/* header with square toggle */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

/* square toggle: same size in expanded & collapsed sidebar */
.sidebar-toggle {
  flex: 0 0 auto;
  width: 30px;
  height: 30px; /* quadratic */
  box-sizing: border-box;
  padding: 0;

  border-radius: 8px;
  display: grid;
  place-items: center;
  background: #151517;
  color: #e6e6e8;
  cursor: pointer;
  outline: none !important;
  box-shadow: none !important;
  border: none;
}
.sidebar-toggle:hover {
  background: #2a2f34;
}

.sidebar-toggle:active {
  background: #1c1e21;
}

.sidebar-toggle:focus,
.sidebar-toggle:focus-visible {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
}
.sidebar-toggle-icon {
  width: 18px;
  height: 18px;
  display: block;
  object-fit: contain;
}

/* collapse behaviour */
.sidebar--collapsed {
  width: 40px;
  padding-left: 20px;
  padding-right: 8px;
  overflow: visible;
  border-radius: 16px;
}

.sidebar--collapsed .sidebar-scrollable {
  display: none;
}

/* hide layer / legend content */
.sidebar-content {
  transition:
    opacity 200ms ease,
    transform 200ms ease;
}
.sidebar--collapsed .sidebar-content {
  opacity: 0;
  transform: translateX(-6px);
  pointer-events: none;
  height: 0;
}

/* when collapsed: hide title but keep toggle */
.sidebar--collapsed .sidebar-header h2 {
  display: none;
}

/* -------- ROUTE PLANNING -------- */
.sidebar-route-planning {
  margin-top: 16px;
}

.route-clean {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 2px 0;
}

.route-connector {
  position: relative;
  width: 16px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 6px;
  padding-bottom: 6px;
}

.route-line {
  position: absolute;
  left: 50%;
  top: 12px;
  bottom: 12px;
  width: 1px;
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-50%);
}

.route-marker {
  position: relative;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #151517;
  border: 2px solid rgba(255, 255, 255, 0.4);
  z-index: 1;
}

.route-marker-start {
  margin-bottom: 18px;
}

.route-marker-end {
  margin-top: 18px;
}

.route-inputs {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.route-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.route-label-float {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
  pointer-events: none;
  transition: all 0.2s ease;
  z-index: 1;
}

.route-label-float--active {
  top: 0;
  transform: translateY(0);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.route-select-clean {
  flex: 1;
  padding: 8px 24px 8px 0;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  color: #eaeaea;
  font-size: 13px;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, rgba(255, 255, 255, 0.5) 50%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.5) 50%, transparent 50%);
  background-position:
    calc(100% - 8px) calc(50% - 1px),
    calc(100% - 2px) calc(50% + 1px);
  background-size:
    4px 4px,
    4px 4px;
  background-repeat: no-repeat;
  transition:
    border-color 0.2s ease,
    padding-top 0.2s ease;
}

.route-input-wrapper:has(.route-label-float--active) .route-select-clean,
.route-input-wrapper:has(.route-select-clean:focus) .route-select-clean {
  padding-top: 16px;
  padding-bottom: 4px;
}

.route-input-wrapper:has(.route-select-clean:focus) .route-label-float {
  top: 0;
  transform: translateY(0);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.route-select-clean:hover {
  border-bottom-color: rgba(255, 255, 255, 0.25);
}

.route-select-clean:focus {
  border-bottom-color: rgba(255, 255, 255, 0.25);
  outline: none;
  box-shadow: none;
}

.route-swap-clean {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.route-swap-clean:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.route-swap-clean:active {
  background: rgba(255, 255, 255, 0.15);
}

/* -------- LEGEND BOX -------- */
.sidebar-legend {
  margin-top: 16px;
}
.legend-box {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 18px;
  background: linear-gradient(180deg, #202124 0%, #171718 100%);
  border: 1px solid #232428;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  box-sizing: border-box;
}

/* -------- PROFILE SECTION -------- */
.profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 14px;
  margin-top: auto;
  border-top: 1px solid #1f2125;
  padding-bottom: 6px;
}

.profile .avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #33343a, #1e1f23);
  color: #eaeaea;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile .info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.profile .name {
  font-size: 14px;
  font-weight: 500;
}

.profile .tier {
  font-size: 12px;
  color: #9aa0a6;
}

/* when collapsed: keep only avatar, hide text */
.sidebar--collapsed .profile .info {
  display: none;
}
.sidebar--collapsed .profile {
  border-top: none;
  padding-top: 0;
  padding-bottom: 6px;
}

/* -------- POPUP -------- */
.popup {
  position: absolute;
  transform: translate(12px, -12px);
  background: #151517;
  border: 1px solid #2a2f34;
  padding: 10px 12px;
  border-radius: 12px;
  pointer-events: none;
  opacity: 0.95;
  z-index: 11;
}

.popup .row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

/* -------- LEGEND COMPONENT Z-INDEX -------- */
.legend {
  z-index: 9;
}

/* -------- MAP SCALE -------- */
.map-scale {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 12;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  pointer-events: none;
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 0.4s ease,
    transform 0.4s ease;
}

.map-scale--visible {
  opacity: 1;
  transform: translateY(0);
}

.scale-line {
  width: 120px;
  height: 3px;
  background: rgba(255, 255, 255, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(0, 0, 0, 0.3);
}

.scale-label {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.85);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
  letter-spacing: 0.01em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* -------- MAP LOCATION -------- */
.map-location {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 12;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  pointer-events: none;
  opacity: 0;
  transform: translateY(-10px);
  transition:
    opacity 0.4s ease,
    transform 0.4s ease;
}

.map-location--visible {
  opacity: 1;
  transform: translateY(0);
}

.location-name {
  font-size: 26px;
  color: #ffffff;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 600;
  letter-spacing: -0.01em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
}

.location-time {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
  letter-spacing: 0.01em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
}
</style>

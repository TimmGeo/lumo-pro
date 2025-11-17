<template>
  <div class="app">
    <!-- Main map viewer -->
    <MapboxViewer
      :mode="mode"
      :heightScale="heightScale"
      @ready="onViewerReady"
    />

    <!-- Floating Routing Dock (top-right, dark & compact) -->
    <div class="routingdock routingdock--compact">
      <div class="rd-card">
        <div class="rd-rail">
          <span class="dot"></span>
          <span class="line"></span>
          <span class="dot"></span>
        </div>

        <div class="rd-fields">
          <div class="rd-field">
            <select v-model="startHub" class="rd-input">
              <option disabled value="">From</option>
              <option v-for="h in hubs" :key="h.id" :value="h.id">
                {{ h.name }}
              </option>
            </select>
          </div>

          <div class="rd-divider"></div>

          <div class="rd-field">
            <select v-model="endHub" class="rd-input">
              <option disabled value="">To</option>
              <option v-for="h in hubs" :key="h.id" :value="h.id">
                {{ h.name }}
              </option>
            </select>
          </div>
        </div>

        <button class="rd-swap" @click="swapHubs()" aria-label="Swap">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M7 4v12M7 4l-3 3M7 4l3 3M17 20V8M17 20l-3-3M17 20l3-3"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Sidebar controls -->
    <aside :class="['sidebar', { 'sidebar--collapsed': sidebarCollapsed }]">
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
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            <rect
              x="4"
              y="4"
              width="16"
              height="16"
              rx="3"
              stroke="currentColor"
              stroke-width="1.2"
              fill="transparent"
            />
          </svg>
        </button>
      </div>

      <!-- Layers -->
      <div class="group sidebar-content">
        <div class="title">Layers</div>
        <button
          :class="{ active: mode === 'lighting' }"
          @click="mode = 'lighting'"
        >
          Lighting
        </button>
        <button
          :class="{ active: mode === 'vibrancy' }"
          @click="mode = 'vibrancy'"
        >
          Vibrancy
        </button>
        <button
          :class="{ active: mode === 'combined' }"
          @click="mode = 'combined'"
        >
          Combined
        </button>
      </div>

      <!-- Legend box placed inside the sidebar -->
      <div class="group sidebar-legend sidebar-content">
        <div class="title">Color Legend</div>
        <div class="legend-box">
          <Legend :mode="mode" />
        </div>
      </div>

      <!-- Profile section (stays visible, text hides when collapsed) -->
      <div class="profile">
        <div class="avatar">TR</div>
        <div class="info">
          <div class="name">Timm Rogenmoser</div>
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
  </div>
</template>

<script setup>
import { ref } from "vue";
import MapboxViewer from "./components/MapboxViewer.vue";
import Legend from "./components/Legend.vue";

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
  font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
}

.app {
  position: relative;
  height: 100%;
  overflow: hidden;
}

/* -------- SIDEBAR -------- */
.sidebar {
  position: absolute;
  top: 0px;
  left: 0px;
  bottom: 0px;
  width: 260px;
  padding: 20px 16px 16px 20px;
  background: #151517;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  z-index: 10;

  display: flex;
  flex-direction: column;
  justify-content: space-between; /* keep profile pinned */
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
.sidebar .title {
  color: #9aa0a6;
  font-size: 12px;
  letter-spacing: 0.02em;
  margin-bottom: 16px;
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
  text-align: left;
  cursor: pointer;
  outline: none;
}

.sidebar button.active {
  background: #1c1e21;
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
}
.sidebar-toggle:hover {
  background: #2a2f34;
}

.sidebar-toggle:active {
  background: #1c1e21;
}

/* collapse behaviour */
.sidebar--collapsed {
  width: 40px;
  padding-left: 20px;
  padding-right: 8px;
  overflow: visible;
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

/* -------- LEGEND BOX -------- */
.sidebar-legend {
  margin-top: 16px;
}
.legend-box {
  width: 230px;
  height: 230px;
  border-radius: 18px;
  background: linear-gradient(180deg, #202124 0%, #171718 100%);
  border: 1px solid #232428;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
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

/* -------- ROUTING DOCK: dark, discrete, top-right -------- */
.routingdock {
  position: fixed;
  right: 16px;
  top: 16px;
  z-index: 20;
}

/* compact: matches sidebar look */
.routingdock--compact .rd-card {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: 10px;
  padding: 10px 46px 10px 12px;
  width: clamp(240px, 26vw, 320px);
  border-radius: 14px;
  background: #151517;
  color: #eaeaea;
  border: 1px solid #202124;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
}

/* left rail (subtle, dark theme) */
.rd-rail {
  display: grid;
  grid-template-rows: 12px 1fr 12px;
  align-items: center;
  justify-items: center;
  width: 16px;
  margin-right: 2px;
}
.rd-rail .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 1.4px solid #7b7f86;
  background: #0b0b0c;
}
.rd-rail .line {
  width: 2px;
  height: 100%;
  background: #2a2f34;
  border-radius: 2px;
}

/* fields column */
.rd-fields {
  flex: 1 1 auto;
  display: grid;
  grid-template-rows: 1fr auto 1fr;
  gap: 6px;
  min-width: 160px;
}
.rd-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.rd-label {
  font-size: 11px;
  color: #9aa0a6;
  letter-spacing: 0.04em;
}

/* compact select, dark */
.rd-input {
  appearance: none;
  background: transparent;
  border: none;
  border-bottom: 1px solid #232428;
  padding: 6px 26px 6px 0;
  font-size: 13.5px;
  color: #eaeaea;
  outline: none;
  background-image:
    linear-gradient(45deg, transparent 50%, #7b7f86 50%),
    linear-gradient(135deg, #7b7f86 50%, transparent 50%);
  background-position:
    calc(100% - 12px) calc(50% - 3px),
    calc(100% - 6px) calc(50% + 3px);
  background-size:
    5px 5px,
    5px 5px;
  background-repeat: no-repeat;
}

.rd-input:focus {
  border-bottom-color: #2f343a;
}

.rd-divider {
  height: 1px;
  background: #232428;
}

/* swap button: small circle that matches dark UI */
.rd-swap {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid #232428;
  background: #1b1d21;
  color: #d6d6d9;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  display: grid;
  place-items: center;
  cursor: pointer;
}

.rd-swap:hover {
  background: #202329;
  border-color: #2a2f34;
}

.rd-swap:focus {
  outline: 2px solid #2f343a;
  outline-offset: 2px;
}

/* very small screens: stretch slightly but keep discrete look */
@media (max-width: 520px) {
  .routingdock--compact .rd-card {
    width: 92vw;
  }
}
</style>

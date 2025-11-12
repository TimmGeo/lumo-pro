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
    <aside class="sidebar">
      <h2>Lumo <span class="muted">Pro</span></h2>

      <!-- Layers -->
      <div class="group">
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

      <!-- Height exaggeration -->
      <div class="group" v-if="mode !== 'lighting'">
        <div class="title">Height exaggeration</div>
        <input
          type="range"
          min="0"
          max="3"
          step="0.1"
          v-model.number="heightScale"
        />
      </div>

      <!-- Profile section -->
      <div class="profile">
        <div class="avatar">TR</div>
        <div class="info">
          <div class="name">Timm Rogenmoser</div>
          <div class="tier">Plus</div>
        </div>
      </div>
    </aside>

    <!-- Dynamic legend -->
    <Legend :mode="mode" />

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
}

.sidebar h2 {
  margin: 6px 0 20px 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: 0.2px;
}

.sidebar h2 .muted {
  color: #b9b9c0;
  font-weight: 600;
}

.sidebar .group {
  margin-top: 18px;
}

.sidebar .title {
  color: #9aa0a6;
  font-size: 2 rem;
  margin-bottom: 16px;
}

.sidebar .hint {
  color: #eaeaea;
  font-size: 13px;
  margin-bottom: 8px;
}

.sidebar button,
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

.sidebar button:hover {
  background: #2a2f34;
}

/* Select polish (consistent height + caret) */
.sidebar select {
  appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, #7b7f86 50%),
    linear-gradient(135deg, #7b7f86 50%, transparent 50%);
  background-position:
    calc(100% - 18px) calc(50% - 3px),
    calc(100% - 12px) calc(50% + 3px);
  background-size:
    6px 6px,
    6px 6px;
  background-repeat: no-repeat;
  padding-right: 28px;
}

/* Range styling */
.sidebar input[type="range"] {
  height: 36px;
  background: transparent;
  padding: 0 4px;
  cursor: ew-resize;
}
.sidebar input[type="range"]::-webkit-slider-runnable-track {
  height: 6px;
  background: #2a2f34;
  border-radius: 999px;
}
.sidebar input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  margin-top: -6px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #eaeaea;
  border: 2px solid #0b0b0c;
}

/* -------- PROFILE SECTION -------- */
.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* keep profile pinned */
}

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
  width: 36px;
  height: 36px;
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

/* -------- LEGEND -------- */
.legend {
  z-index: 9;
}

/* -------- ROUTING DOCK: dark, discrete, top-right -------- */
.routingdock {
  position: fixed;
  right: 16px;
  top: 16px; /* moved to the TOP-RIGHT */
  z-index: 20;
}

/* compact: matches sidebar look */
.routingdock--compact .rd-card {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: 10px;
  padding: 10px 46px 10px 12px; /* tighter padding */
  width: clamp(240px, 26vw, 320px); /* smaller & discrete */
  border-radius: 14px;
  background: #151517; /* same base as sidebar */
  color: #eaeaea;
  border: 1px solid #202124; /* like sidebar border */
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

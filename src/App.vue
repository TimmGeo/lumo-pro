<template>
  <div class="app">
    <!-- Main map viewer -->
    <CesiumViewer
      :mode="mode"
      :heightScale="heightScale"
      @ready="onViewerReady"
    />

    <!-- Sidebar controls -->
    <aside class="sidebar">
      <h2>Lumo <span class="muted">Pro</span></h2>

      <!-- Routing -->
      <div class="group">
        <div class="title">Routing</div>
        <div class="hint">Routing Hubs</div>
        <select v-model="startHub">
          <option disabled value="">Start hub…</option>
          <option v-for="h in hubs" :key="h.id" :value="h.id">
            {{ h.name }}
          </option>
        </select>
        <select v-model="endHub">
          <option disabled value="">Destination hub…</option>
          <option v-for="h in hubs" :key="h.id" :value="h.id">
            {{ h.name }}
          </option>
        </select>
        <button @click="route()">Find bright route</button>
      </div>

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
import CesiumViewer from "./components/CesiumViewer.vue";
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

// When Cesium viewer is ready
function onViewerReady(exposed) {
  api = exposed;
  api.onHover((info) => {
    if (!info) {
      popup.value.show = false;
      return;
    }
    popup.value = { show: true, ...info };
  });
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
  await api.drawRoute(startHub.value, endHub.value);
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
</style>

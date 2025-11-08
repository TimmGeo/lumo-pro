<template>
  <div class="app">
    <!-- Main map viewer -->
    <CesiumViewer
      :mode="mode"
      :heightScale="heightScale"
      @ready="onViewerReady"
    />

    <!-- Floating header -->
    <header class="topbar">Lumo — Walk the (b)right Way</header>

    <!-- Sidebar controls -->
    <aside class="sidebar">
      <h2>Lumo Pro</h2>

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

      <div class="group">
        <div class="title">Routing (hubs)</div>
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
  width: 300px;
  padding: 16px;
  background: #151517;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  z-index: 10;
}

.sidebar h3 {
  margin: 0 0 8px 0;
}

.sidebar .group {
  margin-top: 14px;
}

.sidebar .title {
  color: #9aa0a6;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.sidebar button,
.sidebar select,
.sidebar input[type="range"] {
  width: 100%;
  margin-bottom: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #1d1e20;
  border: 1px solid transparent;
  color: #eaeaea;
  cursor: pointer;
}

.sidebar button.active {
  background: #22262a;
  border-color: #2a2f34;
  box-shadow: 0 0 0 1px #2a2f34 inset;
}

.sidebar button:hover {
  background: #2a2f34;
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

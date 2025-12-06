<template>
  <div class="legend-container" :class="{ 'legend-container--empty': !mode }">
    <!-- Empty state when no layer is selected -->
    <div v-if="!mode" class="legend-empty-state">
      <div class="empty-message">
        Select a layer in the "Layers" section of the left sidebar to view its
        legend
      </div>
      <button class="open-layers-button" @click="openLayersSection">
        Open layers section
      </button>
    </div>

    <!-- Lighting Layer Legend -->
    <div v-else-if="mode === 'lighting'" class="legend-simple">
      <div class="legend-item">
        <div class="legend-item-header">
          <div class="legend-item-title">Lighting Intensity</div>
        </div>
        <div class="legend-item-content">
          <div class="legend-simple-scale">
            <div class="scale-gradient scale-gradient-lighting"></div>
            <div class="scale-labels">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>
          <div class="legend-item-description">
            <span v-if="!lightingExpanded">
              The <strong>color gradient</strong> represents lighting intensity
              across Zurich.
              <button class="show-more-button" @click="lightingExpanded = true">
                Show more
              </button>
            </span>
            <span v-else>
              The <strong>color gradient</strong> represents lighting intensity
              across Zurich. <em>Darker areas</em> indicate lower lighting
              levels, while <em>brighter areas</em> show higher intensity. Use
              this layer to identify <strong>well-lit routes</strong> for safer
              nighttime navigation.
              <button
                class="show-more-button"
                @click="lightingExpanded = false"
              >
                Show less
              </button>
            </span>
          </div>
        </div>
      </div>

      <!-- Lighting Locations -->
      <div v-if="lightingLocations" class="lighting-locations">
        <!-- Highest Intensity -->
        <div class="locations-section">
          <div class="locations-section-title">Highest Intensity</div>
          <div class="locations-list">
            <div
              v-for="(loc, index) in lightingLocations.highest.slice(0, 3)"
              :key="index"
              class="location-button"
            >
              <div class="location-button-image-wrapper">
                <img
                  v-if="getLocationImage(loc.location)"
                  :src="getLocationImage(loc.location)"
                  :alt="loc.location"
                  class="location-button-image"
                />
                <div
                  v-else
                  class="location-button-image-placeholder"
                  :style="{
                    background: `linear-gradient(135deg, ${loc.color} 0%, ${adjustColorBrightness(loc.color, -20)} 100%)`,
                  }"
                >
                  <div
                    class="location-button-color-indicator"
                    :style="{ backgroundColor: loc.color }"
                  ></div>
                </div>
              </div>
              <div class="location-button-content">
                <div class="location-button-name">{{ loc.location }}</div>
                <div v-if="loc.description" class="location-button-description">
                  {{ loc.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Vibrancy Layer Legend -->
    <div v-else-if="mode === 'vibrancy'" class="legend-simple">
      <div class="legend-item">
        <div class="legend-item-header">
          <div class="legend-item-title">Urban Vibrancy</div>
        </div>
        <div class="legend-item-content">
          <div class="legend-simple-scale">
            <div class="scale-bars">
              <div class="scale-bar" style="height: 20%"></div>
              <div class="scale-bar" style="height: 40%"></div>
              <div class="scale-bar" style="height: 60%"></div>
              <div class="scale-bar" style="height: 80%"></div>
              <div class="scale-bar" style="height: 100%"></div>
            </div>
            <div class="scale-labels">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>
          <div class="legend-item-description">
            <span v-if="!vibrancyExpanded">
              The <strong>height of the 3D bars</strong> represents the density
              of Points of Interest.
              <button class="show-more-button" @click="vibrancyExpanded = true">
                Show more
              </button>
            </span>
            <span v-else>
              The <strong>height of the 3D bars</strong> represents the density
              of Points of Interest, including restaurants, cafes, bars, and
              entertainment venues. <em>Taller bars</em> indicate areas with
              higher urban vibrancy and more activity. This layer helps you find
              <strong>lively and engaging routes</strong> through Zurich's most
              vibrant neighborhoods.
              <button
                class="show-more-button"
                @click="vibrancyExpanded = false"
              >
                Show less
              </button>
            </span>
          </div>
        </div>
      </div>

      <!-- Vibrancy Locations -->
      <div v-if="vibrancyLocations" class="lighting-locations">
        <div class="locations-section">
          <div class="locations-section-title">Zurich's Vibrancy Hot-Spots</div>
          <div class="locations-list">
            <div
              v-for="(loc, index) in vibrancyLocations.highest.slice(0, 3)"
              :key="index"
              class="location-button"
            >
              <div class="location-button-image-wrapper">
                <div
                  class="location-button-image-placeholder"
                  :style="{
                    background: `linear-gradient(135deg, #6b7280 0%, #4b5563 100%)`,
                  }"
                >
                  <div
                    class="location-button-color-indicator"
                    style="background-color: #6b7280"
                  ></div>
                </div>
              </div>
              <div class="location-button-content">
                <div class="location-button-name">{{ loc.location }}</div>
                <div v-if="loc.description" class="location-button-description">
                  {{ loc.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Combined Layer Legend -->
    <div v-else-if="mode === 'combined'" class="legend-simple">
      <div class="legend-item">
        <div class="legend-item-header">
          <div class="legend-item-icon legend-icon-combined">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18M9 3v18" />
            </svg>
          </div>
          <div class="legend-item-title">Combined</div>
        </div>
        <div class="legend-item-content">
          <div class="legend-simple-scale">
            <div class="scale-combined">
              <div class="scale-combined-color">
                <div class="scale-gradient scale-gradient-lighting"></div>
                <span>Color = Lighting</span>
              </div>
              <div class="scale-combined-height">
                <div class="scale-bars">
                  <div class="scale-bar" style="height: 20%"></div>
                  <div class="scale-bar" style="height: 40%"></div>
                  <div class="scale-bar" style="height: 60%"></div>
                  <div class="scale-bar" style="height: 80%"></div>
                  <div class="scale-bar" style="height: 100%"></div>
                </div>
                <span>Height = Vibrancy</span>
              </div>
            </div>
          </div>
          <div class="legend-item-description">
            <span v-if="!combinedExpanded">
              This layer <strong>combines lighting intensity</strong> (shown by
              color) <em>and</em> <strong>urban vibrancy</strong> (shown by
              height) into a single visualization.
              <button class="show-more-button" @click="combinedExpanded = true">
                Show more
              </button>
            </span>
            <span v-else>
              This layer <strong>combines lighting intensity</strong> (shown by
              color) <em>and</em> <strong>urban vibrancy</strong> (shown by
              height) into a single visualization. It identifies areas that
              offer both <em>good lighting for safety</em> and
              <em>high activity for an engaging experience</em>. The
              <strong>generated routes</strong> in this application are based on
              this combined score, making it ideal for finding the
              <strong>best balanced routes</strong>.
              <button
                class="show-more-button"
                @click="combinedExpanded = false"
              >
                Show less
              </button>
            </span>
          </div>
        </div>
      </div>

      <!-- Combined Locations -->
      <div v-if="combinedLocations" class="lighting-locations">
        <div class="locations-section">
          <div class="locations-section-title">Highest Combined Score</div>
          <div class="locations-list">
            <div
              v-for="(loc, index) in combinedLocations.highest.slice(0, 3)"
              :key="index"
              class="location-button"
            >
              <div class="location-button-image-wrapper">
                <div
                  class="location-button-image-placeholder"
                  :style="{
                    background: `linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)`,
                  }"
                >
                  <div
                    class="location-button-color-indicator"
                    style="background-color: #60a5fa"
                  ></div>
                </div>
              </div>
              <div class="location-button-content">
                <div class="location-button-name">{{ loc.location }}</div>
                <div v-if="loc.description" class="location-button-description">
                  {{ loc.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const props = defineProps({
  mode: { type: String, required: false, default: null },
  draggedOut: { type: Boolean, default: false },
  inBox: { type: Boolean, default: false },
});

const emit = defineEmits(["openLayersSection"]);

function openLayersSection() {
  emit("openLayersSection");
}

const lightingLocations = ref(null);
const vibrancyLocations = ref(null);
const combinedLocations = ref(null);

const lightingExpanded = ref(false);
const vibrancyExpanded = ref(false);
const combinedExpanded = ref(false);

async function loadLightingLocations() {
  try {
    const BASE = import.meta.env.BASE_URL || "/";
    const url = `${BASE}data/lighting_locations.json?v=${Date.now()}`.replace(
      /\/{2,}/g,
      "/"
    );
    const response = await fetch(url);
    const data = await response.json();

    lightingLocations.value = {
      highest: data.highest ? data.highest.slice(0, 3) : [],
    };
  } catch (error) {
    console.error("Failed to load lighting locations:", error);
  }
}

async function loadVibrancyLocations() {
  try {
    const BASE = import.meta.env.BASE_URL || "/";
    const url = `${BASE}data/vibrancy_locations.json?v=${Date.now()}`.replace(
      /\/{2,}/g,
      "/"
    );
    const response = await fetch(url);
    const data = await response.json();

    vibrancyLocations.value = {
      highest: data.highest ? data.highest.slice(0, 3) : [],
    };
  } catch (error) {
    console.error("Failed to load vibrancy locations:", error);
  }
}

async function loadCombinedLocations() {
  try {
    const BASE = import.meta.env.BASE_URL || "/";
    const url = `${BASE}data/combined_locations.json?v=${Date.now()}`.replace(
      /\/{2,}/g,
      "/"
    );
    const response = await fetch(url);
    const data = await response.json();

    combinedLocations.value = {
      highest: data.highest ? data.highest.slice(0, 3) : [],
    };
  } catch (error) {
    console.error("Failed to load combined locations:", error);
  }
}

function getLocationImage(locationName) {
  // Map location names to image paths
  const BASE = import.meta.env.BASE_URL || "/";
  const imageMap = {
    "Escher Wyss": `${BASE}images/locations/escher-wyss.jpg`,
    Oerlikon: `${BASE}images/locations/oerlikon.jpg`,
    Hardbrücke: `${BASE}images/locations/hardbruecke.jpg`,
    Bahnhofstrasse: `${BASE}images/locations/bahnhofstrasse.jpg`,
    Limmatquai: `${BASE}images/locations/limmatquai.jpg`,
    Paradeplatz: `${BASE}images/locations/paradeplatz.jpg`,
  };

  // Return image path if exists, otherwise null
  // For now, return null to use placeholder
  return null;
}

function adjustColorBrightness(hex, percent) {
  // Simple function to adjust color brightness
  const num = parseInt(hex.replace("#", ""), 16);
  const r = Math.max(0, Math.min(255, (num >> 16) + percent));
  const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00ff) + percent));
  const b = Math.max(0, Math.min(255, (num & 0x0000ff) + percent));
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

onMounted(() => {
  loadLightingLocations();
  loadVibrancyLocations();
  loadCombinedLocations();
});
</script>

<style scoped>
.legend-container {
  width: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 0;
  box-sizing: border-box;
  position: relative;
}

.legend-container--empty {
  align-items: center;
  min-height: 100%;
  height: 100%;
}

.legend-simple {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0;
}

.legend-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-item-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
}

.legend-icon-lighting {
  color: #fbbf24;
}

.legend-icon-vibrancy {
  color: #6b7280;
}

.legend-icon-combined {
  color: #60a5fa;
}

.legend-item-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.01em;
}

.legend-item-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-simple-scale {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.scale-gradient {
  height: 24px;
  border-radius: 4px;
  width: 100%;
}

.scale-gradient-lighting {
  background: linear-gradient(
    to right,
    #1e293b 0%,
    #334155 25%,
    #475569 50%,
    #64748b 75%,
    #94a3b8 100%
  );
}

.scale-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 60px;
}

.scale-bar {
  flex: 1;
  background: linear-gradient(to top, #9ca3af 0%, #6b7280 100%);
  border-radius: 2px 2px 0 0;
  min-width: 8px;
  min-height: 4px;
}

.scale-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
}

.scale-combined {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.scale-combined-color,
.scale-combined-height {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.scale-combined-color span,
.scale-combined-height span {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
}

.legend-item-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  line-height: 1.5;
}

.legend-item-description strong {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.legend-item-description em {
  font-style: italic;
  color: rgba(255, 255, 255, 0.85);
}

.show-more-button {
  background: none;
  border: none;
  color: rgba(147, 197, 253, 0.9);
  font-size: 13px;
  font-weight: 600;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  cursor: pointer;
  padding: 0;
  margin: 0 4px;
  text-decoration: none;
  transition: color 0.2s ease;
  display: inline;
  white-space: nowrap;
}

.show-more-button:hover {
  color: rgba(147, 197, 253, 1);
}

/* Lighting Locations */
.lighting-locations {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.locations-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.locations-section-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

.locations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.location-button {
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: 0;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
  cursor: pointer;
  min-height: 100px;
}

.location-button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.location-button-image-wrapper {
  width: 120px;
  min-width: 120px;
  height: 100px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.location-button-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.location-button-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.location-button-color-indicator {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.location-button-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  min-width: 0;
}

.location-button-name {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.95);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
}

.location-button-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 400;
  line-height: 1.5;
  margin: 0;
}

/* Empty state */
.legend-empty-state {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  flex: 1;
  min-height: 300px;
  gap: 16px;
}

.empty-message {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
  letter-spacing: 0.01em;
  margin: 0;
}

.open-layers-button {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  font-weight: 500;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.open-layers-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.open-layers-button:active {
  transform: translateY(0);
}
</style>

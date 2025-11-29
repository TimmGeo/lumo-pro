<template>
  <div class="legend-container">

    <!-- Empty state when no layer is selected -->
    <div v-if="!mode" class="legend-empty-state">
      <div class="empty-message">No layer selected</div>
    </div>

    <!-- Lighting Layer Legend -->
    <div v-else-if="mode === 'lighting'" class="legend-content legend-lighting">
      <div class="legend-header">
        <div class="legend-title">Lighting Distribution</div>
        <div class="legend-subtitle">Color intensity represents lighting levels</div>
      </div>
      <div class="legend-card">
        <div class="legend-vertical-wrapper">
          <div class="legend-labels-vertical">
            <span class="label-max">
              <span class="label-text">High</span>
            </span>
            <span class="label-min">
              <span class="label-text">Low</span>
            </span>
          </div>
          <div
            class="histogram-container-vertical"
            v-if="colorHistogram.length > 0"
          >
            <div
              class="histogram-bar-vertical"
              v-for="(item, index) in colorHistogram"
              :key="index"
              :style="{
                width: item.height + '%',
                backgroundColor: item.color,
              }"
              :title="`${item.color}: ${item.count} hexagons`"
            >
              <div class="bar-label-vertical" v-if="item.height > 10">
                {{ item.count }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Vibrancy Layer Legend -->
    <div v-else-if="mode === 'vibrancy'" class="legend-content legend-vibrancy">
      <div class="legend-header">
        <div class="legend-title">Vibrancy (POI Density)</div>
        <div class="legend-subtitle">Height represents point of interest density</div>
      </div>
      <div class="legend-card">
        <div class="legend-vertical-wrapper">
          <div class="legend-labels-vertical">
            <span class="label-max">
              <span class="label-text">High</span>
            </span>
            <span class="label-min">
              <span class="label-text">Low</span>
            </span>
          </div>
          <div class="legend-bars-vertical">
            <div
              class="legend-bar-vertical"
              v-for="(bar, index) in vibrancyBars"
              :key="index"
              :style="{ height: bar.height + '%' }"
            >
              <div class="bar-fill-vertical"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="legend-note">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
        Height = POI Count
      </div>
    </div>

    <!-- Combined Layer Legend -->
    <div v-else-if="mode === 'combined'" class="legend-content legend-combined">
      <div class="legend-header">
        <div class="legend-title">Combined View</div>
        <div class="legend-subtitle">Lighting color + Vibrancy height</div>
      </div>
      <div class="combined-legend">
        <div class="combined-section">
          <div class="section-header">
            <div class="section-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <div class="section-label">Color = Lighting</div>
          </div>
          <div class="legend-card">
            <div class="legend-vertical-wrapper">
              <div class="legend-labels-vertical">
                <span class="label-max">
                  <span class="label-text">High</span>
                </span>
                <span class="label-min">
                  <span class="label-text">Low</span>
                </span>
              </div>
              <div
                class="histogram-container-vertical"
                v-if="colorHistogram.length > 0"
              >
                <div
                  class="histogram-bar-vertical"
                  v-for="(item, index) in colorHistogram"
                  :key="index"
                  :style="{
                    width: item.height + '%',
                    backgroundColor: item.color,
                  }"
                  :title="`${item.color}: ${item.count} hexagons`"
                >
                  <div class="bar-label-vertical" v-if="item.height > 10">
                    {{ item.count }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="section-divider"></div>
        <div class="combined-section">
          <div class="section-header">
            <div class="section-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v20M2 12h20"/>
              </svg>
            </div>
            <div class="section-label">Height = Vibrancy</div>
          </div>
          <div class="legend-card">
            <div class="legend-vertical-wrapper">
              <div class="legend-labels-vertical">
                <span class="label-max">
                  <span class="label-text">High</span>
                </span>
                <span class="label-min">
                  <span class="label-text">Low</span>
                </span>
              </div>
            <div class="legend-bars-vertical">
              <div
                class="legend-bar-vertical"
                v-for="(bar, index) in vibrancyBars"
                :key="index"
                :style="{ height: bar.height + '%' }"
              >
                <div class="bar-fill-vertical"></div>
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
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  mode: { type: String, required: false, default: null },
  draggedOut: { type: Boolean, default: false },
  inBox: { type: Boolean, default: false },
});

const hexData = ref(null);
const colorHistogram = ref([]);

// Load hex data to calculate color distribution
async function loadHexData() {
  try {
    const BASE = import.meta.env.BASE_URL || "/";
    const hexUrl = `${BASE}data/hex_light_100m.geojson`.replace(/\/{2,}/g, "/");
    const response = await fetch(hexUrl);
    const data = await response.json();
    hexData.value = data;

    // Calculate color histogram
    const colorCounts = new Map();
    if (data.features) {
      data.features.forEach((feature) => {
        const color = feature.properties?.color || "#969696";
        colorCounts.set(color, (colorCounts.get(color) || 0) + 1);
      });
    }

    // Convert to array and sort by count (descending)
    const sortedColors = Array.from(colorCounts.entries())
      .map(([color, count]) => ({ color, count }))
      .sort((a, b) => b.count - a.count);

    // Calculate max count for normalization
    const maxCount = Math.max(...sortedColors.map((item) => item.count));

    // Create histogram data with normalized heights
    colorHistogram.value = sortedColors.map((item) => ({
      color: item.color,
      count: item.count,
      height: (item.count / maxCount) * 100,
    }));
  } catch (error) {
    console.error("Failed to load hex data for legend:", error);
  }
}

onMounted(() => {
  loadHexData();
});

// Vibrancy bars - showing height progression
const vibrancyBars = computed(() => {
  return [
    { height: 20 },
    { height: 40 },
    { height: 60 },
    { height: 80 },
    { height: 100 },
  ];
});
</script>

<style scoped>
.legend-container {
  width: 100%;
  min-height: 300px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 20px 0;
  box-sizing: border-box;
  position: relative;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.legend-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  gap: 20px;
  padding: 0;
  box-sizing: border-box;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.legend-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
  padding-bottom: 0;
}

.legend-title {
  font-size: 15px;
  font-weight: 700;
  color: rgba(255, 255, 255, 1);
  text-align: left;
  margin: 0;
  padding: 0;
  letter-spacing: -0.01em;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  width: 100%;
  box-sizing: border-box;
}

.legend-subtitle {
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
  text-align: left;
  margin: 0;
  padding: 0;
  letter-spacing: 0.01em;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  line-height: 1.4;
}

.legend-card {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  transition: none;
}

/* Vertical Legend Wrapper */
.legend-vertical-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 14px;
  width: 100%;
  min-height: 200px;
  max-width: 100%;
  padding: 12px 0;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.legend-labels-vertical {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.75);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  min-height: 200px;
  padding: 8px 0;
  box-sizing: border-box;
  flex-shrink: 0;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.label-min,
.label-max {
  font-weight: 600;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.label-text {
  display: inline-block;
  padding: 0;
  background: transparent;
  border-radius: 0;
}

/* Vertical Histogram for Lighting/Combined */
.histogram-container-vertical {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  width: auto;
  min-width: 90px;
  gap: 4px;
  margin: 0;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
  flex: 1;
  min-height: 200px;
  max-height: 100%;
  box-sizing: border-box;
  overflow: hidden;
  transition: none;
  box-shadow: none;
}

.histogram-bar-vertical {
  flex: 1;
  min-height: 8px;
  max-height: 100%;
  border-radius: 0 4px 4px 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 5px;
  transition: opacity 0.2s ease;
  border: none;
  box-shadow: none;
  min-width: 14px;
  box-sizing: border-box;
}

.histogram-bar-vertical:hover {
  opacity: 0.9;
}

.bar-label-vertical {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  text-shadow:
    0 1px 4px rgba(0, 0, 0, 0.9),
    0 0 3px rgba(0, 0, 0, 0.6);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.label-min,
.label-max {
  font-weight: 600;
}

/* Lighting Legend */
.legend-lighting {
  justify-content: flex-start;
  align-items: stretch;
}

/* Vibrancy Legend */
.legend-vibrancy {
  justify-content: flex-start;
  align-items: stretch;
}

.legend-bars-vertical {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-end;
  width: auto;
  min-width: 90px;
  gap: 4px;
  margin: 0;
  padding: 0;
  flex: 1;
  min-height: 200px;
  max-height: 100%;
  background: transparent;
  border-radius: 0;
  border: none;
  box-sizing: border-box;
  overflow: hidden;
  transition: none;
  box-shadow: none;
}

.legend-bar-vertical {
  display: flex;
  align-items: flex-end;
  justify-content: flex-start;
  min-height: 8px;
  width: 100%;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.bar-fill-vertical {
  height: 100%;
  width: 100%;
  background: linear-gradient(to right, #9ca3af 0%, #6b7280 40%, #4b5563 80%, #374151 100%);
  border-radius: 0 4px 4px 0;
  min-width: 8px;
  opacity: 0.85;
  transition: opacity 0.2s ease;
  box-shadow: none;
  border: none;
}

.bar-fill-vertical:hover {
  opacity: 1;
}

.legend-bar {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  min-width: 8px;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(to top, #9ca3af 0%, #6b7280 100%);
  border-radius: 2px 2px 0 0;
  min-height: 4px;
  opacity: 0.8;
}

.legend-note {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  margin-top: 12px;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 400;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.legend-note svg {
  opacity: 0.6;
  flex-shrink: 0;
}

/* Combined Legend */
.legend-combined {
  justify-content: flex-start;
  align-items: stretch;
  gap: 0;
}

.combined-legend {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  justify-content: flex-start;
  align-items: stretch;
  width: 100%;
  padding: 8px 0;
}

.combined-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: stretch;
  justify-content: flex-start;
  width: 100%;
  max-width: 100%;
  flex: 1;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 0;
}

.section-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.section-icon svg {
  width: 100%;
  height: 100%;
}

.section-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  text-align: left;
  font-weight: 600;
  padding: 0;
  margin: 0;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  flex: 1;
  box-sizing: border-box;
  letter-spacing: 0.01em;
}

.section-divider {
  height: 0;
  background: transparent;
  margin: 16px 0;
  flex-shrink: 0;
}

.combined-section .histogram-wrapper {
  min-width: 150px;
}

.combined-section .histogram-container-vertical {
  width: auto;
  min-width: 50px;
  height: 100%;
  flex: 1;
}

.combined-section .legend-bars-vertical {
  width: auto;
  min-width: 50px;
  height: 100%;
  flex: 1;
}

/* Empty state */
.legend-empty-state {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 20px;
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
  padding: 40px 20px;
}
</style>

<template>
  <div
    class="legend-container"
    :class="{
      'legend-container--dragged': draggedOut || isDraggingOut,
      'legend-container--in-box': inBox && !draggedOut && !isDraggingOut,
      'legend-container--dragging-out':
        isDragging && (inBox || isDraggingOut) && !draggedOut,
    }"
    :style="
      draggedOut || isDraggingOut || (isDragging && inBox && !draggedOut)
        ? {
            left: (position.x || 0) + 'px',
            top: (position.y || 0) + 'px',
            width: draggedOut && size ? size.width + 'px' : undefined,
            height: draggedOut && size ? size.height + 'px' : undefined,
            opacity: draggedOut || isDraggingOut ? 1 : 0.9,
            transform: draggedOut || isDraggingOut ? 'none' : 'scale(1)',
            transition: 'none',
            willChange: 'transform, opacity',
          }
        : {}
    "
    @mousedown="handleMouseDown"
    @touchstart="handleMouseDown"
  >
    <!-- Close button when dragged out -->
    <button
      v-if="draggedOut"
      class="legend-close-btn"
      @click="handleClose"
      aria-label="Close legend"
    >
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path
          d="M1 1L13 13M13 1L1 13"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
    </button>

    <!-- Resize handles when dragged out -->
    <template v-if="draggedOut">
      <!-- Corner resize handles -->
      <div
        class="resize-handle resize-handle--nw"
        @mousedown.stop="handleResizeStart($event, 'nw')"
        @touchstart.stop="handleResizeStart($event, 'nw')"
      ></div>
      <div
        class="resize-handle resize-handle--ne"
        @mousedown.stop="handleResizeStart($event, 'ne')"
        @touchstart.stop="handleResizeStart($event, 'ne')"
      ></div>
      <div
        class="resize-handle resize-handle--sw"
        @mousedown.stop="handleResizeStart($event, 'sw')"
        @touchstart.stop="handleResizeStart($event, 'sw')"
      ></div>
      <div
        class="resize-handle resize-handle--se"
        @mousedown.stop="handleResizeStart($event, 'se')"
        @touchstart.stop="handleResizeStart($event, 'se')"
      ></div>
      <!-- Edge resize handles -->
      <div
        class="resize-handle resize-handle--n"
        @mousedown.stop="handleResizeStart($event, 'n')"
        @touchstart.stop="handleResizeStart($event, 'n')"
      ></div>
      <div
        class="resize-handle resize-handle--s"
        @mousedown.stop="handleResizeStart($event, 's')"
        @touchstart.stop="handleResizeStart($event, 's')"
      ></div>
      <div
        class="resize-handle resize-handle--e"
        @mousedown.stop="handleResizeStart($event, 'e')"
        @touchstart.stop="handleResizeStart($event, 'e')"
      ></div>
      <div
        class="resize-handle resize-handle--w"
        @mousedown.stop="handleResizeStart($event, 'w')"
        @touchstart.stop="handleResizeStart($event, 'w')"
      ></div>
    </template>

    <!-- Empty state when no layer is selected -->
    <div v-if="!mode" class="legend-empty-state">
      <div class="empty-message">No layer selected</div>
    </div>

    <!-- Lighting Layer Legend -->
    <div v-else-if="mode === 'lighting'" class="legend-content legend-lighting">
      <div class="legend-title">Lighting Distribution</div>
      <div class="legend-vertical-wrapper">
        <div class="legend-labels-vertical">
          <span class="label-max">High</span>
          <span class="label-min">Low</span>
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

    <!-- Vibrancy Layer Legend -->
    <div v-else-if="mode === 'vibrancy'" class="legend-content legend-vibrancy">
      <div class="legend-title">Vibrancy (POI Density)</div>
      <div class="legend-vertical-wrapper">
        <div class="legend-labels-vertical">
          <span class="label-max">High</span>
          <span class="label-min">Low</span>
        </div>
        <div class="legend-bars-vertical">
          <div
            class="legend-bar-vertical"
            v-for="(bar, index) in vibrancyBars"
            :key="index"
            :style="{ width: bar.height + '%' }"
          >
            <div class="bar-fill-vertical"></div>
          </div>
        </div>
      </div>
      <div class="legend-note">Height = POI Count</div>
    </div>

    <!-- Combined Layer Legend -->
    <div v-else-if="mode === 'combined'" class="legend-content legend-combined">
      <div class="legend-title">Combined View</div>
      <div class="combined-legend">
        <div class="combined-section">
          <div class="section-label">Color = Lighting</div>
          <div class="legend-vertical-wrapper">
            <div class="legend-labels-vertical">
              <span class="label-max">High</span>
              <span class="label-min">Low</span>
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
        <div class="combined-section">
          <div class="section-label">Height = Vibrancy</div>
          <div class="legend-vertical-wrapper">
            <div class="legend-labels-vertical">
              <span class="label-max">High</span>
              <span class="label-min">Low</span>
            </div>
            <div class="legend-bars-vertical">
              <div
                class="legend-bar-vertical"
                v-for="(bar, index) in vibrancyBars"
                :key="index"
                :style="{ width: bar.height + '%' }"
              >
                <div class="bar-fill-vertical"></div>
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
  position: { type: Object, default: () => ({ x: 100, y: 100 }) },
  size: { type: Object, default: () => ({ width: 280, height: 280 }) },
});

const emit = defineEmits([
  "take-out",
  "close",
  "position-update",
  "drag-back",
  "drag-start",
  "drag-end",
  "size-update",
]);

const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const wasInBox = ref(false);
const initialClickPos = ref({ x: 0, y: 0 });
const hasMoved = ref(false);
const dragThreshold = 3; // Very low threshold for immediate response
const currentDragPos = ref({ x: 0, y: 0 });
const offsetFromClick = ref({ x: 0, y: 0 }); // Offset from click position to legend center
const isDraggingOut = ref(false); // Track if currently dragging out

// Resize state
const isResizing = ref(false);
const resizeDirection = ref("");
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0, left: 0, top: 0 });
const minSize = { width: 200, height: 200 };
const maxSize = { width: 800, height: 800 };

function handleMouseDown(e) {
  // Don't start drag if clicking on resize handle
  if (e.target.classList && e.target.classList.contains("resize-handle")) {
    return;
  }

  // If in box, prepare for potential drag
  if (props.inBox && !props.draggedOut) {
    wasInBox.value = true;
    hasMoved.value = false;
    isDraggingOut.value = false;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    initialClickPos.value = { x: clientX, y: clientY };
    currentDragPos.value = { x: clientX, y: clientY };

    // Calculate offset from click to center of legend (140px is half of 280px)
    offsetFromClick.value = {
      x: 140, // Center the legend on cursor
      y: 140,
    };

    // Set drag start immediately for smooth transition
    dragStart.value = {
      x: clientX - offsetFromClick.value.x,
      y: clientY - offsetFromClick.value.y,
    };

    isDragging.value = true;
    // Don't emit drag-start - box should only highlight when dragging back in

    // Immediately show the legend following cursor (Adobe-style)
    const newPosition = {
      x: clientX - offsetFromClick.value.x,
      y: clientY - offsetFromClick.value.y,
    };
    emit("position-update", newPosition);

    e.preventDefault();
    e.stopPropagation();
    return;
  }

  // If already dragged out, continue dragging
  if (props.draggedOut) {
    isDragging.value = true;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    dragStart.value = {
      x: clientX - props.position.x,
      y: clientY - props.position.y,
    };

    e.preventDefault();
  }
}

function handleMouseMove(e) {
  if (!isDragging.value || isResizing.value) return;

  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  currentDragPos.value = { x: clientX, y: clientY };

  // If in box and not yet dragged out, check if moved enough
  if (props.inBox && !props.draggedOut && wasInBox.value) {
    const deltaX = clientX - initialClickPos.value.x;
    const deltaY = clientY - initialClickPos.value.y;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    // Always update position to follow cursor smoothly
    const newPosition = {
      x: clientX - offsetFromClick.value.x,
      y: clientY - offsetFromClick.value.y,
    };
    emit("position-update", newPosition);

    // Take out immediately when threshold is crossed
    if (distance > dragThreshold && !hasMoved.value) {
      hasMoved.value = true;
      isDraggingOut.value = true;
      emit("take-out");
      // Update drag start to maintain smooth dragging after take-out
      // Use the same calculation method for seamless transition
      dragStart.value = {
        x: clientX - newPosition.x,
        y: clientY - newPosition.y,
      };
    }
    return;
  }

  // If already dragged out OR if we've triggered take-out (smooth transition)
  // Continue dragging with consistent calculation
  if (props.draggedOut || isDraggingOut.value) {
    const newPosition = {
      x: clientX - dragStart.value.x,
      y: clientY - dragStart.value.y,
    };

    emit("position-update", newPosition);
  }
}

function handleMouseUp(e) {
  if (isDragging.value) {
    emit("drag-end"); // Notify parent to unhighlight box

    // If was in box but didn't move enough, don't take it out
    if (wasInBox.value && !hasMoved.value && !props.draggedOut) {
      // Just a click, reset position back to box
      emit("position-update", { x: 0, y: 0 });
    } else if (props.draggedOut || isDraggingOut.value) {
      // Emit drag-back event - parent will check if over box
      emit("drag-back");
    }

    // Reset all drag state
    wasInBox.value = false;
    hasMoved.value = false;
    isDraggingOut.value = false;
  }
  isDragging.value = false;
}

function handleClose() {
  emit("close");
}

function handleResizeStart(e, direction) {
  if (!props.draggedOut) return;

  isResizing.value = true;
  resizeDirection.value = direction;
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;

  resizeStart.value = {
    x: clientX,
    y: clientY,
    width: props.size.width,
    height: props.size.height,
    left: props.position.x,
    top: props.position.y,
  };

  e.preventDefault();
  e.stopPropagation();
}

function handleResizeMove(e) {
  if (!isResizing.value) return;

  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;

  const deltaX = clientX - resizeStart.value.x;
  const deltaY = clientY - resizeStart.value.y;

  let newWidth = resizeStart.value.width;
  let newHeight = resizeStart.value.height;
  let newLeft = resizeStart.value.left;
  let newTop = resizeStart.value.top;

  // Handle resize based on direction
  if (resizeDirection.value.includes("e")) {
    newWidth = Math.max(
      minSize.width,
      Math.min(maxSize.width, resizeStart.value.width + deltaX)
    );
  }
  if (resizeDirection.value.includes("w")) {
    newWidth = Math.max(
      minSize.width,
      Math.min(maxSize.width, resizeStart.value.width - deltaX)
    );
    newLeft = resizeStart.value.left + (resizeStart.value.width - newWidth);
  }
  if (resizeDirection.value.includes("s")) {
    newHeight = Math.max(
      minSize.height,
      Math.min(maxSize.height, resizeStart.value.height + deltaY)
    );
  }
  if (resizeDirection.value.includes("n")) {
    newHeight = Math.max(
      minSize.height,
      Math.min(maxSize.height, resizeStart.value.height - deltaY)
    );
    newTop = resizeStart.value.top + (resizeStart.value.height - newHeight);
  }

  emit("size-update", { width: newWidth, height: newHeight });
  emit("position-update", { x: newLeft, y: newTop });
}

function handleResizeEnd() {
  isResizing.value = false;
  resizeDirection.value = "";
}

onMounted(() => {
  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseup", handleMouseUp);
  document.addEventListener("touchmove", handleMouseMove);
  document.addEventListener("touchend", handleMouseUp);

  // Load hex data to calculate color distribution
  loadHexData();
});

onUnmounted(() => {
  document.removeEventListener("mousemove", handleMouseMove);
  document.removeEventListener("mouseup", handleMouseUp);
  document.removeEventListener("touchmove", handleMouseMove);
  document.removeEventListener("touchend", handleMouseUp);
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
  // Use capture phase to ensure we catch events even if they bubble
  document.addEventListener("mousemove", handleMouseMove, { passive: false });
  document.addEventListener("mouseup", handleMouseUp, { passive: false });
  document.addEventListener("touchmove", handleMouseMove, { passive: false });
  document.addEventListener("touchend", handleMouseUp, { passive: false });

  // Resize handlers
  document.addEventListener("mousemove", handleResizeMove);
  document.addEventListener("mouseup", handleResizeEnd);
  document.addEventListener("touchmove", handleResizeMove);
  document.addEventListener("touchend", handleResizeEnd);

  loadHexData();
});

onUnmounted(() => {
  document.removeEventListener("mousemove", handleMouseMove);
  document.removeEventListener("mouseup", handleMouseUp);
  document.removeEventListener("touchmove", handleMouseMove);
  document.removeEventListener("touchend", handleMouseUp);
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
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-sizing: border-box;
  position: relative;
}

.legend-container--in-box {
  cursor: move;
}

.legend-container--dragging-out {
  position: fixed;
  width: 280px;
  height: 280px;
  background: linear-gradient(180deg, #1a1b1e 0%, #141517 100%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 24px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  z-index: 10000;
  cursor: grabbing !important;
  user-select: none;
  transition: none;
  pointer-events: none;
  will-change: transform, opacity;
  backface-visibility: hidden;
  transform-origin: center center;
}

.legend-container--dragged {
  position: fixed;
  width: 280px;
  height: 280px;
  background: linear-gradient(180deg, #1a1b1e 0%, #141517 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  z-index: 10000;
  cursor: move;
  user-select: none;
  will-change: transform;
  backface-visibility: hidden;
  box-sizing: border-box;
  resize: none;
  overflow: hidden;
}

.legend-container--dragged:active {
  cursor: grabbing !important;
}

/* Resize handles */
.resize-handle {
  position: absolute;
  background: transparent;
  z-index: 10001;
}

.resize-handle--nw {
  top: 0;
  left: 0;
  width: 12px;
  height: 12px;
  cursor: nwse-resize;
}

.resize-handle--ne {
  top: 0;
  right: 0;
  width: 12px;
  height: 12px;
  cursor: nesw-resize;
}

.resize-handle--sw {
  bottom: 0;
  left: 0;
  width: 12px;
  height: 12px;
  cursor: nesw-resize;
}

.resize-handle--se {
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  cursor: nwse-resize;
}

.resize-handle--n {
  top: 0;
  left: 12px;
  right: 12px;
  height: 8px;
  cursor: ns-resize;
}

.resize-handle--s {
  bottom: 0;
  left: 12px;
  right: 12px;
  height: 8px;
  cursor: ns-resize;
}

.resize-handle--e {
  top: 12px;
  right: 0;
  bottom: 12px;
  width: 8px;
  cursor: ew-resize;
}

.resize-handle--w {
  top: 12px;
  left: 0;
  bottom: 12px;
  width: 8px;
  cursor: ew-resize;
}

.resize-handle:hover {
  background: rgba(255, 255, 255, 0.1);
}

.legend-close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
  padding: 0;
}

.legend-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 1);
}

.legend-close-btn:active {
  transform: scale(0.95);
}

.legend-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 0;
  box-sizing: border-box;
}

.legend-title {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 1);
  text-align: center;
  margin-bottom: 8px;
  padding: 0;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  width: 100%;
  box-sizing: border-box;
}

/* Vertical Legend Wrapper */
.legend-vertical-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  height: 100%;
  max-width: 100%;
  flex: 1;
  padding: 4px 0;
  box-sizing: border-box;
}

.legend-labels-vertical {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.8);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  height: 100%;
  padding: 4px 0;
  box-sizing: border-box;
  flex-shrink: 0;
}

.label-min,
.label-max {
  font-weight: 600;
  writing-mode: vertical-rl;
  text-orientation: mixed;
}

/* Vertical Histogram for Lighting/Combined */
.histogram-container-vertical {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  width: auto;
  min-width: 60px;
  gap: 2px;
  margin: 0;
  padding: 8px 6px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex: 1;
  height: 100%;
  max-height: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.histogram-bar-vertical {
  flex: 1;
  min-height: 4px;
  max-height: 100%;
  border-radius: 0 3px 3px 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 3px;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  min-width: 8px;
  box-sizing: border-box;
}

.histogram-bar-vertical:hover {
  opacity: 0.9;
  transform: translateX(2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
  z-index: 10;
}

.bar-label-vertical {
  font-size: 8px;
  color: rgba(255, 255, 255, 1);
  font-weight: 700;
  text-shadow:
    0 1px 3px rgba(0, 0, 0, 0.8),
    0 0 2px rgba(0, 0, 0, 0.5);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  white-space: nowrap;
}

.label-min,
.label-max {
  font-weight: 600;
}

/* Lighting Legend */
.legend-lighting {
  justify-content: center;
  align-items: center;
}

/* Vibrancy Legend */
.legend-vibrancy {
  justify-content: center;
  align-items: center;
}

.legend-bars-vertical {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  width: auto;
  min-width: 60px;
  gap: 3px;
  margin: 0;
  padding: 8px 6px;
  flex: 1;
  height: 100%;
  max-height: 100%;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-sizing: border-box;
  overflow: hidden;
}

.legend-bar-vertical {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-height: 8px;
  width: 100%;
}

.bar-fill-vertical {
  height: 100%;
  width: 100%;
  background: linear-gradient(to right, #70f0c3 0%, #70f0c3 100%);
  border-radius: 0 2px 2px 0;
  min-width: 4px;
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
  background: linear-gradient(to top, #70f0c3 0%, #70f0c3 100%);
  border-radius: 2px 2px 0 0;
  min-height: 4px;
}

.legend-note {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  margin-top: 2px;
  padding: 0;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}

/* Combined Legend */
.legend-combined {
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.combined-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.combined-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 100%;
  flex: 1;
  padding: 4px 0;
  box-sizing: border-box;
  overflow: hidden;
}

.section-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  font-weight: 500;
  padding: 0;
  margin-bottom: 4px;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  font-weight: 500;
}
</style>

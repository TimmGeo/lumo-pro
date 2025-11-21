<template>
  <div class="guided-tour" role="dialog" aria-modal="true">
    <div class="tour-card">
      <div class="grid">
        <p class="step-label">
          Step {{ currentStepIndex + 1 }} / {{ steps.length }}
        </p>
        <div class="headline">
          <h2>{{ currentStep.title }}</h2>
          <span class="chip">{{ currentStep.chip }}</span>
        </div>
        <p class="description">{{ currentStep.body }}</p>

        <div class="tour-visual">
          <div class="orbit"></div>
          <div class="pulse"></div>
          <div class="sprite"></div>
          <div class="gifs">
            <div class="gif-line"></div>
            <div class="gif-line short"></div>
            <div class="gif-line"></div>
          </div>
        </div>

        <div class="actions">
          <button
            class="tour-btn secondary"
            type="button"
            :disabled="currentStepIndex === 0"
            @click="previousStep"
          >
            Back
          </button>
          <button class="tour-btn primary" type="button" @click="handlePrimary">
            {{ primaryLabel }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineEmits, ref } from "vue";

const emit = defineEmits(["close"]);

const steps = [
  {
    title: "Hey, I’m Lumo.",
    body: "We turn Zurich’s night into a map you can read: lights, hubs and reassurance in one warm glow.",
    chip: "Intro",
  },
  {
    title: "Sidebar Pulse",
    body: "Layer toggles make it simple to switch between lighting, vibrancy, or the combined story of the city.",
    chip: "Layers",
  },
  {
    title: "Route Signal",
    body: "Select start and end hubs—watch the safest path populate with a single tap.",
    chip: "Routing",
  },
  {
    title: "Launch",
    body: "Ready? Hit Start and keep exploring the illuminated routes of Zürich.",
    chip: "Start",
  },
];

const currentStepIndex = ref(0);
const currentStep = computed(() => steps[currentStepIndex.value]);
const primaryLabel = computed(() =>
  currentStepIndex.value === steps.length - 1 ? "Start" : "Next"
);

function handlePrimary() {
  if (currentStepIndex.value < steps.length - 1) {
    currentStepIndex.value += 1;
    return;
  }
  finish();
}

function previousStep() {
  if (currentStepIndex.value === 0) return;
  currentStepIndex.value -= 1;
}

function finish() {
  currentStepIndex.value = 0;
  emit("close");
}
</script>

<style scoped>
.guided-tour {
  position: absolute;
  inset: 0;
  z-index: 1100;
  display: grid;
  place-items: center;
  background: radial-gradient(circle, rgba(5, 5, 7, 0.75), rgba(0, 0, 0, 1));
}

.tour-card {
  width: min(86vw, 500px);
  padding: 32px;
  border-radius: 32px;
  background: rgba(12, 12, 18, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 40px 110px rgba(0, 0, 0, 0.65);
}

.grid {
  display: grid;
  gap: 12px;
}

.step-label {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}

.headline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.headline h2 {
  margin: 0;
  font-size: clamp(28px, 4vw, 34px);
  font-weight: 600;
}

.chip {
  padding: 4px 14px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 11px;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

.description {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.tour-visual {
  position: relative;
  height: 140px;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(
    130deg,
    rgba(112, 240, 195, 0.08),
    rgba(18, 18, 24, 0.95)
  );
  border: 1px solid rgba(112, 240, 195, 0.15);
}

.orbit {
  position: absolute;
  inset: 12px;
  border-radius: 50%;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  animation: spin 8s linear infinite;
}

.pulse {
  position: absolute;
  width: 110px;
  height: 110px;
  top: 16px;
  left: 48%;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(112, 240, 195, 0.68),
    rgba(112, 240, 195, 0)
  );
  animation: pulse 3.5s ease-in-out infinite;
}

.sprite {
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  top: 20px;
  left: 24px;
  background: rgba(255, 255, 255, 0.8);
  animation: glide 4s ease-in-out infinite alternate;
}

.gifs {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  display: grid;
  gap: 6px;
}

.gif-line {
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  animation: shimmer 1.8s linear infinite;
}

.gif-line.short {
  width: 45%;
  animation-delay: 0.4s;
}

.actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 6px;
}

.tour-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 12px;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  background: transparent;
  color: #fff;
  cursor: pointer;
  transition:
    background 200ms ease,
    transform 200ms ease;
}

.tour-btn.primary {
  background: rgba(112, 240, 195, 0.18);
  border-color: rgba(112, 240, 195, 0.5);
}

.tour-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tour-btn:not(:disabled):hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.tour-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: #fff;
  font-size: 18px;
  display: grid;
  place-items: center;
  cursor: pointer;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0% {
    transform: translateX(-50%) scale(0.7);
    opacity: 0.9;
  }
  70% {
    transform: translateX(-50%) scale(1);
    opacity: 0.2;
  }
  100% {
    opacity: 0;
  }
}

@keyframes glide {
  from {
    transform: translate(0, 0);
  }
  to {
    transform: translate(120px, 60px);
  }
}

@keyframes shimmer {
  0% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    opacity: 0.2;
  }
}
</style>

<template>
  <div class="guided-tour" role="dialog" aria-modal="true">
    <div class="tour-card">
      <button class="tour-close" type="button" @click="finish" aria-label="Close tour">
        ×
      </button>

      <p class="step-label">Step {{ currentStepIndex + 1 }} / {{ steps.length }}</p>
      <h2>{{ currentStep.title }}</h2>
      <p class="description">{{ currentStep.body }}</p>

      <div class="step-dots" aria-hidden="true">
        <span
          v-for="(step, index) in steps"
          :key="step.title"
          :class="['dot', { active: index === currentStepIndex }]"
        ></span>
      </div>

      <div class="tour-actions">
        <button
          class="tour-btn tour-btn-secondary"
          type="button"
          :disabled="currentStepIndex === 0"
          @click="previousStep"
        >
          Back
        </button>
        <button class="tour-btn tour-btn-primary" type="button" @click="handlePrimary">
          {{ primaryLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineEmits, ref } from "vue";

const emit = defineEmits(["close"]);

const steps = [
  {
    title: "Hey, I'm Lumo.",
    body: "This overlay points you to the brightest routes, the quickest POIs, and the safest hubs at night.",
  },
  {
    title: "Content Sidebar",
    body: "Here you can toggle lighting, vibrancy or both layers while the legend keeps you grounded.",
  },
  {
    title: "Route Functionality",
    body: "Pick start and end hubs to draw routes, then tap the little swap button if you want to reverse the direction.",
  },
  {
    title: "You're all set",
    body: "When you are ready, tap Start to jump into the map and keep exploring.",
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
  background: rgba(5, 5, 7, 0.75);
}

.tour-card {
  position: relative;
  width: min(92vw, 640px);
  padding: 48px;
  border-radius: 36px;
  background: linear-gradient(180deg, rgba(17, 18, 23, 0.95), rgba(12, 12, 16, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 40px 120px rgba(0, 0, 0, 0.65);
  color: #f4f4f7;
  text-align: center;
}

.tour-card h2 {
  margin: 12px 0 16px 0;
  font-size: clamp(32px, 4vw, 40px);
  letter-spacing: 0.03em;
  font-weight: 600;
}

.tour-card .description {
  margin: 0;
  font-size: 18px;
  color: rgba(242, 242, 247, 0.76);
  line-height: 1.5;
}

.step-label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.3em;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.step-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 24px 0;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  transition: background 200ms ease;
}

.dot.active {
  background: #fff;
}

.tour-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.tour-btn {
  min-width: 120px;
  padding: 12px 28px;
  border-radius: 999px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.tour-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.tour-btn-primary {
  background: #ffffff;
  color: #08080c;
  box-shadow: 0 20px 60px rgba(255, 255, 255, 0.25);
}

.tour-btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: #f4f4f7;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.tour-btn:not(:disabled):hover {
  transform: translateY(-2px);
}

.tour-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: #fff;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  display: grid;
  place-items: center;
}
</style>


<template>
  <div class="walkthrough" role="dialog" aria-modal="true">
    <div class="wt-inner">
      <h1 class="wt-title">Everything changes when the lights come on</h1>
      <p class="wt-sub">The City's awake. Let's find your way.</p>

      <div class="wt-actions">
        <button class="btn btn-primary" @click="takeTour">Take the Tour</button>
        <button class="btn btn-ghost" @click="skip">Skip to map</button>
      </div>

      <button class="wt-close" @click="skip" aria-label="Close walkthrough">
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, onMounted, onBeforeUnmount } from "vue";

const emit = defineEmits(["close", "takeTour"]);

function skip() {
  emit("close");
}

function takeTour() {
  emit("takeTour");
}

function onKey(e) {
  if (e.key === "Escape") skip();
}

onMounted(() => window.addEventListener("keydown", onKey));
onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>

<style scoped>
.walkthrough {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, rgba(3, 3, 3, 0.85), rgba(3, 3, 3, 0.7));
  z-index: 100;
}
.wt-inner {
  text-align: center;
  max-width: 920px;
  padding: 64px 40px;
}
.wt-title {
  font-size: 44px;
  color: #fff;
  margin: 0 0 18px 0;
  font-weight: 800;
}
.wt-sub {
  font-size: 22px;
  color: #dcdcdc;
  margin: 0 0 28px 0;
}
.wt-actions {
  display: flex;
  gap: 18px;
  justify-content: center;
  margin-top: 8px;
}
.btn {
  padding: 14px 28px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 16px;
  border: none;
  cursor: pointer;
}
.btn-primary {
  background: #ffffff;
  color: #111;
}
.btn-ghost {
  background: rgba(255, 255, 255, 0.06);
  color: #eaeaea;
}
.wt-close {
  position: absolute;
  right: 20px;
  top: 18px;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
}

@media (max-width: 640px) {
  .wt-title {
    font-size: 28px;
  }
  .wt-sub {
    font-size: 16px;
  }
  .wt-inner {
    padding: 40px 18px;
  }
  .btn {
    padding: 12px 18px;
  }
}
</style>

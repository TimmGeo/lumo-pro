<template>
  <div class="walkthrough" role="dialog" aria-modal="true">
    <!-- Slide container -->
    <div class="slides">
      <!-- Slide 1: Intro with main CTA -->
      <section
        class="slide"
        :class="{ active: slide === 1 }"
        aria-hidden="false"
      >
        <h1 class="wt-title">Everything changes when the lights come on</h1>
        <div class="wt-actions">
          <button class="btn btn-primary" @click="goTo(2)">
            Turn the lights on
          </button>
        </div>
      </section>

      <!-- Slide 2: Logo fade in -->
      <section
        class="slide slide--logo"
        :class="{ active: slide === 2 }"
        aria-hidden="true"
      >
        <img class="lumo-logo" src="/Lumo_icon_grey.svg" alt="Lumo" />
      </section>

      <!-- Slide 3: City awake + actions -->
      <section
        class="slide"
        :class="{ active: slide === 3 }"
        aria-hidden="true"
      >
        <h2 class="wt-title wt-title--small">
          The City's awake.<br />Let's find your way.
        </h2>
        <div class="wt-actions">
          <button class="btn btn-primary" @click="takeTour">
            Take the Tour
          </button>
          <button class="btn btn-ghost" @click="skip">Skip to map</button>
        </div>
      </section>
    </div>

    <button class="wt-close" @click="skip" aria-label="Close walkthrough">
      ×
    </button>
  </div>
</template>

<script setup>
import { ref, defineEmits, onMounted, onBeforeUnmount } from "vue";

const emit = defineEmits(["close", "takeTour"]);

const slide = ref(1);
let timer = null;

function clearTimer() {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
}

function goTo(n) {
  clearTimer();
  slide.value = n;

  // If moving to slide 2, auto-advance to 3 after ~3s
  if (n === 2) {
    // allow the logo to fade in then advance
    timer = setTimeout(() => {
      slide.value = 3;
      timer = null;
    }, 3000);
  }
}

function skip() {
  clearTimer();
  emit("close");
}

function takeTour() {
  clearTimer();
  emit("takeTour");
}

function onKey(e) {
  if (e.key === "Escape") skip();
}

onMounted(() => {
  window.addEventListener("keydown", onKey);
});
onBeforeUnmount(() => {
  clearTimer();
  window.removeEventListener("keydown", onKey);
});
</script>

<style scoped>
.walkthrough {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: #0b0b0c; /* opaque background that covers the map */
  z-index: 1000;
}
.slides {
  position: relative;
  width: 100%;
  max-width: 920px;
  padding: 64px 40px;
  box-sizing: border-box;
  text-align: center;
}
.slide {
  position: absolute;
  inset: 0;
  display: grid;
  align-items: center;
  justify-items: center;
  opacity: 0;
  transform: translateY(6px) scale(0.997);
  transition:
    opacity 420ms cubic-bezier(0.2, 0.9, 0.24, 1),
    transform 420ms cubic-bezier(0.2, 0.9, 0.24, 1);
  pointer-events: none;
}
.slide.active {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.wt-title {
  font-size: 44px;
  color: #fff;
  margin: 0 0 18px 0;
  font-weight: 800;
}
.wt-title--small {
  font-size: 36px;
}

.wt-actions {
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

.slide--logo {
  display: grid;
}
.lumo-logo {
  width: clamp(220px, 34vw, 420px);
  opacity: 0;
  transform: scale(0.98);
  animation: logoFade 1s ease forwards;
}
@keyframes logoFade {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
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
  .slides {
    padding: 40px 18px;
  }
  .wt-title {
    font-size: 28px;
  }
  .wt-title--small {
    font-size: 22px;
  }
  .btn {
    padding: 12px 18px;
  }
}
</style>

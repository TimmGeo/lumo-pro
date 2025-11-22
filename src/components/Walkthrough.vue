<template>
  <div
    class="walkthrough"
    :class="{ 'lights-hover': lightsHover && slide === 1 }"
    role="dialog"
    aria-modal="true"
  >
    <!-- Slide container -->
    <div class="slides">
      <!-- Slide 1: Intro with main CTA -->
      <section
        class="slide"
        :class="{ active: slide === 1 }"
        aria-hidden="false"
      >
        <div class="content">
          <h1 class="wt-title">Everything changes when the lights come on</h1>
          <div class="wt-actions">
            <button
              class="btn btn-primary"
              @click="handleTurnOn"
              @mouseenter="lightsHover = true"
              @mouseleave="lightsHover = false"
            >
              Turn the lights on
            </button>
          </div>
        </div>
      </section>

      <!-- Slide 2: Lumo text fade in -->
      <section
        class="slide slide--logo"
        :class="{ active: slide === 2 }"
        aria-hidden="true"
      >
        <div class="content">
          <h1 class="lumo-text" :class="{ 'fade-out': fadingLogo }">Lumo</h1>
        </div>
      </section>

      <!-- Slide 3: City awake + actions -->
      <section
        class="slide slide--final"
        :class="{ active: slide === 3 }"
        aria-hidden="true"
      >
        <div class="content">
          <h2 class="wt-title wt-title--small">
            The City's awake.<br />Let's find your way.
          </h2>
          <div class="wt-actions">
            <button class="btn btn-primary" @click="takeTour">
              Take the Tour
            </button>
            <button class="btn btn-ghost" @click="skipToMap">
              Skip to map
            </button>
          </div>
        </div>
      </section>
    </div>

    <button class="wt-close" @click="skip" aria-label="Close walkthrough">
      ×
    </button>

    <!-- Smooth blackout overlay used to create a full-dark gap between slides -->
    <div
      class="blackout"
      :class="{ active: blackout }"
      aria-hidden="true"
    ></div>

    <!-- Brightness overlay that gradually brightens the screen during hover -->
    <div
      class="brightness-overlay"
      :class="{ active: lightsHover && slide === 1 }"
      aria-hidden="true"
    ></div>
  </div>
</template>

<script setup>
import { ref, defineEmits, onMounted, onBeforeUnmount } from "vue";

const emit = defineEmits(["close", "takeTour", "enterMap"]);

const slide = ref(0); // 0 = black, 1 = intro, 2 = logo, 3 = final
let timer = null;
const fadingLogo = ref(false);
const blackout = ref(true);
const lightsHover = ref(false);

function clearTimer() {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
}

function goTo(n) {
  if (n === slide.value) return;
  clearTimer();
  // fade to blackout, then show the target slide
  blackout.value = true;
  // pause to allow blackout to reach full opacity (matches CSS transition: 500ms)
  timer = setTimeout(() => {
    slide.value = n;
    // remove blackout after a short reveal delay so the new slide fades in gently
    setTimeout(() => {
      blackout.value = false;
      timer = null;
    }, 150);
  }, 500);
}

function handleTurnOn() {
  // Sequence: brightness from hover -> gradually brighten to white -> show Lumo text (white bg, black text) -> after ~3s fade -> smooth transition -> final slide
  clearTimer();
  // Keep brightness active and gradually increase it to full white
  lightsHover.value = true;

  // Gradually brighten the screen, then show Lumo text slide with white background
  timer = setTimeout(() => {
    fadingLogo.value = false;
    slide.value = 2;
    // Keep brightness overlay active to maintain white background
    // No blackout needed - let the brightness overlay create the white background

    // show Lumo for ~2.5s, then transition to final slide using simple blackout
    timer = setTimeout(() => {
      // Turn off brightness overlay
      lightsHover.value = false;
      // Simple blackout transition like goTo function
      blackout.value = true;
      // Wait for blackout to reach full opacity (500ms), then change slide
      timer = setTimeout(() => {
        slide.value = 3;
        // Remove blackout after a short reveal delay so the new slide fades in gently
        setTimeout(() => {
          blackout.value = false;
          timer = null;
        }, 150);
      }, 500);
    }, 2500);
  }, 800); // Give time for brightness to gradually increase
}

function skip() {
  clearTimer();
  emit("close");
}

function skipToMap() {
  clearTimer();
  lightsHover.value = false;
  blackout.value = true;
  emit("enterMap");
  emit("close");
}

function takeTour() {
  clearTimer();
  emit("enterMap");
  emit("takeTour");
}

function onKey(e) {
  if (e.key === "Escape") skip();
}

onMounted(() => {
  window.addEventListener("keydown", onKey);
  // initial dark screen for ~1s, then reveal slide 1 slowly
  clearTimer();
  // blackout starts true; after 1s set slide to 1 and fade blackout out
  timer = setTimeout(() => {
    slide.value = 1;
    // small delay before revealing to ensure slide transition is ready
    setTimeout(() => {
      blackout.value = false;
      timer = null;
    }, 50);
  }, 1000);
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
  background: #151517; /* match sidebar background */
  z-index: 1000;
}
.walkthrough.lights-hover {
  filter: brightness(1.25);
  transition: filter 350ms ease;
}
.slides {
  position: relative;
  width: 100%;
  max-width: 920px;
  padding: 64px 40px;
  box-sizing: border-box;
  text-align: center;
  z-index: 1200;
}
.slide {
  position: absolute;
  inset: 0;
  background: #151517;
  display: grid;
  align-items: center;
  justify-items: center;
  opacity: 0;
  visibility: hidden;
  transform: translateY(6px) scale(0.997);
  transition:
    opacity 800ms cubic-bezier(0.16, 0.84, 0.24, 1),
    transform 800ms cubic-bezier(0.16, 0.84, 0.24, 1),
    visibility 0ms 800ms;
  pointer-events: none;
}

.brightness-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.15);
  opacity: 0;
  pointer-events: none;
  transition:
    opacity 1200ms cubic-bezier(0.16, 0.84, 0.24, 1),
    background 1400ms cubic-bezier(0.16, 0.84, 0.24, 1);
  z-index: 1350;
}
.brightness-overlay.active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.3);
}

.blackout {
  position: absolute;
  inset: 0;
  background: #0b0b0c;
  opacity: 0;
  pointer-events: none;
  transition: opacity 700ms cubic-bezier(0.16, 0.84, 0.24, 1);
  z-index: 1400;
}
.blackout.active {
  opacity: 1;
}

.walkthrough.lights-hover {
  filter: brightness(1.25);
  transition: filter 350ms ease;
}

.slide.active {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
  transition:
    opacity 1000ms cubic-bezier(0.16, 0.84, 0.24, 1),
    transform 1000ms cubic-bezier(0.16, 0.84, 0.24, 1),
    visibility 0ms;
  pointer-events: auto;
}

/* content fade-up for titles/subtext - exclude logo/lumo-text which have their own animations */
.content > :is(.wt-title, .wt-sub, h2):not(.lumo-text) {
  opacity: 0;
  /* start slightly scaled down, blurred and tighter tracking for an elegant emerge */
  transform: scale(0.985);
  filter: blur(6px);
  letter-spacing: -0.01em;
  /* much gentler, slower fade with smooth ease-out */
  transition:
    opacity 1400ms cubic-bezier(0.16, 0.84, 0.24, 1) 200ms,
    transform 1400ms cubic-bezier(0.16, 0.84, 0.24, 1) 200ms,
    filter 1200ms cubic-bezier(0.16, 0.84, 0.24, 1) 200ms;
}
.slide.active .content > :is(.wt-title, .wt-sub, h2):not(.lumo-text) {
  opacity: 1;
  transform: none;
  filter: blur(0);
  letter-spacing: 0;
}

/* buttons appear slightly delayed after the text with more emphasis */
.content .btn {
  opacity: 0;
  transform: translateY(10px) scale(0.995);
  /* slower, more elegant button entrance with a pronounced delay */
  transition:
    opacity 900ms cubic-bezier(0.16, 0.84, 0.24, 1) 600ms,
    transform 900ms cubic-bezier(0.16, 0.84, 0.24, 1) 600ms;
}
.slide.active .content .btn {
  opacity: 1;
  transform: none;
}
.slide--final .content .btn {
  transition:
    opacity 900ms cubic-bezier(0.16, 0.84, 0.24, 1) 900ms,
    transform 900ms cubic-bezier(0.16, 0.84, 0.24, 1) 900ms;
}

.wt-title {
  font-size: 44px;
  color: #fff;
  margin: 0 0 18px 0;
  font-weight: 500;
  white-space: nowrap;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
}
.wt-title--small {
  font-size: 44px;
}

.wt-actions {
  margin-top: 38px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn {
  padding: 14px 28px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 16px;
  border: none;
  cursor: pointer;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  min-width: 140px;
  transition:
    transform 400ms cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 400ms cubic-bezier(0.16, 0.84, 0.24, 1),
    filter 400ms ease;
  transform: scale(1) rotate(0deg);
  position: relative;
}
.btn:hover {
  transform: scale(1.06) rotate(1deg);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
  filter: brightness(1.05);
}
/* Remove brightness filter on hover when parent has brightness filter */
.walkthrough.lights-hover .btn:hover {
  filter: brightness(0.8); /* Keep counteracted brightness, no additional hover brightness */
}
.btn:active {
  transform: scale(1.02) rotate(0.5deg);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  transition:
    transform 150ms cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 150ms ease;
}
.btn-primary {
  background: #ffffff;
  color: #111;
}
.btn-primary:hover {
  background: #ffffff; /* Keep same color, no brightness change */
}
/* Counteract parent brightness filter to keep button at normal brightness */
.walkthrough.lights-hover .btn-primary {
  filter: brightness(0.8); /* Inverse of parent's brightness(1.25) to maintain normal appearance */
  transition: filter 350ms ease, transform 400ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 400ms cubic-bezier(0.16, 0.84, 0.24, 1); /* Match parent transition timing */
}
.btn-ghost {
  background: rgba(255, 255, 255, 0.06);
  color: #eaeaea;
}
.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.06); /* Keep same color */
}

.slide--logo {
  display: grid;
  place-items: center;
  background: #151517;
  position: fixed;
  inset: 0;
  z-index: 1300;
}
.slide--logo .content {
  color: #fff !important;
  background: transparent;
  box-shadow: none !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0;
  width: 100%;
  height: 100%;
}
.slide--logo.active .content {
  color: #fff !important;
  background: transparent;
}
.lumo-text {
  font-size: clamp(96px, 16vw, 180px);
  font-weight: 500;
  color: #ffffff !important;
  margin: 0;
  padding: 0;
  opacity: 0;
  transform: scale(0.92) translateY(8px);
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  letter-spacing: -0.03em;
  line-height: 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  z-index: 1200;
  position: relative;
  mix-blend-mode: normal;
  background: transparent !important;
  box-shadow: none !important;
  filter: none !important;
  text-shadow: none !important;
  /* Only animate when slide 2 is active */
  animation: none;
}
@keyframes lumoFade {
  from {
    opacity: 0;
    transform: scale(0.92) translateY(8px);
    color: #ffffff;
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
    color: #ffffff;
  }
}
.slide--logo.active .lumo-text {
  color: #ffffff !important;
}
.slide--logo.active .lumo-text:not(.fade-out) {
  animation: lumoFade 800ms cubic-bezier(0.16, 0.84, 0.24, 1) 200ms forwards;
}
.slide--logo.active .lumo-text.fade-out {
  animation: lumoFadeOut 800ms cubic-bezier(0.16, 0.84, 0.24, 1) 0ms forwards;
}

@keyframes lumoFadeOut {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
    color: #ffffff;
  }
  to {
    opacity: 0;
    transform: scale(0.92) translateY(-6px);
    color: #ffffff;
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
    white-space: normal;
  }
  .wt-title--small {
    font-size: 28px;
  }
  .btn {
    padding: 12px 18px;
  }
}
</style>

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
        <div class="content">
          <h1 class="wt-title">Everything changes when the lights come on</h1>
          <div class="wt-actions">
            <button class="btn btn-primary" @click="handleTurnOn">
              Turn the lights on
            </button>
          </div>
        </div>
      </section>

      <!-- Slide 2: Logo fade in -->
      <section
        class="slide slide--logo"
        :class="{ active: slide === 2 }"
        aria-hidden="true"
      >
        <div class="content">
          <img
            class="lumo-logo"
            :class="{ 'fade-out': fadingLogo }"
            src="/Lumo_icon_grey.svg"
            alt="Lumo"
          />
        </div>
      </section>

      <!-- Slide 3: City awake + actions -->
      <section
        class="slide"
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
            <button class="btn btn-ghost" @click="skip">Skip to map</button>
          </div>
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

const slide = ref(0); // 0 = black, 1 = intro, 2 = logo, 3 = final
let timer = null;
const fadingLogo = ref(false);

function clearTimer() {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
}

function goTo(n) {
  clearTimer();
  slide.value = n;
}

function handleTurnOn() {
  // Sequence: darken briefly -> show logo -> after ~3s fade logo -> final slide
  clearTimer();
  // darken
  slide.value = 0;

  // short dark pause then show logo
  timer = setTimeout(() => {
    fadingLogo.value = false;
    slide.value = 2;

    // show logo for ~3s, then fade it and move to final slide
    timer = setTimeout(() => {
      // start fade-out animation for the logo
      fadingLogo.value = true;
      timer = setTimeout(() => {
        // move to final slide (text will animate in)
        fadingLogo.value = false;
        slide.value = 3;
        timer = null;
      }, 520); // allow fade-out to complete
    }, 3000);
  }, 420);
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
  // initial dark screen for ~1s, then reveal slide 1 slowly
  clearTimer();
  timer = setTimeout(() => {
    slide.value = 1;
    timer = null;
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
    opacity 700ms cubic-bezier(0.22, 0.9, 0.28, 1),
    transform 700ms cubic-bezier(0.22, 0.9, 0.28, 1);
  pointer-events: none;
}
.slide.active {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

/* content fade-up for titles/subtext/logo */
.content > :is(.wt-title, .wt-sub, .lumo-logo, h2) {
  opacity: 0;
  transform: translateY(22px) scale(0.995);
  /* much gentler, slower fade-up with smooth ease-out */
  transition:
    opacity 1100ms cubic-bezier(0.22, 0.86, 0.28, 1),
    transform 1100ms cubic-bezier(0.22, 0.86, 0.28, 1);
}
.slide.active .content > :is(.wt-title, .wt-sub, .lumo-logo, h2) {
  opacity: 1;
  transform: none;
}

/* buttons appear slightly delayed after the text with more emphasis */
.content .btn {
  opacity: 0;
  transform: translateY(18px) scale(0.995);
  /* slower, more elegant button entrance with a pronounced delay */
  transition:
    opacity 900ms cubic-bezier(0.22, 0.9, 0.28, 1) 520ms,
    transform 900ms cubic-bezier(0.22, 0.9, 0.28, 1) 520ms;
}
.slide.active .content .btn {
  opacity: 1;
  transform: none;
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
  transform: scale(0.92);
  animation: logoFade 900ms cubic-bezier(0.16, 0.84, 0.24, 1) forwards;
}
@keyframes logoFade {
  from {
    opacity: 0;
    transform: scale(0.92) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* logo fade-out animation when sequence moves on */
.lumo-logo.fade-out {
  animation: logoFadeOut 520ms cubic-bezier(0.2, 0.9, 0.24, 1) forwards;
}
@keyframes logoFadeOut {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  to {
    opacity: 0;
    transform: scale(0.9) translateY(-10px);
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

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

    <!-- Smooth blackout overlay used to create a full-dark gap between slides -->
    <div
      class="blackout"
      :class="{ active: blackout }"
      aria-hidden="true"
    ></div>
  </div>
</template>

<script setup>
import { ref, defineEmits, onMounted, onBeforeUnmount } from "vue";

const emit = defineEmits(["close", "takeTour"]);

const slide = ref(0); // 0 = black, 1 = intro, 2 = logo, 3 = final
let timer = null;
const fadingLogo = ref(false);
const blackout = ref(true);

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
  // short pause to allow blackout to reach full opacity (matches CSS transition)
  timer = setTimeout(() => {
    slide.value = n;
    // remove blackout after a short reveal delay so the new slide fades in gently
    setTimeout(() => {
      blackout.value = false;
      timer = null;
    }, 200);
  }, 420);
}

function handleTurnOn() {
  // Sequence: blackout -> show logo -> after ~3s fade logo -> blackout -> final slide
  clearTimer();
  // start blackout quickly
  blackout.value = true;

  // short pause then show logo
  timer = setTimeout(() => {
    fadingLogo.value = false;
    slide.value = 2;
    // reveal logo by removing blackout
    blackout.value = false;

    // show logo for ~3s, then fade it and move to final slide
    timer = setTimeout(() => {
      // start fade-out animation for the logo
      fadingLogo.value = true;
      timer = setTimeout(() => {
        // after logo fade-out, blackout and then show final slide
        fadingLogo.value = false;
        blackout.value = true;
        setTimeout(() => {
          slide.value = 3;
          // reveal final slide gently
          blackout.value = false;
          timer = null;
        }, 420);
      }, 420); // allow fade-out to complete
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
  // blackout starts true; after 1s set slide to 1 and fade blackout out
  timer = setTimeout(() => {
    slide.value = 1;
    blackout.value = false;
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

.blackout {
  position: absolute;
  inset: 0;
  background: #0b0b0c;
  opacity: 0;
  pointer-events: none;
  transition: opacity 420ms cubic-bezier(0.22, 0.9, 0.24, 1);
  z-index: 1200;
}
.blackout.active {
  opacity: 1;
}
.slide.active {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

/* content fade-up for titles/subtext/logo */
.content > :is(.wt-title, .wt-sub, .lumo-logo, h2) {
  opacity: 0;
  /* start slightly scaled down, blurred and tighter tracking for an elegant emerge */
  transform: scale(0.985);
  filter: blur(6px);
  letter-spacing: -0.01em;
  /* much gentler, slower fade with smooth ease-out */
  transition:
    opacity 1500ms cubic-bezier(0.22, 0.86, 0.28, 1),
    transform 1500ms cubic-bezier(0.22, 0.86, 0.28, 1),
    filter 1200ms cubic-bezier(0.22, 0.86, 0.28, 1);
}
.slide.active .content > :is(.wt-title, .wt-sub, .lumo-logo, h2) {
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
    opacity 1000ms cubic-bezier(0.22, 0.9, 0.28, 1) 700ms,
    transform 1000ms cubic-bezier(0.22, 0.9, 0.28, 1) 700ms;
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
  animation: logoFadeOut 420ms cubic-bezier(0.2, 0.9, 0.24, 1) forwards;
}
@keyframes logoFadeOut {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  to {
    opacity: 0;
    transform: scale(0.92) translateY(-6px);
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

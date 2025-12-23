<template>
  <transition name="toast-fade">
    <div v-if="visible" class="toast" role="status" aria-live="polite">
      <div class="toast-bg-pulse"></div>
      <div class="toast-content">
        <p class="toast-message">The City's awake. Let's find your way.</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, defineEmits, defineProps } from "vue";

const props = defineProps({
  mapReady: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "takeTour", "enterMap"]);

const visible = ref(true);

onMounted(() => {
  // Show toast for 4 seconds, then fade out
  setTimeout(() => {
    visible.value = false;
    // Emit close after animation completes to clean up
    setTimeout(() => {
      emit("close");
    }, 300);
  }, 4000);
});
</script>

<style scoped>
.toast {
  position: fixed;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  pointer-events: none;
}

.toast-bg-pulse {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(150, 150, 150, 0.6);
  z-index: 1999;
  animation: pulse-bg 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes pulse-bg {
  0% {
    background-color: rgba(150, 150, 150, 0.4);
  }
  50% {
    background-color: rgba(150, 150, 150, 0.8);
  }
  100% {
    background-color: rgba(150, 150, 150, 0.4);
  }
}

.toast-content {
  position: relative;
  background-color: #1c1c1e !important;
  border-radius: 14px;
  padding: 14px 20px;
  box-shadow:
    0 4px 16px rgba(0, 0, 0, 0.3),
    0 0 0 0.5px rgba(255, 255, 255, 0.1);
  min-width: 280px;
  max-width: 90vw;
  z-index: 2001;
  transition: none !important;
  animation: none !important;
}

.toast-message {
  position: relative;
  z-index: 1;
  margin: 0;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: -0.01em;
  line-height: 1.4;
  text-align: center;
  font-family:
    "SF Pro Display",
    "SF Pro Text",
    -apple-system,
    BlinkMacSystemFont,
    system-ui,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Fade animations */
.toast-fade-enter-active {
  transition:
    opacity 400ms cubic-bezier(0.16, 1, 0.3, 1),
    transform 400ms cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-fade-enter-active .toast-content {
  transition: none !important;
}

.toast-fade-leave-active {
  transition:
    opacity 300ms cubic-bezier(0.4, 0, 1, 1),
    transform 300ms cubic-bezier(0.4, 0, 1, 1);
}

.toast-fade-leave-active .toast-content {
  transition: none !important;
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px) scale(0.96);
}

.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px) scale(0.96);
}

@media (max-width: 640px) {
  .toast {
    top: 40px;
    left: 20px;
    right: 20px;
    transform: none;
  }

  .toast-content {
    width: 100%;
    padding: 12px 18px;
  }

  .toast-message {
    font-size: 14px;
  }

  .toast-fade-enter-from,
  .toast-fade-leave-to {
    transform: translateY(-10px) scale(0.96);
  }
}
</style>

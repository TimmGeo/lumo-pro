<template>
  <!-- Placeholder legend intentionally left empty -->
  <div class="legend-empty" aria-hidden="true"></div>
</template>

<script setup>
// Keep prop definition so parent usage <Legend :mode="mode"/> stays valid
defineProps({ mode: { type: String, required: true } });
</script>

<style scoped>
.legend-empty {
  width: 100%;
  height: 100%;
}
</style>

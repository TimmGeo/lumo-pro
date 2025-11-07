<template>
  <div class="legend">
    <template v-if="mode === 'lighting' || mode === 'combined'">
      <div class="label">Lighting</div>
      <div class="ramp">
        <span v-for="c in ramp" :key="c" :style="{ background: c }"></span>
      </div>
      <div class="ticks"><span>Dim</span><span>Bright</span></div>
    </template>
    <template v-if="mode !== 'lighting'">
      <div class="label">Vibrancy (height)</div>
      <div class="bars"><span /><span /><span /></div>
    </template>
  </div>
</template>

<script setup>
defineProps({ mode: { type: String, required: true } });
const ramp = ["#0d0f10", "#1d2326", "#274048", "#2e7567", "#70f0c3"];
</script>

<style scoped>
.legend {
  position: absolute;
  right: 16px;
  bottom: 16px;
  background: #151517;
  border: 1px solid #2a2f34;
  border-radius: 14px;
  padding: 12px 14px;
  min-width: 180px;
}
.label {
  color: #9aa0a6;
  font-size: 0.8rem;
  margin-bottom: 6px;
}
.ramp {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  height: 12px;
  margin-bottom: 6px;
}
.ramp span {
  border-radius: 3px;
}
.ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #9aa0a6;
}
.bars {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}
.bars span {
  width: 18px;
  height: 10px;
  background: #9aa0a6;
  opacity: 0.35;
  border-radius: 3px;
}
</style>

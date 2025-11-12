<template>
  <div id="map" style="width: 100%; height: 100vh"></div>
</template>

<script setup>
import mapboxgl from "mapbox-gl";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

const map = new mapboxgl.Map({
  container: "map",
  style: "mapbox://styles/mapbox/dark-v11",
  center: [8.55, 47.37], // Zürich
  zoom: 11,
});
</script>

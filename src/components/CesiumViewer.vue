<template>
  <div class="scene">
    <div id="cesium"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from "vue";
import "cesium/Build/Cesium/Widgets/widgets.css";
import {
  Viewer,
  Color,
  UrlTemplateImageryProvider,
  GeoJsonDataSource,
  Cartesian3,
  NearFarScalar,
} from "cesium";

/* Small helper to work with Vite's base path ("/" locally, "/project/trogenmoser/" in deploy) */
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");

let viewer;

onMounted(async () => {
  try {
    // Viewer (minimal UI)
    viewer = new Viewer("cesium", {
      baseLayerPicker: false,
      animation: false,
      timeline: false,
      geocoder: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      fullscreenButton: true,
    });

    // Night look
    viewer.scene.skyBox.show = false;
    viewer.scene.skyAtmosphere.show = false;
    viewer.scene.backgroundColor = Color.fromCssColorString("#0b0b0c");
    viewer.scene.globe.show = true;
    viewer.scene.globe.baseColor = Color.fromCssColorString("#161718");

    // Token-free dark basemap (softened)
    const dark = new UrlTemplateImageryProvider({
      url: "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      credit: "© OpenStreetMap contributors © CARTO",
      minimumLevel: 0,
      maximumLevel: 19,
    });
    const baseLayer = viewer.imageryLayers.addImageryProvider(dark);
    baseLayer.brightness = 0.35;
    baseLayer.contrast = 0.85;
    baseLayer.saturation = 0.2;
    baseLayer.gamma = 0.95;

    // --- Load your routing hubs (WGS84 GeoJSON) ---
    const hubsDS = await GeoJsonDataSource.load(hubsUrl, {
      clampToGround: true,
    });

    // Style: mint dots + subtle labels
    hubsDS.entities.values.forEach((e) => {
      const name = e.properties?.CHSTNAME?.getValue?.() ?? "";

      // point symbol
      e.point = {
        pixelSize: 5,
        color: Color.fromCssColorString("#70f0c3"),
        outlineColor: Color.fromCssColorString("#0b0b0c"),
        outlineWidth: 0,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      };

      // label (small, fades with distance)
      e.label = {
        text: name,
        font: "12px Avenir, system-ui, sans-serif",
        fillColor: Color.fromCssColorString("#e9f7f2"),
        outlineColor: Color.fromCssColorString("#0b0b0c"),
        outlineWidth: 2,
        style: 0, // FILL
        pixelOffset: new Cartesian3(0, -14, 0),
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        translucencyByDistance: new NearFarScalar(1_000, 0.0, 15_000, 1.0), // fade out when far
      };
    });

    viewer.dataSources.add(hubsDS);
    await viewer.zoomTo(hubsDS);

    // Handy for console
    window.viewer = viewer;
    console.log("Loaded hubs:", hubsDS.entities.values.length, hubsUrl);
  } catch (e) {
    console.error("Cesium init / hubs load failed:", e);
  }
});

onBeforeUnmount(() => {
  try {
    viewer?.destroy();
  } catch {}
});
</script>

<style scoped>
.scene,
#cesium {
  position: fixed;
  inset: 0;
  z-index: 0;
}
</style>

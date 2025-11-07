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
  ImageryLayer,
  Cartesian3,
  WebMapTileServiceImageryProvider,
  WebMercatorTilingScheme,
  Rectangle,
} from "cesium";

/* keep App.vue happy */
const props = defineProps({
  mode: { type: String, default: "combined" },
  heightScale: { type: Number, default: 1.5 },
});
const emit = defineEmits(["ready"]);
function onHover() {}
async function drawRoute() {}
emit("ready", { onHover, drawRoute });

let viewer;

onMounted(async () => {
  try {
    viewer = new Viewer("cesium", {
      baseLayerPicker: false,
      animation: false,
      timeline: false,
      geocoder: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      fullscreenButton: false,
    });

    // Night look
    viewer.scene.skyBox.show = false;
    viewer.scene.skyAtmosphere.show = false; // remove blue halo
    viewer.scene.backgroundColor = Color.fromCssColorString("#0b0b0c");
    viewer.scene.globe.show = true;
    viewer.scene.globe.baseColor = Color.fromCssColorString("#161718");

    // Token-free dark basemap (CARTO Dark Matter)
    const cartoDark = new UrlTemplateImageryProvider({
      url: "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      credit: "© OpenStreetMap contributors © CARTO",
      minimumLevel: 0,
      maximumLevel: 19,
    });
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.add(new ImageryLayer(cartoDark));

    // Optional: subtle Swiss WMTS overlay (low alpha)
    const switzerland = Rectangle.fromDegrees(
      5.140224,
      45.398101,
      11.47757,
      48.230651
    );
    const wmts = new WebMapTileServiceImageryProvider({
      url: "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{TileMatrix}/{TileCol}/{TileRow}.jpeg",
      tilingScheme: new WebMercatorTilingScheme(),
      rectangle: switzerland,
      format: "image/jpeg",
    });
    const chLayer = viewer.imageryLayers.addImageryProvider(wmts);
    chLayer.alpha = 0.22; // faint texture
    chLayer.brightness = 0.45;

    // Fly to Zürich
    await viewer.camera.flyTo({
      destination: Cartesian3.fromDegrees(8.54, 47.37, 3000),
      orientation: { pitch: -0.5 },
      duration: 2.0,
    });

    window.viewer = viewer;
  } catch (e) {
    console.error("Cesium init failed:", e);
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

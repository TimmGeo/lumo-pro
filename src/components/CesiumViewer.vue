<template>
  <div class="scene">
    <div id="cesium"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, defineProps } from "vue";
import "cesium/Build/Cesium/Widgets/widgets.css";
import {
  Viewer,
  Color,
  UrlTemplateImageryProvider,
  GeoJsonDataSource,
  Cartesian2,
  Cartesian3,
  NearFarScalar,
  DistanceDisplayCondition,
  HorizontalOrigin,
  VerticalOrigin,
} from "cesium";

/* Props from App.vue */
const props = defineProps({
  mode: { type: String, default: "combined" },
  heightScale: { type: Number, default: 1.5 },
});

/* Paths that work both locally and in deploy */
const BASE = import.meta.env.BASE_URL || "/";
const hubsUrl = `${BASE}data/routing_hubs.geojson`.replace(/\/{2,}/g, "/");
const hexUrl = `${BASE}data/hex_kreis_light_300m.geojson`.replace(
  /\/{2,}/g,
  "/"
);

let viewer;
let hexDS = null;
let hubsDS = null;

onMounted(async () => {
  try {
    // --- Cesium viewer setup ---
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

    // Dark basemap
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

    // --- Routing hubs (points) ---
    hubsDS = await GeoJsonDataSource.load(hubsUrl, { clampToGround: true });

    hubsDS.entities.values.forEach((e) => {
      const name = e.properties?.CHSTNAME?.getValue?.() ?? "";

      // remove default icon
      e.billboard = undefined;

      // point (slightly larger)
      e.point = {
        pixelSize: 8,
        color: Color.fromCssColorString("#70f0c3"),
        outlineColor: Color.fromCssColorString("#0b0b0c"),
        outlineWidth: 0,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      };

      // label: to the right, visible out to ~12 km
      e.label = {
        text: name,
        font: "bold 20px Helvetica, system-ui, sans-serif",
        fillColor: Color.fromCssColorString("#e9f7f2"),
        outlineColor: Color.fromCssColorString("#0b0b0c"),
        outlineWidth: 2,
        style: 0, // FILL
        pixelOffset: new Cartesian2(14, 0),
        horizontalOrigin: HorizontalOrigin.LEFT,
        verticalOrigin: VerticalOrigin.CENTER,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        distanceDisplayCondition: new DistanceDisplayCondition(0.0, 12000.0),
        translucencyByDistance: new NearFarScalar(0.0, 1.0, 12000.0, 0.85),
        scaleByDistance: new NearFarScalar(0.0, 1.1, 12000.0, 0.7),
      };
    });
    viewer.dataSources.add(hubsDS);

    // --- Lighting hexagons (polygons) with radial fade (Option B) ---
    hexDS = await GeoJsonDataSource.load(hexUrl, { clampToGround: true });

    // Fade parameters
    const centerOpacity = 0.55; // alpha at center
    const rimOpacity = 0.15; // alpha at rim
    const falloffPow = 1.6; // softness; higher = softer
    const bgTint = Color.fromCssColorString("#161718"); // basemap tint to blend toward

    // 1) First pass: compute approximate centroids, center, and max distance
    const centroids = [];
    hexDS.entities.values.forEach((e) => {
      if (!e.polygon) return;
      const hier = e.polygon.hierarchy.getValue?.();
      const positions = hier?.positions;
      if (!positions?.length) return;

      // simple average of positions (good enough for visual falloff)
      let sx = 0,
        sy = 0,
        sz = 0;
      for (const p of positions) {
        sx += p.x;
        sy += p.y;
        sz += p.z;
      }
      const c = new Cartesian3(
        sx / positions.length,
        sy / positions.length,
        sz / positions.length
      );
      centroids.push({ entity: e, c });
    });

    // center point = average of centroids
    let cx = 0,
      cy = 0,
      cz = 0;
    centroids.forEach(({ c }) => {
      cx += c.x;
      cy += c.y;
      cz += c.z;
    });
    const center = new Cartesian3(
      cx / centroids.length,
      cy / centroids.length,
      cz / centroids.length
    );

    // max distance from center
    let maxD = 0;
    centroids.forEach((o) => {
      o.d = Cartesian3.distance(o.c, center);
      if (o.d > maxD) maxD = o.d;
    });

    // 2) Second pass: style each polygon with alpha + color lerp toward bg tint
    centroids.forEach(({ entity: e, d }) => {
      const baseHex = e.properties?.color?.getValue?.() || "#969696";
      const baseCol = Color.fromCssColorString(baseHex);

      const t = Math.min(1, Math.max(0, d / maxD)); // 0 center → 1 rim
      const k = Math.pow(1 - t, falloffPow); // easing: 1 center → 0 rim
      const alpha = rimOpacity + k * (centerOpacity - rimOpacity);

      // mix base color toward background as we approach the rim
      const mixed = new Color();
      Color.lerp(baseCol, bgTint, 1 - k, mixed);
      mixed.alpha = alpha;

      e.polygon.material = mixed;
      e.polygon.outline = false;
    });

    // style any polylines consistently (rare)
    hexDS.entities.values.forEach((e) => {
      if (!e.polyline) return;
      const baseHex = e.properties?.color?.getValue?.() || "#969696";
      const col = Color.fromCssColorString(baseHex).withAlpha(centerOpacity);
      e.polyline.material = col;
      e.polyline.width = 1;
    });

    viewer.dataSources.add(hexDS);

    // Initial visibility based on mode
    hexDS.show = props.mode === "lighting";

    // Zoom to the hex area
    await viewer.zoomTo(hexDS);

    // Debug
    window.viewer = viewer;
    console.log("Loaded:", {
      hubs: hubsDS.entities.values.length,
      hex: hexDS.entities.values.length,
    });
  } catch (e) {
    console.error("Cesium init / data load failed:", e);
  }
});

/* React to sidebar mode changes */
watch(
  () => props.mode,
  (m) => {
    if (hexDS) hexDS.show = m === "lighting";
  }
);

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

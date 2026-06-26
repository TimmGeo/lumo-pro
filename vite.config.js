import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import vue from "@vitejs/plugin-vue";

const cesiumSource = "node_modules/cesium/Build/Cesium";
const cesiumBaseUrl = "cesium";

// The GitHub Actions workflow sets GITHUB_PAGES=true, so the build uses the
// GitHub Pages path. Locally and for the ETH GitLab deployment it falls back
// to the ETH path, so that deployment keeps working unchanged.
const base = process.env.GITHUB_PAGES ? "/lumo-pro/" : "/project/trogenmoser/";

export default defineConfig({
  base,
  plugins: [
    vue(),
    viteStaticCopy({
      targets: [
        { src: `${cesiumSource}/ThirdParty`, dest: cesiumBaseUrl },
        { src: `${cesiumSource}/Workers`, dest: cesiumBaseUrl },
        { src: `${cesiumSource}/Assets`, dest: cesiumBaseUrl },
        { src: `${cesiumSource}/Widgets`, dest: cesiumBaseUrl },
      ],
    }),
  ],
  server: {
    port: 3000,
    open: true,
  },
  preview: {
    port: 3010,
    open: true,
  },
  define: {
    CESIUM_BASE_URL: JSON.stringify(cesiumBaseUrl),
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          cesium: ["cesium"],
        },
      },
    },
    chunkSizeWarningLimit: 5000,
  },
});

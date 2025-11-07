import {
  WebMapTileServiceImageryProvider,
  WebMercatorTilingScheme,
  Rectangle,
} from "cesium";

// WMTS basemap (templated URL form)
const switzerland = Rectangle.fromDegrees(
  5.140224,
  45.398101,
  11.47757,
  48.230651
);
const kulturtypWMTS = new WebMapTileServiceImageryProvider({
  url: "https://wmts.geo.admin.ch/1.0.0/ch.blw.bodeneignung-kulturtyp/default/current/3857/{TileMatrix}/{TileCol}/{TileRow}.png",
  tilingScheme: new WebMercatorTilingScheme(),
  rectangle: switzerland,
  format: "image/png",
});

const layer = viewer.scene.imageryLayers.addImageryProvider(kulturtypWMTS);
viewer.zoomTo(layer);

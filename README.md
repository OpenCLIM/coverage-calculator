## Coverage Calculator

Creates a GeoTIFF with coverage (m<sup>2</sup>) of polygons inside 100m<sup>2</sup> grid cells.

A single GeoPackage (.gpkg) or Shapefile (.shp) containing polygons is required.

`gdal_rasterize` is used to burn the value `1` into a 1m resolution raster.
`gdalwarp` then resamples this raster to 100m resolution by summing cell values.

### Usage
`docker build -t coverage-calculator . && docker run -v "data:/data" --name coverage-calculator coverage-calculator` 
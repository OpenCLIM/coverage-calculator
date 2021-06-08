## UDM Rasterise Coverage

Creates an ASCII raster with coverage in (m<sup>2</sup>) of polygons inside 100m<sup>2</sup> grid cells.

A single GeoPackage (.gpkg) or Shapefile (.shp) containing polygons is required.

`gdal_rasterize` is used to burn the value `1` into a 1m resolution raster.
`gdalwarp` resamples this raster to 100m resolution by summing cell values.
'gdal_translate' converts to an ascii raster suitable for input to UDM. 

### Usage
`docker build -t udm-rasterise-coverage . && docker run -v "data:/data" --name udm-rasterise-coverage udm-rasterise-coverage` 
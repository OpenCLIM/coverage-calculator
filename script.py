import subprocess
from pathlib import Path

outputs = Path("/data/outputs")
outputs.mkdir(exist_ok=True)

subprocess.call(['gdal_rasterize',
                 '-burn', '1',
                 '-tr', '1', '1',
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',
                 '-ot', 'UInt16',
                 '/data/inputs/polygons/green_belt.gpkg', outputs / 'green_belt_1m.tif'])

subprocess.call(['gdalwarp',
                 '-tr', '100', '100',
                 '-r', 'sum',
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',
                 '-ot', 'UInt16',
                 '-overwrite',
                 outputs / 'green_belt_1m.tif', outputs / 'green_belt_100m.tif'])
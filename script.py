import subprocess
from pathlib import Path

outputs = Path("/data/outputs")
inputs = Path("/data/inputs")

input_files = []
for ext in ['shp', 'gpkg']:
    input_files.extend(list(inputs.glob(f"*/*.{ext}")))

assert len(input_files) > 0, 'No input files found'

outputs.mkdir(exist_ok=True)

subprocess.call(['gdal_rasterize',
                 '-burn', '1',
                 '-tr', '1', '1',
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',
                 '-ot', 'UInt16',
                 '-at',  # all pixels touched by polygons will be burned
                 input_files[0], outputs / 'coverage_1m.tif'])

subprocess.call(['gdalwarp',
                 '-tr', '100', '100',
                 '-r', 'sum',
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',
                 '-ot', 'UInt16',
                 '-overwrite',
                 outputs / 'coverage_1m.tif', outputs / 'coverage_100m.tif'])

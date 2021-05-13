import subprocess
from pathlib import Path
import os
import logging

outputs = Path("/data/outputs")
inputs = Path("/data/inputs")

outputs.mkdir(exist_ok=True)

logger = logging.getLogger('coverage_calculator')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(outputs / 'coverage_calculator.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

input_files = []
for ext in ['shp', 'gpkg']:
    input_files.extend(list(inputs.glob(f"*/*.{ext}")))

assert len(input_files) > 0, 'No input files found'

extent = os.getenv('EXTENT')
if extent == 'None' or extent is None:
    extent = []
else:
    extent = ['-te', *extent.split(',')]

selected_file = input_files[0]
logger.info(f'Rasterizing {selected_file}')

subprocess.call(['gdal_rasterize',
                 '-burn', '1',
                 '-tr', '1', '1',
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',
                 '-ot', 'UInt16',
                 '-at',  # all pixels touched by polygons will be burned
                 *extent,
                 selected_file, outputs / 'coverage_1m.tif'])

logger.info('Rasterizing completed')

logger.info('Upscaling raster')

subprocess.call(['gdalwarp',
                 '-tr', '100', '100',
                 '-r', 'sum',
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',
                 '-ot', 'UInt16',
                 '-overwrite',
                 outputs / 'coverage_1m.tif', outputs / 'coverage_100m.tif'])

logger.info('Upscaling completed')

import subprocess
from pathlib import Path
import os
import logging
import string
import random

#import variables as v

#------------------------------------------------------------------------------------------------------------------------------
#rasterise_1m

#configure directory/subdirectories
#current_dir = str(Path.cwd())
#print(current_dir)
#inputs = Path(current_dir + '/data/inputs/')
inputs = Path("/data/inputs/")
#print(inputs)

#temp = Path(current_dir + '/data/temp/')
temp = Path("/data/temp/")
#print(temp)

#outputs = Path(current_dir + '/data/outputs/')
outputs = Path("/data/outputs/")
#print(outputs)

temp.mkdir(exist_ok=True)
outputs.mkdir(exist_ok=True)

#configure output
logger = logging.getLogger('udm-rasterise-coverage')
logger.setLevel(logging.INFO)
log_name = 'udm-rasterise-coverage-%s.log' %(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
fh = logging.FileHandler(outputs / log_name)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#get input polygons
input_polygons = []
for ext in ['shp', 'gpkg']:
    input_polygons.extend(list(inputs.glob(f"*/*.{ext}")))

assert len(input_polygons) > 0, 'No input polygons found'

# use the first file in the list as the input polygons, or fetch the name passed if more than one input file found
if len(input_polygons) > 1:
    input_file_name = os.getenv('INPUTFILE')
    if input_file_name is not None:
        #selected_polygons = [s for s in input_polygons if input_file_name in s]
    
        for file in input_polygons:
            if input_file_name in str(file):
                selected_polygons = file
                break
    else:
        selected_polygons = selected_polygons[0]
else:
    selected_polygons = input_polygons[0]

#get extent 'xmin,ymin,xmax,ymax'
#extent = '459000,202000,501000,244000'
extent = os.getenv('EXTENT')

if extent == 'None' or extent is None:
    extent = []
else:
    extent = ['-te', *extent.split(',')]

#------------------------------------------------------------------------------------------------------------------------------
#rasterise_1m

logger.info(f'Rasterizing {selected_polygons}')

subprocess.call(['gdal_rasterize',
                 '-burn', '1',		#fixed value to burn for all objects
                 '-tr', '1', '1',	#target resolution <xres> <yres>
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',	#creation options
                 '-ot', 'UInt16',	#output data type
                 '-at',  			#enable all-touched rasterisation
                 *extent,			#'-te' <xmin> <ymin> <xmax> <ymax> 
                 selected_polygons, temp / 'rasterise_1m.tif'])	#src_datasource, dst_filename

logger.info('Rasterizing completed')

#------------------------------------------------------------------------------------------------------------------------------
#sum_resample_100m

logger.info('Sum resampling raster')

subprocess.call(['gdalwarp',
                 '-tr', '100', '100',	#target resolution <xres> <yres>
                 '-r', 'sum',			#resampling method e.g. sum OR mode
                 '-co', 'COMPRESS=LZW', '-co', 'NUM_THREADS=ALL_CPUS',	#creation options
                 '-ot', 'UInt16',		#output data type
                 '-overwrite',			#overwrite target dataset if already exists
                 temp / 'rasterise_1m.tif', temp / 'sum_resample_100m.tif'])	#srcfile, dstfile

logger.info('Sum resampling completed')

#------------------------------------------------------------------------------------------------------------------------------
#translate

#get layer name
#layer = 'test_region_coverage_100m.asc'
layer = os.getenv('LAYER') + '_coverage_100m.asc'



logger.info('Translating raster')

subprocess.call(['gdal_translate',
                 '-tr', '100', '100',	#target resolution <xres> <yres>                
                 '-ot', 'UInt16',		#output data type    
                 '-a_nodata', '0',		#set nodata value             
                 temp / 'sum_resample_100m.tif', outputs / layer])	#srcfile, dstfile

logger.info('Translating completed')

#------------------------------------------------------------------------------------------------------------------------------


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

#------------------------------------------------------------------------------------------------------------------------------
#set output metadata file
def metadata_json_template(output_title, output_description, bbox):
    """
    Generate a metadata json file used to catalogue the outputs of the UDM model on DAFNI
    """

    # Create metadata file
    metadata = f"""{{
      "@context": ["metadata-v1"],
      "@type": "dcat:Dataset",
      "dct:language": "en",
      "dct:title": "{output_title}",
      "dct:description": "{output_description}",
      "dcat:keyword": [
        "UDM"
      ],
      "dct:subject": "Environment",
      "dct:license": {{
        "@type": "LicenseDocument",
        "@id": "https://creativecommons.org/licences/by/4.0/",
        "rdfs:label": null
      }},
      "dct:creator": [{{"@type": "foaf:Organization"}}],
      "dcat:contactPoint": {{
        "@type": "vcard:Organization",
        "vcard:fn": "DAFNI",
        "vcard:hasEmail": "support@dafni.ac.uk"
      }},
      "dct:created": "{datetime.now().isoformat()}Z",
      "dct:PeriodOfTime": {{
        "type": "dct:PeriodOfTime",
        "time:hasBeginning": null,
        "time:hasEnd": null
      }},
      "dafni_version_note": "created",
      "dct:spatial": {{
        "@type": "dct:Location",
        "rdfs:label": null
      }},
      "geojson": {bbox}
    }}
    """
    
    return metadata

#------------------------------------------------------------------------------------------------------------------------------
# rasterise process
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
        selected_polygons = input_polygons[0]
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

# if output title passed, assume metadat file not being used
if os.getenv('OUTPUTTITLE') is not None:

    dataset = rasterio.open(outputs / layer)
    bbox = dataset.bounds
    geojson = Polygon([[(bbox.left,bbox.top), (bbox.right, bbox.top), (bbox.right,bbox.bottom), (bbox.left, bbox.bottom)]])


    metadata = metadata_json_template(os.getenv('OUTPUTTITLE'), os.getenv('OUTPUTDESCRIPTION'), geojson)



    # write metadata json to file
    with open(join(output_path, '%s.json' % file_name), 'w') as f:
        f.write(metadata)
        

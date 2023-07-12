import logging
import os
import subprocess
from datetime import datetime

path = "D:/git/gbl/musterstadt-giesst-treedata/weather_data/data_files/"

# setting up logging
logging.basicConfig()
LOGGING_MODE = None
if "LOGGING" in os.environ:
    LOGGING_MODE = os.getenv("LOGGING")
    if LOGGING_MODE == "ERROR":
        logging.root.setLevel(logging.ERROR)
    elif LOGGING_MODE == "WARNING":
        logging.root.setLevel(logging.WARNING)
    elif LOGGING_MODE == "INFO":
        logging.root.setLevel(logging.INFO)
    else:
        logging.root.setLevel(logging.NOTSET)
else:
    logging.root.setLevel(logging.NOTSET)

last_received = datetime.strptime("1970-01-01 01:00:00", '%Y-%m-%d %H:%M:%S')

# collecting all the files that need importing in one list
filelist = []
for (dirpath, dirnames, filenames) in os.walk(path):
    for dirname in dirnames:
        dpath = path + dirname
        for (ddirpath, ddirnames, ffilenames) in os.walk(dpath):
            for ffilename in ffilenames:
                filelist.append(dpath + "/" + ffilename)

for counter, file in enumerate(filelist):
    input_file = file

    file_split = file.split("/")
    date_time_obj = datetime.strptime(file_split[len(file_split) - 1], 'RW_%Y%m%d-%H%M.asc')
    if date_time_obj > last_received:
        last_received = date_time_obj
    logging.info("Processing: {} / {}".format(len(filelist), counter + 1))

    output_file = path + "temp.tif"

    # clean the temporary folder
    for del_file in [output_file, path + "temp.shp", path + "temp.shx", path + "temp.prj", path + "temp.dbf"]:
        if os.path.exists(del_file):
            os.remove(del_file)

    # for some reason the python gdal bindings are ****.
    # after hours of trying to get this to work in pure python,
    # this has proven to be more reliable and efficient. sorry.

    buffer_file = "D:/git/gbl/musterstadt-giesst-treedata/tree_data/data_files/buffer-small.shp"

    # filter data
    cmdline = ['gdalwarp', input_file, output_file,
               "-s_srs", "+proj=stere +lon_0=10.0 +lat_0=90.0 +lat_ts=60.0 +a=6370040 +b=6370040 +units=m",
               "-t_srs", "+proj=stere +lon_0=10.0 +lat_0=90.0 +lat_ts=60.0 +a=6370040 +b=6370040 +units=m",
               "-r", "near", "-of", "GTiff", "-cutline", buffer_file]
    subprocess.call(cmdline)

    # polygonize data
    cmdline = ['gdal_polygonize.py', output_file, "-f",
               "ESRI Shapefile", path + "temp.shp", "temp", "MYFLD"]
    # gdal_polygonize.py D:/git/gbl/musterstadt-giesst-treedata/weather_data/data_files/temp.tif -f "ESRI Shapefile" D:/git/gbl/musterstadt-giesst-treedata/weather_data/data_files/temp.shp temp MYFLD
    subprocess.call(cmdline)

import os
import numpy
import linecache

ROOT_DIR = os.path.abspath(os.curdir)
RADOLAN_PATH = f"{ROOT_DIR}/resources/radolan/"


# we need to give each grid cell a unique value, otherwise gdal_polygonize will combine cells with equal values
def create_radolon_grid():
    base_grid_file = f"{RADOLAN_PATH}grid-germany.asc"
    asc_data = numpy.loadtxt(base_grid_file, skiprows=6)
    col_value = 1
    for r_idx, row in enumerate(asc_data):
        for c_idx, col in enumerate(row):
            asc_data[r_idx][c_idx] = col_value
            col_value += 1

    header = linecache.getline(base_grid_file, 1) + \
        linecache.getline(base_grid_file, 2) + \
        linecache.getline(base_grid_file, 3) + \
        linecache.getline(base_grid_file, 4) + \
        linecache.getline(base_grid_file, 5) + \
        linecache.getline(base_grid_file, 6)

    numpy.savetxt(f"{RADOLAN_PATH}grid-transform.asc", asc_data,
                  header=header.rstrip(), comments='', fmt='%i')

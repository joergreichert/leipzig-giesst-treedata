# Musterstadt Gießt – Tree Data

Please review the content of the `README.md` and adjust it to the project.

## Prerequisites
 * [Python 3.11](https://www.python.org/downloads/)

## Install & Development

### Windows
#### QGIS
 * https://qgis.org/en/site/forusers/download.html
 * this will install also `OSGeo4W Shell` where gdal is available (check `gdalinfo --version`)
 
### Local PostgreSQL
 * Download latest (15.3) and install: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads 
 * Download latest PostGIS and install in before installed Postgres folder: https://download.osgeo.org/postgis/windows/pg15/ 
 * Connect to database and execute:
```
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```
 
#### Miniconda
 * https://docs.conda.io/en/latest/miniconda.html#windows-installers
 * Open `Anaconda prompt (miniconda3)` from Quick start

### Linux
#### Miniconda

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
rm ./Miniconda3-latest-Linux-x86_64.sh
```

### All
#### Miniconda
 * change to folder containing this locally checked out Git repo

```
conda update conda
conda create -n treedata
conda activate treedata
conda install pip
pip install -r requirements.txt
```

### PyCharm
 * Download Community Edition: https://www.jetbrains.com/pycharm/
 * https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html#create-a-conda-environment
   * select existing environment `treedata`
 * open new terminal to see activated conda environment `treedata`

### Next steps
 * copy `treedata/sample.env` to `treedata/.env`
   * set your (locally) PostgreSQL connection data

## Demo
 * Download city shape WFS file to geojson: `python ./tree_data/get_city_shape_from_wfs.py`
 * Download trees WFS file to geojson: `python ./tree_data/get_data_from_wfs.py`
 * Process geojson: `python ./tree_data/main.py`
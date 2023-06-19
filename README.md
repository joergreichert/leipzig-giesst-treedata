# Musterstadt Gießt – Tree Data

Please review the content of the `README.md` and adjust it to the project.

## Prerequisites

- [Python 3.8](https://www.python.org/downloads/)
- [pyenv](https://github.com/pyenv/pyenv) (optional)
- [Miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html#install-linux-silent)
- [GeoPandas](https://geopandas.org/en/v0.7.0/install.html)


## Install & Development

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
rm ./Miniconda3-latest-Linux-x86_64.sh
conda update conda
conda create -n treedata
conda activate treedata
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
conda install python=3 gdal geopandas requests
```

## Demo

`python3 ./01_download_wfs_to_shp.py --url https://kommisdd.dresden.de/net3/public/ogcsl.ashx?nodeid=1633&service=wfs&request=getcapabilities`
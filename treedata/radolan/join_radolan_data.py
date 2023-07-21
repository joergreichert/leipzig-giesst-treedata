import logging
import os
import pandas
import geopandas
from datetime import datetime

ROOT_DIR = os.path.abspath(os.curdir)
path = f"{ROOT_DIR}/resources/radolan"


def get_radolan_geometry():
    filelist = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for ffilename in filenames:
            if "shp" in ffilename:
                filelist.append(path + "/" + ffilename)

    gdf = None
    for counter, file in enumerate(filelist):
        df = geopandas.read_file(file)
        df = df.to_crs("epsg:3857")
        if df['geometry'].count() > 0:
            geo_series = geopandas.GeoSeries(data=df['geometry'])
            centroid = geo_series.centroid
            df['centroid'] = centroid
            df = df.drop('MYFLD', axis=1)
            if gdf is None:
                gdf = df
            else:
                gdf = pandas.concat([gdf, df], ignore_index=True)
    unique = gdf.drop_duplicates()
    return unique


def join_radolan_data():
    filelist = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for ffilename in filenames:
            if "shp" in ffilename:
                filelist.append(path + "/" + ffilename)

    gdf = None
    for counter, file in enumerate(filelist):
        file_split = file.split("/")
        file_name = file_split[len(file_split) - 1].split('.')[0]
        date_time_obj = datetime.strptime(file_name, 'RW_%Y%m%d-%H%M')

        df = geopandas.read_file(file)
        df = df.to_crs("epsg:3857")

        # if there was no rain on that timestamp, there will be no data to insert
        if df['geometry'].count() > 0:
            clean = df[(df['MYFLD'] > 0) & (df['MYFLD'].notnull())]
            if len(clean) > 0:
                logging.info("🌧 Found some rain")
                df['measured_at'] = date_time_obj.strftime('%Y-%m-%d')
                if gdf is None:
                    gdf = df
                else:
                    gdf = pandas.concat([gdf, df], ignore_index=True)
    return gdf

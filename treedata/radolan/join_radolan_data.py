import logging
import os
from shapely.wkt import dumps
import pandas
import geopandas
from datetime import datetime

path = "./resources/radolan"


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
            clean = df[(df['MYFLD'] == 0) & (df['MYFLD'].notnull())]
            if len(clean) > 0:
                logging.info("🌧 Found some rain")
                df['measured_at'] = date_time_obj.strftime('%Y-%m-%d')
                if gdf is None:
                    gdf = df
                else:
                    gdf = pandas.concat([gdf, df], ignore_index=True)
    return gdf

# def store_to_db():
#     with conn.cursor() as cur:
#         # just to be sure
#         cur.execute("DELETE FROM radolan_temp;")
#         try:
#             psycopg2.extras.execute_batch(
#                 cur,
#                 "INSERT INTO radolan_temp (geometry, value, measured_at) VALUES (ST_Multi(ST_Transform(ST_GeomFromText(%s, 3857), 4326)), %s, %s);",
#                 values
#             )
#         except:
#             logging.error("❌Could not insert into radolan_temp")
#         # in order to keep our database fast and small, we are not storing the original polygonized data, but instead we are using a grid and only store the grid ids and the corresponding precipitation data
#         cur.execute \
#             ("INSERT INTO radolan_data (geom_id, value, measured_at) SELECT radolan_geometry.id, radolan_temp.value, radolan_temp.measured_at FROM radolan_geometry JOIN radolan_temp ON ST_WithIn(radolan_geometry.centroid, radolan_temp.geometry);")
#         cur.execute("DELETE FROM radolan_temp;")
#         conn.commit()

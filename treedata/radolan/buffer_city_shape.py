# building a buffer shape for filtering the weather data
import os
import geopandas
from shapely.ops import unary_union

ROOT_DIR = os.path.abspath(os.curdir)


def create_buffered_city_shape(input_file_name, output_file_name, buffer_radius, simplify_tolerance):
    city_shape = geopandas.read_file(f"{ROOT_DIR}/resources/city_shape/{input_file_name}.geojson")
    city_shape = city_shape.to_crs("epsg:3857")
    polygon = unary_union(city_shape['geometry'])
    geo_series = geopandas.GeoSeries(data=[polygon])
    if not buffer_radius is None:
        geo_series = geo_series.buffer(distance=int(buffer_radius))
    if not simplify_tolerance is None:
        geo_series = geo_series.simplify(int(simplify_tolerance))
    city_shape_buffer = geopandas.GeoDataFrame(geometry=geo_series, crs="epsg:3857")
    city_shape_buffer.to_file(f"{ROOT_DIR}/resources/city_shape/{output_file_name}.shp")

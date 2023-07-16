# building a buffer shape for filtering the weather data
import geopandas
from shapely.ops import cascaded_union


def create_buffered_city_shape(input_file_name, output_file_name, buffer, simplify_factor):
    city_shape = geopandas.read_file(f"./resources/city_shape/{input_file_name}.geojson")
    city_shape = city_shape.to_crs("epsg:3857")
    city_shape_boundary = geopandas.GeoDataFrame(
        geopandas.GeoSeries(cascaded_union(city_shape['geometry']))
    )
    city_shape_boundary = city_shape_boundary.rename(columns={0: 'geometry'}).set_geometry('geometry')

    city_shape_buffer = city_shape_boundary.buffer(buffer)
    city_shape_buffer = city_shape_buffer.simplify(simplify_factor)

    city_shape_buffer = geopandas.GeoDataFrame(city_shape_buffer)
    city_shape_buffer = city_shape_buffer.rename(columns={0: 'geometry'}).set_geometry('geometry')
    city_shape_buffer.crs = "epsg:3857"
    city_shape_buffer.to_file(f"./resources/city_shape/{output_file_name}.shp")

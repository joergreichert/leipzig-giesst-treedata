import geopandas
from shapely import Point


def __get_district__(point, polygons):
    result = point.within(polygons)
    for index, res in enumerate(result):
        if res:
            return polygons['bez'][index]
    return None


def get_district(x, y, city_shape):
    return __get_district__(
        geopandas.GeoSeries(
            Point([x, y]),
            crs=city_shape.crs,
            index=city_shape.index
        ),
        city_shape
    )

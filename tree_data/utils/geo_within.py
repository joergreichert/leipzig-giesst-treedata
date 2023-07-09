from get_data_from_wfs import read_geojson


def get_district(point, polygons):
    result = point.within(polygons)
    if result[0]:
        return polygons['bez']
    return None

city_shape = read_geojson('./tree_data/data_files/city_shape-small.geojson')
trees = read_geojson('./tree_data/data_files/s_wfs_baumbestand_2023-07-08-small.geojson')
print(get_district(trees, city_shape))
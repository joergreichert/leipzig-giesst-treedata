import json
from datetime import datetime


def create_feature(prop_id, geometry, data):
    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "id": prop_id,
            "data": [
                data
            ]
        }
    }


def transform_to_features(grid, clean, calc_fun):
    features = []
    for cellindex, cell in enumerate(grid):
        data = calc_fun(clean[cellindex])
        features.append(create_feature(
            prop_id=cell[1],
            geometry=cell[0],
            data=data
        ))
    return features


def transform_to_weather_geojson_features(grid, clean):
    def calc_fun(value):
        return ",".join(map(str, value))

    return transform_to_features(grid, clean, calc_fun)


def transform_to_weather_light_geojson_features(grid, clean):
    def calc_fun(value):
        return sum(value)

    return transform_to_features(grid, clean, calc_fun)


def create_geo_json(start_date, end_date, features):
    return {
        "type": "FeatureCollection",
        "properties": {
            "start": start_date,
            "end": end_date
        },
        "features": features
    }


def datetime_handler(value):
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unknown type: {value}")


def write_geojson(path, file_name, start_date, end_date, feature_list):
    geojson = create_geo_json(
        start_date=start_date,
        end_date=end_date,
        features=feature_list
    )
    file_path = f"{path}{file_name}.geojson"
    with open(file_path, 'w') as f:
        f.write(json.dumps(geojson, default=datetime_handler))
    return f"{file_name}.geojson"


def process_geojson(path, file_name, start_date, end_date, feature_list):
    write_geojson(path, file_name, start_date, end_date, feature_list)


objects_to_write = {
    "weather": transform_to_weather_geojson_features,
    "weather_light": transform_to_weather_light_geojson_features,
}


def write_radolan_geojsons(path, start_date, end_date, grid, clean):
    for file_name in objects_to_write:
        transform_fun = objects_to_write[file_name]
        features = transform_fun(grid=grid, clean=clean)
        process_geojson(
            path=path,
            file_name=file_name,
            start_date=start_date,
            end_date=end_date,
            feature_list=features,
        )


def get_radolan_files_for_upload(path):
    file_path_to_file_name = {}
    for file_name in objects_to_write:
        file_path = f"{path}{file_name}.geojson"
        for file_path in [file_path, f"{file_path}.gz"]:
            file_path_to_file_name[file_path] = file_name
    return file_path_to_file_name

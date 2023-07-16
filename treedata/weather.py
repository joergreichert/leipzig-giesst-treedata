import argparse

from radolan.buffer_city_shape import create_buffered_city_shape
from radolan.download_weather_data import download_weather_data
from radolan.extract_weather_data import extract_weather_data
from radolan.polygonize_weather_data import polygonize_weather_data
from radolan.join_radolan_data import join_radolan_data
from utils.get_data_from_wfs import store_as_geojson


def configure_weather_args(parser=argparse.ArgumentParser(description='Process weather data')):
    parser.add_argument('--start-days-offset', dest='start_days_offset', action='store',
                        help='number of days from today in past to start downloading radolan data', default=2)
    parser.add_argument('--end-days-offset', dest='end_days_offset', action='store',
                        help='number of days from today in past to stop downloading radolan data', default=1)
    parser.add_argument('--city-shape-geojson-file-name', dest='city_shape_file_name', action='store',
                        help='Provide GeoJSON file name of city shape to use', default='city_shape-small')
    parser.add_argument('--city-shape-buffer-file-name', dest='city_shape_buffer_file_name', action='store',
                        help='file name to store buffered city shape under', default='city_shape-small-buffered')
    parser.add_argument('--city-shape-buffer', dest='city_shape_buffer', action='store',
                        help='buffer to apply for buffering city shape', default=2000)
    parser.add_argument('--city-shape-simplify', dest='city_shape_simplify', action='store',
                        help='simplify factor to apply for simplifying city shape', default=1000)
    parser.add_argument('--skip-download-weather-data', dest='skip_download_weather_data', action='store_true',
                        help='skip step of downloading radolan data', default=False)
    parser.add_argument('--skip-unzip-weather-data', dest='skip_unzip_weather_data', action='store_true',
                        help='skip step of unzipping radolan data', default=False)
    parser.add_argument('--skip-buffer-city-shape', dest='skip_buffer_city_shape', action='store_true',
                        help='skip step of creating buffer shape of city shape', default=False)
    parser.add_argument('--skip-polygonize-weather-data', dest='skip_polygonize_weather_data', action='store_true',
                        help='skip step of polygnize radolan data as shape files', default=False)
    parser.add_argument('--skip-join-radolan-data', dest='skip_join_radolan_data', action='store_true',
                        help='skip step of joining radolan shp files to geojson', default=False)
    parser.set_defaults(which='weather', func=handle_weather)


def handle_weather(args):
    if not args.skip_buffer_city_shape:
        create_buffered_city_shape(
            input_file_name=args.city_shape_file_name,
            output_file_name=args.city_shape_buffer_file_name,
            buffer=args.city_shape_buffer,
            simplify_factor=args.city_shape_simplify
        )
    if not args.skip_download_weather_data:
        download_weather_data(
            start_days_offset=args.start_days_offset,
            end_days_offset=args.end_days_offset,
        )
    if not args.skip_unzip_weather_data:
        extract_weather_data()
    if not args.skip_polygonize_weather_data:
        polygonize_weather_data(args.city_shape_buffer_file_name)
    if not args.skip_join_radolan_data:
        radolan_data = join_radolan_data()
        store_as_geojson(radolan_data, f"./resources/radolan/radolan-joined")

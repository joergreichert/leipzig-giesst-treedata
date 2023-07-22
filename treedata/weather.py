import os
import argparse
from datetime import datetime, timedelta

from radolan.buffer_city_shape import create_buffered_city_shape
from radolan.download_weather_data import download_weather_data
from radolan.extract_weather_data import extract_weather_data
from radolan.polygonize_weather_data import polygonize_weather_data
from radolan.join_radolan_data import join_radolan_data
from radolan.upload_radolan import upload_radolan_data, purge_data_older_than_time_limit_days, purge_duplicates
from radolan.create_radolan_schemas import create_radolan_schema
from radolan.update_tree_radolan_days import get_weather_data_grid_cells, get_sorted_cleaned_grid_cells, \
    update_tree_radolan_days, update_statistics_db, get_sorted_cleaned_grid
from radolan.write_radolan_geojsons import write_radolan_geojsons, get_radolan_files_for_upload
from radolan.write_radolan_csvs import write_radolan_csvs
from utils.gzip_file import gzip_files
from utils.s3_client import create_s3_client, upload_files_to_s3
from utils.interact_with_database import get_db_engine
from utils.get_data_from_wfs import store_as_geojson, read_geojson

ROOT_DIR = os.path.abspath(os.curdir)
RADOLAN_PATH = f"{ROOT_DIR}/resources/radolan"
TIME_LIMIT_DAYS = 30


def configure_weather_args(parser=argparse.ArgumentParser(description='Process weather data')):
    parser.add_argument('--start-days-offset', dest='start_days_offset', action='store',
                        help='number of days from today in past to start downloading radolan data', default=2)
    parser.add_argument('--end-days-offset', dest='end_days_offset', action='store',
                        help='number of days from today in past to stop downloading radolan data', default=1)
    parser.add_argument('--city-shape-geojson-file-name', dest='city_shape_file_name', action='store',
                        help='Provide GeoJSON file name of city shape to use', default='city_shape')
    parser.add_argument('--city-shape-buffer-file-name', dest='city_shape_buffer_file_name', action='store',
                        help='file name to store buffered city shape under', default='city_shape-buffered')
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
    parser.add_argument('--skip-upload-radolan-data', dest='skip_upload_radolan_data', action='store_true',
                        help='skip step of upload radolan geojson to DB', default=False)
    parser.add_argument('--skip-update-tree-radolan-days', dest='skip_update_tree_radolan_days', action='store_true',
                        help='skip step of updating trees with radolan days', default=False)
    parser.add_argument('--skip-upload-geojsons-to-s3', dest='skip_upload_geojsons_to_s3', action='store_true',
                        help='skip step of radolan data geojson file generation and S3 upload', default=False)
    parser.add_argument('--skip-upload-csvs-to-s3', dest='skip_upload_csvs_to_s3', action='store_true',
                        help='skip step of radolan data CSV file generation and S3 upload', default=False)
    parser.set_defaults(which='weather', func=handle_weather)


def handle_weather(args):
    if not args.skip_buffer_city_shape:
        create_buffered_city_shape(
            input_file_name=args.city_shape_file_name,
            output_file_name=args.city_shape_buffer_file_name,
            buffer_radius=args.city_shape_buffer,
            simplify_tolerance=args.city_shape_simplify
        )
    if not args.skip_download_weather_data:
        download_weather_data(
            start_days_offset=int(args.start_days_offset),
            end_days_offset=int(args.end_days_offset),
        )
    if not args.skip_unzip_weather_data:
        extract_weather_data()
    if not args.skip_polygonize_weather_data:
        filelist, last_received = polygonize_weather_data(args.city_shape_buffer_file_name)
        db_engine = get_db_engine()
        update_statistics_db(filelist, db_engine, TIME_LIMIT_DAYS, last_received)
    joined_path = f"{RADOLAN_PATH}/radolan-joined"
    if not args.skip_join_radolan_data:
        radolan_data = join_radolan_data()
        store_as_geojson(radolan_data, joined_path)
    else:
        radolan_data = read_geojson(f"{joined_path}.geojson")
    if not args.skip_upload_radolan_data:
        db_engine = get_db_engine()
        create_radolan_schema(db_engine)
        upload_radolan_data(db_engine, radolan_data)
        purge_data_older_than_time_limit_days(db_engine, TIME_LIMIT_DAYS)
        purge_duplicates(db_engine)
    if not args.skip_update_tree_radolan_days:
        db_engine = get_db_engine()
        grid = get_weather_data_grid_cells(engine=db_engine, time_limit_days=TIME_LIMIT_DAYS)
        clean = get_sorted_cleaned_grid(grid, TIME_LIMIT_DAYS)
        start_date = datetime.now() + timedelta(days=-TIME_LIMIT_DAYS)
        start_date = start_date.replace(hour=0, minute=50, second=0, microsecond=0)
        end_date = datetime.now() + timedelta(days=-1)
        end_date = end_date.replace(hour=23, minute=50, second=0, microsecond=0)
        write_radolan_geojsons(
            path=f"{RADOLAN_PATH}/",
            start_date=start_date,
            end_date=end_date,
            grid=grid,
            clean=clean
        )
        values = get_sorted_cleaned_grid_cells(clean)
        update_tree_radolan_days(db_engine, values)
    if not args.skip_upload_geojsons_to_s3:
        file_path_to_file_name = get_radolan_files_for_upload(path=f"{RADOLAN_PATH}/")
        gzip_file_path_to_file_name = gzip_files(file_path_to_file_name)
        file_path_to_file_name_union = file_path_to_file_name | gzip_file_path_to_file_name
        if False:
            s3_client = create_s3_client(
                aws_access_key=os.getenv("ACCESS_KEY"),
                aws_secret_key=os.getenv("SECRET_KEY")
            )
            upload_files_to_s3(
                s3_client=s3_client,
                s3_bucket_name=os.getenv("S3_BUCKET"),
                file_path_to_file_name=file_path_to_file_name_union
            )
    if not args.skip_upload_csvs_to_s3:
        db_engine = get_db_engine()
        file_path_to_file_name = write_radolan_csvs(
            engine=db_engine,
            time_limit_days=TIME_LIMIT_DAYS,
            path=f"{RADOLAN_PATH}/"
        )
        gzip_file_path_to_file_name = gzip_files(file_path_to_file_name)
        file_path_to_file_name_union = file_path_to_file_name | gzip_file_path_to_file_name
        if False:
            s3_client = create_s3_client(
                aws_access_key=os.getenv("ACCESS_KEY"),
                aws_secret_key=os.getenv("SECRET_KEY")
            )
            upload_files_to_s3(
                s3_client=s3_client,
                s3_bucket_name=os.getenv("S3_BUCKET"),
                file_path_to_file_name=file_path_to_file_name_union
            )



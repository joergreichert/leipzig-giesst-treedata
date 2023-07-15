import argparse
import logging
from utils.get_data_from_wfs import read_geojson, store_as_geojson
from utils.interact_with_database import get_db_engine, add_to_db
from trees.utils.process_data import read_config, transform_new_tree_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

attribute_list = [
    'id',
    'geometry',
    'strname',
    'haus_nr',
    'artbot',
    'artdtsch',
    'standort_nr',
    'baumhoehe',
    'stammdurch',
    'kronedurch',
    'zuletztakt',
    'gattung',
    'gattungdeutsch2',
    'pflanzjahr',
    'stammumfg',
    'xcoord',
    'ycoord',
    'bezirk'
]

source_encoding_default = 'ISO-8859-1'
geojson_file_name_default = 'trees-transformed'
database_table_name_default = 'trees_tmp'


def configure_trees_process_args(parser=argparse.ArgumentParser(description='Transform trees data')):
    parser.add_argument('-c', '--city-shape-geojson-file-name', dest='city_shape_file_name', action='store',
                        help='Provide GeoJSON file name of city shape to use', default='city_shape-small')
    parser.add_argument('-t', '--trees-geojson-file-name', dest='trees_file_name', action='store',
                        help='Provide GeoJSON file name of tress data to use',
                        default='s_wfs_baumbestand_2023-07-08-small')
    parser.add_argument('-e', '--source-encoding', dest='source_encoding', action='store', help='Provide WFS Encoding',
                        default=source_encoding_default)
    parser.add_argument('-j', '--geojson-file-name', dest='geojson_file_name', action='store',
                        help='Provide file name to store GeoJSON file locally',
                        default=geojson_file_name_default)
    parser.add_argument('-d', '--database-table-name', dest='database_table_name', action='store',
                        help='database table name to store the Geo data frame',
                        default=database_table_name_default)
    parser.add_argument('--skip-transform', dest='skip_transform', action='store_true',
                        help='skip step of transforming tree data', default=False)
    parser.add_argument('--skip-store-as-geojson', dest='skip_store_as_geojson', action='store_true',
                        help='skip step of storing transform Geo data frame to GeoJSON file', default=False)
    parser.add_argument('--skip-upload-to-db', dest='skip_upload_to_db', action='store_true',
                        help='skip storing Geo data frame to database', default=False)
    parser.set_defaults(which='trees_process', func=handle_trees_process)


def handle_trees_process(args):
    city_shape = read_geojson(f"./resources/city_shape/{args.city_shape_file_name}.geojson")
    schema_mapping_dict, schema_calculated_dict = read_config()

    if not args.skip_transform:
        new_trees = read_geojson(f"./resources/trees/{args.trees_file_name}.geojson")
        transformed_trees = transform_new_tree_data(
            new_trees=new_trees,
            attribute_list=attribute_list,
            schema_mapping_dict=schema_mapping_dict,
            schema_calculated_dict=schema_calculated_dict,
            city_shape=city_shape
        )
    else:
        transformed_trees = read_geojson(f"./resources/trees/{args.geojson_file_name}.geojson")

    if not args.skip_store_as_geojson:
        store_as_geojson(transformed_trees, f"./resources/trees/{args.geojson_file_name}.geojson")

    #for att in attribute_list:
    #    if att in transformed_trees:
    #        logger.info(transformed_trees[att])

    if not args.skip_upload_to_db:
        logger.info("Adding new trees to database...")
        db_engine = get_db_engine()
        add_to_db(db_engine, transformed_trees, args.database_table_name)

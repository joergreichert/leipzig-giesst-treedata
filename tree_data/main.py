import logging
import time

from tree_data.utils.get_data_from_wfs import read_geojson
from utils.interact_with_database import start_db_connection,  add_to_db
from utils.process_data import read_config, transform_new_tree_data

logger = logging.getLogger('root')
FORMAT = "[%(levelname)s %(name)s] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

start = time.time()

new_trees_paths_list, schema_mapping_dict, schema_calculated_dict, database_dict, year = read_config()

conn = start_db_connection()

new_trees = read_geojson(new_trees_paths_list[0])
attribute_list = [
    'id',
    'geom',
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
transformed_trees = transform_new_tree_data(new_trees, attribute_list, schema_mapping_dict)

logger.info("Adding new trees to database...")
add_to_db(conn, transformed_trees, 'trees')

end = time.time() - start
logger.info("It took {} seconds to run the script".format(end))
import argparse
import logging
import time
from city_wfs import configure_city_shape_args
from trees_wfs import configure_trees_args
from trees_process import configure_trees_process_args

logger = logging.getLogger('root')
FORMAT = "[%(levelname)s %(name)s] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

start = time.time()

parser = argparse.ArgumentParser(description='Processing city shape, tree data and weather data')
subparsers = parser.add_subparsers(help='actions', dest='action')

city_shape_parser = subparsers.add_parser('city_shape', help="Download and process city shape")
configure_city_shape_args(city_shape_parser)

trees_parser = subparsers.add_parser('trees', help="Download and process tree data")
configure_trees_args(trees_parser)

trees_process_parser = subparsers.add_parser('trees_process', help="Transform and upload tree data")
configure_trees_process_args(trees_process_parser)


res = parser.parse_args()
res.func(res)

end = time.time() - start
logger.info("It took {} seconds to run the script".format(end))
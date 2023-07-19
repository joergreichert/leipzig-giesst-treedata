import os
import argparse

from utils.wfs_with_args import configure_wfs_args, handle_wfs

wfs_url_base_default = 'https://kommisdd.dresden.de/net3/public/ogcsl.ashx?nodeid=188&service=' \
                       'wfs&request=getcapabilities'
ROOT_DIR = os.path.abspath(os.curdir)
base_folder = '$ROOT_DIR/../resources/city_shape'
xml_file_name_default = 'city_shape'
geojson_file_name_default = 'city_shape'


def configure_city_shape_args(parser=argparse.ArgumentParser(description='Process city shape')):
    configure_wfs_args(
        wfs_url_base_default,
        xml_file_name_default,
        geojson_file_name_default,
        parser=parser,
    )
    parser.set_defaults(which='city_shape', func=handle_city_shape)


def handle_city_shape(args):
    handle_wfs(args, base_folder)



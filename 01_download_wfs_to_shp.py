from requests import Request
import geopandas as gpd
import argparse

parser = argparse.ArgumentParser(description='Export WFS')
parser.add_argument('--url', dest='url', action='store', help='Provide WFS URL',
                    default='https://kommisdd.dresden.de/net3/public/ogcsl.ashx?'
                            + 'nodeid=1633&service=wfs&request=getcapabilities')
args = parser.parse_args()

q = Request('GET', args.url).prepare().url
df = gpd.read_file(q, format='GML')
df.crs = 'EPSG:4326'

df.to_file('output.shp')
from requests import Request
import geopandas as gpd
import fiona
import argparse

fiona.drvsupport.supported_drivers['WFS'] = 'r'

parser = argparse.ArgumentParser(description='Export WFS')
parser.add_argument('--url', dest='url', action='store', help='Provide WFS URL',
                    default='https://kommisdd.dresden.de/net3/public/ogcsl.ashx?'
                            + 'nodeid=1633&service=wfs&request=getcapabilities')
args = parser.parse_args()

q = Request('GET', args.url).prepare().url
df = gpd.read_file(q, format='WFS', layer='cls:L1261')
df.crs = 'EPSG:4326'

df.to_file('output.shp')
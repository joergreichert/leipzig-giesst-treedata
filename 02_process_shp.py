from requests import Request
import geopandas as gpd
import argparse

parser = argparse.ArgumentParser(description='Process shape file')
parser.add_argument('--url', dest='url', action='store', help='Provide shpae file',
                    default='output.hsp')
args = parser.parse_args()

q = Request('GET', args.url).prepare().url
df = gpd.read_file(q)
df.crs = 'EPSG:4326'

#add geometry attributes

#rename attributes

#calculate derived attributes

#export shape file

#import shapefile to database
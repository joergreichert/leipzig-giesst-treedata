from datetime import datetime

from utils.get_data_from_wfs import get_wfs_request_url, convert_xml_to_geojson, download_wfs_to_xml

dateFormat = "{:0>2d}"
currentDay = dateFormat.format(datetime.now().day)
currentMonth = dateFormat.format(datetime.now().month)
currentYear = str(datetime.now().year)
dateStr = f"{currentYear}-{currentMonth}-{currentDay}"

wfs_url_base = 'https://kommisdd.dresden.de/net3/public/ogcsl.ashx?nodeid=1633&service=wfs&request=getcapabilities'
wfs_url_with_params = get_wfs_request_url(wfs_url_base)

xml_file_name = 'wfs.xml'
source_encoding = 'iso-8859-1'
download_wfs_to_xml(wfs_url=wfs_url_with_params, source_encoding=source_encoding, outfile_name=xml_file_name)

geojson_file_name = f"treedata/data_files/s_wfs_baumbestand_{dateStr}"
convert_xml_to_geojson(infile_name=xml_file_name, source_encoding=source_encoding, outfile_name=geojson_file_name)

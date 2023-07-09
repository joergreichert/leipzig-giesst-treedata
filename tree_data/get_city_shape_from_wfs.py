from utils.get_data_from_wfs import get_wfs_request_url, convert_xml_to_geojson, download_wfs_to_xml


wfs_url_base = 'https://kommisdd.dresden.de/net3/public/ogcsl.ashx?nodeid=188&service=wfs&request=getcapabilities'
wfs_url_with_params = get_wfs_request_url(wfs_url_base)

xml_file_name = './tree_data/data_files/city_shape.xml'
source_encoding = 'iso-8859-1'
download_wfs_to_xml(wfs_url=wfs_url_with_params, source_encoding=source_encoding, outfile_name=xml_file_name)

geojson_file_name = f"tree_data/data_files/city_shape"
convert_xml_to_geojson(infile_name=xml_file_name, source_encoding=source_encoding, outfile_name=geojson_file_name)

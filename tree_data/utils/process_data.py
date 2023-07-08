import logging

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_config():
    with open("conf.yml", 'r') as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.exception('Error occurred while reading the conf.yml: {}'.format(e))
            raise

    new_trees_paths_list = conf['new-data-paths']
    schema_mapping_dict = conf['data-schema']['mapping']
    schema_calculated_dict = conf['data-schema']['calculated']
    database_dict = conf['database']
    year = conf['year']

    return new_trees_paths_list, schema_mapping_dict, schema_calculated_dict, database_dict, year


def transform_new_tree_data(new_trees, attribute_list, schema_mapping_dict):
    transformed_trees = new_trees.rename(columns=schema_mapping_dict)

    # transform gmlid here
    transformed_trees['gmlid'] = transformed_trees['gmlid'].str.split(pat=".").str[1]

    # drop not needed colums based on the columns of the old data
    for column in transformed_trees.columns:
        if column == "geometry":
            continue
        else:
            if column not in attribute_list:
                transformed_trees = transformed_trees.drop([column], axis=1)

    duplicates_count = len(transformed_trees) - len(transformed_trees.drop_duplicates(subset=['gmlid']))

    # drop duplicate features based on gmlid
    transformed_trees = transformed_trees.drop_duplicates(subset=['gmlid'])

    # replace NA values with 'undefined' and transform dataformats to string
    for column in transformed_trees.columns:
        if column != "geometry":
            if transformed_trees[
                column].dtype != object or column == 'kronedurch':  # 'kronedurch' is from type object but is loaded to the db as double precision, this is why we have to make this hack here
                transformed_trees[column] = transformed_trees[column].fillna('99999')
                transformed_trees[column] = transformed_trees[column].astype(int).astype(str)
    transformed_trees = transformed_trees.replace(['99999'], 'undefined')
    transformed_trees = transformed_trees.replace('', 'undefined')

    transformed_trees['lng'] = (transformed_trees.geometry.y).round(5).astype(str)
    transformed_trees['lat'] = (transformed_trees.geometry.x).round(5).astype(str)

    logger.info("ℹ️ " + str(duplicates_count) + " trees with a duplicated gmlid were dropped.")
    return transformed_trees

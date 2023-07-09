import logging

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_config():
    with open("./tree_data/conf.yml", 'r') as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.exception(f'Error occurred while reading the conf.yml: {e}')
            raise

    new_trees_paths_list = conf['new-data-paths']
    schema_mapping_dict = conf['data-schema']['mapping']
    schema_calculated_dict = conf['data-schema']['calculated']
    database_dict = conf['database']

    return new_trees_paths_list, schema_mapping_dict, schema_calculated_dict, database_dict


def transform_new_tree_data(new_trees, attribute_list, schema_mapping_dict):
    transformed_trees = new_trees.rename(columns=schema_mapping_dict)

    # transform gml_id here
    transformed_trees['id'] = str(transformed_trees['standort_nr']).split(".")[1]

    # drop not needed columns based on the columns of the old data
    for column in transformed_trees.columns:
        if column == "geometry":
            continue
        else:
            if column not in attribute_list:
                try:
                    transformed_trees = transformed_trees.drop([column], axis=1)
                except:
                    print(f'{column} not found')

    duplicates_count = len(transformed_trees) - len(transformed_trees.drop_duplicates(subset=['id']))

    # drop duplicate features based on gml_id
    transformed_trees = transformed_trees.drop_duplicates(subset=['id'])

    # replace NA values with 'undefined' and transform data formats to string
    for column in transformed_trees.columns:
        if column != "geometry":
            dtype = transformed_trees[column].dtype
            if str(dtype).startswith('datetime64'):
                transformed_trees[column] = transformed_trees[column].astype(str)
            elif dtype != object or column == 'kronedurch':
                # 'kronedurch' is from type object but is loaded to the db as double precision,
                # this is why we have to make this hack here
                transformed_trees[column] = transformed_trees[column].fillna('99999')
                try:
                    transformed_trees[column] = transformed_trees[column].astype(int).astype(str)
                except:
                    print(f'{column} has type {transformed_trees[column].dtype}')
    transformed_trees = transformed_trees.replace(['99999'], 'undefined')
    transformed_trees = transformed_trees.replace('', 'undefined')

    transformed_trees['lng'] = transformed_trees.geometry.y.round(5).astype(str)
    transformed_trees['lat'] = transformed_trees.geometry.x.round(5).astype(str)

    logger.info("ℹ️ " + str(duplicates_count) + " trees with a duplicated id were dropped.")
    return transformed_trees

import logging
from math import pi
import yaml
import datetime

current_year = int(datetime.datetime.now().date().strftime("%Y"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_genus_mapping():
    with open("./tree_data/genus.yml", 'r', encoding='utf-8') as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.exception(f'Error occurred while reading the genus.yml: {e}')
            raise

    return conf['genus']


genus_mapping = read_genus_mapping()


def lookup_genus(species):
    return species.split(" ")[0]


def lookup_genus_german(species):
    genus = lookup_genus(species)
    print(genus_mapping)
    if genus in genus_mapping:
        return genus_mapping[genus]
    else:
        logger.info(f'{genus} not in genus mapping')
        return None


def calc_plant_year(age):
    return current_year - int(age)


def calc_trunc_circumference(diameter):
    return (pi * diameter).round(2)

def lookup_district(geometry):
    return None


calc_funs = {
    "lookup_genus": lookup_genus,
    "lookup_genus_german": lookup_genus_german,
    "calc_plant_year": calc_plant_year,
    "calc_trunc_circumference": calc_trunc_circumference,
    "lookup_district": lookup_district
}


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


def transform_new_tree_data(new_trees, attribute_list, schema_mapping_dict, schema_calculated_dict):
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

    for key, value in schema_calculated_dict.items():
        if 'inputs' in value:
            input_fields = value['inputs']
            if 'function' in value:
                calc_fun = value['function']
                for input_field in input_fields:
                    if input_field in new_trees:
                        input_value = new_trees[input_field]
                        if calc_fun in calc_funs:
                            calculated = calc_funs[calc_fun](input_value[0])
                            logger.info(f'Calculated {calculated} for input {input_value[0]} with function {calc_fun}')
                            transformed_trees[key] = calculated
                        else:
                            logger.info(f'Function {calc_fun} for calculation of {key} not among known functions')
                    else:
                        logger.info(f'Input field {input_field} for calculation of {key} not among known columns')
            else:
                logger.info(f'No function definition in calculation of {key}')
        else:
            logger.info(f'No inputs definition in calculation of {key}')

    logger.info("ℹ️ " + str(duplicates_count) + " trees with a duplicated id were dropped.")
    return transformed_trees



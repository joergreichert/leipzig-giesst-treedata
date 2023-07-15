import logging
from math import pi

import pandas
import yaml
import datetime

from .geo_within import get_district

current_year = int(datetime.datetime.now().date().strftime("%Y"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_config():
    with open("./resources/conf.yml", 'r') as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.exception(f'Error occurred while reading the conf.yml: {e}')
            raise

    schema_mapping_dict = conf['data-schema']['mapping']
    schema_calculated_dict = conf['data-schema']['calculated']

    return schema_mapping_dict, schema_calculated_dict


def read_genus_mapping():
    with open("./resources/genus.yml", 'r', encoding='utf-8') as stream:
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
    if genus in genus_mapping:
        return genus_mapping[genus]
    else:
        logger.info(f'{genus} not in genus mapping')
        return None


def calc_plant_year(age):
    try:
        return current_year - int(age)
    except:
        return 'undefined'


def calc_trunc_circumference(diameter):
    try:
        return (pi * diameter).round(2)
    except:
        return 'undefined'


def lookup_district(geometry, city_shape):
    return get_district(
        geometry.x.round(5),
        geometry.y.round(5),
        city_shape
    )


calc_funs = {
    "lookup_genus": lookup_genus,
    "lookup_genus_german": lookup_genus_german,
    "calc_plant_year": calc_plant_year,
    "calc_trunc_circumference": calc_trunc_circumference,
    "lookup_district": lookup_district
}


def transform_new_tree_data(new_trees, attribute_list, schema_mapping_dict, schema_calculated_dict, city_shape):
    transformed_trees = new_trees.rename(columns=schema_mapping_dict)

    # transform gml_id here
    transformed_trees['id'] = transformed_trees['standort_nr'].str.split(pat=".").str[1]

    # drop not needed columns based on the columns of the old data
    for column in transformed_trees.columns:
        if column == "geometry":
            continue
        else:
            if column not in attribute_list:
                try:
                    transformed_trees = transformed_trees.drop([column], axis=1)
                except:
                    logger.error(f'{column} not found')

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
                    logger.error(f'{column} has type {transformed_trees[column].dtype}')
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
                        input_values = new_trees[input_field]
                        if calc_fun in calc_funs:
                            for index, input_value in enumerate(input_values):
                                if calc_fun == 'lookup_district':
                                    calculated = calc_funs[calc_fun](input_value, city_shape)
                                else:
                                    calculated = calc_funs[calc_fun](input_value)
                                #logger.info(f'Calculated {calculated} for input {input_value} with function {calc_fun}')
                                calculatedSeries = pandas.Series([calculated], index=[index])
                                transformed_trees[key] = calculatedSeries
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



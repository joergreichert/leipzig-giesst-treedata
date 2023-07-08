import logging
import os

import geopandas as gpd
from dotenv import load_dotenv
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def start_db_connection():
    load_dotenv()
    for env_var in ["PG_DB", "PG_PORT", "PG_USER", "PG_PASS", "PG_DB"]:
        if env_var not in os.environ:
            logger.error(f"Environmental variable {env_var} does not exist")
    pg_server = os.getenv("PG_SERVER")
    pg_port = os.getenv("PG_PORT")
    pg_username = os.getenv("PG_USER")
    pg_password = os.getenv("PG_PASS")
    pg_database = os.getenv("PG_DB")

    conn_string = f"postgresql://{pg_username}:{pg_password}@{pg_server}:{pg_port}/{pg_database}"

    conn = create_engine(conn_string)
    try:
        conn.execute("SET statement_timeout TO 30000")
        logger.info("Statement timeout increased to 30 seconds")

        conn.connect()
        logger.info("Database connection established")

        return conn
    except:
        msg = f"Could not establish a database connection to {conn_string}"
        logger.error(msg)
        raise Exception(msg)


def add_to_db(conn, result, table_name):
    result['geometry'] = gpd.points_from_xy(result.lat, result.lng)
    result = result.rename(columns={'geometry': 'geom'}).set_geometry('geom')
    result.to_postgis('added_trees_tmp', conn, if_exists='replace', index=False)
    try:
        # execute sql query for adding the data
        sql = "UPDATE added_trees_tmp SET geom = ST_SetSRID(geom,4326)"

        # there is a problem with uppercase header names, so we have to bring all column names to "" here
        conn.execute(sql)
        cols = ''
        for c in result.columns:
            cols += '"%s", ' % c
        cols = cols[:-2]

        append_sql = f"INSERT INTO {table_name}({cols}) SELECT * FROM added_trees_tmp"
        conn.execute(append_sql)

        logger.info(
            "Successfully added " + str(len(result)) + " new trees to the database table '" + table_name + "'.")

    except Exception as e:
        logger.info('No trees to add.')
        logging.exception('Error occurred while adding trees to database: {}'.format(e))

    # delete the temporary table
    sql = 'DROP TABLE added_trees_tmp'
    conn.execute(sql)


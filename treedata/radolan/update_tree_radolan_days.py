import json
from datetime import datetime
from datetime import timedelta
import logging
import psycopg2
import psycopg2.extras
from sqlalchemy import text

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# get all grid cells, get data for last 30 days for each grid cell,
# generate a list for each grid cell
# as we don't store "0" events, those need to be generated,
# afterwards trees are updated and a geojson is being created

def get_weather_data_grid_cells(engine, time_limit_days):
    with engine.connect() as conn:
        result = conn.execute(text(f'''
            SELECT 
                radolan_geometry.id, 
                ST_AsGeoJSON(radolan_geometry.geometry), 
                ARRAY_AGG(radolan_data.measured_at) AS measured_at, 
                ARRAY_AGG(radolan_data.value) AS value 
            FROM radolan_geometry 
            JOIN radolan_data ON radolan_geometry.id = radolan_data.geom_id 
            WHERE radolan_data.measured_at > NOW() - INTERVAL '{time_limit_days} days' 
            GROUP BY radolan_geometry.id, radolan_geometry.geometry
        '''))
        return result.fetchall()


def get_sorted_cleaned_grid(grid, time_limit_days, now=datetime.now()):
    clean = []
    for cell in grid:
        end_date = now
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = now + timedelta(days=-time_limit_days+1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        clean_data = []
        while start_date <= end_date:
            found = False
            for dateindex, date in enumerate(cell[2]):
                if start_date == date:
                    found = True
                    clean_data.append(cell[3][dateindex])
                    break
                    # TODO: Add the algorithm that calculates the actually absorbed amount of water (upper & lower threshold)
            if not found:
                clean_data.append(0)
            start_date += timedelta(days=1)
        clean.append(clean_data)
    return clean


def get_sorted_cleaned_grid_cells(cleaned_grid, grid):
    cells = []
    for cellindex, cell in enumerate(grid):
        cells.append([
            cleaned_grid[cellindex],
            sum(cleaned_grid[cellindex]),
            cell[1]
        ])
    return cells


def update_statistics_db(filelist, engine, time_limit_days, last_received):
    if len(filelist) > 0:
        end_date = datetime.now() + timedelta(days=-1)
        end_date = end_date.replace(hour=23, minute=50, second=0, microsecond=0)
        start_date = datetime.now() + timedelta(days=-time_limit_days)
        start_date = start_date.replace(hour=0, minute=50, second=0, microsecond=0)
        datetime_format = "%Y-%m-%d %H:%M:%S"
        with engine.connect() as conn:
            conn.execute(text(f'''
                UPDATE radolan_harvester SET 
                    collection_date = '{last_received.strftime(datetime_format)}', 
                    start_date = '{start_date.strftime(datetime_format)}', 
                    end_date = '{end_date.strftime(datetime_format)}' 
                WHERE id = 1
            '''))
            conn.commit()


def update_tree_radolan_days_for_query(engine, values, query, info):
    logging.info(info)
    try:
        with engine.connect() as conn:
            for index, value in enumerate(values):
                try:
                    resolved_query = query.format(f"ARRAY{value[0]}", value[1], value[2])
                    result = conn.execute(text(resolved_query))
                    conn.commit()
                    logger.info(f"Updated {index}. radolan square: {result.rowcount} trees affected")
                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(f"Error: {error}")
    except:
        logging.error("❌Could not update radolan days")


def update_tree_radolan_days(engine, values):
    first_query = '''
        UPDATE trees SET radolan_days = {}, radolan_sum = {} 
        WHERE ST_CoveredBy(geom, ST_SetSRID(ST_GeomFromGeoJSON('{}'), 4326))
    '''
    first_info = "updating trees 🌳"
    update_tree_radolan_days_for_query(engine, values, first_query, first_info)
    second_query = '''
        UPDATE trees SET radolan_days = {}, radolan_sum = {} 
        WHERE trees.radolan_sum IS NULL 
        AND ST_CoveredBy(geom, 
            ST_Buffer(ST_SetSRID(ST_GeomFromGeoJSON('{}'), 4326), 0.00005)
        )
    '''
    second_info = "updating sad trees 🌳"
    update_tree_radolan_days_for_query(engine, values, second_query, second_info)
